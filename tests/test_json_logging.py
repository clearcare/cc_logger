import json
import logging
import sys

import cc_logger

import pytest


def get_logger(name='test_json_logger', **kwargs):
    return cc_logger.loggers.create_logger(name, **kwargs)

def parse_json_log_output(_capsys):
    out, err = _capsys.readouterr()
    return json.loads(out)


def test_name_sanitizer():
    name = cc_logger.loggers.sanitize_name('this is my log')
    assert name == 'this_is_my_log'


def test_info_logging(capsys):
    cclog = get_logger()
    cclog.info('test_info_logging')
    json_log = parse_json_log_output(capsys)

    assert json_log.get('environment') == ''
    assert json_log.get('name') == 'test_json_logger'
    assert json_log.get('module') == 'test_json_logging'
    assert json_log.get('filename') == 'test_json_logging.py'
    assert json_log.get('funcName') == 'test_info_logging'
    assert json_log.get('levelname') == 'INFO'
    assert json_log.get('levelno') == 20
    assert json_log.get('args') == []
    assert json_log.get('@timestamp')
    assert json_log.get('process')
    assert json_log.get('host')


def test_environment_set(capsys):
    cclog = get_logger(name='my_env', environment='1123testing')
    cclog.info('my_event')
    json_log = parse_json_log_output(capsys)
    assert json_log.get('environment') == '1123testing'


def test_warning_logging(capsys):
    cclog = get_logger()
    cclog.warning('test_warning_logging')
    json_log = parse_json_log_output(capsys)
    assert json_log.get('levelname') == 'WARNING'
    assert json_log.get('levelno') == 30


def test_error_logging(capsys):
    cclog = get_logger()
    cclog.error('test_error_logging')
    json_log = parse_json_log_output(capsys)
    assert json_log.get('levelname') == 'ERROR'
    assert json_log.get('levelno') == 40


def test_event_logging(capsys):
    cclog = get_logger()
    cclog.event('test_event_logging', time='now', username='brianz', age=29)
    json_log = parse_json_log_output(capsys)
    assert json_log.get('time') == 'now'
    assert json_log.get('username') == 'brianz'
    assert json_log.get('age') == 29


def test_event_from_extra_dict(capsys):
    cclog = get_logger()
    extra = {'time': 'now', 'username': 'brianz', 'age': 29}
    cclog.event('test_event_extras_from_dict', top_level=1, fooey=True, extra=extra)
    json_log = parse_json_log_output(capsys)
    assert json_log.get('time') == 'now'
    assert json_log.get('username') == 'brianz'
    assert json_log.get('age') == 29
    assert json_log.get('top_level') == 1
    assert json_log.get('fooey') == True


def test_event_from_dict(capsys):
    cclog = get_logger()
    d = {'time': 'now', 'username': 'brianz', 'age': 29}
    cclog.event('test_event_extras_from_dict', wow=True, **d)
    json_log = parse_json_log_output(capsys)
    assert json_log.get('time') == 'now'
    assert json_log.get('username') == 'brianz'
    assert json_log.get('age') == 29
    assert json_log.get('wow') == True


def test_extra_dict_flattened(capsys):
    cclog = get_logger()
    extra = {'this_is': 'extra', 'nested': {'this_is': '2nd level'}}
    cclog.event('test_extra_dict_flattened', first_level=True, extra=extra)
    json_log = parse_json_log_output(capsys)
    assert json_log.get('first_level') == True
    assert json_log.get('this_is') == 'extra'
    assert json_log.get('nested') == {'this_is': '2nd level'}


def test_timer_logging_with_int(capsys):
    cclog = get_logger()
    cclog.timer('element_response_time', 33)
    json_log = parse_json_log_output(capsys)
    assert json_log.get('DTM_STATS') == 'element_response_time'
    assert json_log.get('stat_type') == 'timer'
    assert json_log.get('stat_value') == 33


def test_timer_logging_with_float(capsys):
    cclog = get_logger()
    cclog.timer('user_clicked', 0.1233, action='clicked', location='upperleft')
    json_log = parse_json_log_output(capsys)
    assert json_log.get('DTM_STATS') == 'user_clicked'
    assert json_log.get('stat_type') == 'timer'
    assert json_log.get('stat_value') == 0.1233
    assert json_log.get('action') == 'clicked'
    assert json_log.get('location') == 'upperleft'


def test_counter_logging(capsys):
    cclog = get_logger()
    cclog.counter('something_happened', seriously=True)
    json_log = parse_json_log_output(capsys)
    assert json_log.get('DTM_STATS') == 'something_happened'
    assert json_log.get('stat_type') == 'counter'
    assert json_log.get('seriously') == True


def test_gauge_logging(capsys):
    cclog = get_logger()
    cclog.gauge('revs', 6400, scale='rpm', redline=8900)
    json_log = parse_json_log_output(capsys)
    assert json_log.get('DTM_STATS') == 'revs'
    assert json_log.get('stat_type') == 'gauge'
    assert json_log.get('stat_value') == 6400
    assert json_log.get('scale') == 'rpm'
    assert json_log.get('redline') == 8900


def test_exception_logging(capsys):
    cclog = get_logger()
    try:
        assert False
    except AssertionError, err:
        cclog.exception(err)
    json_log = parse_json_log_output(capsys)
    exc = json_log.get('exception')
    assert exc
    assert 'Traceback' in exc[0]
    assert 'AssertionError' in ''.join(exc)
    assert json_log.get('levelname') == 'ERROR'
    assert json_log.get('levelno') == 40
