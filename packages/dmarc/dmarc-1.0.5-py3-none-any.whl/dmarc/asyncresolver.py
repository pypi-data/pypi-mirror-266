"""DMARC asyncresolver

Typical Usage:

    >>> from dmarc.asyncresolver import resolve, RecordNotFoundError, RecordMultiFoundError, RecordResolverError
    >>> try:
    ...     record = await resolve('example.com')
    ... except RecordNotFoundError:
    ...     pass
    ... except RecordMultiFoundError:
    ...     raise # permerror
    ... except RecordResolverError:
    ...     raise # temperror
    ... 
"""

from dns.asyncresolver import resolve as resolver, NXDOMAIN, NoAnswer
from dns.exception import DNSException
from .resolver import response, RecordResolverError, RecordNotFoundError, RecordNoDataError, RecordMultiFoundError

async def resolve(domain):
    try:
        answers = await resolver('_dmarc.{0}'.format(domain), 'TXT')
        return response(answers)
    except NXDOMAIN as err:
        raise RecordNotFoundError(err)
    except NoAnswer as err:
        raise RecordNoDataError(err)
    except DNSException as err:
        raise RecordResolverError(err)
