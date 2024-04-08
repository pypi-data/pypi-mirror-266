import unittest

from dmarc import (
    DMARCPolicy,
    SPF,
    DKIM,
)

from dmarc.ar import (
    authres,
    AuthenticationResultsHeader,
    SPFAuthenticationResult,
    DKIMAuthenticationResult,
)

class TestAuthenticationResults(unittest.TestCase):
    
    def setUp(self):
        self.dmarc = DMARCPolicy(record='v=DMARC1; p=reject;', domain='example.com')
    
    def test_authres(self):
        expected = ("Authentication-Results: myhostname; dmarc=pass (domain=example.com adkim=r aspf=r p=reject pct=100) "
                    "header.from=example.com policy.dmarc=none (disposition=none dkim=pass spf=pass)"
        )
        aspf = SPFAuthenticationResult(result='pass', smtp_mailfrom='email@news.example.com')
        adkim = DKIMAuthenticationResult(result='pass', header_d='example.com')
        self.dmarc.verify(SPF.from_authres(aspf), DKIM.from_authres(adkim))
        result = AuthenticationResultsHeader(authserv_id='myhostname', results=[authres(self.dmarc.result)])
        self.assertEqual(expected, str(result))
