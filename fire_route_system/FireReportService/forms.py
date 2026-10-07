from django import forms
from DataAccess.models import FireReport

class FireReportForm(forms.ModelForm):
    class Meta:
        model = FireReport
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.DateTimeField):
                field.widget = forms.DateTimeInput(format='%d-%m-%Y %I:%M %p', attrs={'data-datepicker': 'datetime', 'placeholder': 'dd-mm-yyyy hh:mm AM/PM'})
                field.input_formats = ['%d-%m-%Y %I:%M %p']
            elif isinstance(field, forms.DateField):
                field.widget = forms.DateInput(format='%d-%m-%Y', attrs={'data-datepicker': 'date', 'placeholder': 'dd-mm-yyyy'})
                field.input_formats = ['%d-%m-%Y']
