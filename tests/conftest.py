import cc_logger

# Patch the caching so that we always reconstruct the loggers during testing
cc_logger.loggers.get_cached_logger = lambda name: None
