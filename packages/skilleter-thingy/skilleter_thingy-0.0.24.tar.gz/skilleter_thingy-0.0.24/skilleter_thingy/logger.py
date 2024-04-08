#! /usr/bin/env python3

################################################################################
""" Thingy logging functionality - wraps the Pythong logging module

    Copyright (c) 2017 John Skilleter

    Licence: GPL v3 or later
"""
################################################################################

import os

import logging

################################################################################

CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET

LOG_LEVELS = {
    'CRITICAL': CRITICAL, 'ERROR': ERROR, 'WARNING': WARNING, 'INFO': INFO,
    'DEBUG': DEBUG, 'NOTSET': NOTSET
}

__config_done__ = False

################################################################################

def set_logging(log, name):
    """ If an environment variable called NAME_DEBUG is set and defines a
        log level that is more verbose than the current level then set
        that level (you can only increase verbosity via the variable, not
        decrease it). """

    # Check whether there is an environment variable setting the debug level

    env_name = '%s_DEBUG' % name.upper()

    value = os.getenv(env_name, None)

    if value is not None:
        value = value.upper()

        current = log.getEffectiveLevel()

        # Check for a textual level in the value and if no match, try
        # for an integer level ignoring invalid values.

        if value in LOG_LEVELS:
            if current > LOG_LEVELS[value]:
                log.setLevel(LOG_LEVELS[value])
        else:
            try:
                intlevel = int(value)

                if current > intlevel:
                    log.setLevel(intlevel)

            except ValueError:
                pass

    return log

################################################################################

def init(name):
    """ Initilise logging and create a logger.
        If the environment variable NAME_DEBUG is set to a value in LOG_LEVELS
        then the log level is set to that level. If NAME_DEBUG is an integer
        then the same applies, otherwise, by default, the log level is CRITICAL """

    # Create the new logger

    log = logging.getLogger(name)

    # Default log level is CRITICAL

    log.setLevel(CRITICAL)

    # Set logging according to the value of THINGY_DEBUG (if set) then
    # override with the logger-specific variable (again, if set)

    set_logging(log, 'THINGY')
    set_logging(log, name)

    return log

################################################################################
# Entry point

# Ensure that the logging module is initialise

if not __config_done__:
    logging.basicConfig()
    __config_done__ = True

if __name__ == '__main__':
    demo = init('wombat')

    demo.critical('Critical error')

    # These messages should only appear if the WOMBAT_DEBUG environment variable
    # is set to an appropriate value (ERROR, WARNING or INFO)

    demo.error('Error message')
    demo.warning('Warning message')
    demo.info('Info message')
