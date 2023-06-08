from django import forms
from greatkartapp.models import Account,Order,ReviewRating


class RegistraionForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control',
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Re-enter Password',
        'class': 'form-control',
    }))

    class Meta:
        model=Account
        fields=['first_name','last_name','phone_number','email','password']


    def clean(self):
        cleaned_data=super(RegistraionForm,self).clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match"
            )


    def __init__(self, *args, **kwargs):
        super(RegistraionForm,self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Mobile Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'





# Order form


class OrderForm(forms.ModelForm):
    class Meta:
        model=Order
        fields = ['first_name','last_name','phone','email','address_line_1','address_line_2','country','state','city','district','street','postal_code','order_note']



class ReviewForm(forms.ModelForm):
    class Meta:
        model=ReviewRating
        fields=['subject','review','rating']