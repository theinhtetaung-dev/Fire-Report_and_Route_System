from datetime import timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from DataAccess.models import FireStation
from .models import Deployment


def admin_chart_data(incidents):
    today = timezone.localdate()
    first_day = today - timedelta(days=13)
    daily = {
        row['day']: row['total']
        for row in incidents.filter(reported_at__date__range=(first_day, today))
        .annotate(day=TruncDate('reported_at')).values('day').annotate(total=Count('pk'))
    }
    days = [first_day + timedelta(days=offset) for offset in range(14)]
    workload = dict(
        Deployment.objects.filter(incident__in=incidents)
        .exclude(state__in=['Returned', 'Cancelled'])
        .values('station_id').annotate(total=Count('pk')).values_list('station_id', 'total')
    )
    stations = list(FireStation.objects.annotate(
        available=Count('vehicle', filter=Q(vehicle__status='Available')),
        committed=Count('vehicle', filter=Q(vehicle__status__in=['Reserved', 'Deployed'])),
        unavailable=Count('vehicle', filter=Q(vehicle__status__in=['Maintenance', 'Inactive'])),
    ).order_by('name', 'pk'))
    return {
        'dates': [day.isoformat() for day in days],
        'reported': [daily.get(day, 0) for day in days],
        'stations': [
            {'name': station.name, 'open': workload.get(station.pk, 0),
             'available': station.available, 'committed': station.committed,
             'unavailable': station.unavailable}
            for station in stations
        ],
    }
