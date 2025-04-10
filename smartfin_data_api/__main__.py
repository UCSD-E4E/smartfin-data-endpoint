'''Entry points
'''
import asyncio

from smartfin_data_api.config import configure_logging
from smartfin_data_api.service import Service


def main():
    """Main Entry Point
    """
    configure_logging()
    asyncio.run(Service().run())

def cli():
    """CLI Entry Point
    """
    configure_logging()
