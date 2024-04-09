import os
import unittest

from modelbest_sdk.dataset.mbtable_iterable_dataset import MBTableIterableDataset
from modelbest_sdk.dataset.sampler.weighted_dataset import WeightedDataset
from modelbest_sdk.dataset.table_record_dataset import TableRecordDataset
from modelbest_sdk.dataset.thrift_wrapper.dataset_context import DatasetContext
from modelbest_sdk.dataset.thrift_wrapper.dataset_checkpoint import Chunk, DatasetCheckpointList, DatasetInfo, DatasetInfoList
from modelbest_sdk.dataset.thrift_wrapper.dataset_context import DatasetContext
from test.test_base import TestBase

class TestCheckpoint(TestBase):
    def test_simple_dataset_checkpoint(self):
        # dataset has 20 records, each records length is 7, max_epoch is 1
        # context suggest to use 16 as batch size * max len, so every 2 records will be grouped into one batch
        context = DatasetContext.load_from_file(self.simple_dataset_context_path)
        dataset = TableRecordDataset(context, batch_size=1, max_len=16, prefetch_factor=1, cuda_prefetch=False)
        for i, batch in enumerate(dataset, start=1):
            dataset.update(batch['indexes'])
            if i == 5:
                break
        dataset.save()
        
        assert dataset.checkpoint().checkpoint_list[0].used.active == {Chunk(epoch=0, start=0, stop=20): {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}}
        
        context = DatasetContext.load_from_file(self.simple_dataset_context_path)
        dataset = TableRecordDataset(context, batch_size=1, max_len=16, cuda_prefetch=False)
        dataset.resume()

        for i, batch in enumerate(dataset, start=1):
            dataset.update(batch['indexes'])
            
        assert dataset.checkpoint().checkpoint_list[0].used.active == {}
        assert dataset.checkpoint().checkpoint_list[0].used.done == {0: {Chunk(epoch=0, start=0, stop=20)}}


    def test_dist_dataset_checkpoint(self):
        context = DatasetContext.load_from_file(self.dist_dataset_context_path)
        dataset = TableRecordDataset(context, batch_size=1, max_len=16, cuda_prefetch=False)
        for i, batch in enumerate(dataset, start=1):
            dataset.update(batch['indexes'])
            print(batch)
            if i == 5:
                break


if __name__ == '__main__':
    unittest.main()