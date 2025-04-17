from django import forms

class AddressForm(forms.Form):
    street_address = forms.CharField(max_length=255, required=True)
    city = forms.CharField(max_length=100, required=True)
    postal_code = forms.CharField(max_length=10, required=True)
    country = forms.CharField(max_length=100, required=True)
    contact_number = forms.CharField(max_length=15,required=True,min_length=10)
    
