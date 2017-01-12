from app import application
import logging
import os.path

_logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
_logger.addHandler(handler)
_logger.setLevel(logging.INFO)

if __name__ == "__main__":
    if os.path.isfile("config.json"):
        _logger.info("Application started")
        application.debug = True
        application.run(host='0.0.0.0', port=5035)
    else:
        _logger.error("Config file not found!")
