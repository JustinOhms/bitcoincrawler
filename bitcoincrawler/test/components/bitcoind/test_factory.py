from unittest import TestCase
from bitcoincrawler.components.bitcoind.factory import BitcoindFactory
from bitcoincrawler.components.bitcoind.model import BTCDTransaction, BTCDBlock, BTCDVin, BTCDVout
from types import GeneratorType

import json
from decimal import Decimal
from mock import Mock

class TestBitcoindFactory(TestCase):
    def setUp(self):
        self.btcd = Mock()
        self.sut = BitcoindFactory(self.btcd)

    def tearDown(self):
        self.btcd.reset_mock()

    def test_get_mempool_transactions(self):
        response = ["txid1", "txid2", "txid3"]
        self.btcd.get_raw_mempool.side_effect = [response]
        i, limit = 0, 2
        r = self.sut.get_mempool_transactions(limit=limit)
        self.assertIsInstance(r, GeneratorType)
        self.btcd.get_raw_mempool.assert_called_once_with()
        for i, x in enumerate(r):
            self.assertIsInstance(x, BTCDTransaction)
        self.assertEqual(i+1, limit)

    def test_get_transactions(self):
        request = ["txid1", "txid2", "txid3"]
        get_raw_transactions_response = ["rawtx1", "rawtx2", "rawtx3"]
        decode_raw_transactions_response = [{"txid": "rawtx1"}, {"txid": "rawtx2"}, {"txid": "rawtx3"}]
        i = 0
        self.btcd.get_raw_transaction.side_effect = get_raw_transactions_response
        self.btcd.decode_raw_transaction.side_effect = decode_raw_transactions_response
        r = self.sut.get_transactions(request)
        self.assertIsInstance(r, GeneratorType)
        for i, x in enumerate(r):
            self.assertIsInstance(x, BTCDTransaction)
            self.assertEqual(x.txid, decode_raw_transactions_response[i]['txid'])
        self.assertEqual(i+1, len(request))

    def test_generate_blocks_from_height_explicit_stop(self):
        i, limit = 0, 3
        get_block_hash_response = ["block_hash_1", "block_hash_2", "block_hash_3"]
        get_block_response = [{'nextblockhash': 'block_hash_2',
                               'hash': 'block_hash_1'},
                              {'nextblockhash': 'block_hash_3',
                               'hash': 'block_hash_2'},
                              {'nextblockhash': 'block_hash_4',
                               'hash': 'block_hash_3'}]
        self.btcd.get_block_hash.side_effect = get_block_hash_response
        self.btcd.get_block.side_effect = get_block_response
        blocks = self.sut.generate_blocks(height=1, max_iterations=limit)
        for i, block in enumerate(blocks):
            self.assertIsInstance(block, BTCDBlock)
            self.assertEqual(block.hash, get_block_response[i]['hash'])
        self.assertEqual(i+1, limit)

    def test_generate_blocks_from_height_0__explicit_stop(self):
        i, limit = 0, 3
        get_block_hash_response = ["block_hash_1", "block_hash_2", "block_hash_3"]
        get_block_response = [{'nextblockhash': 'block_hash_2',
                               'hash': 'block_hash_1'},
                              {'nextblockhash': 'block_hash_3',
                               'hash': 'block_hash_2'},
                              {'nextblockhash': 'block_hash_4',
                               'hash': 'block_hash_3'}]
        self.btcd.get_block_hash.side_effect = get_block_hash_response
        self.btcd.get_block.side_effect = get_block_response
        blocks = self.sut.generate_blocks(height=0, max_iterations=limit)
        for i, block in enumerate(blocks):
            self.assertIsInstance(block, BTCDBlock)
            self.assertEqual(block.hash, get_block_response[i]['hash'])
        self.assertEqual(i+1, limit)

    def test_generate_blocks_from_hash_explicit_stop(self):
        i, limit = 0, 3
        get_block_response = [{'nextblockhash': 'block_hash_2',
                               'hash': 'block_hash_1'},
                              {'nextblockhash': 'block_hash_3',
                               'hash': 'block_hash_2'},
                              {'nextblockhash': 'block_hash_4',
                               'hash': 'block_hash_3'}]
        self.btcd.get_block.side_effect = get_block_response
        blocks = self.sut.generate_blocks(hash='block_hash_1', max_iterations=limit)
        for i, block in enumerate(blocks):
            self.assertIsInstance(block, BTCDBlock)
            self.assertEqual(block.hash, get_block_response[i]['hash'])
        self.assertEqual(i+1, limit)
