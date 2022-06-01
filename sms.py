import logging
import requests
from twilio.rest import Client
from django.conf import settings

logger = logging.getLogger(__name__)

# Your Account Sid and Auth Token from twilio.com/console
account_sid = 'AC92cec6d5754aa6c87234b855ae2169a3'
auth_token = '5a90a26e497041a68c808801e625acac'
client = Client(account_sid, auth_token)


def send_sms(body, to, agrinet=False):
    if not is_sending_sms_allowed():
        return

    if agrinet:
        return send_sms_agrinet(body, to)
    else:
        return send_sms_twilio(body, to)


def send_sms_twilio(body, to):
    # TODO: Depending on country, can use Alphanumeric Sender ID to make from_ = to say Kudu if you want only 1-way communication. Canada does NOT allow this, so can't test...

    message = client.messages \
        .create(
        body=body,
        from_='+16042109019',
        to=to
    )
    if message.error_code:
        logger.warning(f'{message.error_code}: {message.error_message}')
    return message


def send_sms_agrinet(body, to):
    url = "https://sms.dmarkmobile.com/v2/api/send_sms/"
    if len(body) > 158:
        logger.warning(f'A long message has been sent, please correct the user. {body}')
    values = dict(numbers=to, msg=body, spname='agrinet', sppass='Agripwd2020', type='json')
    try:
        r = requests.get(url, params=values)
        r.raise_for_status()
    except Exception as e:
        logger.error(f'Could not send SMS message {body} to {to}')
        raise e


def is_sending_sms_allowed():
    return settings.SEND_SMS
