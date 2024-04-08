import os
import asyncio
from asyncio_pool import AioPool
import time
from metaapi_cloud_sdk import MetaApi
from metaapi_cloud_sdk.metaApi.reservoir.reservoir import Reservoir
from metaapi_cloud_sdk.clients.metaApi.synchronizationListener import SynchronizationListener
from metaapi_cloud_sdk.metaApi.models import MetatraderDeal, random_id
from metaapi_cloud_sdk.metaApi.metaApiConnection import MetaApiConnection
from metaapi_cloud_sdk.metaApi.metatraderAccount import MetatraderAccount
from metaapi_cloud_sdk.metaApi.historyStorage import HistoryStorage
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from functools import reduce
from datetime import datetime
from typing import List
from multiprocessing import Process
import math
import logging
import json
from random import random
import sys
from collections import deque


token = os.getenv("TOKEN_CLIENT")

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        temp_linebuf = self.linebuf + buf
        self.linebuf = ''
        for line in temp_linebuf.splitlines(True):
            # From the io.TextIOWrapper docs:
            #   On output, if newline is None, any '\n' characters written
            #   are translated to the system default line separator.
            # By default sys.stdout.write() expects '\n' newlines and then
            # translates them so this is still cross platform.
            if line[-1] == '\n':
                self.logger.log(self.log_level, line.rstrip())
            else:
                self.linebuf += line

    def flush(self):
        if self.linebuf != '':
            self.logger.log(self.log_level, self.linebuf.rstrip())
        self.linebuf = ''

logging.basicConfig(filename='./logs/script.log',
                    filemode='a',
                    format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

logging.getLogger('asyncio').setLevel(logging.DEBUG)
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('root').setLevel(logging.DEBUG)
logging.getLogger('stdout').setLevel(logging.DEBUG)
stdout_logger = logging.getLogger('STDOUT')
sl = StreamToLogger(stdout_logger, logging.INFO)
sys.stdout = sl

logger_status = logging.getLogger('status_log')
logger_accounts = logging.getLogger('account_log')


class NullOpHistoryStorage(HistoryStorage):
    async def load_data_from_disk(self):
        pass
    async def clear(self):
        pass
    async def last_history_order_time(self, instance_index: int = None):
        return datetime.utcnow()
    async def last_deal_time(self, instance_index: int = None):
        return datetime.utcnow()
    async def on_history_order_added(self, instance_index: int, history_order):
        pass
    async def on_deal_added(self, instance_index: int, deal):
        pass
    async def on_deal_synchronization_finished(self, instance_index: int, synchronization_id: str):
        pass
    async def update_disk_storage(self):
        pass

class ConnectionManager:
    def __init__(self, pid: str, index: int):
        self._pid = pid
        self._index = index
        self._connections = {}
        self._last_healthy_at = {}
        self._pending_connections = []
        self._pool_size = 40
        self._counter = 0
        self._accounts_launched = 0
        self._accounts_per_process = 700
        self._total_initialization_time = 0
        self._start_time = time.time()
        self._os_times = os.times()
        self.health_reservoirs = {
            'connected': Reservoir(24 * 7, 7 * 24 * 60 * 60 * 1000),
            'connectedToBroker': Reservoir(24 * 7, 7 * 24 * 60 * 60 * 1000),
            'quoteStreamingHealthy': Reservoir(24 * 7, 7 * 24 * 60 * 60 * 1000),
            'synchronized': Reservoir(24 * 7, 7 * 24 * 60 * 60 * 1000)
        }
        self.stats = {
            'healthy': 0,
            'synchronized': 0,
            'total': 0
        }
        asyncio.create_task(self.status_job())
        asyncio.create_task(self.record_health_job())
        asyncio.create_task(self.display_health_job())

    async def record_health_job(self):
        while True:
            stats = {
                'connected': 0,
                'connectedToBroker': 0,
                'quoteStreamingHealthy': 0,
                'synchronized': 0
            }
            connection_amount = len(self._connections.values())
            if connection_amount:
                for connection in self._connections.values():
                    health_status = connection.health_monitor.health_status
                    if health_status['connected']:
                        stats['connected'] += 1
                    if health_status['connectedToBroker']:
                        stats['connectedToBroker'] += 1
                    if health_status['quoteStreamingHealthy']:
                        stats['quoteStreamingHealthy'] += 1
                    if health_status['synchronized']:
                        stats['synchronized'] += 1

                for key in stats.keys():
                    self.health_reservoirs[key].push_measurement(stats[key] / connection_amount)
            await asyncio.sleep(1)

    async def display_health_job(self):
        while True:
            avg_stats = {
                'connected': 0,
                'connectedToBroker': 0,
                'quoteStreamingHealthy': 0,
                'synchronized': 0
            }
            for key in avg_stats.keys():
                avg_stats[key] = f'{round(self.health_reservoirs[key].get_statistics()["average"] * 100, 2)}%'
            print(f'Average stats {self._pid} {self._index} {avg_stats}')
            await asyncio.sleep(60)

    async def status_job(self):
        while True:
            account_amount = len(self._connections.values())
            if account_amount:
                def reducer_func_healthy(acc, connection: MetaApiConnection):
                    healthy = connection.health_monitor.health_status['healthy']
                    return acc + (1 if healthy else 0)

                def reducer_func_synchronized(acc, connection: MetaApiConnection):
                    return acc + (1 if connection.synchronized else 0)
                healthy_accounts = reduce(reducer_func_healthy, self._connections.values(), 0)
                synchronized_accounts = reduce(reducer_func_synchronized, self._connections.values(), 0)
                self.stats['healthy'] = healthy_accounts
                self.stats['synchronized'] = synchronized_accounts
                self.stats['total'] = account_amount
                if 0 < self.stats['synchronized'] - self.stats['healthy'] < 10:
                    for connection in self._connections.values():
                        if not connection.health_monitor.health_status['healthy']:
                            print(f'Account unhealthy {connection.account.id} {datetime.now().isoformat()} '
                                  f'{json.dumps(connection.health_monitor.health_status)}')
            await asyncio.sleep(10)

    def is_connected(self, accountId):
      return accountId in self._connections

    def connect(self, account):
      self._pending_connections.append(account)

    async def process_connections(self, api):
      await asyncio.sleep(random() * 15)
      futures = []
      async with AioPool(size = self._pool_size) as pool:
        while self._accounts_launched < self._accounts_per_process and len(self._pending_connections) > 0:
          account = None
          if len(self._pending_connections) > 0:
            account = self._pending_connections[0]
          if account is None:
            time.sleep(5)
          else:
            futures.append(await pool.spawn(self.synchronize_account(api, account)))
            self._accounts_launched += 1
            del self._pending_connections[0]
      for f in futures:
        f.result()

    async def synchronize_account(self, api, account):
        synchronized = False
        while not synchronized:
            try:
                await account.wait_connected()
                connection = await account.connect(history_storage=NullOpHistoryStorage())
                deal_listener = DealListener(account)
                connection.add_synchronization_listener(deal_listener)
                self._connections[account.id] = connection
                # most likely next line is not needed for your app, so that it is commented out
                await connection.wait_synchronized({'timeoutInSeconds': 600})
                await connection.subscribe_to_market_data(symbol='EURUSD')
                synchronized = True
                self._counter += 1
                self._total_initialization_time += time.time() - self._start_time
                logger_accounts.info(f'{self._pid} {self._index} Finished syncing %s accounts' % (self._counter) + account.id)
                #print("Launched %s accounts, avg startup time is %s" % (self._counter, self._total_initialization_time / self._counter))
                #print("Average CPU load was %s percents" % ((os.times()[0] + os.times()[1] - self._os_times[0] - self._os_times[1]) / (time.time() - self._start_time) * 100))
            except Exception as err:
                logger_accounts.error(api.format_error(err))
                if err.__class__.__name__ == 'TooManyRequestsException':
                    await asyncio.sleep(random() * 15)
            await asyncio.sleep(5)


class DealListener(SynchronizationListener):

    def __init__(self, account):
        self._id = account.id
        self._synchronized = False

    async def on_connected(self, instance_index: int, replicas: int):
        pass
        # print('CONNECTED', self._id)

    async def on_disconnected(self, instance_index: int):
        self._synchronized = False
        pass
        # print('DISCONNECTED', self._id, datetime.now().isoformat())

    async def on_deal_synchronization_finished(self, instance_index: int, synchronization_id: str):
        pass
        if not self._synchronized:
            print(f'ACCOUNT SYNCHRONIZED {self._id} {datetime.now().isoformat()}')
            self._synchronized = True

    async def on_deal_added(self, instanceIndex: int, deal: MetatraderDeal):
        # print('Deal', self._id)
        pass


def process_task(account_indices: List[int]):
    print('ACCOUNT INDICES', account_indices)

    async def status_job(pid, managers):
        while True:
            total_stats = {
                'healthy': reduce(lambda acc, manager: acc + manager.stats["healthy"], managers, 0),
                'synchronized': reduce(lambda acc, manager: acc + manager.stats["synchronized"], managers, 0),
                'total': reduce(lambda acc, manager: acc + manager.stats["total"], managers, 0),
            }
            logger_status.info(f'Stats for process id {pid} {datetime.now().isoformat()} ' +
                  json.dumps(list(map(lambda manager: f'{manager.stats["healthy"]}/{manager.stats["synchronized"]}/'
                           f'{manager.stats["total"]}', managers))) + f' total: {total_stats["healthy"]}/'
                                                                              f'{total_stats["synchronized"]}/'
                                                                              f'{total_stats["total"]}')
            await asyncio.sleep(10)

    async def task_coroutine():
        process_id = random_id(5)
        logger_status.info(f'Launching process {process_id} with {account_indices[1] - account_indices[0]} accounts')
        api_count = 4
        apis = []
        managers = []
        coroutines = []
        accounts_amount = (account_indices[1] - account_indices[0])
        api_account_indices = []
        accounts_per_api = math.ceil(accounts_amount / api_count)
        for i in range(api_count):
            api_account_indices.append([account_indices[0] +
                                        i * accounts_per_api, min(account_indices[0] + i * accounts_per_api +
                                                                  accounts_per_api,
                                                                  account_indices[0] + accounts_amount)])

        for i in range(api_count):
            api = MetaApi(token, {'application': 'MetaApi', 'maxConcurrentSynchronizations': 5})
            apis.append(api)
            managers.append(ConnectionManager(process_id, i))
            print('Indices', api_account_indices[i])
            accounts = await apis[i].metatrader_account_api.get_accounts(accounts_filter={
                "offset": api_account_indices[i][0], "limit": api_account_indices[i][1] - api_account_indices[i][0],
                "state": ["DEPLOYED"]})
            for x in range(len(accounts)):
                account = accounts[x]
                managers[i].connect(account)

        for i in range(len(managers)):
            coroutines.append(managers[i].process_connections(apis[i]))

        asyncio.create_task(status_job(process_id, managers))

        await asyncio.gather(*coroutines)

    process_loop = asyncio.new_event_loop()
    process_loop.create_task(task_coroutine())
    process_loop.run_forever()


async def synchronize_accounts():
    print(f'Launch date {datetime.now().isoformat()}')
    try:
        api = MetaApi(token, {'application': 'MetaApi'})

        process_count = 2
        accounts = await api.metatrader_account_api.get_accounts(accounts_filter={"offset": 0, "limit": 1000, "state": ["DEPLOYED"]})
        print(len(accounts))
        accounts_per_process = math.ceil(len(accounts) / process_count)
        account_indices = []
        for i in range(process_count):
            account_indices.append([i * accounts_per_process, min(i * accounts_per_process + accounts_per_process,
                                                                  len(accounts))])
        procs = []
        for i in range(process_count):
            proc = Process(target=process_task, args=(account_indices[i],))
            procs.append(proc)
            proc.start()

        for proc in procs:
            proc.join()

    except Exception as err:
        print(err)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(synchronize_accounts())
    loop.run_forever()
