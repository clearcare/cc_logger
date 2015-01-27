import logging
import sys

import cc_logger

import pytest


_logstash_file_config = {
        'filename': '/tmp/cc_logger_test.log',
        'maxBytes': 64000,
        'backupCount': 2,
        'mode': 'w',
}

_stream_config = {
        'stream': sys.stderr,
}

@pytest.fixture
def cclog():
    return cc_logger.create_logger(
                'test_logger',
                _logstash_file_config,
                stream_config=_stream_config,
                level=logging.INFO)

def test_info_logging(cclog):
    cclog.info('This is a an info message')

def test_error_logging(cclog):
    cclog.warning('This is a warning message')

def test_error_logging(cclog):
    cclog.error('This is an error message')

def test_event_logging(cclog):
    cclog.event('foo')
    cclog.event('foo', time='now', username='brianz', age=29)

def test_timer_logging(cclog):
    cclog.timer('click', 0.1233)
    cclog.timer('click', 1233, action='clicked', location='upperleft')

def test_counter_logging(cclog):
    cclog.counter('thing')
    cclog.counter('thing', something=0.123)

def test_gauge_logging(cclog):
    cclog.gauge('tachometer', 6400)
    cclog.gauge('tachometer', 6400, scale='rpm', redline=8900)
