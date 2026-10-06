from DataAccess.models import FireReport


def console_context(request):
    from .models import User
    query=request.GET.copy();query.pop('page',None);query.pop('export',None)
    groups=query.copy();groups.pop('period',None)
    return {'filter_query':query.urlencode(),'group_query':groups.urlencode(),'statuses':FireReport.STATUS_CHOICES,'levels':FireReport.FIRE_SCALE_CHOICES,
        'replacements':User.objects.filter(role__role_name='Firefighter',status='Active').order_by('full_name') if request.user.is_authenticated and getattr(request.user,'is_admin',False) else []}
