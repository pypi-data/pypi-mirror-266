import logging
import logging.handlers
import sys

# Log configuration --------------------------------------
LOG_FILENAME = '/tmp/radixTree.out'

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}


def get_params(param_name):
    """
    Detection of an argument on the command line like <param_name>=<value>
    Return <value> if any or ''
    Example :
      level=debug
      01234567890
           ^
      p_name=5
    """
    p_name = len(param_name)
    ret = ''
    if len(sys.argv)>1:
        for ar in range(len(sys.argv)):
            arg = sys.argv[ar]
            # print("arg : %s" % arg)
            a = len(arg)
            if a > p_name:
                # print("arg[p_name] : %s" %arg[p_name])
                # print("arg[0:p_name-1] : %s" %arg[0:p_name])
                if arg[p_name] == '=' and arg[0:p_name] == param_name:
                    ret = arg[p_name+1:]
    # print("Return value : %s" %ret)
    return ret

level = logging.NOTSET  # Par défaut, pas de log

level_name = get_params('level')
if level_name:
    level = LEVELS.get(level_name, logging.NOTSET)

my_logger = logging.getLogger(__name__)
my_logger.setLevel(level)

# Add the handler
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=1048576, backupCount=5)
# Formatter creation
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
# Add formatter to handler
handler.setFormatter(formatter)
my_logger.addHandler(handler)

handler = logging.StreamHandler()
# Formatter creation
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)d %(message)s")
# Add formatter to handler
handler.setFormatter(formatter)
my_logger.addHandler(handler)

my_logger.debug("End init radix_config")
# End log configuration --------------------------------------
