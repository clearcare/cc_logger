import logging
import logging.handlers
import re
from logging.config import dictConfig

from threading import Lock

_log_lock = Lock()
_log_registy = {}


DefaultLoggerClass = logging.getLoggerClass()

LOGSTASH = logging.INFO + 1
logging.addLevelName(LOGSTASH, 'LOGSTASH')

_spaces_re = re.compile(r'\s+')


def sanitize_name(name):
    return _spaces_re.sub('_', name.strip())


class CCLogstashLogger(DefaultLoggerClass):

    def __init__(self, name, **kwargs):
        if not isinstance(name, basestring):
            raise TypeError('name must be of type string, received type %s', type(name))

        if not name.strip():
            raise ValueError('name must be non-empty')

        self.name = sanitize_name(name)
        logging.Logger.__init__(self, self.name, **kwargs)

    def event(self, event_name, **extra):
        event_name = sanitize_name(event_name)
        extra.update({
            'DTM_EVENT': event_name,
            'app_name': self.name,
            'environment': self.environment,
        })
        self.log(LOGSTASH, 'event: %s' % event_name, extra=extra)

    def timer(self, timer_name, timer_value, **extra):
        timer_name = sanitize_name(timer_name)
        extra.update({
            'DTM_STATS': timer_name,
            'app_name': self.name,
            'stat_value': timer_value,
            'stat_type': 'timer',
            'environment': self.environment,
        })
        self.log(LOGSTASH, 'timer: %s: %s' % (timer_name, timer_value), extra=extra)

    def counter(self, counter_name, **extra):
        counter_name = sanitize_name(counter_name)
        extra.update({
            'DTM_STATS': counter_name,
            'app_name': self.name,
            'stat_type': 'counter',
            'environment': self.environment,
        })
        self.log(LOGSTASH, 'counter: %s' % counter_name, extra=extra)

    def gauge(self, gauge_name, gauge_value, **extra):
        gauge_name = sanitize_name(gauge_name)
        extra.update({
            'DTM_STATS': gauge_name,
            'app_name': self.name,
            'stat_value': gauge_value,
            'stat_type': 'gauge',
            'environment': self.environment,
        })
        self.log(LOGSTASH, 'gauge: %s' % gauge_name, extra=extra)


logging.setLoggerClass(CCLogstashLogger)


def create_logger(name, environment='', level=None):
    base_config = {
        u'version': 1,
        u'formatters': {
            u'logstashformatter': {
                u'()': u'logstash_formatter.LogstashFormatter'
            },
        },
        u'handlers': {
            u'console': {
                u'class': u'logging.StreamHandler',
                u'level': u'DEBUG',
                u'formatter': u'logstashformatter',
                u'stream': u'ext://sys.stdout',
            },
        },
        u'disable_existing_loggers': False,
    }

    if name in _log_registy:
        return _log_registy[name]

    if level is None:
        level = LOGSTASH

    # Set up a new logger and add all of the handlers to it.
    loggers = base_config.get(u'loggers', {})
    loggers[name] = {
        u'level': level,
        u'handlers': [base_handler for base_handler in base_config.get(u'handlers', [])],
    }
    base_config[u'loggers'] = loggers
    dictConfig(base_config)

    with _log_lock:
        logger = logging.getLogger(name)
        logger.environment = environment
        _log_registy[name] = logger
        return logger
