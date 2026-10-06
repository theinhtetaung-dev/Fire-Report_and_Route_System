from django.db.models import Q
from django.utils import timezone
from .models import ActingAssignment, Deployment, Post
from DataAccess.models import FireReport


def managed_station_ids(user):
    if not user.is_authenticated: return []
    ids = list(ActingAssignment.objects.filter(employee=user, leave__status='Approved', starts_at__lte=timezone.now(), ends_at__gt=timezone.now()).values_list('station_id', flat=True))
    if user.has_role('Station Admin') and user.station_id: ids.append(user.station_id)
    return list(set(ids))


def incidents_for(user):
    if user.is_admin: return FireReport.objects.all()
    ids = managed_station_ids(user)
    if user.station_id: ids.append(user.station_id)
    return FireReport.objects.filter(Q(user_id=user.pk) | Q(deployments__station_id__in=ids)).distinct()


def posts_for(user):
    query = Q(audience='Public')
    if user.is_authenticated:
        if user.is_admin: return Post.objects.all()
        if user.is_firefighter or user.is_station_admin:
            query |= Q(audience='Staff') | Q(audience='Station', station_id__in=[user.station_id] + managed_station_ids(user))
    return Post.objects.filter(query, published=True)
