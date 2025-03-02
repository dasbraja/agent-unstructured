import logging as log
import os

LOG_FORMAT = '%(asctime)s %(levelname)s: [%(name)s/%(module)s/%(funcName)s] %(message)s'
DEFAULT_LOGLEVEL = log.INFO


def validate_loglevel_intstr(loglevel):  # pragma: no cover
    try:
        return int(loglevel) in log._nameToLevel.values()  # noqa
    except Exception as oops:
        print('EXCEPTION:', oops)
        log.exception('EXCEPTION! %s', oops)
        return False


def set_or_reset_logging(
        loglevel):  # pragma: no cover
    try:
        if validate_loglevel_intstr(loglevel):
            log.basicConfig(format=LOG_FORMAT, level=int(loglevel), force=True)  # force requires py 3.8
            return True
    except Exception as oops:
        print('EXCEPTION:', oops)
        log.exception('EXCEPTION! %s', oops)
        return


LOGLEVEL_CONSOLE = int(os.environ.get('LOGLEVEL_CONSOLE', DEFAULT_LOGLEVEL)) if validate_loglevel_intstr(
    os.environ.get('LOGLEVEL_CONSOLE', DEFAULT_LOGLEVEL)) else DEFAULT_LOGLEVEL
set_or_reset_logging(LOGLEVEL_CONSOLE)
