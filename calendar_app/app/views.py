from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from django.db.models import Q
from .models import Event, Calendar
from .serializers import EventSerializer
import calendar
from datetime import datetime, timedelta
import pytz

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import iso8601

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        flags = tools.argparser.parse_args([])
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_prev_month(month, year):
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1
    return prev_month, prev_year


def get_next_month(month, year):
    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1

    return next_month, next_year


@api_view(['GET'])
def index(request):
    return render(request, 'index.html')


@api_view(['POST'])
def create_event(request):
    response = {'response': {}}
    data = request.data

    try:
        name = data['name']
        if not name:
            name = 'No title'
    except KeyError as e:
        response['response']['message'] = 'Event name is required'
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    location = data.get('location')

    try:
        start_date = data['start_date']
    except KeyError as e:
        response['response']['message'] = 'Start date is required'
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    try:
        end_date = data['end_date']
    except KeyError as e:
        response['response']['message'] = 'End date is required'
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    start_time = data.get('start_time')
    end_time = data.get('end_time')
    all_day = data.get('all_day')
    description = data.get('description')

    start_date = datetime.strptime(start_date, '%m/%d/%Y').date()
    end_date = datetime.strptime(end_date, '%m/%d/%Y').date()
    if start_time:
        start_time = datetime.strptime(start_time, '%I:%M %p').time()
        start_datetime = datetime.combine(start_date, start_time)
        start_datetime = start_datetime - timedelta(hours=5, minutes=30)
        start_date = start_datetime.date()
        start_time = start_datetime.time()
    if end_time:
        end_time = datetime.strptime(end_time, '%I:%M %p').time()
        end_datetime = datetime.combine(end_date, end_time)
        end_datetime = end_datetime - timedelta(hours=5, minutes=30)
        end_date = end_datetime.date()
        end_time = end_datetime.time()

    kwargs = {
        'name': name,
        'location': location,
        'start_date': start_date,
        'end_date': end_date,
        'start_time': start_time,
        'end_time': end_time,
        'all_day': all_day,
        'description': description
    }

    event = Event.objects.create(**kwargs)
    event.save()

    response['response']['status'] = True
    response['response']['message'] = 'Event successfully created.'

    return Response(response)


@api_view(['POST'])
def update_event(request, pk):
    response = {'response': {}}
    data = request.data

    event_id = pk

    try:
        name = data['name']
        if not name:
            name = 'No title'
    except KeyError as e:
        response['response']['message'] = 'Event name is required'
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    location = data.get('location')

    try:
        start_date = data['start_date']
    except KeyError as e:
        response['response']['message'] = 'Start date is required'
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    try:
        end_date = data['end_date']
    except KeyError as e:
        response['response']['message'] = 'End date is required'
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    start_time = data.get('start_time')
    end_time = data.get('end_time')
    all_day = data.get('all_day')
    description = data.get('description')

    start_date = datetime.strptime(start_date, '%m/%d/%Y').date()
    end_date = datetime.strptime(end_date, '%m/%d/%Y').date()
    if start_time:
        start_time = datetime.strptime(start_time, '%I:%M %p').time()
        start_datetime = datetime.combine(start_date, start_time)
        start_datetime = start_datetime - timedelta(hours=5, minutes=30)
        start_date = start_datetime.date()
        start_time = start_datetime.time()
    if end_time:
        end_time = datetime.strptime(end_time, '%I:%M %p').time()
        end_datetime = datetime.combine(end_date, end_time)
        end_datetime = end_datetime - timedelta(hours=5, minutes=30)
        end_date = end_datetime.date()
        end_time = end_datetime.time()

    kwargs = {
        'name': name,
        'location': location,
        'start_date': start_date,
        'end_date': end_date,
        'start_time': start_time,
        'end_time': end_time,
        'all_day': all_day,
        'description': description
    }

    event = Event.objects.filter(id=event_id)
    event.update(**kwargs)
    event = event.first()
    event.save()

    response['response']['status'] = True
    response['response']['message'] = 'Event successfully updated.'

    return Response(response)


@api_view(['POST'])
def delete_event(request, pk):
    response = {'response': {}}
    data = request.data

    event_id = pk

    kwargs = {'is_active': False}
    event = Event.objects.filter(id=event_id)
    event.update(**kwargs)
    event = event.first()
    event.save()

    response['response']['status'] = True
    response['response']['message'] = 'Event successfully deleted.'

    return Response(response)


@api_view(['GET'])
def fetch_all_events(request):
    response = {'response': {}}

    events = Event.objects.filter(is_active=True)
    event_serializer = EventSerializer(events, many=True)

    response['response']['data'] = event_serializer.data

    return Response(response)


@api_view(['GET'])
def get_month_data(request):
    response = {'response': {}}
    blocks_data = []
    view_start_date = None
    view_end_date = None
    today = datetime.utcnow() + timedelta(hours=5, minutes=30)
    try:
        month = int(request.GET['month'])
    except KeyError as e:
        response['response']['message'] = 'Month is required'
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    try:
        year = int(request.GET['year'])
    except KeyError as e:
        response['response']['message'] = 'Year is required'
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    starting_weekday, no_of_days = calendar.monthrange(year, month)
    no_of_rows = 5
    if (starting_weekday == 4 and no_of_days == 31) or (starting_weekday == 5 and no_of_days > 29):
        no_of_rows = 6
    no_of_blocks = no_of_rows*7
    blocks_prev_month = starting_weekday + 1
    if blocks_prev_month == 7:
        blocks_prev_month = 0
    blocks_curr_month = no_of_days
    blocks_next_month = no_of_blocks - blocks_prev_month - blocks_curr_month
    
    prev_month, prev_year = get_prev_month(month, year)
    next_month, next_year = get_next_month(month, year)

    prev_month_starting_weekday, prev_month_no_of_days = calendar.monthrange(prev_year, prev_month)
    block_id = 0
    current_date_id = None
    
    for i in range(blocks_prev_month):
        temp_dict = dict()
        temp_dict['id'] = block_id
        temp_dict['is_current_month'] = False
        temp_dict['is_current_date'] = False
        actual_date_string = str(prev_month_no_of_days - blocks_prev_month + i + 1) \
                + '-' + str(prev_month) + '-' + str(prev_year)
        actual_date = datetime.strptime(actual_date_string, '%d-%m-%Y')
        temp_dict['actual_date'] = actual_date_string
        if i == 0:
            view_start_date = actual_date
            temp_dict['display_date'] = str(prev_month) + '/' + \
                str(prev_month_no_of_days - blocks_prev_month + i + 1)
        else:
            temp_dict['display_date'] = str(prev_month_no_of_days - blocks_prev_month + i + 1)
        block_id += 1
        blocks_data.append(temp_dict)
    for i in range(blocks_curr_month):
        temp_dict = dict()
        temp_dict['id'] = block_id
        temp_dict['is_current_month'] = True
        temp_dict['is_current_date'] = False
        actual_date_string = str(i + 1) + '-' + str(month) + '-' + str(year)
        actual_date = datetime.strptime(actual_date_string, '%d-%m-%Y')
        if actual_date.date() == today.date():
            current_date_id = i
            temp_dict['is_current_date'] = True
            temp_dict['weather'] = {'type': 'cloudy', 'max': 28, 'min': 20}
        temp_dict['actual_date'] = actual_date_string
        if current_date_id:
            if i == (current_date_id + 1) or i == (current_date_id + 2) or i == (current_date_id + 3):
                if i == (current_date_id + 1):
                    temp_dict['weather'] = {'type': 'sunny', 'max': 28, 'min': 20}
                if i == (current_date_id + 2):
                    temp_dict['weather'] = {'type': 'rainy', 'max': 28, 'min': 20}
                if i == (current_date_id + 3):
                    temp_dict['weather'] = {'type': 'cloudy', 'max': 28, 'min': 20}
        if i == 0:
            curr_month = actual_date.strftime('%B %Y')
            if not view_start_date:
                view_start_date = actual_date
            temp_dict['display_date'] = str(month) + '/' + str(i+1)
        else:
            temp_dict['display_date'] = str(i+1)
            if i == blocks_curr_month - 1:
                if blocks_next_month == 0:
                    view_end_date = actual_date
        block_id += 1
        blocks_data.append(temp_dict)
    for i in range(blocks_next_month):
        temp_dict = dict()
        temp_dict['id'] = block_id
        temp_dict['is_current_month'] = False
        temp_dict['is_current_date'] = False
        actual_date_string = str(i + 1) + '-' + str(next_month) + '-' + str(next_year)
        actual_date = datetime.strptime(actual_date_string, '%d-%m-%Y')
        temp_dict['actual_date'] = actual_date_string
        if i == 0:
            temp_dict['display_date'] = str(next_month) + '/' + str(i+1)
        else:
            temp_dict['display_date'] = str(i+1)
        if i == blocks_next_month - 1:
            if not view_end_date:
                view_end_date = actual_date
        block_id += 1
        blocks_data.append(temp_dict)

    view_start_date = view_start_date.replace(tzinfo=pytz.utc)
    view_end_date = view_end_date.replace(tzinfo=pytz.utc)
    
    all_events_curr_month = Event.objects.filter(Q(start_date__lte=view_start_date.date(),
        end_date__gte=view_start_date.date()) | Q(start_date__gte=view_start_date.date(),
        end_date__lte=view_end_date.date()) | Q(start_date__lte=view_end_date.date(),
        end_date__gte=view_end_date.date()) | Q(start_date__lte=view_start_date.date(),
        end_date__gte=view_end_date.date()), is_active=True).order_by('start_date')

    for block in blocks_data:
        block['events'] = []
        for event in all_events_curr_month:
            start_date = event.start_date
            end_date = event.end_date
            if not event.all_day:
                start_time = event.start_time
                end_time = event.end_time
                start_datetime = datetime.combine(start_date, start_time)
                start_datetime = start_datetime + timedelta(hours=5, minutes=30)
                start_date = start_datetime.date()
                start_time = start_datetime.time()
                end_datetime = datetime.combine(end_date, end_time)
                end_datetime = end_datetime + timedelta(hours=5, minutes=30)
                end_date = end_datetime.date()
                end_time = end_datetime.time()
            when_start_time = ''
            when_end_time = ''
            when_start_day = start_date.strftime('%A, %d %b %y')
            when_end_day = end_date.strftime('%A, %d %b %y')
            if start_date < view_start_date.date():
                start_date = view_start_date.date()
            if end_date > view_end_date.date():
                end_date = view_end_date.date()

            actual_date_string = block['actual_date']
            actual_date = datetime.strptime(actual_date_string, '%d-%m-%Y')

            if actual_date.date() == start_date:
                start_date_string = start_date.strftime('%m/%d/%Y')
                end_date_string = end_date.strftime('%m/%d/%Y')
                if event.all_day:
                    all_day = True
                    start_time_string = None
                    end_time_string = None
                else:
                    all_day = False
                    # start_time = event.start_time
                    # end_time = event.end_time
                    start_time_string = start_time.strftime('%I:%M %p')
                    end_time_string = end_time.strftime('%I:%M %p')
                temp_object = dict()
                diff_days = (end_date - start_date).days
                temp_object['id'] = event.id
                temp_object['name'] = event.name
                temp_object['length'] = diff_days + 1
                temp_object['location'] = event.location
                temp_object['description'] = event.description
                temp_object['start_date'] = start_date_string
                temp_object['end_date'] = end_date_string
                temp_object['start_time'] = start_time_string
                temp_object['end_time'] = end_time_string
                temp_object['all_day'] = all_day
                # start_time = event.start_time
                # end_time = event.end_time
                if start_date == end_date:
                    if event.all_day:
                        when = when_start_day
                        temp_object['start_time_short'] = ''
                    else:
                        start_time_hour = start_time.strftime('%H')
                        start_time_minute = start_time.strftime('%M')
                        meridiem = 'a'
                        if int(start_time_hour) > 11:
                            meridiem = 'p'
                            if int(start_time_hour) > 12:
                                start_time_hour = str(int(start_time_hour) - 12)
                        else:
                            if start_time_hour == '00':
                                start_time_hour = '12'
                            else:
                            	start_time_hour = str(int(start_time_hour))
                        
                        when_start_time = start_time_hour + ':' + start_time_minute + '' + meridiem + 'm, '
                        temp_object['start_time_short'] = start_time_hour + '' + meridiem
                        when = when_start_time + '' + when_start_day
                else:
                    if event.all_day:
                        when = when_start_day + ' - ' + when_end_day
                        temp_object['start_time_short'] = ''
                    else:
                        start_time_hour = start_time.strftime('%H')
                        start_time_minute = start_time.strftime('%M')
                        meridiem = 'a'
                        if int(start_time_hour) > 11:
                            meridiem = 'p'
                            if int(start_time_hour) > 12:
                                start_time_hour = str(int(start_time_hour) - 12)
                        else:
                            if start_time_hour == '00':
                                start_time_hour = '12'
                            else:
                            	start_time_hour = str(int(start_time_hour))
                        
                        when_start_time = start_time_hour + ':' + start_time_minute + '' + meridiem + 'm, '
                        temp_object['start_time_short'] = start_time_hour + '' + meridiem
                        end_time_hour = end_time.strftime('%H')
                        end_time_minute = end_time.strftime('%M')
                        meridiem = 'am'
                        if int(end_time_hour) > 11:
                            meridiem = 'pm'
                            if int(end_time_hour) > 12:
                                end_time_hour = str(int(end_time_hour) - 12)
                        else:
                            if end_time_hour == '00':
                                end_time_hour = '12'
                            else:
                            	end_time_hour = str(int(end_time_hour))
                        
                        when_end_time = end_time_hour + ':' + end_time_minute + '' + meridiem + ', '
                        when = when_start_time + '' + when_start_day + ' - ' + when_end_time + '' + when_end_day

                temp_object['when'] = when
                block['events'].append(temp_object)

    response['response']['data'] = blocks_data
    response['response']['curr_month'] = curr_month
    return Response(response)


def update_google_event(event, gid, service):
    g_event = service.events().get(calendarId='primary', eventId=gid).execute()
    summary = '' if event.name == 'No title' else event.name
    location = event.location
    description = event.description
    start_date = event.start_date
    start_date_string = start_date.strftime('%Y-%m-%d')
    end_date = event.end_date
    end_date_string = end_date.strftime('%Y-%m-%d')
    all_day = event.all_day
    if all_day:
        start = {'date': start_date_string}
        end = {'date': end_date_string}
    else:
        start_time = event.start_time
        end_time = event.end_time
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
        start_datetime = start_datetime.isoformat() + 'Z'
        end_datetime = end_datetime.isoformat() + 'Z'
        start = {'dateTime': start_datetime}
        end = {'dateTime': end_datetime}
    g_event['summary'] = summary
    g_event['location'] = location
    g_event['description'] = description
    g_event['start'] = start
    g_event['end'] = end
    updated_event = service.events().update(calendarId='primary', eventId=gid, body=g_event).execute()


def create_google_event(event, service):
    summary = '' if event.name == 'No title' else event.name
    location = event.location
    description = event.description
    start_date = event.start_date
    start_date_string = start_date.strftime('%Y-%m-%d')
    end_date = event.end_date
    end_date_string = end_date.strftime('%Y-%m-%d')
    all_day = event.all_day
    if all_day:
        start = {'date': start_date_string}
        end = {'date': end_date_string}
    else:
        start_time = event.start_time
        end_time = event.end_time
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
        start_datetime = start_datetime.isoformat() + 'Z'
        end_datetime = end_datetime.isoformat() + 'Z'
        start = {'dateTime': start_datetime}
        end = {'dateTime': end_datetime}
    g_event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': start,
        'end': end
    }
    g_event = service.events().insert(calendarId='primary', body=g_event).execute()
    return g_event['id']


def delete_google_account(gid, service):
    service.events().delete(calendarId='primary', eventId=gid).execute()


@api_view(['GET'])
def sync(request):
    response = {'response': {}}
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    try:
        calendar = Calendar.objects.latest('id')
        last_synced_at = calendar.last_synced_at
        token = calendar.token
        # last_synced_at_iso = last_synced_at.isoformat()
        googleEventsResult = service.events().list(calendarId='primary', syncToken=token).execute()
        events = Event.objects.filter(updated_at__gt=last_synced_at)
    except:
        googleEventsResult = service.events().list(calendarId='primary').execute()
        events = Event.objects.filter(is_active=True)
    next_token = googleEventsResult['nextSyncToken']
    g_events = googleEventsResult.get('items', [])
    for event in events:
        gid = event.gid
        if gid != '':
            if event.is_active:
                update_google_event(event, gid, service)
            else:
                delete_google_account(gid, service)
        else:
            if event.is_active:
                gid = create_google_event(event, service)
                event.gid = gid
                event.save()

    for g_event in g_events:
        event_id = g_event['id']
        status = g_event['status']
        event = Event.objects.filter(gid=event_id)
        if event:
            if status == 'cancelled':
                event = event.first()
                event.is_active = False
                event.save()
            else:
                summary = g_event['summary'] if 'summary' in g_event else 'No title'
                location = g_event['location'] if 'location' in g_event else ''
                description = g_event['description'] if 'description' in g_event else ''
                start = g_event['start']
                end = g_event['end']
                if 'date' in start:
                    all_day = True
                    start_date = start['date']
                    end_date = end['date']
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                    end_date = datetime.strptime(end_date, '%Y-%m-%d')
                    end_date = end_date - timedelta(days=1)
                    start_time = None
                    end_time = None
                else:
                    all_day = False
                    start_datetime = start['dateTime']
                    end_datetime = end['dateTime']
                    start_datetime = iso8601.parse_date(start_datetime)
                    end_datetime = iso8601.parse_date(end_datetime)
                    start_datetime = start_datetime - timedelta(hours=5, minutes=30)
                    end_datetime = end_datetime - timedelta(hours=5, minutes=30)
                    start_date = start_datetime.date()
                    end_date = end_datetime.date()
                    start_time = start_datetime.time()
                    end_time = end_datetime.time()
                kwargs = {
                    'name': summary,
                    'location': location,
                    'start_date': start_date,
                    'end_date': end_date,
                    'start_time': start_time,
                    'end_time': end_time,
                    'all_day': all_day,
                    'description': description
                }
                event.update(**kwargs)
                event = event.first()
                event.save()
        else:
            if status != 'cancelled':
                summary = g_event['summary'] if 'summary' in g_event else 'No title'
                location = g_event['location'] if 'location' in g_event else ''
                description = g_event['description'] if 'description' in g_event else ''
                start = g_event['start']
                end = g_event['end']
                gid = g_event['id']
                if 'date' in start:
                    all_day = True
                    start_date = start['date']
                    end_date = end['date']
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                    end_date = datetime.strptime(end_date, '%Y-%m-%d')
                    end_date = end_date - timedelta(days=1)
                    start_time = None
                    end_time = None
                else:
                    all_day = False
                    start_datetime = start['dateTime']
                    end_datetime = end['dateTime']
                    start_datetime = iso8601.parse_date(start_datetime)
                    end_datetime = iso8601.parse_date(end_datetime)
                    start_datetime = start_datetime - timedelta(hours=5, minutes=30)
                    end_datetime = end_datetime - timedelta(hours=5, minutes=30)
                    start_date = start_datetime.date()
                    end_date = end_datetime.date()
                    start_time = start_datetime.time()
                    end_time = end_datetime.time()
                kwargs = {
                    'name': summary,
                    'location': location,
                    'start_date': start_date,
                    'end_date': end_date,
                    'start_time': start_time,
                    'end_time': end_time,
                    'all_day': all_day,
                    'description': description,
                    'gid': gid
                }
                event = Event.objects.create(**kwargs)
                event.save()
    now = datetime.utcnow()
    calendar = Calendar(last_synced_at=now, token=next_token)
    calendar.save()

    response['response']['status'] = True
    response['response']['message'] = 'Calendars successfully synced'
    return Response(response)
