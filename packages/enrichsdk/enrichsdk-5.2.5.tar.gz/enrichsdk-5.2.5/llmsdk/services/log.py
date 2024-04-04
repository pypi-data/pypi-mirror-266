# https://stackoverflow.com/questions/62894952/fastapi-gunicon-uvicorn-access-log-format-customization
import os
import logging

if 'LOGDIR' in os.environ:
    APP_LOG_FILE = os.path.join(os.environ['LOGDIR'],
                                os.environ['AGENTNAME'],
                                "app.json.log")
    try:
        os.makedirs(os.path.dirname(APP_LOG_FILE))
    except:
        pass
    applogconfig = {
        "level": "DEBUG",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": APP_LOG_FILE,
        "maxBytes": 1024 * 1024 * 10,  # 10
        "backupCount": 100,
        "formatter": "json",
    }
else:
    applogconfig = {
        "formatter": "default",
        "class": "logging.StreamHandler",
        "stream": "ext://sys.stdout",
    }


log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(message)%(levelname)%(name)%(asctime)%(funcName)%(lineno)%(pathname)%(module)%(created)",
        },
        'access': {
            '()': 'uvicorn.logging.AccessFormatter',
            'fmt': '%(levelprefix)s %(asctime)s - %(client_addr)s - "%(request_line)s" %(status_code)s',
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": False
        },
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": False
        },
    },
    "handlers": {
        "app": applogconfig,
        'access': {
            'class': 'logging.StreamHandler',
            'formatter': 'access',
            'stream': 'ext://sys.stdout'
        },
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {

        "app": {
            "handlers": ["app"],
            "level": "DEBUG",
            "propagate": False
        },
        "uvicorn": {
            "handlers": ["access"],
            "level": "DEBUG",
            "propagate": True
        },
        'uvicorn.access': {
            'handlers': ['access'],
            'level': 'INFO',
            'propagate': False
        },
        'uvicorn.error': {
            'level': 'INFO',
            'propagate': False
        }
    },
}


def get_logger():
    return logging.getLogger("app")
