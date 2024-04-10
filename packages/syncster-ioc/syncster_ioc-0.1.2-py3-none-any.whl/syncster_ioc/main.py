#!/usr/bin/python3

from syncster_ioc.application import SyncsterApplication

import logging, asyncio
logger = logging.getLogger("syncster_ioc")
from os import environ


def main(prefix=None, sim=False):
    
     logging.basicConfig(level={
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "WARN": logging.WARNING,
     }[environ.get('SYNCSTER_LOG_LEVEL', 'INFO').upper()])


     if prefix is None:
          prefix = environ.get('SYNCSTER_PREFIX', 'SYNCSTER:')
          logger.info(f'Prefix: {prefix}')

     if sim:
          app = SyncsterApplication(prefix)
          
     else:
          #dds_port = environ.get('SYNCSTER_DDS_PORT', '/dev/ttyUSB1')
          #logger.info(f'Want DDS-120 box: {dds_port}')    
          app = SyncsterApplication(prefix, rre_port, engine_params)

     asyncio.run(app.run()) 


if __name__ == "__main__":
    main()
