import geckoterminal

from .config import NETWORK, TOKEN_ADDRESS, TOKEN_ADDRESSES, POOL_ADDRESS, POOL_ADDRESSES

def test_get_networks():
    assert geckoterminal.get_networks()['data']

def test_get_dexes():
    assert geckoterminal.get_dexes(network=NETWORK)['data']

def test_get_pool():
    assert geckoterminal.get_pool(network=NETWORK, pool_address=POOL_ADDRESS)['data']

def test_get_pools():
    assert geckoterminal.get_pools(network=NETWORK, pool_addresses=POOL_ADDRESSES)['data']

def test_get_top_pools():
    assert geckoterminal.get_top_pools(network=NETWORK)['data']

def test_get_new_pools():
    assert geckoterminal.get_new_pools(network=NETWORK)['data']

def test_get_token():
    assert geckoterminal.get_token(network=NETWORK, token_address=TOKEN_ADDRESS)['data']

def test_get_tokens():
    assert geckoterminal.get_tokens(network=NETWORK, token_addresses=TOKEN_ADDRESSES)['data']

def test_get_top_pools_for_token():
    assert geckoterminal.get_top_pools_for_token(network=NETWORK, token_address=TOKEN_ADDRESS)['data']

def test_get_token_info():
    assert geckoterminal.get_token_info(network=NETWORK, token_address=TOKEN_ADDRESS)['data']

def test_get_pool_info():
    assert geckoterminal.get_pool_info(network=NETWORK, pool_address=POOL_ADDRESS)['data']

def test_get_pool_ohlcv():
    assert geckoterminal.get_pool_ohlcv(network=NETWORK, pool_address=POOL_ADDRESS)['data']

def test_get_pool_ohlcv():
    assert geckoterminal.get_pool_ohlcv(network=NETWORK, pool_address=POOL_ADDRESS)['data']