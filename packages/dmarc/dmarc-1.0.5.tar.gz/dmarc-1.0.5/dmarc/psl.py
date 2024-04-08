from publicsuffix2 import PublicSuffixList

PSL = None

def load(psl_file, idna=True):
    global PSL
    PSL = PublicSuffixList(psl_file, idna)
    return PSL

def get_public_suffix(domain):
    return PSL.get_sld(domain) if PSL else load(psl_file=None).get_sld(domain)
