'''Not allowed to import anything from models.py'''


def exchange_rate(date):
    '''Return the UGX:USD exchange rate'''
    return 1. / 3600


def exchange(value, date):
    '''Convert UGX to USD'''
    return value * exchange_rate(date)


def make_link(model):
    return '<a href="{url}">{pk}</a>'.format(url=model.get_absolute_url(), pk=model.pk)