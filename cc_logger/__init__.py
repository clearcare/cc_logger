import logging
import logging.handlers

from logstash_formatter import LogstashFormatter

from threading import Lock

_log_lock = Lock()
_log_registy = {}


DefaultLoggerClass = logging.getLoggerClass()

LOGSTASH = logging.ERROR + 1
logging.addLevelName(LOGSTASH, 'LOGSTASH')


class CCLogstashLogger(DefaultLoggerClass):

    def __init__(self, name, **kwargs):
        if not isinstance(name, basestring):
            raise TypeError('name must be of type string, received type %s', type(name))

        if not name.strip():
            raise ValueError('name must be non-empty')

        self.name = name
        logging.Logger.__init__(self, name, **kwargs)

    def event(self, event_name, **extra):
        extra.update({
            'DTM_EVENT': event_name,
            'app_name': self.name,
        })
        self.log(LOGSTASH, 'event: %s' % event_name, extra=extra)

    def timer(self, timer_name, timer_value, **extra):
        extra.update({
            'DTM_STATS': timer_name,
            'app_name': self.name,
            'stat_value': timer_value,
            'stat_type': 'timer',
        })
        self.log(LOGSTASH, 'timer: %s: %s' % (timer_name, timer_value), extra=extra)

    def counter(self, counter_name, **extra):
        extra.update({
            'DTM_STATS': counter_name,
            'app_name': self.name,
            'stat_type': 'counter',
        })
        self.log(LOGSTASH, 'counter: %s' % counter_name, extra=extra)

    def gauge(self, gauge_name, gauge_value, **extra):
        extra.update({
            'DTM_STATS': gauge_name,
            'app_name': self.name,
            'stat_value': gauge_value,
            'stat_type': 'gauge',
        })
        self.log(LOGSTASH, 'gauge: %s' % gauge_name, extra=extra)


logging.setLoggerClass(CCLogstashLogger)


def create_logger(name, filehandler_config, stream_config=None, level=logging.WARNING):
    if name in _log_registy:
        return _log_registy[name]

    with _log_lock:
        logger = logging.getLogger(name)
        logger.setLevel(level)

        logstash_formatter = LogstashFormatter()

        fh_handler = logging.handlers.RotatingFileHandler(**filehandler_config)
        fh_handler.setLevel(level)
        fh_handler.setFormatter(logstash_formatter)
        logger.addHandler(fh_handler)

        if stream_config:
            stream_handler = logging.StreamHandler(stream=stream_config.get('stream'))
            stream_handler.setLevel(stream_config.get('level', level))
            stream_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            stream_handler.setFormatter(stream_formatter)
            logger.addHandler(stream_handler)

        _log_registy[name] = logger
        return logger
