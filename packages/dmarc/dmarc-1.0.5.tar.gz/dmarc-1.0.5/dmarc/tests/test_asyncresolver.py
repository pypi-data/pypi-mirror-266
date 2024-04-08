import unittest

from dmarc.asyncresolver import (
    resolve,
    RecordNotFoundError,
)

class TestResolver(unittest.IsolatedAsyncioTestCase):
    
    async def test_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            await resolve('domain.invalid')
    
    async def test_found(self):
        expected = u'v=DMARC1; p=none; pct=100; rua=mailto:reports@dmarc.org; ruf=mailto:reports@dmarc.org'
        result = await resolve('dmarc.org')
        self.assertEqual(expected, result)
