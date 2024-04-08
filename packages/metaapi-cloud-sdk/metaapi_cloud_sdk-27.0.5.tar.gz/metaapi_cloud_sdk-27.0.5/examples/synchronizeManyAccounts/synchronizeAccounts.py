import os
import asyncio
from asyncio_pool import AioPool
import time
from metaapi_cloud_sdk import MetaApi
from metaapi_cloud_sdk.clients.metaApi.synchronizationListener import SynchronizationListener
from metaapi_cloud_sdk.metaApi.models import MetatraderDeal

token = os.getenv("TOKEN")

class ConnectionManager:
    def __init__(self):
      self._connections = {}
      self._pending_connections = []
      self._pool_size = 50
      self._counter = 0
      self._accounts_launched = 0
      self._accounts_per_process = 700
      self._total_initialization_time = 0
      self._start_time = time.time()
      self._os_times = os.times()

    def is_connected(self, accountId):
      return accountId in self._connections

    def connect(self, account):
      self._pending_connections.append(account)

    async def process_connections(self, api):
      futures = []
      async with AioPool(size = self._pool_size) as pool:
        while self._accounts_launched < self._accounts_per_process and len(self._pending_connections) > 0:
          account = None
          if len(self._pending_connections) > 0:
            account = self._pending_connections[0];
          if account is None:
            time.sleep(5)
          else:
            futures.append(await pool.spawn(self.synchronize_account(api, account)))
            self._accounts_launched += 1;
            del self._pending_connections[0];
      for f in futures:
        f.result()

    async def synchronize_account(self, api, account):
      launched = False
      while not launched:
        try:
          await account.wait_connected()
          connection = await account.connect()
          deal_listener = DealListener()
          connection.add_synchronization_listener(deal_listener)
          # most likely next line is not needed for your app, so that it is commented out
          #await connection.wait_synchronized();
          self._connections[account.id] = True
          self._counter += 1
          self._total_initialization_time += time.time() - self._start_time
          print("Launched %s accounts, avg startup time is %s" % (self._counter, self._total_initialization_time / self._counter))
          print("Average CPU load was %s percents" % ((os.times()[0] + os.times()[1] - self._os_times[0] - self._os_times[1]) / (time.time() - self._start_time) * 100))
          launched = True
        except Exception as err:
          print(api.format_error(err))

class DealListener(SynchronizationListener):
    async def on_deal_added(self, instanceIndex: int, deal: MetatraderDeal):
        #print(deal)
        pass

async def synchronize_accounts():
    try:
        api = MetaApi(token)
        manager = ConnectionManager()

        accounts = await api.metatrader_account_api.get_accounts(accounts_filter={"offset": 0, "limit": 1000, "state": ["DEPLOYED"]})

        accounts.sort(key = lambda account: account.id)

        for account in accounts:
          manager.connect(account)

        await manager.process_connections(api)

    except Exception as err:
        print(api.format_error(err))

loop = asyncio.get_event_loop()
loop.create_task(synchronize_accounts())
loop.run_forever()
