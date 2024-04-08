import unittest

from dmarc.psl import (
    load,
    get_public_suffix,
    PublicSuffixList,
)

class TestPublicSuffixList(unittest.TestCase):
    
    def test_get_public_suffix(self):
        self.assertEqual('example.com', get_public_suffix('example.com'))
        self.assertEqual('example.com', get_public_suffix('news.example.com'))
    
    def test_load(self):
        self.assertIsInstance(load(psl_file=None), PublicSuffixList)
