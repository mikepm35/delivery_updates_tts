import logging
from aenum import Enum
from datetime import datetime
import json
from utils import *
import scrapers.caviar as caviar
import requests

_logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
_logger.addHandler(handler)
_logger.setLevel(logging.INFO)

class Order():
    def __init__(self, opendatetime, lastupdate, service, username, password,
                    status_text, order_id, general_status):
        self.initialize(opendatetime, lastupdate, service, username, password,
                        status_text, order_id, general_status)

    def initialize(self, opendatetime, lastupdate, service, username, password,
                    status_text, order_id, general_status):
        self.opendatetime = opendatetime
        self.lastupdate = lastupdate
        self.service = service
        self.username = username
        self.password = password
        self.status_text = status_text
        self.order_id = order_id
        self.session = requests.session()
        self.general_status = general_status


    def get_order(self):
        now = datetime.now()
        if self.service == Services.caviar.value:
            order_id = caviar.caviar_get_order(order=self)
            if not order_id:
                _logger.error("Order ID is empty")
            self.order_id = order_id
            self.lastupdate = now

        return

    def update_status(self):
        now = datetime.now()
        if self.service == Services.caviar.value:
            status_text = caviar.caviar_update_status(order=self)
            self.status_text = status_text
            self.lastupdate = now

        return
