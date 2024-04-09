from os import environ
from pathlib import Path

import requests

class Const :
    # local GitHub token absolute filepath $HOME/.gt.json, I assume it is in the home directory
    lg = Path(environ['HOME']) / '.gt'
    # GitHub username
    gu = 'imahdimir'

c = Const()

def get_gt() :
    with open(c.lg , 'r') as f :
        gt = f.read()
    return gt

def get_all_tokens_fr_tokens_repo() -> dict :
    """ Gets all tokens from the private tokens repo """
    tok = get_gt()

    trg_repo = 'tokens'
    br = 'main'
    fn = 'main.json'
    url = ret_github_url_for_private_access_to_file(tok , trg_repo , br , fn)

    _hdr = {
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
            }

    r = requests.get(url , headers = _hdr)
    j = r.json()

    return j

def ret_github_url_for_private_access_to_file(tok , trg_repo , brnch , fn) :
    return f'https://{c.gu}:{tok}@raw.githubusercontent.com/{c.gu}/{trg_repo}/{brnch}/{fn}'
