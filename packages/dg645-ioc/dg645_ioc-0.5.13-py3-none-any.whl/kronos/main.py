#!/usr/bin/python3

#if environ.get("COVERAGE_PROCESS_START", "no") == "yes":
#    import coverage
#    coverage.process_startup()

from kronos import application
import logging, asyncio
from os import environ

logger = logging.getLogger("kronos")

def main():

    log_level_name = environ.get('DG645_LOGGING', 'info').lower()
    log_level = {
        'info': logging.INFO,
        'debug': logging.DEBUG,
        'warn': logging.WARNING,
        'warning': logging.WARNING,
        'error': logging.ERROR
    }[log_level_name]

    logging.basicConfig()
    logger.setLevel(log_level)
    logging.getLogger('emmi').setLevel(log_level)

    logger.info(f"Starting, requested log level: {log_level_name}")
    logger.debug("Debug level logging active")

    try:
        from kronos._version import version
        logger.info(f'Kronos IOC version {version}')
    except:
        logger.info('Cannot read package version info')
        
    app = application.Application()
    
    asyncio.run(app.async_run())

if __name__ == "__main__":
    main()
