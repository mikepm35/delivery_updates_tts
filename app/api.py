from app import application
import logging
from models import *
from utils import *
from flask import request
import json
import requests
from datetime import datetime
import sys

_logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
_logger.addHandler(handler)
_logger.setLevel(logging.INFO)

openOrder = Order(opendatetime=datetime.now(), lastupdate=datetime.now(),
                    service="", username="", password="", status_text="",
                    order_id="", general_status=GeneralStatus.empty.value)
_logger.debug("openOrder created: %s", openOrder)

@application.route('/api/getstatus', methods=['POST'])
def get_status():
    if request.method == 'POST':
        _logger.debug("Full request: %s", request.data)
        delivery_scraper_password = request.args.get('password')

        if request.json.get('service'):
            service_input = request.json.get('service')
            input_success, tts_response, service = check_inputs(delivery_scraper_password, service_input)
        else:
            _logger.error("JSON post not read")
            tts_response = TTSResponses.internal_error.value
            input_success = False

        tts_url = get_tts_url()
        _logger.debug("TTS url: %s", tts_url)

        if not input_success:
            _logger.error("Input was not successfully parsed")
            payload = {"message": tts_response}
            requests.post(tts_url, data=json.dumps(payload))
        else:
            _logger.info("API input was successfully parsed")

            # Determine status of the openOrder instance
            now = datetime.now()
            diff_hrs = get_time_diff(later_time=now, earlier_time=openOrder.lastupdate)
            if openOrder.general_status == GeneralStatus.empty.value or openOrder.general_status == GeneralStatus.closed.value or diff_hrs > 2:
                _logger.info("Update existing openOrder instance: %s, %s", openOrder.general_status, diff_hrs)

                username, password = get_service_credentials(service)

                openOrder.initialize(opendatetime=now, lastupdate=now,
                                    service=service, username=username,
                                    password=password, status_text="",
                                    order_id="",
                                    general_status=GeneralStatus.pending.value)

                openOrder.get_order()

            # Get delivery information
            openOrder.update_status()
            tts_response = openOrder.status_text
            payload = {"message": tts_response}
            requests.post(tts_url, data=json.dumps(payload))

        return "complete"
