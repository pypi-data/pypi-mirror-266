# DMARC (Domain-based Message Authentication, Reporting & Conformance)

DMARC email authentication module implemented in Python.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dmarc.

```bash
pip install dmarc
```

## Usage

```python
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
>>> # dmarc rr resolver example
>>> from dmarc.resolver import resolve, RecordNotFoundError, RecordMultiFoundError, RecordResolverError
>>> from dmarc.psl import get_public_suffix
>>> domain = 'example.com'
>>> try:
...     record = resolve(domain)
... except RecordNotFoundError:
...     org_domain = get_public_suffix(domain)
...     if org_domain != domain:
...             record = resolve(org_domain)
... except RecordMultiFoundError:
...     raise # permerror
... except RecordResolverError:
...     raise # temperror
... 
>>> # dmarc authres header example
>>> from dmarc.ar import authres, AuthenticationResultsHeader
>>> dares = authres(admarc.result) #DMARCAuthenticationResult factory
>>> header = AuthenticationResultsHeader(authserv_id='myhostname', results=[dares])
>>> str(header)
'Authentication-Results: myhostname; dmarc=pass (domain=example.com adkim=r aspf=r p=reject pct=100) header.from=example.com policy.dmarc=none (disposition=none dkim=pass spf=pass)'
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
