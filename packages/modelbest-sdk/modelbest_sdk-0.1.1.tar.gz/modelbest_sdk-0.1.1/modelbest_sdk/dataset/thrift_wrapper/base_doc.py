import logging
import thriftpy2
from thriftpy2.utils import deserialize, serialize
import os

from modelbest_sdk.dataset.thrift_wrapper.utils import Utils

proto_dir = os.path.join(os.path.dirname(__file__), "../..", "proto")

doc_thrift = thriftpy2.load(os.path.join(proto_dir, "traindoc.thrift"), module_name="doc_thrift")
logger = logging.getLogger(__name__)


class BaseDoc:
    def __init__(self, token_ids, mask=None, docid=None, tag=None, token=None, tokenizer_version=None, reserved_col=None):
        self.token_ids = token_ids
        self.mask = mask
        self.docid = docid
        self.tag = tag
        self.token = token
        self.tokenizer_version = tokenizer_version
        self.reserved_col = reserved_col
    
    @staticmethod
    def deserialize(bin):
        return BaseDoc.from_thrift(deserialize(doc_thrift.BaseDoc(), bin))
    
    def to_thrift(self):
        return doc_thrift.BaseDoc(
            token_ids=self.token_ids,
            mask=self.mask,
            docid=self.docid,
            tag=self.tag,
            token=self.token,
            tokenizer_version=self.tokenizer_version,
            reserved_col=self.reserved_col
        )
    
    @staticmethod
    def from_thrift(thrift_base_doc):
        return BaseDoc(
            token_ids=thrift_base_doc.token_ids,
            mask=thrift_base_doc.mask,
            docid=thrift_base_doc.docid,
            tag=thrift_base_doc.tag,
            token=thrift_base_doc.token,
            tokenizer_version=thrift_base_doc.tokenizer_version,
            reserved_col=thrift_base_doc.reserved_col
        )
        
    def __repr__(self) -> str:
        return f"BaseDoc(token_ids={self.token_ids}, mask={self.mask}, docid={self.docid}, tag={self.tag}, token={self.token}, tokenizer_version={self.tokenizer_version}, reserved_col={self.reserved_col})"
    