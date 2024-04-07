import ctypes
import os

class ByteArray(ctypes.Structure):
    _fields_ = [("data", ctypes.POINTER(ctypes.c_char)),
                ("length", ctypes.c_size_t)]

lib_path = os.path.join(os.path.dirname(__file__), 'lib', 'libmbtable_sdk_shared.so')
lib = ctypes.CDLL(lib_path)


lib.MbTableOpen.argtypes = [ctypes.c_char_p]
lib.MbTableOpen.restype = ctypes.c_void_p

lib.MbTableClose.argtypes = [ctypes.c_void_p]
lib.MbTableClose.restype = None

lib.MbTableRead.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
lib.MbTableRead.restype = ctypes.POINTER(ByteArray)

lib.MbTableGetMetaData.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
lib.MbTableGetMetaData.restype = ctypes.POINTER(ByteArray)

lib.MbTableGetEntryCount.argtypes = [ctypes.c_void_p]
lib.MbTableGetEntryCount.restype = ctypes.c_int32

lib.MbTableCreateIterator.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
lib.MbTableCreateIterator.restype = ctypes.c_void_p

lib.IteratorGetRecord.argtypes = [ctypes.c_void_p]
lib.IteratorGetRecord.restype = ctypes.POINTER(ByteArray)

lib.IteratorHasNext.argtypes = [ctypes.c_void_p]
lib.IteratorHasNext.restype = ctypes.c_bool

lib.IteratorNext.argtypes = [ctypes.c_void_p]
lib.IteratorNext.restype = None

lib.IteratorDelete.argtypes = [ctypes.c_void_p]
lib.IteratorDelete.restype = None

lib.FreeByteArray.argtypes = [ctypes.POINTER(ByteArray)]
lib.FreeByteArray.restype = None

class MbTable:
    def __init__(self, path: str, max_retry=5):
        self.path = path
        self.max_retry = max_retry
        
    def get_handle(self):
        self.handle = lib.MbTableOpen(self.path.encode('utf-8'))
        retry = 0
        while not self.handle and retry < self.max_retry:
            retry += 1
            print('Failed to open mbtable, retrying in 5 second')
            import time
            import random
            time.sleep(random.randint(1, 5))
            self.handle = lib.MbTableOpen(self.path.encode('utf-8'))
        if not self.handle:
            raise Exception('Failed to open mbtable after {} retries'.format(self.max_retry))

        return self.handle

    def read(self, index):
        '''
        only use this method if you seek few non-sequential records, otherwise use iterator
        '''
        self.get_handle()
        value_bytes = lib.MbTableRead(self.handle, index).contents
        value = ctypes.string_at(value_bytes.data, value_bytes.length)
        lib.FreeByteArray(value_bytes)
        self.close()
        return value

    def get_metadata(self, metadata_key):
        self.get_handle()
        key_bytes = metadata_key.encode('utf-8')
        value_bytes = lib.MbTableGetMetaData(self.handle, key_bytes).contents
        value = ctypes.string_at(value_bytes.data, value_bytes.length)
        lib.FreeByteArray(value_bytes)
        self.close()
        return value

    def get_entry_count(self):
        self.get_handle()
        count = lib.MbTableGetEntryCount(self.handle)
        self.close()
        return count

    def close(self):
        if self.handle:
            lib.MbTableClose(self.handle)
            self.handle = None

class MbTableIterator:
    def __init__(self, path, start_index=0, max_iterations=None):
        self.path = path
        self.start_index = start_index
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.iterator = None
        self.mbtable = None

    def __enter__(self):
        self.mbtable = MbTable(self.path)
        self.iterator = lib.MbTableCreateIterator(self.mbtable.get_handle(), self.start_index)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.iterator:
            lib.IteratorDelete(self.iterator)
        if self.mbtable:
            self.mbtable.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.max_iterations is not None and self.current_iteration >= self.max_iterations:
            raise StopIteration
        if lib.IteratorHasNext(self.iterator):
            self.current_iteration += 1
            value = self.get_record()
            lib.IteratorNext(self.iterator)
            return value
        else:
            raise StopIteration

    def next(self):
        # Python 2的兼容性方法
        return self.__next__()
    
    def get_record(self):
        ret = lib.IteratorGetRecord(self.iterator).contents
        record = ctypes.string_at(ret.data, ret.length)
        lib.FreeByteArray(ret)
        return record


if __name__ == '__main__':
    mbt_path = 'test/data/test.mbt'
    mbtable = MbTable(mbt_path)
    print(mbtable.get_entry_count())
    print(mbtable.read(1))
    print(mbtable.get_metadata('meta_key'))
    with MbTableIterator(mbt_path) as it:
        for record in it:
            print(record)