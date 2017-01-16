import logging
from aenum import Enum
from datetime import datetime
import json

_logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
_logger.addHandler(handler)
_logger.setLevel(logging.INFO)

class Services(Enum):
    caviar = "Caviar"

class GeneralStatus(Enum):
    empty = ""
    pending = "pending"
    closed = "closed"

class TTSResponses(Enum):
    internal_error = "Sorry, there was an internal error processing the request."
    order_parse_error = 'Sorry, there was an error getting your order information.'
    no_service_match = "Sorry, your request does not match a supported service."
    no_recent_order = "Sorry, I was not able to find a recent order"

def check_inputs(delivery_scraper_password, service_input):
    #process password
    try:
        with open('config.json') as config_data:
            config = json.load(config_data)
    except IOError:
        _logger.error("There was an error opening the config file")
        tts_response = TTSResponses.internal_error.value
        return False, tts_response, ""

    if delivery_scraper_password != config['delivery_scraper_password'] or not delivery_scraper_password:
        _logger.error("Password sent to service was not correct")
        tts_response = TTSResponses.internal_error.value
        return False, tts_response, ""

    #process service input
    if not service_input:
        logger.error("Service request did not exist")
        tts_response = TTSResponses.internal_error.value
        return False, tts_response, ""

    for s in Services:
        if s.value.lower() in service_input.lower():
            _logger.info("Matched service to %s", s.value)
            return True, "", s.value

    _logger.error("Did not match a service to input: %s", service_input)
    tts_response = TTSResponses.no_service_match.value
    return False, tts_response, ""

def get_tts_url():
    try:
        with open('config.json') as config_data:
            config = json.load(config_data)
    except IOError:
        _logger.error("There was an error opening the config file")
        return ""

    # endpoint = config['hass']['protocol'] + '://' + config['hass']['ip'] + ':' \
    #             + config['hass']['port'] + '/api/services/tts/' + \
    #             config['hass']['tts_service'] + '?api_password=' + \
    #             config['hass']['api_password']
    endpoint = config['update_url']

    return endpoint

def get_service_credentials(service):
    try:
        with open('config.json') as config_data:
            config = json.load(config_data)
    except IOError:
        _logger.error("There was an error opening the config file")
        tts_response = TTS
        return False, tts_response, ""

    username = config[service]['username']
    password = config[service]['password']

    return username, password

def get_time_diff(later_time, earlier_time):
    diff_hr = ((later_time - earlier_time).days * 24) \
                + ((later_time - earlier_time).seconds / 3600)

    return diff_hr
