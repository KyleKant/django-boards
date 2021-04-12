from django.test import TestCase
from django import forms
from ..templatetags.form_tags import field_type, input_class


class ExampleForm(forms.Form):
    name = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        fields = ('name', 'password')


class FieldTypeTests(TestCase):
    def test_field_widget_type(self):
        form = ExampleForm()
        self.assertEquals('TextInput', field_type(form['name']))
        self.assertEquals('PasswordInput', field_type(form['password']))
        pass


class InputClassTest(TestCase):
    def test_unbound_field_initiate_state(self):
        form = ExampleForm()  # unbound form
        self.assertEquals('form-control ', input_class(form['name']))
        pass

    def test_valid_bound_field(self):
        form = ExampleForm({'name': 'john', 'password': '123'})
        self.assertEquals('form-control is-valid', input_class(form['name']))
        self.assertEquals('form-control ', input_class(form['password']))
        pass

    def test_invalid_bound_field(self):
        form = ExampleForm({'name': '', 'password': '123'})
        self.assertEquals('form-control is-invalid', input_class(form['name']))
        pass
