from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Avg, Max, Min, Count
from django.db.models.functions import TruncDate, TruncHour
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.db.models import Sum, Avg, Max, Min, Count, Q, StdDev
from django.db.models.functions import TruncDate, TruncHour, ExtractWeekDay
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Measurement
from django.db.models import Avg, StdDev
import json


def home(request):
    total_measurements = Measurement.objects.count()
    context = {'total_measurements': total_measurements}
    return render(request, 'measurements/home.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'measurements/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@csrf_exempt
@require_http_methods(["POST"])
def insert_measurement(request):
    try:
        data = json.loads(request.body)
        
        required_fields = ['meter_id', 'timestamp', 'consumption_kwh' , 'cost']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'success': False, 'error': f'Missing required field: {field}'}, status=400)
        
        timestamp = parse_datetime(data['timestamp'])
        if timestamp is None:
            return JsonResponse({'success': False, 'error': 'Invalid timestamp format. Use ISO format (e.g., 2024-01-15T10:30:00Z)'}, status=400)
        
        measurement, created = Measurement.objects.update_or_create(
            meter_id=data['meter_id'],
            timestamp=timestamp,
            defaults={
                'consumption_kwh': Decimal(str(data['consumption_kwh'])),
                'cost': Decimal(str(data.get('cost'))),
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Measurement created' if created else 'Measurement updated',
            'measurement_id': measurement.id,
            'meter_id': measurement.meter_id,
            'timestamp': measurement.timestamp.isoformat()
        }, status=201 if created else 200)
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def list_measurements(request):
    meter_id = request.GET.get('meter_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    measurements = Measurement.objects.all()
    
    if meter_id:
        measurements = measurements.filter(meter_id=meter_id)
    if start_date:
        start_datetime = parse_datetime(start_date)
        if start_datetime:
            measurements = measurements.filter(timestamp__gte=start_datetime)
    if end_date:
        end_datetime = parse_datetime(end_date)
        if end_datetime:
            measurements = measurements.filter(timestamp__lte=end_datetime)
    
    measurements = measurements[:100]
    meter_ids = Measurement.objects.values_list('meter_id', flat=True).distinct()
    
    context = {
        'measurements': measurements,
        'meter_ids': meter_ids,
        'selected_meter': meter_id,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'measurements/list.html', context)


@login_required
def dashboard(request):
    earliest = Measurement.objects.order_by('timestamp').first()
    latest = Measurement.objects.order_by('timestamp').last()
    
    # Set defaults if no data exists at all
    if earliest:
        start_date = earliest.timestamp
        end_date = latest.timestamp
    else:
        # No data in DB, use a default 30-day range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
    
    if request.GET.get('start_date'):
        start_date = parse_datetime(request.GET.get('start_date')) or start_date
    if request.GET.get('end_date'):
        end_date = parse_datetime(request.GET.get('end_date')) or end_date
    
    measurements = Measurement.objects.filter(timestamp__range=[start_date, end_date])
    
    # In the dashboard function, update the aggregation:
    overall_stats = measurements.aggregate(
        total_consumption=Sum('consumption_kwh'),
        avg_consumption=Avg('consumption_kwh'),
        max_consumption=Max('consumption_kwh'),
        total_cost=Sum('cost'),
        avg_cost=Avg('cost'),
        total_measurements=Count('id'),
        # NEW METRICS
        avg_power=Avg('average_power_kw'),
        max_power=Max('average_power_kw'),
        avg_rate=Avg('cost_per_kwh'),
        min_rate=Min('cost_per_kwh'),
        max_rate=Max('cost_per_kwh'),
        avg_duration=Avg('duration_minutes'),
          
    )

    weekday_stats = measurements.annotate(
    # 'iso_weekday' = 1 (Mon) to 7 (Sun)
    iso_weekday=ExtractWeekDay('timestamp', 'iso_8601') 
    ).aggregate(
        # Weekdays are 1-5 (Mon-Fri)
        avg_weekday=Avg('consumption_kwh', filter=Q(iso_weekday__in=[1, 2, 3, 4, 5])),
        # Weekends are 6-7 (Sat-Sun)
        avg_weekend=Avg('consumption_kwh', filter=Q(iso_weekday__in=[6, 7]))
    )

        
    daily_consumption = measurements.annotate(date=TruncDate('timestamp')).values('date').annotate(
        total=Sum('consumption_kwh'),
        avg=Avg('consumption_kwh'),
        count=Count('id')
    ).order_by('date')
    
    hourly_consumption = measurements.annotate(hour=TruncHour('timestamp')).values('hour').annotate(
        total=Sum('consumption_kwh'),
        avg=Avg('consumption_kwh')
    ).order_by('hour')[:24]
    
    meter_stats = measurements.values('meter_id').annotate(
        total_consumption=Sum('consumption_kwh'),
        avg_consumption=Avg('consumption_kwh'),
        measurement_count=Count('id')
    ).order_by('-total_consumption')
    
    peak_measurements = measurements.order_by('-consumption_kwh')[:10]
    
    daily_labels = [item['date'].strftime('%Y-%m-%d') for item in daily_consumption]
    daily_values = [float(item['total']) if item['total'] else 0 for item in daily_consumption]
    
    hourly_labels = [item['hour'].strftime('%H:%M') for item in hourly_consumption]
    hourly_values = [float(item['avg']) if item['avg'] else 0 for item in hourly_consumption]
    
    context = {
        'overall_stats': overall_stats,
        'weekday_stats': weekday_stats,
        'daily_consumption': daily_consumption,
        'hourly_consumption': hourly_consumption,
        'meter_stats': meter_stats,
        'peak_measurements': peak_measurements,
        'start_date': start_date,
        'end_date': end_date,
        'daily_labels': json.dumps(daily_labels),
        'daily_values': json.dumps(daily_values),
        'hourly_labels': json.dumps(hourly_labels),
        'hourly_values': json.dumps(hourly_values),
    }
    
    return render(request, 'measurements/dashboard.html', context)