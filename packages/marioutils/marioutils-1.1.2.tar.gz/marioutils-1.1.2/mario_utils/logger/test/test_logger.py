import pytest
from .. import src
import os


@pytest.fixture
def logger():
    logger = src.logger(name='test.log', level=src.Levels.DEBUG)
    yield logger


def test_file_creation(logger):
    logger.debug('Test file creation')
    assert os.path.exists('test.log')


def test_correct_level(logger):
    test_msg = 'TEST'
    logger.debug(test_msg)
    with open('test.log', 'r') as f:
        # The last item is an empty string
        last_record = f.read().split('\n')[-2]
        msg = last_record.split(' - ')[-1]
    assert test_msg == msg
