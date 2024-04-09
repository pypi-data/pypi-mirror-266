import os
import sys
import logging
import traceback
import openobserve

stream_global = 'default'
organization_global = 'default'

logs_dir = os.path.join(os.path.expanduser('~'), '.openobserve', 'logs')

if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

logging.basicConfig(filename=logs_dir + '/log.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')
openobserve.additional_info = True


def log_unhandled_exceptions(exctype, value, tb) -> None:
    global stream_global, organization_global

    openobserve.send(
        job=str(exctype.__name__),
        message=str(value),
        level='FATAL_ERROR',
        traceback=str("".join(traceback.format_tb(tb))),
        _stream=stream_global,
        _organization=organization_global
    )

    logging.error(str(exctype.__name__) + ' ' + str(value) + ' - ' + str("".join(traceback.format_tb(tb))))


sys.excepthook = log_unhandled_exceptions
