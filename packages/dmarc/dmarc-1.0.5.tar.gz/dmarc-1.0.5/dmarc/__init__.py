"""DMARC (Domain-based Message Authentication, Reporting & Conformance)

Typical Usage:

    >>> import dmarc
    >>>
    >>> # Represent verified SPF and DKIM status
    >>> aspf = dmarc.SPF(domain='news.example.com', result=dmarc.SPF_PASS)
    >>> #aspf = dmarc.SPF.from_authres(SPFAuthenticationResult(result='pass', smtp_mailfrom='email@news.example.com'))
    >>> 
    >>> adkim = dmarc.DKIM(domain='example.com', result=dmarc.DKIM_PASS)
    >>> #adkim = dmarc.DKIM.from_authres(DKIMAuthenticationResult(result='pass', header_d='example.com'))
    >>>
    >>> try:
    ...     admarc = dmarc.DMARCPolicy(record='v=DMARC1; p=reject;', domain='example.com')
    ...     admarc.verify(spf=aspf, dkim=adkim)
    ...     #admarc.verify(auth_results=[aspf, adkim, dmarc.DKIM('news.example.com', dmarc.DKIM_FAIL)])
    ...     adict = admarc.result.as_dict() # dict repr
    ... except dmarc.PolicyNoneError:
    ...     pass
    ... except dmarc.PolicyQuarantineError:
    ...     raise
    ... except dmarc.PolicyRejectError:
    ...     raise
    ... except dmarc.RecordSyntaxError:
    ...     raise
    ...
"""

__author__ = 'Dusan Obradovic <dusan@euracks.net>'
__version__ = '1.0.5'

import re

SPF_PASS = 0
SPF_NEUTRAL = 1
SPF_FAIL = 2
SPF_TEMPFAIL = 3
SPF_PERMFAIL = 4
SPF_SOFTFAIL = 5
SPF_SCOPE_MFROM = 0
SPF_SCOPE_HELO = 1

DKIM_PASS = 0
DKIM_FAIL = 1
DKIM_TEMPFAIL = 2
DKIM_PERMFAIL = 3
DKIM_NEUTRAL = 4

POLICY_PASS = 0
POLICY_FAIL = 1
POLICY_DIS_NONE = 2
POLICY_DIS_REJECT = 3
POLICY_DIS_QUARANTINE = 4
POLICY_SPF_ALIGNMENT_PASS = 5
POLICY_SPF_ALIGNMENT_FAIL = 6
POLICY_DKIM_ALIGNMENT_PASS = 7
POLICY_DKIM_ALIGNMENT_FAIL = 8

RECORD_P_UNSPECIFIED = None
RECORD_P_NONE = 'n'
RECORD_P_REJECT = 'r'
RECORD_P_QUARANTINE = 'q'
RECORD_A_UNSPECIFIED = None
RECORD_A_RELAXED = 'r'
RECORD_A_STRICT = 's'
RECORD_RF_UNSPECIFIED = 0x0
RECORD_RF_AFRF = 0x1
RECORD_RF_IODEF = 0x2
RECORD_FO_UNSPECIFIED = 0x0
RECORD_FO_0 = 0x1
RECORD_FO_1 = 0x2
RECORD_FO_D = 0x4
RECORD_FO_S = 0x8

def reverse_domain(domain):
    return '.'.join(reversed(domain.split('.')))

class Error(Exception):
    pass

class RecordSyntaxError(Error):
    pass

class RecordValueError(RecordSyntaxError):
    pass

class PolicyError(Error):
    pass

class PolicyNoneError(PolicyError):
    pass

class PolicyRejectError(PolicyError):
    pass

class PolicyQuarantineError(PolicyError):
    pass

class SPF(object):
    AR = {
        'pass': SPF_PASS,
        'neutral': SPF_NEUTRAL,
        'fail': SPF_FAIL,
        'temperror': SPF_TEMPFAIL,
        'permerror': SPF_PERMFAIL,
        'softfail': SPF_SOFTFAIL
    }
    
    def __init__(self, domain, result, scope=None):
        """Represent a single domain SPF verification status
        
        Args:
            domain: Domain part of RFC5321.MailFrom
            result: one of SPF_PASS, SPF_FAIL, SPF_SOFTFAIL, SPF_NEUTRAL, SPF_TEMPFAIL, SPF_PERMFAIL
            scope: one of SPF_SCOPE_MFROM, SPF_SCOPE_HELO
        """
        self.domain = domain
        self.result = result
        self.scope = scope
    
    @classmethod
    def from_authres(cls, ar):
        """
        Args:
            ar: SPFAuthenticationResult object
        
        Returns:
            SPF object
        """
        
        if ar.smtp_mailfrom:
            domain = ar.smtp_mailfrom.split('@')[-1]
            scope = SPF_SCOPE_MFROM
        else:
            domain = ar.smtp_helo
            scope = SPF_SCOPE_HELO
        
        return cls(domain, cls.AR.get(ar.result), scope)

class DKIM(object):
    AR = {
        'pass': DKIM_PASS,
        'fail': DKIM_FAIL,
        'temperror': DKIM_TEMPFAIL,
        'permerror': DKIM_PERMFAIL,
        'neutral': DKIM_NEUTRAL
    }
    
    def __init__(self, domain, result, selector=None):
        """Represent a single domain DKIM verification status
        
        Args:
            domain: Domain value of the signature header d= tag
            result: one of DKIM_PASS, DKIM_FAIL, DKIM_NEUTRAL, DKIM_TEMPFAIL, DKIM_PERMFAIL
            selector: Selector value of the signature header s= tag
        """
        self.domain = domain
        self.result = result
        self.selector = selector
    
    @classmethod
    def from_authres(cls, ar):
        """
        Args:
            ar: DKIMAuthenticationResult object
        
        Returns:
            DKIM object
        """
        
        return cls(ar.header_d, cls.AR.get(ar.result), ar.header_s)

class Policy(object):
    """Policy object:
    
    v: Protocol version
    p: Policy for organizational domain
    sp: Policy for subdomains of the OD
    adkim: Alignment mode for DKIM
    aspf: Alignment mode for SPF
    pct: Percentage of messages subjected to filtering
    ri: Reporting interval
    rf: Reporting format
    rua: Reporting URI of aggregate reports
    ruf: Reporting URI for forensic reports
    fo: Error reporting policy
    domain: Domain part of RFC5322.From header
    org_domain: Organizational Domain of the sender domain
    ip_addr: Source IP address
    """
    def __init__(self, version, domain, org_domain=None, ip_addr=None):
        self.v = version
        self.p = RECORD_P_UNSPECIFIED
        self.sp = RECORD_P_UNSPECIFIED
        self.adkim = RECORD_A_UNSPECIFIED
        self.aspf = RECORD_A_UNSPECIFIED
        self.pct = -1
        self.ri = -1
        self.rf = RECORD_RF_UNSPECIFIED
        self.rua = []
        self.ruf = []
        self.fo = RECORD_FO_UNSPECIFIED
        self.domain = domain
        self.org_domain = org_domain
        self.ip_addr = ip_addr
    
    def parse_record(self, record):
        """Parse DMARC DNS record
        
        Args:
            record: TXT RR value
        """
        
        # The record must start with "v=DMARC1"
        # and the string "DMARC" is the only portion that is case-sensitive...
        pr = re.compile(r'^\s*([^=\s]+)\s*=(.*)$')
        parts = record.split(';')
        if len(parts) < 2:
            raise RecordSyntaxError('Record must specify at least 2 tags')
        
        part = parts[0].strip()
        if not part:
            raise RecordSyntaxError('Record no tag specified')
        
        res = pr.match(part)
        try:
            tag = res.group(1).strip().lower()
            value = res.group(2).strip()
        except AttributeError:
            raise RecordSyntaxError(part)
        
        if tag != 'v' or value != self.v:
            raise RecordSyntaxError('Record must start with v=DMARC1')
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            res = pr.match(part)
            try:
                tag = res.group(1).strip().lower()
                value = res.group(2).strip().lower()
            except AttributeError:
                raise RecordSyntaxError(part)
            
            if tag == 'p':
                if 'none'.startswith(value):
                    self.p = RECORD_P_NONE
                    
                elif 'reject'.startswith(value):
                    self.p = RECORD_P_REJECT
                    
                elif 'quarantine'.startswith(value):
                    self.p = RECORD_P_QUARANTINE
                    
                else:
                    raise RecordValueError(part)
                
            elif tag == 'sp':
                if 'none'.startswith(value):
                    self.sp = RECORD_P_NONE
                    
                elif 'reject'.startswith(value):
                    self.sp = RECORD_P_REJECT
                    
                elif 'quarantine'.startswith(value):
                    self.sp = RECORD_P_QUARANTINE
                    
                else:
                    raise RecordValueError(part)
            
            elif tag == 'adkim':
                if 'relaxed'.startswith(value):
                    self.adkim = RECORD_A_RELAXED
                
                elif 'strict'.startswith(value):
                    self.adkim = RECORD_A_STRICT
                
                else:
                    raise RecordValueError(part)
            
            elif tag == 'aspf':
                if 'relaxed'.startswith(value):
                    self.aspf = RECORD_A_RELAXED
                
                elif 'strict'.startswith(value):
                    self.aspf = RECORD_A_STRICT
                
                else:
                    raise RecordValueError(part)
            
            elif tag == 'pct':
                try:
                    self.pct = int(value)
                except ValueError:
                    raise RecordValueError(part)
                
                if self.pct < 0 or self.pct > 100:
                    raise RecordValueError(part)
            
            elif tag == 'ri':
                try:
                    self.ri = int(value)
                except ValueError:
                    raise RecordValueError(part)
            
            elif tag == 'rf':
                for x in value.split(','):
                    if 'afrf'.startswith(x):
                        self.rf |= RECORD_RF_AFRF
                    
                    elif 'iodef'.startswith(x):
                        self.rf |= RECORD_RF_IODEF
                    
                    else:
                        raise RecordValueError(part)
            
            elif tag == 'rua':
                self.rua = value.split(',')
            
            elif tag == 'ruf':
                self.ruf = value.split(',')
            
            elif tag == 'fo':
                for x in value.split(':'):
                    if x == '0':
                        self.fo |= RECORD_FO_0
                    
                    elif x == '1':
                        self.fo |= RECORD_FO_1
                    
                    elif x == 'd':
                        self.fo |= RECORD_FO_D
                    
                    elif x == 's':
                        self.fo |= RECORD_FO_S
                    
                    else:
                        raise RecordValueError(part)
        
        
        if self.p == RECORD_P_UNSPECIFIED:
            raise RecordValueError('Record required tag p unspecified')
        
        if self.adkim == RECORD_A_UNSPECIFIED:
            self.adkim = RECORD_A_RELAXED
        
        if self.aspf == RECORD_A_UNSPECIFIED:
            self.aspf = RECORD_A_RELAXED
        
        if self.pct < 0:
            self.pct = 100
        
        if self.rf == RECORD_RF_UNSPECIFIED:
            self.rf = RECORD_RF_AFRF
        
        if self.ri < 0:
            self.ri = 86400
        
        if self.fo == RECORD_FO_UNSPECIFIED:
            self.fo = RECORD_FO_0

class Result(object):
    """Result object keeps policy evaluated 
    results:
    
    dkim:         DKIM identifier alignment result,
                  one of POLICY_DKIM_ALIGNMENT_PASS, POLICY_DKIM_ALIGNMENT_FAIL
    
    spf:          SPF identifier alignment result,
                  one of POLICY_SPF_ALIGNMENT_PASS, POLICY_SPF_ALIGNMENT_FAIL
                  
    result:       Policy evaluated result,
                  one of POLICY_PASS, POLICY_FAIL
                  
    disposition:  Policy to enforce,
                  one of POLICY_DIS_NONE, POLICY_DIS_REJECT, POLICY_DIS_QUARANTINE
    
    policy:       Policy object
    
    aspf:         SPF object
    
    adkim:        DKIM object
    """
    def __init__(self, policy, aspf, adkim):
        self.dkim = None
        self.spf = None
        self.result = None
        self.disposition = None
        self.policy = policy
        self.aspf = aspf
        self.adkim = adkim
    
    def verify(self):
        """Policy disposition verification
        
        Returns:
            None
        
        Raises:
            PolicyNoneError: if POLICY_FAIL and POLICY_DIS_NONE
            PolicyQuarantineError: if POLICY_FAIL and POLICY_DIS_QUARANTINE
            PolicyRejectError: if POLICY_FAIL and POLICY_DIS_REJECT
            PolicyError: if POLICY_FAIL and unknown disposition error
        """
        if self.result == POLICY_FAIL:
            if self.disposition == POLICY_DIS_NONE:
                raise PolicyNoneError
            
            elif self.disposition == POLICY_DIS_QUARANTINE:
                raise PolicyQuarantineError
            
            elif self.disposition == POLICY_DIS_REJECT:
                raise PolicyRejectError
            
            else:
                raise PolicyError
    
    def as_dict(self):
        policy_published = {}
        policy_evaluated = {}
        row = {}
        identifiers = {}
        auth_results = {}
        dkim = {}
        spf = {}
        
        policy_published['domain'] = self.policy.org_domain or self.policy.domain
        policy_published['adkim'] = self.policy.adkim
        policy_published['aspf'] = self.policy.aspf
        if self.policy.p == RECORD_P_NONE:
            policy_published['p'] = 'none'
        elif self.policy.p == RECORD_P_QUARANTINE:
            policy_published['p'] = 'quarantine'
        elif self.policy.p == RECORD_P_REJECT:
            policy_published['p'] = 'reject'
        
        if self.policy.sp == RECORD_P_NONE:
            policy_published['sp'] = 'none'
        elif self.policy.sp == RECORD_P_QUARANTINE:
            policy_published['sp'] = 'quarantine'
        elif self.policy.sp == RECORD_P_REJECT:
            policy_published['sp'] = 'reject'
        
        policy_published['pct'] = self.policy.pct
        
        if self.disposition == POLICY_DIS_NONE:
            policy_evaluated['disposition'] = 'none'
        elif self.disposition == POLICY_DIS_QUARANTINE:
            policy_evaluated['disposition'] = 'quarantine'
        elif self.disposition == POLICY_DIS_REJECT:
            policy_evaluated['disposition'] = 'reject'
        
        if self.dkim == POLICY_DKIM_ALIGNMENT_PASS:
            policy_evaluated['dkim'] = 'pass'
        elif self.dkim == POLICY_DKIM_ALIGNMENT_FAIL:
            policy_evaluated['dkim'] = 'fail'
        
        if self.spf == POLICY_SPF_ALIGNMENT_PASS:
            policy_evaluated['spf'] = 'pass'
        elif self.spf == POLICY_SPF_ALIGNMENT_FAIL:
            policy_evaluated['spf'] = 'fail'
        
        if self.policy.ip_addr:
            row['source_ip'] = self.policy.ip_addr
        
        row['count'] = 1
        row['policy_evaluated'] = policy_evaluated
        
        identifiers['header_from'] = self.policy.domain
        
        if self.adkim:
            dkim['domain'] = self.adkim.domain
            if self.adkim.result == DKIM_FAIL:
                dkim['result'] = 'fail'
            elif self.adkim.result == DKIM_NEUTRAL:
                dkim['result'] = 'neutral'
            elif self.adkim.result == DKIM_PASS:
                dkim['result'] = 'pass'
            elif self.adkim.result == DKIM_PERMFAIL:
                dkim['result'] = 'permerror'
            elif self.adkim.result == DKIM_TEMPFAIL:
                dkim['result'] = 'temperror'
            elif self.adkim.result is None:
                dkim['result'] = 'none'
            
            if self.adkim.selector:
                dkim['selector'] = self.adkim.selector
            
            auth_results['dkim'] = dkim
        
        if self.aspf:
            spf['domain'] = self.aspf.domain
            if self.aspf.scope == SPF_SCOPE_HELO:
                spf['scope'] = 'helo'
            elif self.aspf.scope == SPF_SCOPE_MFROM:
                spf['scope'] = 'mfrom'
            
            if self.aspf.result == SPF_FAIL:
                spf['result'] = 'fail'
            elif self.aspf.result == SPF_NEUTRAL:
                spf['result'] = 'neutral'
            elif self.aspf.result == SPF_PASS:
                spf['result'] = 'pass'
            elif self.aspf.result == SPF_PERMFAIL:
                spf['result'] = 'permerror'
            elif self.aspf.result == SPF_SOFTFAIL:
                spf['result'] = 'softfail'
            elif self.aspf.result == SPF_TEMPFAIL:
                spf['result'] = 'temperror'
            elif self.aspf.result is None:
                spf['result'] = 'none'
            
            auth_results['spf'] = spf
        
        return {
            'policy_published':policy_published,
            'record':{
                'row':row,
                'identifiers':identifiers,
                'auth_results':auth_results
            }
        }        

class DMARC(object):
    def __init__(self, publicsuffix=None):
        """The DMARC constructor accepts PublicSuffixList object,
        and (if given) will be used for determining Organizational Domain
        """
        self.publicsuffix = publicsuffix
    
    def get_result(self, policy, spf=None, dkim=None):
        """Policy evaluation
        
        Args:
            policy: Policy object
            spf: SPF object
            dkim: DKIM object
        
        Returns:
            Result object
        """
        ret = Result(policy, aspf=spf, adkim=dkim)
        ret.dkim = POLICY_DKIM_ALIGNMENT_FAIL
        ret.spf = POLICY_SPF_ALIGNMENT_FAIL
        ret.result = POLICY_FAIL
        
        if dkim and dkim.result == DKIM_PASS:
            if self.check_alignment(policy.domain, dkim.domain, policy.adkim, self.publicsuffix):
                ret.dkim = POLICY_DKIM_ALIGNMENT_PASS
        
        if spf and spf.result == SPF_PASS:
            if self.check_alignment(policy.domain, spf.domain, policy.aspf, self.publicsuffix):
                ret.spf = POLICY_SPF_ALIGNMENT_PASS
        
        if ret.spf == POLICY_SPF_ALIGNMENT_PASS or ret.dkim == POLICY_DKIM_ALIGNMENT_PASS:
            ret.result = POLICY_PASS
            ret.disposition = POLICY_DIS_NONE
            
            return ret
        
        if policy.org_domain and policy.sp != RECORD_P_UNSPECIFIED:
            if policy.sp == RECORD_P_REJECT:
                ret.disposition = POLICY_DIS_REJECT
            
            elif policy.sp == RECORD_P_QUARANTINE:
                ret.disposition = POLICY_DIS_QUARANTINE
            
            elif policy.sp == RECORD_P_NONE:
                ret.disposition = POLICY_DIS_NONE
            
            return ret
            
        if policy.p == RECORD_P_REJECT:
            ret.disposition = POLICY_DIS_REJECT
        
        elif policy.p == RECORD_P_QUARANTINE:
            ret.disposition = POLICY_DIS_QUARANTINE
        
        elif policy.p == RECORD_P_NONE:
            ret.disposition = POLICY_DIS_NONE
        
        return ret
    
    def check_alignment(self, fd, ad, mode, psl=None):
        if not all((fd, ad, mode)):
            raise ValueError
        
        rev_fd = reverse_domain(fd.lower()) + '.'
        rev_ad = reverse_domain(ad.lower()) + '.'
        
        if rev_ad == rev_fd:
            return True
        
        if rev_fd[:len(rev_ad)] == rev_ad and mode == RECORD_A_RELAXED:
            return True
        
        if rev_ad[:len(rev_fd)] == rev_fd and mode == RECORD_A_RELAXED:
            return True
        
        if psl:
            return self.check_alignment(fd, psl.get_public_suffix(ad), mode)
        
        return False
    
    def parse_record(self, record, domain, org_domain=None, ip_addr=None):
        """Parse DMARC DNS record
        
        Args:
            record: TXT RR value
            domain: Domain part of RFC5322.From header
            org_domain: Organizational Domain of the sender domain
            ip_addr: Source IP address
        
        Returns:
            Policy object
        """
        policy = Policy('DMARC1', domain, org_domain, ip_addr)
        policy.parse_record(record)
        return policy
    
class DMARCPolicy(object):
    """DMARC evaluation
    
    Args:
        record: TXT RR value
        domain: Domain part of RFC5322.From header
        org_domain: Organizational Domain of the sender domain
        ip_addr: Source IP address
        publicsuffix: PublicSuffixList object
    """
    def __init__(self, record, domain, org_domain=None, ip_addr=None, publicsuffix=None):
        self.dmarc = DMARC(publicsuffix)
        self.policy = self.dmarc.parse_record(record, domain, org_domain, ip_addr)
        self.result = None
    
    def verify(self, spf=None, dkim=None, auth_results=[]):
        """Policy disposition verification
        
        Args:
            spf: SPF object
            dkim: DKIM object
            auth_results: Iterable (of authentication results)
        
        Returns:
            None
        
        Raises:
            PolicyNoneError: if POLICY_FAIL and POLICY_DIS_NONE
            PolicyQuarantineError: if POLICY_FAIL and POLICY_DIS_QUARANTINE
            PolicyRejectError: if POLICY_FAIL and POLICY_DIS_REJECT
            PolicyError: if POLICY_FAIL and unknown disposition error
        """
        for ar in auth_results:
            # The aligned authentication result is chosen over any result
            if isinstance(ar, SPF):
                spf = ar if self.isaligned(ar) else spf or ar
            elif isinstance(ar, DKIM):
                dkim = ar if self.isaligned(ar) else dkim or ar
        
        self.result = self.dmarc.get_result(self.policy, spf, dkim)
        self.result.verify()
    
    def isaligned(self, ar):
        if isinstance(ar, SPF):
            return (
                ar.result == SPF_PASS and 
                self.dmarc.check_alignment(
                        self.policy.domain, ar.domain, self.policy.aspf, self.dmarc.publicsuffix)
            )
        elif isinstance(ar, DKIM):
            return (
                ar.result == DKIM_PASS and 
                self.dmarc.check_alignment(
                        self.policy.domain, ar.domain, self.policy.adkim, self.dmarc.publicsuffix)
            )
        else:
            raise ValueError("invalid authentication result '{0}'".format(ar))
