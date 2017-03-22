var date = new Date();
var month = date.getMonth() + 1;
var year = date.getFullYear();
var weeks = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
var months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

function getRow(eventHTML, eventsData, before, after, eventForNextMonth, isCurrentDate, id) {
    if(isCurrentDate && eventsData.length === 0) {
        $('.sidebar-event').html('No events for today');
    }
    var todayEvents = '';
    eventsData.map(function(event) {
        if(isCurrentDate) {
            document.getElementsByClassName('week-calendar')[id % 7].className = 'week week-calendar active';
            todayEvents = todayEvents + '<div><span>' + event.name + '</span><span>' + event.start_time_short + '</span></div>';
        }
        var row = '';
        for(var k = 0; k < before; k++) {
            row = row + '<td>&nbsp;</td>';
        }
        row = row + '<td class="has-event" colspan="' + Math.min(event.length, after)
            + '" data-id="' + event.id
            + '" data-name="' + event.name
            + '" data-location="' + event.location
            + '" data-description="' + event.description
            + '" data-start-time="' + event.start_time
            + '" data-end-time="' + event.end_time
            + '" data-start-date="' + event.start_date
            + '" data-end-date="' + event.end_date
            + '" data-all-day="' + event.all_day
            + '" data-when="' + event.when
            + '">' + event.name + '<span>' + event.start_time_short + '</span></td>';
        if(event.length < after) {
            for(var k = 0; k < after - event.length; k++) {
                row = row + '<td>&nbsp;</td>';
            } 
        }
        if(event.length > after) {
            var leftEvent = $.extend(true, {}, event);
            leftEvent.length = event.length - after;
            eventForNextMonth.push(leftEvent);
        }
        eventHTML = eventHTML + '<tr>' + row + '</tr>';
    });
    if(isCurrentDate && eventsData.length > 0) {
        $('.sidebar-event').html(todayEvents); 
    }
    return {events: eventHTML, eventForNextMonth: eventForNextMonth};
}

function getData(m, y) {
    $.ajax({
        url: 'month-data',
        data: {'month': m, 'year': y} ,
        type: 'GET',
        success: function(result) {
            console.log(result);
            var data = result.response.data;
            $('.header-text').html(result.response.curr_month);
            $('.sidebar-header').first().html(result.response.curr_month);
            var parent = $('#days');
            var parentSide = $('#sidebar-days');
            parent.html('');
            parentSide.html('');
            var eventForNextMonth = [];
            for(var i = 0; i < data.length/7; i++) {
                parent.append("<div class='day-row day-row-calendar' style='top:" + (i*20) + "%'></div>");
                parentSide.append("<div class='day-row day-row-sidebar'></div>");
                var elem = '';
                var events = '<tr></tr>';
                var elemSide = '';

                var newEventForNextMonth = [];
                // Append previous month's events
                computedEvents = getRow(events, eventForNextMonth, 0, 7, newEventForNextMonth, false);
                events = computedEvents.events;
                newEventForNextMonth = computedEvents.eventForNextMonth;

                // empty eventForNextMonth after appending
                eventForNextMonth = newEventForNextMonth.slice(0, newEventForNextMonth.length);

                // create each day's data
                for(var j = 0; j < 7; j++) {
                    var item = data[j + (7*i)];

                    computedEvents = getRow(events, item.events, j, 7 - j, eventForNextMonth, item.is_current_date, item.id);
                    events = computedEvents.events;
                    eventForNextMonth = computedEvents.eventForNextMonth;

                    var weather = '';
                    if(item.weather) {
                        weather = weather + '<div class="weather"><i class="fa ' + (item.weather.type === 'cloudy' ? 'fa-cloud' : (item.weather.type === 'sunny' ? 'fa-sun-o' : 'fa-bolt')) + '"></i>';
                        weather = weather + '<span>' + item.weather.max + '&deg;</span>/';
                        weather = weather + '<span>' + item.weather.min + '&deg;</span></div>';
                        if(item.is_current_date) {
                            $('.sidebar-weather').html(weather + '<div>' + item.weather.type + '</div>');
                        }
                    }

                    var className = 'day' + (item.is_current_month ? '' : ' day-prev') + (item.is_current_date ? ' day-current' : '');
                    elem = elem + '<td class="' + className + '" data-date="' + item.actual_date + '">' + item.display_date + weather + '</td>';
                    var date = item.display_date.split('/');
                    elemSide = elemSide + '<div class="' + className + '">' + (date[1] ? date[1] : date[0])  + '</div>';
                }
                // append week's data
                document.getElementsByClassName('day-row-calendar')[i].innerHTML = '<table><tbody><tr>'
                    + elem + '</tr></tbody></table><table class="events-table"><tbody>'
                    + events + '</tbody></table>';
                document.getElementsByClassName('day-row-sidebar')[i].innerHTML = '<div>'
                    + elemSide + '</div>';
            }
        },
        error: function() {
        }
    });
}

function resetForm() {
    $('#title').val('');
    $('#location').val('');
    $('#datepicker-start').val('');
    $('#datepicker-end').val('');
    $('#timepicker-start').val('');
    $('#timepicker-end').val('');
    $('#all-day').prop('checked', true);
    $('#description').val('');
    $('#timepicker-start').attr('disabled', true);
    $('#timepicker-end').attr('disabled', true);
    $('#all-day').next('.fa').addClass('fa-check-square-o');
    $('#all-day').next('.fa').removeClass('fa-square-o');
    $('.date-label').hide();
}

function openModal(e) {
    $('.container').css('pointerEvents', 'none');
    var prev = $(e.target).prevAll().length;
    if(prev > 3) {
        var right = ((7 - prev) * 12) + 4;
        $('.modal').removeClass('modal-left');
        $('.modal').addClass('modal-right');
        $('.modal').css('left', '');
        $('.modal').css('right', right + '%');
    } else {
        var left = ((prev + 1) * 12) + 1;
        $('.modal').addClass('modal-left');
        $('.modal').removeClass('modal-right');
        $('.modal').css('right', '');
        $('.modal').css('left', left + '%');
    }
    if($(e.target).hasClass('has-event')) {
        $('#save').attr('data-type', 'update');
        $('.edit-modal').show();
        var data = e.target.dataset;
        $('[data-id="' + data.id + '"]').addClass('active');
        $('.event-name').html(data.name);
        $('.where').html(data.location);
        $('.when').html(data.when);
        $('.description').html(data.description);
        if(data.when !== '') {
            $('.when').prev().show();
        }
        if(data.location !== '') {
            $('.where').prev().show();
        }
        if(data.description !== '') {
            $('.description').prev().show();
        } 
    } else {
        $('#modal').show();
        var date = e.target.dataset.date.split('-');
        $('#datepicker-start').val(date[1] + '/' + date[0] + '/' + date[2]);
        $('#datepicker-end').datepicker('option', 'minDate', new Date(date[1] + '/' + date[0] + '/' + date[2])).val(date[1] + '/' + date[0] + '/' + date[2]);
        $('.selected-date').html(weeks[prev] + ', ' + date[0] + ' ' + months[date[1] - 1] + ' ' + year);
    }
}

function validate(startDate, endDate, startTime, endTime, allDay) {
    if(startDate === '' || endDate === '') {
        alert('Please enter start and end date');
        return false;
    }
    if(!allDay && (startTime === '' || endTime === '')) {
        alert('Either check ALL DAY or enter start and end time');
        return false;
    }
    return true;
}

function modalClose() {
    $('.container').css('pointerEvents', 'initial');
    $('.active').removeClass('active');
    resetForm();
    $('#save').attr('data-type', 'create');
    $('.modal').hide();
}

function setTime() {
    var now = new Date();
    var hour = now.getHours()
    var meridian = '<span class="meridian">' + (hour > 12 ? 'pm' : 'am') + '</span>';
    hour = hour > 12 ? hour - 12 : hour;
    hour = hour === 0 ? 12 : hour;
    var min = now.getMinutes();
    $('.sidebar-time').html(hour + ':' + (min < 10 ? '0' + min : min) + meridian);
}

function resize() {
    $('.calendar').height((window.innerHeight - 78) + 'px');   
}

var minDate = '';
$(document).ready(function() {
    setTime();
    setInterval(setTime, 60000);
  getData(month, year);
  $("#datepicker-start").datepicker({
    onSelect: function(dateText) {
        minDate = new Date(dateText);
        $("#datepicker-end").datepicker('option', 'minDate', minDate);
    }
  });
  $("#datepicker-end").datepicker({
    minDate: minDate === '' ? new Date() : minDate
  });
  $('#timepicker-start').timepicker({
    interval: 60,
    change: function() {
        var startTime = $("#timepicker-start").val();
        var endTime = $("#timepicker-end").val();
        var startMeridian = startTime.split(' ')[1];
        var endMeridian = endTime.split(' ')[1];
        if(startTime > endTime || (startMeridian == 'PM' && endMeridian == 'AM')){
            $("#timepicker-end").val('');
        }
        if($("#datepicker-start").val() === $("#datepicker-end").val()) {
            $("#timepicker-end").timepicker('option', 'minTime', $('#timepicker-start').val());
        } else {
            $("#timepicker-end").timepicker('option', 'minTime', '0');    
        }
    }
  });
  $('#timepicker-end').timepicker({
    interval: 60
  });
  $('.cancel').on('click', modalClose);
  $('#save').on('click', function(e) {
    var title = $('#title').val();
    var location = $('#location').val();
    var startDate = $('#datepicker-start').val();
    var endDate = $('#datepicker-end').val();
    var startTime = $('#timepicker-start').val();
    var endTime = $('#timepicker-end').val();
    var allDay = $('#all-day').is(':checked');
    var description = $('#description').val();
    var data = {
        name: title,
        location: location,
        start_date: startDate,
        end_date: endDate,
        all_day: allDay,
        description: description
    };
    if(!allDay) {   
        data.start_time = startTime;
        data.end_time = endTime;
    }
    if(validate(startDate, endDate, startTime, endTime, allDay)) {
        $(this).attr('disabled', true);
        var self = this;
        $.ajax({
            url: e.target.dataset.type === 'create' ? 'events/create/' : 'events/' + $('.has-event.active').data('id') + '/update/',
            type: 'POST',
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json',
            success: function() {
                $(self).attr('disabled', false);
                modalClose();
                getData(month, year);
            },
            error: function() {}
        });
    }
  });

  $('#edit').on('click', function(e) {
        $('.edit-modal').hide();
        $('#modal').show();
        var data = $('.has-event.active').data();
        $('#title').val(data.name);
        $('#location').val(data.location);
        $('#datepicker-start').val(data.startDate);
        $('#datepicker-end').val(data.endDate);
        $('#all-day').prop('checked', data.allDay);
        $('#description').val(data.description);
        if(!data.allDay) {
            $('#timepicker-start').attr('disabled', false);
            $('#timepicker-end').attr('disabled', false);
            $('#timepicker-start').val(data.startTime);
            $('#timepicker-end').val(data.endTime);
            $('#all-day').next('.fa').addClass('fa-square-o');
            $('#all-day').next('.fa').removeClass('fa-check-square-o');
        } else {
            $('#timepicker-start').attr('disabled', true);
            $('#timepicker-end').attr('disabled', true);
            $('#all-day').next('.fa').addClass('fa-check-square-o');
            $('#all-day').next('.fa').removeClass('fa-square-o');
        }
  });

  $('#delete').on('click', function(e) {
    $(this).attr('disabled', true);
    var self = this;
    $.ajax({
        url: 'events/' + $('.has-event.active').data('id') + '/delete/',
        type: 'POST',
        success: function() {
            $(self).attr('disabled', false);
            modalClose();
            getData(month, year);
        },
        error: function() {}
    });
  });

  $('.fa-chevron-up').on('click', function() {
    month = month === 1 ? 12 : --month;
    year = month === 12 ? --year : year;
    $('.week-calendar.active').removeClass('active');
    getData(month, year);
  });

  $('.fa-chevron-down').on('click', function() {
    month = month === 12 ? 1 : ++month;
    year = month === 1 ? ++year : year;
    $('.week-calendar.active').removeClass('active');
    getData(month, year);
  });

  $('.fa-refresh').on('click', function() {
    $(this).addClass('disabled');
    var self = this;
    $.ajax({
        url: 'sync',
        type: 'GET',
        success: function() {
            $(self).removeClass('disabled');
            getData(month, year);
        },
        error: function() {}
    })
  });

  $('#all-day').on('change', function(e) {
    if(e.target.checked) {
        $(this).next('.fa').addClass('fa-check-square-o');
        $(this).next('.fa').removeClass('fa-square-o');
        $('#timepicker-start').attr('disabled', true);
        $('#timepicker-end').attr('disabled', true);
    } else {
        $(this).next('.fa').addClass('fa-square-o');
        $(this).next('.fa').removeClass('fa-check-square-o');
        $('#timepicker-start').attr('disabled', false);
        $('#timepicker-end').attr('disabled', false);
    }
  });
  resize();
  $(window).resize(resize);

  document.getElementById('days').addEventListener('click', openModal, true);
});
