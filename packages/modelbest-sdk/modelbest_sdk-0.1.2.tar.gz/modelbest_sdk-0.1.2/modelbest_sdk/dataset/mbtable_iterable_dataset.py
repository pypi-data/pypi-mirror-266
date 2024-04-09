import itertools
import math
import operator
import random
import threading
import time
from typing import List
import torch
from modelbest_sdk.dataset.cache import AllCached, CacheFull, CacheNotFilled, PrefetchCache
from modelbest_sdk.dataset.range import Range
from modelbest_sdk.dataset.thrift_wrapper.base_doc import BaseDoc
from modelbest_sdk.dataset.thrift_wrapper.dataset_checkpoint import *
from modelbest_sdk.dataset.thrift_wrapper.dataset_context import DatasetContext
from modelbest_sdk.dataset.utils import get_worker_info
from modelbest_sdk.file_format.mbtable import MbTable, MbTableIterator
from modelbest_sdk.file_format.mbtable_partition import MbTablePartition, MbTablePartitionIterator


class MBTableIterableDataset(torch.utils.data.IterableDataset):
    def __init__(
        self, 
        context: DatasetContext, 
        path, 
        max_epoch,
        prefetch_chunk_cnt=20, 
        chunk_size=1024):
        
        self.context = context
        self.path = path
        self.max_epoch = max_epoch
        
        self.is_dir = os.path.isdir(path)
        if self.is_dir:
            self.mbtable_partition = MbTablePartition(path)
            self._length = self.mbtable_partition.get_total_count()
        
        else:
            self.mbtable = MbTable(path)
            self._length = self.mbtable.get_entry_count()
        
        self.prefetch_chunk_cnt = prefetch_chunk_cnt
        self.chunk_size, self.num_chunks = self.safe_chunk_size(chunk_size)
        
        self.cache = None
        self.exhausted = False
        self.used = Used()
        
    def __len__(self):
        return self._length
    
    def get_chunk_data(self, chunk):
        assert isinstance(chunk, Chunk)
        start_index = chunk.start
        max_iter = chunk.stop - chunk.start
        ret = []
        # print(f"start_index: {start_index}, max_iter: {max_iter}")
        if self.is_dir:
            with MbTablePartitionIterator(self.mbtable_partition, start_index, max_iter) as iter:
                for record in iter:
                    ret.append(record)
        else:
            with MbTableIterator(self.path, start_index, max_iter) as iter:
                for record in iter:
                    ret.append(record)
        return ret
    
    def __iter__(self):
        self.init_epoch()
        prefetch_thread = threading.Thread(target=self.prefetch)
        prefetch_thread.start()
        while True:
            try:
                chunk_data = self.cache.get()
                for data in chunk_data:
                    yield data
            except CacheNotFilled:
                time.sleep(0.1)
            except StopIteration:
                self.exhausted = True
                return
    
    def init_epoch(self):
        if self.used.epoch >= self.max_epoch:
            self.exhausted = True
        self.cache = PrefetchCache(size=self.prefetch_chunk_cnt)
        chunks = itertools.chain.from_iterable(
            (self.random_chunks(epoch) for epoch in range(self.used.epoch, self.max_epoch))
        )
        chunks = itertools.filterfalse(
            lambda chunk: chunk in self.used.done.get(chunk.epoch, set()), chunks
        )
        self.cache.submit(chunks)

    def safe_chunk_size(self, chunk_size):
        total_workers = self.context.num_workers * self.context.world_size
        if len(self) < total_workers:
            raise ValueError(
                f"more concurrent loaders ({total_workers}) than " f"data entries ({len(self)}) in '{self.path}'"
            )
        num_chunks = math.ceil(len(self) / chunk_size)
        if num_chunks <= total_workers:
            chunk_size = math.ceil(len(self) / total_workers)
            num_chunks = math.ceil(len(self) / chunk_size)
        return chunk_size, num_chunks

    def random_chunks(self, epoch):
        world_size = self.context.world_size
        rank = self.context.rank
        num_workers, worker_id = get_worker_info()
        # we only iteratre through start ids as they uniquely mark each slice
        r = Range(0, len(self), self.chunk_size)
        # split index among multi-gpu workers
        r = r.subrange(split=rank, nsplits=world_size)
        # split index among multi-process dataloader workers
        r = r.subrange(split=worker_id, nsplits=num_workers)
        # obtain random chunks
        chunks = (Chunk(epoch, st, min(st + self.chunk_size, len(self))) for st in r.random_iterate())
        return chunks

    def prefetch(self):
        while True:
            try:
                chunk = self.cache.pull_task()
                chunk_data = self.get_chunk_data(chunk)
                unused_chunk_data = [
                    dict(chunk=chunk, index=i, doc=BaseDoc.deserialize(data))
                    for i, data in zip(range(chunk.start, chunk.stop), chunk_data)
                    if (data is not None) and (i not in self.used.active.get(chunk, set()))
                ]
                self.cache.put_result(unused_chunk_data)
            except CacheFull:
                time.sleep(0.1)
            except AllCached:
                break

    def checkpoint(self):
        return DatasetCheckpoint(
            dataset_info=DatasetInfo(
                path=self.path, 
                max_epoch=self.max_epoch),
            used=self.used, 
            chunk_size=self.chunk_size, 
            num_chunks=self.num_chunks
            )
    
    def load_checkpoint(self, checkpoint: DatasetCheckpoint):
        if len(checkpoint.used.active) == 0 and len(checkpoint.used.done) == 0:
            self.used.epoch = 0
        else:
            epochs_not_exhausted = set()
            for chunk in checkpoint.used.active.keys():
                epochs_not_exhausted.add(chunk.epoch)
            epoch = 0
            for epoch in sorted(list(checkpoint.used.done.keys())):
                if len(checkpoint.used.done[epoch]) == checkpoint.num_chunks:
                    del checkpoint.used.done[epoch]
                else:
                    epochs_not_exhausted.add(epoch)
                    break
        epochs_not_exhausted.add(epoch + 1)
        checkpoint.used.epoch = min(epochs_not_exhausted, default=0)
        self.used = checkpoint.used        
    
    def update(self, entries: Dict[Chunk, List[int]]):
        for chunk, indexes in entries.items():
            self.used.active.setdefault(chunk, set()).update(set(indexes))
            
            if len(self.used.active[chunk]) == chunk.stop - chunk.start:
                self.used.done.setdefault(chunk.epoch, set()).add(chunk)
                del self.used.active[chunk]
            
            for epoch in range(chunk.epoch - 1, 0, -1):
                cur_chunk = Chunk(epoch, chunk.start, chunk.stop)
                if cur_chunk in self.used.active:
                    del self.used.active[cur_chunk]
                    self.used.done.setdefault(epoch, set()).add(cur_chunk)
                else:
                    break
    

if __name__ == '__main__':
    context = DatasetContext(world_size=1, rank=0, num_workers=1)
    dataset = MBTableIterableDataset(
        context=context, 
        path="/home/emr-user/modelbest_sdk/test/base_doc_simple",
        max_epoch=3)
    i = 0
    for data in dataset:
        entries = {data['chunk']: [data['index']]}
        dataset.update(entries=entries)
        i += 1
        if i == 29:
            checkpoint = dataset.checkpoint()
            break
    
    print(checkpoint)
    dataset_next = MBTableIterableDataset(
        context=context, 
        path="/home/emr-user/modelbest_sdk/test/base_doc_simple",
        max_epoch=3)
    dataset_next.load_checkpoint(checkpoint)
    for data in dataset_next:
        entries = {data['chunk']: [data['index']]}
        dataset_next.update(entries=entries)
        i += 1
        print(data)
        if i == 59:
            break
    checkpoint = dataset_next.checkpoint()
    print(checkpoint)