from django import forms


class EventForm(forms.Form):
    name = forms.CharField(max_length=100)
    location = forms.CharField(max_length=255, required=False)
    start_date = forms.DateTimeField(input_formats=['%Y-%m-%d'], required=False)
    start_time = forms.TimeField(required=False)
    end_date = forms.DateTimeField(input_formats=['%Y-%m-%d'], required=False)
    end_time = forms.TimeField(required=False)
    all_day = forms.BooleanField(required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

    @classmethod
    def populate_form(self, event):
        form = PlaceGodForm(initial={'name': event.name, 'location': event.location,
        							 'start_date': 
                                     })
        return form