LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'default_format': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },

    'handlers': {
        # 'console': {
        #     'level': 'DEBUG',
        #     'class': 'logging.StreamHandler',
        #     'formatter': 'default_format'
        # },
        # 'sentry_handler': {
        #     'level': SENTRY_LOG_LEVEL,
        #     'class': 'raven.handlers.logging.SentryHandler',
        #     'dsn': DSN,
        # },

        "file_handler": {
            'level': 'INFO',
            "class": 'logging.FileHandler',
            "filename": "log.log",
            "formatter": "default_format"
        },
        "similar_photos_handler": {
            'level': 'INFO',
            "class": 'logging.FileHandler',
            "filename": "similar_photos_logger.log",
            "formatter": "default_format"
        }

    },

    'loggers': {
        # 'root': {
        #     'handlers': ['console'],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
        # 'sentry': {
        #     'handlers': ['sentry_handler'],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
        'file': {
            'handlers': ['file_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'similar_photos_logger': {
            'handlers': ['similar_photos_handler'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}
