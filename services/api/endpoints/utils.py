"""
Endpoint Module for global usage like logging
Author: Po-Chun, Lu

"""

import time
import logging

from flask import request as req


def add_common_arguments(parser, arguments):
    for arg, required in arguments:
        parser.add_argument(
            arg,
            type=str,
            required=required,
            location='values',
            help=f'need to add {arg} to storage',
            dest=arg,
        )


def get_logger_adapter(resource="Request"):
    """ get log require args """
    return logging.LoggerAdapter(
        logging.getLogger("app"),
        {
            "tz": int(-(time.timezone / 3600)),
            "resource": resource,
            "method": req.method,
            "path": req.path,
            "ip": req.environ["REMOTE_ADDR"],
        },
    )


def log_context(resource="Request", context=None):
    """ function for logging text """
    logger = get_logger_adapter(resource)
    logger.info(log_contents(req, context))


def log_headers(request):
    """ get log of wsgi header args """
    common_headers = [
        "Host",
        "User-Agent",
        "Accept",
        "Accept-Language",
        "Accept-Encoding",
        "Connection",
        "Upgrade-Insecure-Requests",
        "Cache-Control",
        "Accept-Encoding",
        "Connection",
        "Content-Length",
        "Cookie",
    ]

    # remove common headers, only left customize headers
    request_dict = dict(request.headers.to_wsgi_list())
    for item in common_headers:
        try:
            del request_dict[item]
        except (KeyError, IndexError):
            pass

    return request_dict


def log_contents(request, option=None):
    """ format log text """
    log = log_headers(request)
    if option:
        log = {**log, **option}

    return "{}".format(log)
