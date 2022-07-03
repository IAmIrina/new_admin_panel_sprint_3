"""Logging settings."""

import os
import sys
import types

log_level = os.environ.get('LOG_LEVEL', 'DEBUG').upper()

LOG_STDOUT = 'stdout'

LOGGING = types.MappingProxyType({
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'file': {
            'format': '%(asctime)s: [ %(levelname)s ]: %(module)s : [%(process)d]: %(message)s',
        },
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'file',
            'stream': sys.stdout,
        },
    },
    'loggers': {
        'database.pg_database': {
            'level': log_level,
            'handlers': [LOG_STDOUT],
            'propagate': False,
        },
        'processors.enricher': {
            'level': log_level,
            'handlers': [LOG_STDOUT],
            'propagate': False,
        },
        'processors.extractor': {
            'level': log_level,
            'handlers': [LOG_STDOUT],
            'propagate': False,
        },
        'processors.loader': {
            'level': log_level,
            'handlers': [LOG_STDOUT],
            'propagate': False,
        },
        'processors.transformer': {
            'level': log_level,
            'handlers': [LOG_STDOUT],
            'propagate': False,
        },
    },
    'root': {
        'level': log_level,
        'handlers': [LOG_STDOUT],
    },
})
