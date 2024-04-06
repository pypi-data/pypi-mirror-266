import os, pickle
from multiprocessing import shared_memory, managers

class Server():
    def __init__(self, dataloader, name='server_share_data', address=('127.0.0.1', 5566), authkey=b'server_torch_manager'):
        SyncManager = managers.SyncManager
        SyncManager.register('next', self.next)
        self.manager = SyncManager(address=address, authkey=authkey)
        self.share_name = name
        self.data_name = 'server_torch_data'
        self.pid = os.getpid()
        self.address = address
        self.authkey = authkey

        shared_data = {
            'pid': self.pid,
            'address': self.address,
            'authkey': self.authkey,
        }
        shared_data_pkl = pickle.dumps(shared_data)

        self.shm_shared_data = shared_memory.SharedMemory(self.share_name, create=True, size=len(shared_data_pkl))
        self.shm_shared_data.buf[:] = shared_data_pkl[:]

        self.dataloader = dataloader
        self.size = 4096
        self.shm_data = shared_memory.SharedMemory(name=self.data_name, create=True, size=self.size)
        self.iterloader = iter(self.dataloader)

        self.manager.get_server().serve_forever()

    def next(self):
        try:
            data = next(self.iterloader)
        except StopIteration:
            self.iterloader = iter(self.dataloader)
            data = next(self.iterloader)
        data_pkl = pickle.dumps(data)
        data_len = len(data_pkl)

        if data_len > self.size:
            self.shm_data.close()
            self.shm_data.unlink()
            self.shm_data = shared_memory.SharedMemory(name=self.data_name, create=True, size=data_len)
            self.size = data_len

        self.shm_data.buf[:data_len] = data_pkl

class Client():
    def __init__(self):
        self.share_name = 'server_share_data'
        self.data_name = 'server_torch_data'

        self.shm_shared_data = shared_memory.SharedMemory(self.share_name)

        self.shared_data = pickle.loads(self.shm_shared_data.buf)
        address = self.shared_data['address']
        authkey = self.shared_data['authkey']

        SyncManager = managers.SyncManager
        SyncManager.register('next')

        self.manager = SyncManager(address=address, authkey=authkey)
        self.manager.connect()

    def next(self):
        self.manager.next()
        self.shm_data = shared_memory.SharedMemory(self.data_name)
        data = pickle.loads(self.shm_data.buf)
        self.shm_data.close()
        return data
