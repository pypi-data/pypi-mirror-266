from .helpers import c
from .helpers import get_all_tokens_fr_tokens_repo
from .helpers import get_gt

def get_token(key = None) :
    """ Gets the token by a key from the private tokens repo on my GitHub """

    if not c.lg.exists() :
        raise ValueError(f'GitHub Token Not Found.')

    # If key is None, return the GitHub token itself
    if key is None :
        return get_gt()

    # Get all tokens from the private tokens repo
    all_toks = get_all_tokens_fr_tokens_repo()

    target_tok = all_toks[key]

    return target_tok
