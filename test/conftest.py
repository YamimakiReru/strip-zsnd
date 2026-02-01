# coding: utf-8
 
import pytest
from collapse_wav_dropouts import LogConfigurator

@pytest.fixture(scope='session', autouse=True)
def global_setup():
    print('=== GLOBAL SETUP ===')
    LogConfigurator().configre()

    yield

    print('=== GLOBAL TEARDOWN ===')
