import time

from commons_lib.utils import ttl_cache


@ttl_cache(10)
def call_expensive(a: int):
    time.sleep(5)
    return a**2




def test_ttl_cache():
    start=time.time()

    call_expensive(999)

    e1=time.time()

    assert  (e1-start) > 3

    call_expensive(999)
    e2=time.time()

    assert  (e2-e1) < 3






