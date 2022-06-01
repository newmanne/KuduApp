from django import forms

from agrotrade.models import ProduceDefinition


class AbstractBidForm(forms.Form):
    produce = forms.ModelChoiceField(queryset=ProduceDefinition.objects.filter(active=True))
    quantity = forms.IntegerField(min_value=0)
    price = forms.IntegerField(label='Price (UGX)', min_value=0)