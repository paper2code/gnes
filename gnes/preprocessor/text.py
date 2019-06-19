import re
from typing import TextIO, List

from ..proto import gnes_pb2


def txt_file2pb_docs(fp: TextIO, start_id: int = 0) -> List['gnes_pb2.Document']:
    data = [v for v in fp if v.strip()]
    docs = []
    for doc_id, doc_txt in enumerate(data, start_id):
        doc = line2pb_doc(doc_txt, doc_id)
        docs.append(doc)
    return docs


def line2pb_doc(line: str, doc_id: int = 0, deliminator: str = r'[.。！？!?]+') -> 'gnes_pb2.Document':
    doc = gnes_pb2.Document()
    doc.doc_id = doc_id
    doc.doc_type = gnes_pb2.Document.TEXT
    doc.meta_info = line.encode()
    if deliminator:
        for ci, s in enumerate(re.split(deliminator, line)):
            if s.strip():
                c = doc.chunks.add()
                c.doc_id = doc_id
                c.text = s
                c.offset_1d = ci
    else:
        c = doc.chunks.add()
        c.doc_id = doc_id
        c.text = line
        c.offset_1d = 0
    return doc