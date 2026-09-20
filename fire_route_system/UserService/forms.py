from django import forms
from django.contrib.auth.hashers import make_password
from .models import Role, User

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = '__all__'


class UserForm(forms.ModelForm):
    password_hash = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(render_value=False),
        required=False,
        help_text="Leave blank to keep existing password when editing."
    )

    class Meta:
        model = User
        fields = ['role', 'username', 'email', 'password_hash', 'phone_number', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['password_hash'].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        raw_pw = self.cleaned_data.get('password_hash')
        if raw_pw:
            user.set_password(raw_pw)
        elif not user.pk and not user.password_hash:
            user.set_password('defaultpassword123')
        if commit:
            user.save()
        return user