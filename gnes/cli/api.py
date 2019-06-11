#  Tencent is pleased to support the open source community by making GNES available.
#
#  Copyright (C) 2019 THL A29 Limited, a Tencent company. All rights reserved.
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# pylint: disable=low-comment-ratio


def encode(args):
    from ..service.encoder import EncoderService
    with EncoderService(args) as es:
        es.join()


def index(args):
    from ..service.indexer import IndexerService
    with IndexerService(args) as es:
        es.join()


def proxy(args):
    from ..service import proxy as my_proxy
    if not args.proxy_type:
        raise ValueError(
            '--proxy_type is required when starting a proxy from CLI')
    with getattr(my_proxy, args.proxy_type)(args) as es:
        es.join()


def frontend(args):
    from ..service.grpc import GRPCFrontend
    import threading
    with GRPCFrontend(args):
        forever = threading.Event()
        forever.wait()


def client(args):
    import grpc

    from ..helper import batch_iterator
    from ..proto import gnes_pb2, gnes_pb2_grpc
    from ..preprocessor.text import txt_file2pb_docs

    pb_docs = txt_file2pb_docs(args.txt_file)

    with grpc.insecure_channel(
            '%s:%s' % (args.grpc_host, args.grpc_port),
            options=[('grpc.max_send_message_length', 50 * 1024 * 1024),
                     ('grpc.max_receive_message_length', 50 * 1024 * 1024)]) as channel:
        stub = gnes_pb2_grpc.GnesRPCStub(channel)

        if args.mode == 'train':
            # feed and accumulate training data
            for p in batch_iterator(pb_docs, args.batch_size):
                req = gnes_pb2.Request()
                req.train.docs.extend(p)
                resp = stub._Call(req)
                print(resp)

            # start the real training
            req = gnes_pb2.Request()
            req.control.command = gnes_pb2.Request.ControlRequest.FLUSH
            resp = stub._Call(req)
            print(resp)
        elif args.mode == 'index':
            for p in batch_iterator(pb_docs, args.batch_size):
                req = gnes_pb2.Request()
                req.index.docs.extend(p)
                resp = stub._Call(req)
                print(resp)

        elif args.mode == 'query':
            for idx, doc in enumerate(pb_docs):
                req = gnes_pb2.Request()
                req.search.query.CopyFrom(doc)
                resp = stub._Call(req)
                print('query %d result: %s' % (idx, resp))
                input('press any key to continue...')


def http(args):
    from ..service.http import HttpService
    mh = HttpService(args)
    mh.run()
