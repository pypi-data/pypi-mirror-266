import thriftpy2
from modelbest_sdk.file_format.mbtable_builder import MbTableBuilder
from modelbest_sdk.file_format.mbtable_partition import MbTablePartition, MbTablePartitionIterator
from thriftpy2.utils import serialize, deserialize


# for i in range(10):
#     builder = MbTableBuilder(f"test/partition_data/part_{i}.mbt")
#     for j in range(100):
#         builder.write(f"file_{i}_value_{j}")
#     builder.add_metadata("meta_key", "meta_value")
#     builder.flush()
# builder = MbTableBuilder(f"test/base_doc_simple/part_1.mbt")
# dataset = MbTablePartitionIterator(MbTablePartition("test/base_doc"))
# for i, data in enumerate(dataset):
#     builder.write(data)
# builder.flush()
base_doc_thrift = thriftpy2.load("modelbest_sdk/proto/traindoc.thrift", module_name="proto_base_doc_thrift")

for i in range(2):
    builder = MbTableBuilder(f"test/base_doc_easy/part_{i}.mbt")
    for j in range(10):
        doc = base_doc_thrift.BaseDoc()
        doc.docid = f"doc_{i}_{j}"
        doc.token_ids = [-1, 2, 3, 4, 5, 6, 0]
        doc.mask = [False, False, False, False, False, False, True]
        doc.tag=["mock"]
        doc_str = serialize(doc)
        builder.write(doc_str)
    builder.flush()