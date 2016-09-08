import logging
import logging.handlers
import re
from logging.config import dictConfig

from threading import Lock

_log_lock = Lock()
_log_registy = {}


default_level = logging.INFO

_spaces_re = re.compile(r'\s+')


def sanitize_name(name):
    return _spaces_re.sub('_', name.strip())


class CCLoggerAdapter(logging.LoggerAdapter):

    def process(self, msg, kwargs):
        """Flatten the log message so we can support arbitrary kwargs as well as the `extra` dict.

        ::

            log.event('something', when="now", why="just because")
            log.info('booya', level=1, extra={'foo': 'bar', 'srsly': True})

        All keys and values will be flattened into a single level:

            {"DTM_EVENT": "something", "when": "now", "why": "just_because"}
            {"DTM_EVENT": "booya", "level": 1, "foo": "bar", "srsly": true}
        """
        extra = kwargs.pop('extra', {})
        extra.update(kwargs)
        extra.update(self.extra)
        return msg, {'extra': extra}

    def event(self, event_name, level=default_level, **kwargs):
        event_name = sanitize_name(event_name)
        kwargs['DTM_EVENT'] = event_name
        self.log(level, 'event: %s' % event_name, **kwargs)

    def timer(self, timer_name, timer_value, level=default_level, **kwargs):
        timer_name = sanitize_name(timer_name)
        kwargs.update({
            'DTM_STATS': timer_name,
            'stat_value': timer_value,
            'stat_type': 'timer',
        })
        self.log(level, 'timer: %s: %s' % (timer_name, timer_value), **kwargs)

    def counter(self, counter_name, level=default_level, **kwargs):
        counter_name = sanitize_name(counter_name)
        kwargs.update({
            'DTM_STATS': counter_name,
            'stat_type': 'counter',
        })
        self.log(level, 'counter: %s' % counter_name, **kwargs)

    def gauge(self, gauge_name, gauge_value, level=default_level, **kwargs):
        gauge_name = sanitize_name(gauge_name)
        kwargs.update({
            'DTM_STATS': gauge_name,
            'stat_value': gauge_value,
            'stat_type': 'gauge',
        })
        self.log(level, 'gauge: %s' % gauge_name, **kwargs)


def get_cached_logger(name):
    """Lookup loggers in a global dict.

    Delegate this to a function mostly for testing purposes.

    """
    return _log_registy.get(name, None)


def create_logger(name, environment='', level=default_level):
    base_config = {
        u'version': 1,
        u'formatters': {
            u'logstashformatter': {
                u'()': u'cc_logger.formatters.CCFormatter'
            },
            u'json': {
                u'format': u'{"loggerName": "%(name)s", "asciTime": "%(asctime)s", "fileName": "%(filename)s", "logRecordCreationTime": "%(created)f", "functionName": "%(funcName)s", "levelNo": "%(levelno)s", "lineNo": "%(lineno)d", "time": "%(msecs)d", "levelName": "%(levelname)s", "message": %(message)s}'
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

    name = sanitize_name(name)

    log_adapter = get_cached_logger(name)
    if log_adapter:
        return log_adapter

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
        log_adapter = CCLoggerAdapter(logger, {'environment': environment})
        _log_registy[name] = log_adapter
        return log_adapter
