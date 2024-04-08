import unittest

from dmarc.resolver import (
    resolve,
    RecordNotFoundError,
)

class TestResolver(unittest.TestCase):
    
    def test_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            resolve('domain.invalid')
    
    def test_found(self):
        expected = u'v=DMARC1; p=none; pct=100; rua=mailto:reports@dmarc.org; ruf=mailto:reports@dmarc.org'
        result = resolve('dmarc.org')
        self.assertEqual(expected, result)
