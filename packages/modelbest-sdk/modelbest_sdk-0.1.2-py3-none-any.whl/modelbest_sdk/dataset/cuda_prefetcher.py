import copy
import json
from typing import Iterable
import numpy as np
import torch

from modelbest_sdk.dataset.thrift_wrapper.dataset_context import DatasetContext


class CudaPrefetcher(Iterable):
    """
    Wrap around a batch iterator for asynchornously copying data to gpu to shield memcpy latency.
    """

    def __init__(self, context: DatasetContext, loader):
        self.context = context
        self.loader = iter(loader)
        self.tp_size = context.tp_size
        self.tp_rank = context.tp_rank
        self.stream = torch.cuda.Stream()
        self.preload()

    def preload(self):
        try:
            if self.tp_size > 1:
                if self.tp_rank == 0:
                    data = next(self.loader)
                    print(f"Rank {self.context.rank}, Preload data done.")
                    d = {}
                    with open(f"/dev/shm/TP_{self.context.tp_rank}.bin", "wb") as fb:
                        for key in data.keys():
                            if isinstance(data[key], torch.Tensor):
                                np_cur_data = data[key].cpu().numpy()
                                bs = np_cur_data.tobytes()
                                fb.write(bs)
                                d[key] = ["TORCH", str(np_cur_data.dtype), len(bs)] + list(np_cur_data.shape)
                            else:
                                d[key] = data[key]
                        try:
                            _ = json.dumps(d)
                        except TypeError:
                            print(d)
                        with open(f"/dev/shm/TP_{self.context.tp_rank}.json", "w") as f:
                            json.dump(d, f)
                torch.cuda.synchronize()
                if self.tp_rank != 0:
                    with open(f"/dev/shm/TP_{self.context.tp_rank}.json", "r") as f:
                        data = json.load(f)
                    with open(f"/dev/shm/TP_{self.context.tp_rank}.bin", "rb") as fb:
                        bs = fb.read()
                        offset = 0
                        for key in data.keys():
                            if isinstance(data[key], list) and len(data[key]) > 1 and data[key][0] == "TORCH":
                                nw_offset = offset + data[key][2]
                                data[key] = torch.from_numpy(
                                    np.frombuffer(bs[offset:nw_offset], dtype=data[key][1])
                                    .reshape(data[key][3:])
                                    .copy()
                                )
                                offset = nw_offset
                self.data = data
            else:
                self.data = next(self.loader)
        except StopIteration:
            self.data = None
            return
        with torch.cuda.stream(self.stream):
            for key in self.data.keys():
                if isinstance(self.data[key], torch.Tensor):
                    self.data[key] = self.data[key].cuda(non_blocking=True)

    def __next__(self):
        torch.cuda.current_stream().wait_stream(self.stream)
        data = copy.deepcopy(self.data)
        self.preload()
        return data

    def __iter__(self):
        return self
