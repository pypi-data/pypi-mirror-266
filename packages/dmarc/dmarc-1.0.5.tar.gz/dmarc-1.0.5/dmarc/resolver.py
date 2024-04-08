"""DMARC resolver

Typical Usage:

    >>> from dmarc.resolver import resolve, RecordNotFoundError, RecordMultiFoundError, RecordResolverError
    >>> try:
    ...     record = resolve('example.com')
    ... except RecordNotFoundError:
    ...     pass
    ... except RecordMultiFoundError:
    ...     raise # permerror
    ... except RecordResolverError:
    ...     raise # temperror
    ... 
"""

from dns.resolver import resolve as resolver, NXDOMAIN, NoAnswer
from dns.exception import DNSException
from . import Error

class RecordResolverError(Error):
    pass

class RecordNotFoundError(RecordResolverError):
    pass

class RecordMultiFoundError(RecordResolverError):
    pass

class RecordNoDataError(RecordNotFoundError):
    pass

def resolve(domain):
    try:
        answers = resolver('_dmarc.{0}'.format(domain), 'TXT')
        return response(answers)
    except NXDOMAIN as err:
        raise RecordNotFoundError(err)
    except NoAnswer as err:
        raise RecordNoDataError(err)
    except DNSException as err:
        raise RecordResolverError(err)

def response(answers):
    if len(answers) > 1:
        raise RecordMultiFoundError('A domain can only have one DMARC record.')
    return b''.join(answers[0].strings).decode()
        