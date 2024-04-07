from collections import defaultdict
import numpy as np
import torch

# from modelbest_sdk.dataset.collater.collater import Collater
from modelbest_sdk.dataset.sampler.weighted_dataset import WeightedDataset
from modelbest_sdk.dataset.thrift_wrapper.base_doc import BaseDoc
from modelbest_sdk.dataset.thrift_wrapper.dataset_checkpoint import *
from modelbest_sdk.dataset.thrift_wrapper.dataset_context import DatasetContext


class BatchedDataset(torch.utils.data.IterableDataset):
    def __init__(self, context, weighted_dataset, batch_size, max_len, drop_last=False):
        self.context = context
        self.weighted_dataset = weighted_dataset
        self.max_total_length = batch_size * max_len
        self.batch_size = 1
        self.drop_last = drop_last
        
        
        self.buffer = []
        self.current_length = 0
        

    def put(self, data):
        self.buffer.append(data)
        self.current_length += len(data['doc'].token_ids)
    
    def pop(self):
        lengths = []
        indexes = defaultdict()
        
        inputs = torch.zeros((self.batch_size, self.max_total_length), dtype=torch.int32)
        targets = torch.full((self.batch_size, self.max_total_length), dtype=torch.int32, fill_value=-100)
        dataset_ids = torch.full((self.batch_size, self.max_total_length), dtype=torch.int32, fill_value=-1)
        position_ids = torch.zeros((self.batch_size, self.max_total_length), dtype=torch.int32)

        span_begin = 0
        while self.buffer:
            data = self.buffer.pop()
            chunk = data['chunk']
            index = data['index']
            dataset_idx = data['dataset_idx']
            doc: BaseDoc = data['doc']
            token_ids = doc.token_ids
            mask = doc.mask
            tag = doc.tag
            target_ids = [token_id if not mask_val else -100 for token_id, mask_val in zip(token_ids[1:], mask[1:])] + [-100]
            
            span_end = span_begin + len(token_ids)
            # TODO: what if the inputs is longer than max_total_length?
            # RuntimeError: The expanded size of the tensor (16) must match the existing size (385) at non-singleton dimension 0.  Target sizes: [16].  Tensor sizes: [385]
            inputs[0, span_begin:span_end] = torch.tensor(token_ids, dtype=torch.int32)
            targets[0, span_begin:span_end] = torch.tensor(target_ids, dtype=torch.int32)
            dataset_ids[0, span_begin:span_end] = torch.tensor(dataset_idx, dtype=torch.int32)
            position_ids[0, span_begin:span_end] = torch.from_numpy(np.arange(len(token_ids), dtype=np.int32))
            lengths.append(len(token_ids))
            if indexes.get(int(dataset_idx)) is None:
                indexes[int(dataset_idx)] = {}
            if indexes[int(dataset_idx)].get(chunk) is None:
                indexes[int(dataset_idx)][chunk] = []
                # TODO: better way
            indexes[int(dataset_idx)][chunk].append(index)
            span_begin = span_end
        cu_seqlens = torch.cat(
            [torch.tensor([0] + lengths).cumsum(dim=-1), torch.tensor([self.max_total_length], dtype=torch.int32)],
            dim=0,
        ).int()
        batch = {
            "inputs": inputs,
            "targets": targets,
            "dataset_ids": dataset_ids,
            "indexes": indexes,
            "cu_seqlens": cu_seqlens,
            "max_seqlen": int(torch.max(cu_seqlens[1:] - cu_seqlens[:-1])),
            "lengths": torch.tensor(sum(lengths)).int(),
            "position_ids": position_ids,
            # TODO: add tags
        }
        self.current_length = 0
        return batch
        # TODO: return data directly, and pack in collate_fn
        

    def will_exceed(self, data):
        return self.current_length + len(data['doc'].token_ids) > self.max_total_length
        

    def __iter__(self):
        for data in self.weighted_dataset:
            if self.will_exceed(data):
                yield self.pop()
            self.put(data)
        # TODO: drop last batch if it is not full

    @staticmethod
    def collate_fn(batch):
        return batch[0]
    

if __name__ == '__main__':
    context = DatasetContext(world_size=1, rank=0, num_workers=1)

    dataset_info_list = [
        DatasetInfo(
            path="/home/emr-user/modelbest_sdk/test/base_doc_simple",
            weight=1,
            max_epoch=1
        ),
        DatasetInfo(
            path="/home/emr-user/modelbest_sdk/test/base_doc_easy",
            weight=2,
            max_epoch=2
        )
    ]
    
    dataset_info_list = DatasetInfoList(dataset_info_list)
    
    w_dataset = WeightedDataset(
        context=context,
        dataset_info_list=dataset_info_list
    )
    
    dataset = BatchedDataset(
        context=context,
        weighted_dataset=w_dataset,
        batch_size=16,
        max_len=1
    )
    
    for data in dataset:
        print(data)
        print(data['indexes'].keys())
        print(data['indexes'].values())
    