import logging

# from fk.batch.Server import Server

logger = logging.getLogger(__name__)


def _test_server():
    config = {}
    server = Server(config)
    server.run()
    return True
