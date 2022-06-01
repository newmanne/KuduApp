from django.core.exceptions import ValidationError
from django.utils import translation

from agrotrade.i18n import _
from agrotrade.models import UserSubmission, UserProfile, User, STATUS_UNSEEN
import logging
import re
from agrotrade.sms import send_sms_agrinet, send_sms
from agrotrade.seller import make_ask
import phonenumbers

logger = logging.getLogger(__name__)

def get_or_lightweight_register_user(phone_number):
    try:
        user = UserProfile.objects.get(phone_number=phone_number)
    except UserProfile.DoesNotExist:
        user = None

    if user is None:
        new_user = User.objects.create(username=phone_number)
        user = UserProfile.objects.create(
            phone_number=phone_number,
            user=new_user,
        )
    return user


def detect_language(message, userprofile=None):
    if userprofile and userprofile.language:
        return userprofile.language

    m = re.findall('\S+', message)
    lang = 'lug'  # Default language is Luganda
    eng = ('register', 'sell', 'buy', 'accept', 'reject', 'price', 'rate', 'block', 'update')
    lug = ('wandiisa', 'tunda', 'ntunda', 'gula', 'ngula', 'kkiriza', 'gaana', 'beeyi', 'gombolola')
    luo = ('dony', 'cat', 'wil', 'gam', 'kwer', 'wel')
    swa = ('jiandikisha', 'kuuza', 'nunua', 'kubali', 'kataa', 'bei')

    # Really rudimentary language detection
    for token in m:
        token = token.lower()
        if token in eng:
            lang = 'english'
            break
        elif token in lug:
            lang = 'lug'
            break
        elif token in luo:
            lang = 'luo'
            break
        elif token in 'swa':
            lang = swa
            break

    return lang


def detect_intent(message):
    pass

def process_msg(number, message):
    logger.info(f"{number} sent {message}")

    validation = phonenumbers.parse(number, None)
    if not phonenumbers.is_valid_number(validation):
        raise ValidationError(
            _('%(value) is not a valid phone number'),
            params={'value': number},
        )

    user_profile = get_or_lightweight_register_user(number)
    UserSubmission.objects.create(
        owner=user_profile,
        message=message,
        status=STATUS_UNSEEN,
    )

    # TODO: Biggest problem is the UI for Miryam. Placing an ask ON BEHALF of someone. Way to view messages and mark them as dealt with

    language = detect_language(message)
    with translation.override(language):
        response = (_('Thanks for your submission to Kudu. We will contact you shortly if more details are required.'))
        send_sms(response, number)

    # intent = detect_intent(message)
    # Should ANYTHING go into the DB until someone has looked at it? I'm tempted to say no...
    #     if intent == 'sell':
    #     elif intent == 'buy':
    #     else:
    #         logger.warning("Unrecognized intent, needs manual looking over")

        # if keyword in ('sell', 'tunda', 'ntunda', 'cat'):
        # TODO: Parse out the rest of the message, see if you can match up produce quantity and price
        #     # make_ask(user_profile, message.lower(), lang, medium=medium, solicited=solicited)
        #     # response =
        # elif keyword in ('buy', 'gula', 'ngula', 'wil'):
        #     response = Buyer().buy(user, message.lower(), lang, medium=medium, solicited=solicited)
    # TODO: Infrastructure for Miryam is going to be the hardest to create
