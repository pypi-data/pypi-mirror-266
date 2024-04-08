from authres import AuthenticationResultsHeader, AuthenticationResultProperty, SPFAuthenticationResult, DKIMAuthenticationResult, AuthResError
from authres.dmarc import DMARCAuthenticationResult
from . import POLICY_PASS, POLICY_FAIL

def authres(result=None, **kwargs):
    """This is a convenience factory function that uses the dmarc.Result object
    to make the DMARCAuthenticationResult object.
    
    Args:
        result: dmarc.Result object
    
    Returns:
        DMARCAuthenticationResult object
    """
    kwargs['result'] = 'none'
    if result:
        adict = result.as_dict()
        policy_published = adict['policy_published']
        policy_evaluated = adict['record']['row']['policy_evaluated']
        
        if result.result == POLICY_PASS:
            kwargs['result'] = 'pass'
        elif result.result == POLICY_FAIL:
            kwargs['result'] = 'fail'
        
        kwargs['result_comment'] = ' '.join('{0}=%({1})s'.format(key,key) for key in policy_published) % policy_published
        kwargs['header_from'] = result.policy.domain
        kwargs['policy'] = policy_evaluated['disposition']
        kwargs['policy_comment'] = ' '.join('{0}=%({1})s'.format(key,key) for key in policy_evaluated) % policy_evaluated
    
    return DMARCAuthenticationResult(**kwargs)
