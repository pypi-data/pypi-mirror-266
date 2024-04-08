import unittest

from dmarc import (
    DMARC,
    SPF,
    DKIM,
    Result,
    DMARCPolicy,
    RecordSyntaxError,
    RecordValueError,
    PolicyNoneError,
    PolicyRejectError,
    PolicyQuarantineError,
    RECORD_P_UNSPECIFIED,
    RECORD_P_NONE,
    RECORD_P_REJECT,
    RECORD_P_QUARANTINE,
    RECORD_A_RELAXED,
    RECORD_A_STRICT,
    SPF_PASS,
    SPF_FAIL,
    SPF_SCOPE_MFROM,
    DKIM_PASS,
    DKIM_FAIL,
    POLICY_PASS,
    POLICY_FAIL,
    POLICY_DIS_NONE,
    POLICY_DIS_REJECT,
    POLICY_DIS_QUARANTINE,
    POLICY_SPF_ALIGNMENT_PASS,
    POLICY_SPF_ALIGNMENT_FAIL,
    POLICY_DKIM_ALIGNMENT_PASS,
    POLICY_DKIM_ALIGNMENT_FAIL,
)

class TestDMARC(unittest.TestCase):
    
    def setUp(self):
        self.dmarc = DMARC()
    
    def test_parse_record(self):
        def policy(record):
            return self.dmarc.parse_record(record, 'example.com')
        self.assertRaises(RecordSyntaxError, policy, '')
        self.assertRaises(RecordSyntaxError, policy, 'v=DMARC1 p=none')
        self.assertRaises(RecordSyntaxError, policy, 'p=none')
        self.assertRaises(RecordSyntaxError, policy, 'v=DMARC1; p:none')
        self.assertRaises(RecordSyntaxError, policy, 'v=DAMRC1; p=none')
        self.assertRaises(RecordSyntaxError, policy, 'v=dmarc1; p=none;')
        self.assertRaises(RecordSyntaxError, policy, 'p=DMARC1; p=none')
        self.assertRaises(RecordValueError, policy, 'v=DMARC1; sp=none')
        self.assertRaises(RecordValueError, policy, 'v=DMARC1; p=reject; sp=pass')
        self.assertRaises(RecordValueError, policy, 'v=DMARC1; p=pass')
        self.assertRaises(RecordValueError, policy, 'v=DMARC1; p=none sp=none')
        self.assertRaises(RecordValueError, policy, 'v=DMARC1; p=none; adkim=none')
        self.assertRaises(RecordValueError, policy, 'v=DMARC1; p=none; aspf=none')
        self.assertEqual(policy('v=DMARC1; p=none; sp=reject;').p, RECORD_P_NONE)
        self.assertEqual(policy('v=DMARC1; p=reject; sp=none;').p, RECORD_P_REJECT)
        self.assertEqual(policy('v=DMARC1; p=quarantine; sp=reject;').p, RECORD_P_QUARANTINE)
        self.assertEqual(policy('v=DMARC1; p=reject; sp=none;').sp, RECORD_P_NONE)
        self.assertEqual(policy('v=DMARC1; p=none; sp=reject;').sp, RECORD_P_REJECT)
        self.assertEqual(policy('v=DMARC1; p=none; sp=quarantine;').sp, RECORD_P_QUARANTINE)
        self.assertEqual(policy('v=DMARC1; p=reject;').adkim, RECORD_A_RELAXED)
        self.assertEqual(policy('v=DMARC1; p=reject; adkim=r').adkim, RECORD_A_RELAXED)
        self.assertEqual(policy('v=DMARC1; p=reject; adkim=s').adkim, RECORD_A_STRICT)
        self.assertEqual(policy('v=DMARC1; p=reject;').aspf, RECORD_A_RELAXED)
        self.assertEqual(policy('v=DMARC1; p=reject; aspf=r').aspf, RECORD_A_RELAXED)
        self.assertEqual(policy('v=DMARC1; p=reject; aspf=s').aspf, RECORD_A_STRICT)
    
    def test_alignment(self):
        self.assertRaises(ValueError, self.dmarc.check_alignment, fd=None, ad=None, mode=None)
        self.assertTrue(self.dmarc.check_alignment('example.com', 'news.example.com', RECORD_A_RELAXED))
        self.assertTrue(self.dmarc.check_alignment('news.example.com', 'example.com', RECORD_A_RELAXED))
        self.assertFalse(self.dmarc.check_alignment('example.com', 'news.example.com', RECORD_A_STRICT))
        self.assertFalse(self.dmarc.check_alignment('news.example.com', 'example.com', RECORD_A_STRICT))
    
    def test_result_pass(self):
        aspf = SPF(domain='news.example.com', result=SPF_PASS)
        adkim = DKIM(domain='example.com', result=DKIM_PASS)
        policy = self.dmarc.parse_record(record='v=DMARC1; p=reject;', domain='example.com')
        result = self.dmarc.get_result(policy, aspf, adkim)
        self.assertEqual(result.result, POLICY_PASS)
        self.assertEqual(result.disposition, POLICY_DIS_NONE)
        self.assertEqual(result.spf, POLICY_SPF_ALIGNMENT_PASS)
        self.assertEqual(result.dkim, POLICY_DKIM_ALIGNMENT_PASS)
    
    def test_result_reject(self):
        aspf = SPF(domain='news.example.com', result=SPF_PASS)
        adkim = DKIM(domain='example.com', result=DKIM_FAIL)
        policy = self.dmarc.parse_record(record='v=DMARC1; p=reject; aspf=s; adkim=s;', domain='example.com')
        result = self.dmarc.get_result(policy, aspf, adkim)
        self.assertEqual(result.result, POLICY_FAIL)
        self.assertEqual(result.disposition, POLICY_DIS_REJECT)
        self.assertEqual(result.spf, POLICY_SPF_ALIGNMENT_FAIL)
        self.assertEqual(result.dkim, POLICY_DKIM_ALIGNMENT_FAIL)
        self.assertRaises(PolicyRejectError, result.verify)
    
    def test_result_quarantine(self):
        aspf = SPF(domain='news.example.com', result=SPF_PASS)
        adkim = DKIM(domain='example.com', result=DKIM_PASS)
        policy = self.dmarc.parse_record(record='v=DMARC1; p=none; sp=quarantine; adkim=s;', domain='mail.example.com', org_domain='example.com')
        result = self.dmarc.get_result(policy, aspf, adkim)
        self.assertEqual(result.result, POLICY_FAIL)
        self.assertEqual(result.disposition, POLICY_DIS_QUARANTINE)
        self.assertEqual(result.spf, POLICY_SPF_ALIGNMENT_FAIL)
        self.assertEqual(result.dkim, POLICY_DKIM_ALIGNMENT_FAIL)
        self.assertRaises(PolicyQuarantineError, result.verify)
    
    def test_result_as_dict(self):
        expected = {
            'policy_published': {'domain': 'example.com', 'adkim': 'r', 'aspf': 'r', 'p': 'reject', 'pct': 100},
            'record': {
                'row': {
                    'count': 1,
                    'policy_evaluated': {'disposition': 'none', 'dkim': 'pass', 'spf': 'pass'}
                },
                'identifiers': {'header_from': 'example.com'},
                'auth_results': {
                    'dkim': {'domain': 'example.com', 'result': 'pass'},
                    'spf': {'domain': 'news.example.com', 'scope': 'mfrom', 'result': 'pass'}
                }
            }
        }
        aspf = SPF(domain='news.example.com', result=SPF_PASS, scope=SPF_SCOPE_MFROM)
        adkim = DKIM(domain='example.com', result=DKIM_PASS)
        policy = self.dmarc.parse_record(record='v=DMARC1; p=reject;', domain='example.com')
        result = self.dmarc.get_result(policy, aspf, adkim)
        self.assertEqual(expected, result.as_dict())

class TestDMARCPolicy(unittest.TestCase):
    
    def setUp(self):
        self.dmarc = DMARCPolicy(record='v=DMARC1; p=reject;', domain='example.com')
    
    def test_verify_pass(self):
        self.dmarc.verify(SPF(domain='news.example.com', result=SPF_PASS))
        self.dmarc.verify(auth_results=[SPF('news.example.com', SPF_FAIL), DKIM('example.com', DKIM_PASS)])
        self.assertIsInstance(self.dmarc.result, Result)
    
    def test_verify_reject(self):
        with self.assertRaises(PolicyRejectError):
            self.dmarc.verify()
    
    def test_isaligned(self):
        self.assertRaises(ValueError, self.dmarc.isaligned, None)
        self.assertTrue(self.dmarc.isaligned(SPF('news.example.com', SPF_PASS)))
        self.assertTrue(self.dmarc.isaligned(DKIM('news.example.com', DKIM_PASS)))
        self.assertFalse(self.dmarc.isaligned(SPF('news.example.com', SPF_FAIL)))
        self.assertFalse(self.dmarc.isaligned(DKIM('news.example.com', DKIM_FAIL)))
