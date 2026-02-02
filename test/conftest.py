# coding: utf-8
 
import pytest
# from strip_zsnd import LogConfigurator

@pytest.fixture(scope='session', autouse=True)
def global_setup():
    print('=== GLOBAL SETUP ===')
    # LogConfigurator().configre()

    yield

    print('=== GLOBAL TEARDOWN ===')
