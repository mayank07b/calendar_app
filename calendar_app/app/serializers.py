from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    start_datetime = serializers.SerializerMethodField()
    end_datetime = serializers.SerializerMethodField()

    @staticmethod
    def get_start_datetime(event):
        return '1'

    @staticmethod
    def get_end_datetime(event):
        return '1'

    class Meta:
        model = Event
        fields = ('id', 'name', 'location', 'start_datetime', 'end_datetime', 'all_day',
                  'description')
