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
    cclog.info('test_info_logging')

def test_warning_logging(cclog):
    cclog.warning('test_warning_logging')

def test_error_logging(cclog):
    cclog.error('test_error_logging')

def test_event_logging(cclog):
    cclog.event('test_event_logging')
    cclog.event('test_event_logging', time='now', username='brianz', age=29)

def test_event_extras_from_dict(cclog):
    d = {'time': 'now', 'username': 'brianz', 'age': 29}
    cclog.event('test_event_extras_from_dict', wow=True, **d)

def test_timer_logging(cclog):
    cclog.timer('test_timer_logging', 0.1233)
    cclog.timer('test_timer_logging', 1233, action='clicked', location='upperleft')

def test_counter_logging(cclog):
    cclog.counter('test_counter_logging')
    cclog.counter('test_counter_logging', something=0.123)

def test_gauge_logging(cclog):
    cclog.gauge('test_gauge_logging', 6400)
    cclog.gauge('test_gauge_logging', 6400, scale='rpm', redline=8900)

