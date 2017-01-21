from lxml import html
import json
from datetime import datetime
from utils import *
import logging
import os
import requests

_logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
_logger.addHandler(handler)
_logger.setLevel(logging.INFO)

def caviar_sign_in(order):
    order_html = order.session.get('https://www.trycaviar.com/users/sign_in')
    _logger.debug("Headers: %s", order_html.headers)
    try:
        tree = html.fromstring(order_html.text)
    except:
        _logger.error('Error reading html from sign in page')
        return ""

    token_elements = tree.xpath('//meta[@name="csrf-token"]')
    token = token_elements[0].get('content')
    if not token:
        _logger.error('Unable to get token for sign in')
        return ""

    payload = {'action': '/users/sign_in', 'user[password]': order.password,
                'user[remember_me]': '1', 'user[email]': order.username,
                'authenticity_token': token}

    response = order.session.post('https://www.trycaviar.com/users/sign_in', payload)
    _logger.debug("Headers: %s", response.headers)
    if response.status_code >= 400:
        _logger.error('Sign in post returned an HTTP error code: %s', response.status_code)
        return ""
    else:
        _logger.info("Successfully logged in: %s", response.status_code)
        return "success"


def caviar_get_html(order, endpoint):
    _logger.info("Calling caviar endpoint: %s", endpoint)
    order_html = order.session.get('https://www.trycaviar.com'+endpoint)
    _logger.debug("Headers: %s", order_html.headers)
    _logger.info("Order page retrieved: %s", order_html.status_code)
    try:
        tree = html.fromstring(order_html.text)
    except:
        _logger.error('Error reading html from orders page')
        return ""

    title_element = tree.xpath('//title/text()')

    if 'Sign In' in title_element[0]:
        _logger.info("Orders page redirected to sign in")
        sign_in_response = caviar_sign_in(order=order)
        if not sign_in_response:
            _logger.error("Sign in was not successful")
            return ""

        order_html = order.session.get('https://www.trycaviar.com'+endpoint)
        try:
            tree = html.fromstring(order_html.text)
        except:
            _logger.error('Error reading html from orders page')
            return ""
    else:
        _logger.info("Already signed in, using orders page")

    return tree

def caviar_get_order(order):
    tree = caviar_get_html(order=order, endpoint="/orders")
    if len(tree) == 0:
        _logger.error("HTML order response tree is empty")
        return ""

    element_list = tree.xpath('//li[@class="order-history_orders_content-body-column order-history_orders_content-column"]/text()')
    try:
        recent_datestr = element_list[0]
    except:
        _logger.warning('Not able to parse any order list items, returning empty order_id')
        return ""

    recent_datetime = datetime.strptime(recent_datestr, '%m/%d/%y %I:%M%p')
    _logger.debug('Most recent order datetime: %s', recent_datetime)

    now = datetime.now()
    diff_hrs = get_time_diff(later_time=now, earlier_time=recent_datetime)
    _logger.debug('Hours from last order: %s', diff_hrs)

    if diff_hrs > 4:
        _logger.warning("No recent orders found")
        order_id = ""
    else:
        href_elements = tree.xpath('//ul[@class="order-history_orders_content-body"]//a')
        try:
            order_id = href_elements[1].get('href')
        except:
            _logger.error('Not able to parse order url, returning empty order_id')
            return ""
        _logger.info("Using recent order: %s", order_id)

    return order_id

def caviar_update_status(order):
    tree = caviar_get_html(order=order, endpoint=order.order_id)
    if len(tree) == 0:
        _logger.error("HTML order_id response tree is empty")
        return ""
    else:
        _logger.info("Successfully retrieved order_id html tree")

    xmlblob = tree.xpath('//div[@data-react-class="OrderStatus"]')
    try:
        jsonblob = xmlblob[0].get('data-react-props')
    except:
        _logger.error("Not able to parse order information from html")
        order_statusfriendly = TTSResponses.order_parse_error.value

    jsondata = json.loads(jsonblob)

    order_status = jsondata['initial_status']
    order_time = 'It ' + jsondata['order_status_text'].split('.')[0].split('Your order ')[1].encode() + '.'

    _logger.info("Caviar initial_status: %s", order_status)

    if order_status == 'received_and_confirmed':
        order_statusfriendly = 'Your order has been received and confirmed by Caviar. ' + order_time
    elif order_status == 'being_made':
        order_statusfriendly = 'The kitchen is preparing your order. ' + order_time
    elif order_status == 'cancelled':
        order_statusfriendly = 'Your order has been cancelled.'
    elif order_status == 'out_for_delivery':
        order_statusfriendly = jsondata['order_status_hash']['out_for_delivery']['now_text'].encode()
    elif order_status == 'delivered':
        order_statusfriendly = 'Caviar says your order was delivered at ' + jsondata['order_status_hash']['delivered']['at'].encode() + '.'
        _logger.info("Order is delivered, so mark status as closed")
        order.general_status = GeneralStatus.closed.value
    else:
        _logger.error("Not able to extract order information from html")
        order_statusfriendly = TTSResponses.order_parse_error.value

    return order_statusfriendly
