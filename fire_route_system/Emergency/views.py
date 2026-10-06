import csv
import json
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied,ValidationError
from django.core.paginator import Paginator
from django.db import transaction,IntegrityError
from django.db.models import Q,Count,Sum
from django.http import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from DataAccess.models import User,Role,FireReport,FireStation
from .models import *
from .forms import FORM_TYPES,RegisterForm,IncidentForm,ConfirmForm
from .permissions import managed_station_ids,incidents_for,posts_for
from . import services

TITLES={'stations':'မီးသတ်စခန်းများ','staff':'ဝန်ထမ်းနှင့် အကောင့်များ','vehicle-types':'ယာဉ်အမျိုးအစားများ','vehicles':'မီးသတ်ယာဉ်များ','plans':'Level အလိုက် အစီအစဉ်များ','requirements':'စခန်း/ယာဉ် လိုအပ်အရေအတွက်','duties':'တာဝန်ချိန်နှင့် တာဝန်များ','leaves':'ခွင့်စာများ','posts':'သတင်းနှင့် အသိပညာပေး Post များ'}


def register(request):
    form=RegisterForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        try:user=form.save()
        except IntegrityError:form.add_error(None,'အကောင့်ရှိပြီးဖြစ်သည်။')
        else:
            login(request,user,backend='DataAccess.backends.RoleAuthBackend');return redirect('emergency:dashboard')
    return render(request,'emergency/form.html',{'form':form,'title':'Citizen အကောင့်ဖွင့်ရန်'})


@login_required
def dashboard(request):
    user=request.user
    incidents=incidents_for(user)
    counts=list(incidents.values('status').annotate(total=Count('pk')))
    for row in counts:row['status_display']=dict(FireReport.STATUS_CHOICES).get(row['status'],row['status'])
    return render(request,'emergency/dashboard.html',{'incidents':incidents.order_by('-reported_at')[:10],
        'counts':counts,'active_count':incidents.exclude(status__in=['Resolved','False Alarm']).count(),
        'duties':Duty.objects.filter(employee=user,ends_at__gt=timezone.now()).order_by('starts_at')[:10],
        'notices':Notice.objects.filter(recipient=user).order_by('-pk')[:20],
        'managed_stations':managed_station_ids(user),'titles':TITLES})


def scope(request,kind):
    user=request.user;model,_=FORM_TYPES[kind];query=model.objects.all();ids=managed_station_ids(user)
    if kind=='posts':
        if user.is_admin:return query
        if ids:return query.filter(author=user)
        raise PermissionDenied
    if user.is_admin:return query
    if kind=='staff':return query.filter(station_id__in=ids) if ids else query.filter(pk=user.pk)
    if kind=='vehicles':return query.filter(station_id__in=ids or [user.station_id])
    if kind=='duties' or kind=='leaves':return query.filter(employee__station_id__in=ids) if ids else query.filter(employee=user)
    if kind=='stations':return query.filter(pk__in=ids or [user.station_id])
    raise PermissionDenied


@login_required
def listing(request,kind):
    if kind not in FORM_TYPES:raise PermissionDenied
    query=scope(request,kind)
    search=request.GET.get('q','').strip()
    if search:
        fields={'staff':['full_name','username','phone_number','rank'],'stations':['name','address'],'vehicles':['registration','kind__name'],'vehicle-types':['name'],'plans':['home_station__name'],'requirements':['station__name','kind__name'],'duties':['employee__full_name','task'],'leaves':['employee__full_name','reason'],'posts':['title','body']}[kind]
        condition=Q()
        for field in fields:condition|=Q(**{field+'__icontains':search})
        query=query.filter(condition)
    if request.GET.get('status') and kind in ['staff','stations','vehicles','leaves']:query=query.filter(status=request.GET['status'])
    page=Paginator(query.order_by('-pk'),20).get_page(request.GET.get('page'))
    can_create=request.user.is_admin or kind=='leaves' or (bool(managed_station_ids(request.user)) and kind in ['staff','duties','posts'])
    return render(request,'emergency/list.html',{'title':TITLES[kind],'kind':kind,'page_obj':page,'can_create':can_create,'query':search})


@login_required
def edit(request,kind,pk=None):
    if kind not in FORM_TYPES:raise PermissionDenied
    user=request.user;ids=managed_station_ids(user);model,form_type=FORM_TYPES[kind]
    obj=get_object_or_404(scope(request,kind),pk=pk) if pk else model()
    if kind=='posts' and pk and not user.is_admin and obj.author_id!=user.pk:raise PermissionDenied
    if not user.is_admin:
        if kind=='leaves':
            if pk:raise PermissionDenied
            obj.employee=user
        elif not ids or kind not in ['staff','duties','vehicles','posts']:raise PermissionDenied
        elif kind=='staff' and pk and obj.role.role_name!='Firefighter':raise PermissionDenied
        elif kind=='vehicles' and not pk:raise PermissionDenied
    if kind=='leaves':obj.employee=user
    if kind=='posts' and not pk:obj.author=user;obj.station_id=user.station_id or (ids[0] if ids else None)
    form=form_type(request.POST or None,instance=obj)
    if kind=='posts' and not user.is_admin:
        form.fields['station'].queryset=FireStation.objects.filter(pk__in=ids)
    if kind=='staff' and not user.is_admin:
        form.fields['role'].queryset=Role.objects.filter(role_name='Firefighter')
        form.fields['station'].queryset=FireStation.objects.filter(pk__in=ids)
    if kind=='duties':
        form.fields['employee'].queryset=User.objects.filter(status='Active',role__role_name__in=['Station Admin','Firefighter'])
        if not user.is_admin:form.fields['employee'].queryset=form.fields['employee'].queryset.filter(station_id__in=ids)
    if kind=='vehicles':
        form.fields['status'].choices=[(s,s) for s in ['Available','Maintenance','Inactive']]
        if not user.is_admin:
            for field in ['station','kind','registration']:form.fields[field].disabled=True
    if kind=='leaves' and not (user.is_firefighter or user.has_role('Station Admin')):raise PermissionDenied
    if request.method=='POST' and form.is_valid():
        try:
            with transaction.atomic():
                if kind=='duties':User.objects.select_for_update().get(pk=form.cleaned_data['employee'].pk)
                if kind=='vehicles' and pk:
                    locked=Vehicle.objects.select_for_update().get(pk=pk)
                    if locked.status in ['Reserved','Deployed']:raise ValidationError('စေလွှတ်ထားသောယာဉ်ကို ပြင်မရပါ။')
                saved=form.save(commit=False)
                if kind=='staff' and pk:
                    locked_user=User.objects.select_for_update().get(pk=pk)
                    if StaffParticipation.objects.filter(employee=locked_user,active=True).exists() and (saved.station_id!=locked_user.station_id or saved.status!='Active' or saved.role_id!=locked_user.role_id):raise ValidationError('ဖြစ်စဉ်တွင်ပါဝင်နေသူ၏ စခန်း/role/အကောင့်အခြေအနေကို မပြောင်းနိုင်ပါ။')
                if kind=='posts' and saved.audience=='Station' and not saved.station_id:raise ValidationError('စခန်းသီးသန့် Post အတွက် စခန်းလိုသည်။')
                saved.full_clean();saved.save();services.audit(user,'save',saved)
            messages.success(request,'သိမ်းဆည်းပြီးပါပြီ။');return redirect('emergency:list',kind=kind)
        except (ValidationError,IntegrityError) as error:form.add_error(None,error if isinstance(error,ValidationError) else 'ဒေတာထပ်နေသည်။')
    return render(request,'emergency/form.html',{'form':form,'title':TITLES[kind]})


def posts(request):
    query=posts_for(request.user)
    if request.GET.get('q'):query=query.filter(Q(title__icontains=request.GET['q'])|Q(body__icontains=request.GET['q']))
    return render(request,'emergency/posts.html',{'page_obj':Paginator(query.order_by('-pk'),20).get_page(request.GET.get('page'))})


@login_required
def report(request):
    form=IncidentForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        incident=form.save(commit=False);incident.user_id=request.user.pk;incident.reporter_phone=request.user.phone_number;incident.fire_scale=0;incident.status='Pending';incident.save()
        for admin in User.objects.filter(role__role_name__in=['Administrator','Admin'],status='Active'):
            Notice.objects.create(recipient=admin,incident=incident,message=f'မီးသတင်းအသစ် #{incident.pk}')
        services.audit(request.user,'report_fire',incident)
        messages.success(request,'မီးသတင်းပေးပို့ပြီးပါပြီ။');return redirect('emergency:incident',pk=incident.pk)
    return render(request,'emergency/form.html',{'form':form,'title':'မီးသတင်းပေးပို့ရန်','location_picker':True})


def filter_incidents(request):
    query=incidents_for(request.user)
    if request.GET.get('q'):query=query.filter(Q(address__icontains=request.GET['q'])|Q(reporter_phone__icontains=request.GET['q']))
    if request.GET.get('status'):query=query.filter(status=request.GET['status'])
    if request.GET.get('level','') in ['0','1','2','3','4','5']:query=query.filter(fire_scale=int(request.GET['level']))
    for key,lookup in [('start','reported_at__date__gte'),('end','reported_at__date__lte')]:
        value=request.GET.get(key)
        if value:
            try:timezone.datetime.strptime(value,'%Y-%m-%d')
            except ValueError:continue
            query=query.filter(**{lookup:value})
    return query.order_by('-reported_at')


@login_required
def incidents(request):
    query=filter_incidents(request)
    return render(request,'emergency/incidents.html',{'page_obj':Paginator(query,20).get_page(request.GET.get('page')),'summary':query.values('status').annotate(total=Count('pk'))})


@login_required
def incident(request,pk):
    obj=get_object_or_404(incidents_for(request.user),pk=pk)
    can_manage=request.user.is_admin
    form=ConfirmForm(instance=obj) if can_manage and not obj.closed_at else None
    nearest=None
    if obj.latitude is not None and obj.longitude is not None:
        stations=list(FireStation.objects.filter(status='Active'))
        if stations:nearest=min(stations,key=lambda s:services.distance((s.latitude,s.longitude),(obj.latitude,obj.longitude)))
    plan,rows=services.preview(obj)
    deployments=obj.deployments.select_related('station')
    if not request.user.is_admin:
        deployments=deployments.filter(station_id__in=managed_station_ids(request.user)+([request.user.station_id] if request.user.is_firefighter else []))
    for d in deployments:
        d.can_manage=request.user.is_admin or d.station_id in managed_station_ids(request.user)
        d.eligible=services.eligible_staff(d) if d.can_manage else User.objects.none()
    routes=[d.route for d in deployments if d.route.get('coordinates')]
    return render(request,'emergency/incident.html',{'incident':obj,'form':form,'nearest':nearest,'plan':plan,'requirements':rows,
        'available':Vehicle.objects.filter(status='Available',station__status='Active').select_related('station','kind') if can_manage else [],
        'deployments':deployments,'updates':obj.updates.select_related('author','station').order_by('-pk')[:50] if request.user.is_admin or request.user.is_station_admin or request.user.is_firefighter else [],
        'routes':routes,'can_final':request.user.is_admin or obj.lead_station_id in managed_station_ids(request.user)})


@login_required
@require_POST
@transaction.atomic
def action(request,pk,action):
    incident=get_object_or_404(incidents_for(request.user).select_for_update(),pk=pk)
    user=request.user;data=request.POST
    try:
        if incident.closed_at:raise ValidationError('ဖြစ်စဉ်ပိတ်ပြီးဖြစ်သည်။')
        if action=='confirm':
            if not user.is_admin:raise PermissionDenied
            if incident.closed_at:raise ValidationError('ပိတ်ပြီးဖြစ်စဉ် ပြင်မရပါ။')
            form=ConfirmForm(data,instance=incident)
            if not form.is_valid():raise ValidationError(str(form.errors.as_text()))
            incident=form.save(commit=False)
            if incident.status=='Pending':incident.status='Confirmed'
            incident.save();services.audit(user,'confirm_level',incident,level=incident.fire_scale)
        elif action=='dispatch':services.dispatch(user,pk,[int(v) for v in data.getlist('vehicles')],data.get('reason',''),data.get('manual_reason',''))
        elif action=='state':
            if not user.is_admin:raise PermissionDenied
            if data.get('status') not in ['Confirmed','Under Control','Resolved','False Alarm']:raise ValidationError('အခြေအနေ မမှန်ပါ။')
            if incident.closed_at:raise ValidationError('ဖြစ်စဉ်ပိတ်ပြီးဖြစ်သည်။')
            if data['status']=='False Alarm' and incident.deployments.exclude(state__in=['Returned','Cancelled']).exists():raise ValidationError('ပါဝင်စခန်းများ ပြန်ရောက်ရန်လိုသည်။')
            incident.status=data['status'];incident.save(update_fields=['status'])
            IncidentUpdate.objects.create(incident=incident,author=user,message=data['status']);services.audit(user,'incident_state',incident,status=data['status'])
        elif action=='update':
            station_id=int(data.get('station') or 0)
            if not user.is_admin and (station_id not in managed_station_ids(user) or not incident.deployments.filter(station_id=station_id).exists()):raise PermissionDenied
            text=data.get('message','').strip()
            if not text:raise ValidationError('အခြေအနေမှတ်တမ်း ဖြည့်ပါ။')
            update=IncidentUpdate.objects.create(incident=incident,author=user,station_id=station_id or None,message=text)
            services.audit(user,'incident_update',update)
        elif action=='final':
            if not user.is_admin and incident.lead_station_id not in managed_station_ids(user):raise PermissionDenied
            if incident.status!='Resolved':raise ValidationError('မီးငြှိမ်းသတ်ပြီးမှ နောက်ဆုံးအစီရင်ခံစာတင်ပါ။')
            if incident.closed_at:raise ValidationError('ဖြစ်စဉ်ပိတ်ပြီးဖြစ်သည်။')
            narrative=data.get('narrative','').strip()
            if not narrative:raise ValidationError('ဖြစ်ပွားပုံ ဖြည့်ပါ။')
            final,_=FinalReport.objects.update_or_create(incident=incident,defaults={'narrative':narrative,'snapshot':services.aggregate(incident),'submitted_by':user,'state':'Submitted','reviewed_by':None,'review_note':''})
            services.audit(user,'final_submit',final)
        elif action=='review-final':
            if not user.is_admin:raise PermissionDenied
            with transaction.atomic():
                incident=FireReport.objects.select_for_update().get(pk=pk)
                final=get_object_or_404(FinalReport.objects.select_for_update(),incident=incident,state='Submitted')
                decision=data.get('decision')
                if decision not in ['Approved','Revision']:raise ValidationError('ဆုံးဖြတ်ချက်ရွေးပါ။')
                if decision=='Approved':
                    if incident.status!='Resolved' or incident.deployments.exclude(state__in=['Returned','Cancelled']).exists():raise ValidationError('စခန်းအားလုံး ပြန်ရောက်ပြီး မီးငြှိမ်းသတ်ပြီးဖြစ်ရမည်။')
                    incident.closed_at=timezone.now();incident.save(update_fields=['closed_at'])
                final.state=decision;final.reviewed_by=user;final.review_note=data.get('note','');final.save();services.audit(user,'final_review',final,state=decision)
        else:raise ValidationError('Unknown action')
        messages.success(request,'ဆောင်ရွက်ပြီးပါပြီ။')
    except (ValidationError,ValueError) as error:messages.error(request,str(error))
    return redirect('emergency:incident',pk=pk)


@login_required
@require_POST
@transaction.atomic
def deployment_action(request,pk,action):
    deployment=get_object_or_404(Deployment,pk=pk)
    if not request.user.is_admin and deployment.station_id not in managed_station_ids(request.user):raise PermissionDenied
    incident=FireReport.objects.select_for_update().get(pk=deployment.incident_id)
    deployment=Deployment.objects.select_for_update().get(pk=pk)
    try:
        if incident.closed_at:raise ValidationError('ဖြစ်စဉ်ပိတ်ပြီးဖြစ်သည်။')
        if action=='state':services.deployment_state(request.user,pk,request.POST.get('state'))
        elif action=='staff':services.assign_staff(request.user,pk,[int(v) for v in request.POST.getlist('employees')])
        elif action=='release':
            with transaction.atomic():
                Deployment.objects.select_for_update().get(pk=pk)
                person=get_object_or_404(StaffParticipation.objects.select_for_update(),pk=request.POST.get('person'),deployment=deployment,active=True)
                person.active=False;person.released_at=timezone.now();person.save();services.audit(request.user,'staff_release',person)
        elif action=='withdraw':
            if not request.user.is_admin:raise PermissionDenied
            if not request.POST.get('reason','').strip():raise ValidationError('ရုတ်သိမ်းရသည့် အကြောင်းပြချက်ဖြည့်ပါ။')
            with transaction.atomic():
                Deployment.objects.select_for_update().get(pk=pk)
                participation=get_object_or_404(VehicleParticipation,pk=request.POST.get('vehicle'),deployment=deployment,active=True)
                vehicle=Vehicle.objects.select_for_update().get(pk=participation.vehicle_id)
                participation.active=False;participation.returned_at=timezone.now();participation.save()
                vehicle.status='Available';vehicle.save();services.audit(request.user,'vehicle_withdraw',participation,reason=request.POST['reason'])
                if not deployment.vehicles.filter(active=True).exists():
                    deployment.state='Returned' if deployment.vehicles.filter(actual=True).exists() else 'Cancelled'
                    deployment.save(update_fields=['state'])
                    deployment.personnel.filter(active=True).update(active=False,released_at=timezone.now())
        elif action=='report':
            if deployment.incident.closed_at:raise ValidationError('ဖြစ်စဉ်ပိတ်ပြီးဖြစ်သည်။')
            if deployment.state!='Returned':raise ValidationError('စခန်းပြန်ရောက်ပြီးမှ အစီရင်ခံစာတင်ပါ။')
            from decimal import Decimal,InvalidOperation
            try:water=Decimal(request.POST.get('water_gallons',''))
            except InvalidOperation:raise ValidationError('ရေဂါလန် မမှန်ပါ။')
            narrative=request.POST.get('narrative','').strip()
            if not narrative or not water.is_finite() or water<0:raise ValidationError('ဖြစ်ပွားပုံနှင့် အနုတ်မဟုတ်သောရေဂါလန်ဖြည့်ပါ။')
            report,_=StationReport.objects.update_or_create(deployment=deployment,defaults={'narrative':narrative,'water_gallons':water,'submitted_by':request.user})
            FinalReport.objects.filter(incident=deployment.incident,state='Submitted').update(state='Revision',review_note='စခန်းအစီရင်ခံစာပြောင်းလဲထားသည်။ ပြန်စုစည်းတင်ပါ။')
            services.audit(request.user,'station_report',report)
        else:raise ValidationError('Unknown action')
    except (ValidationError,ValueError) as error:messages.error(request,str(error))
    return redirect('emergency:incident',pk=deployment.incident_id)


@login_required
@require_POST
def leave_review(request,pk):
    try:services.review_leave(request.user,pk,request.POST.get('decision')=='Approved',request.POST.get('replacement'),request.POST.get('note',''))
    except ValidationError as error:messages.error(request,str(error))
    return redirect('emergency:list',kind='leaves')


@login_required
def map_view(request):return render(request,'emergency/map.html')


@login_required
def reports(request):
    query=filter_incidents(request)
    period=request.GET.get('period','day')
    from django.db.models.functions import TruncDay,TruncMonth,TruncYear
    trunc={'day':TruncDay,'month':TruncMonth,'year':TruncYear}.get(period,TruncDay)
    summary=query.order_by().annotate(period=trunc('reported_at')).values('period','fire_scale').annotate(total=Count('pk')).order_by('-period','fire_scale')
    if request.GET.get('export')=='csv':
        response=HttpResponse(content_type='text/csv; charset=utf-8-sig');response['Content-Disposition']='attachment; filename="incidents.csv"';response.write('\ufeff')
        writer=csv.writer(response);writer.writerow(['ID','Reported','Address','Level','Status'])
        for i in query:writer.writerow([i.pk,timezone.localtime(i.reported_at).isoformat(),i.address,i.fire_scale,i.status])
        return response
    if request.GET.get('export')=='pdf':
        from .pdf import report_pdf
        return report_pdf(request,query)
    return render(request,'emergency/reports.html',{'page_obj':Paginator(summary,20).get_page(request.GET.get('page')),'period':period})


@login_required
def incident_pdf(request,pk):
    obj=get_object_or_404(incidents_for(request.user),pk=pk)
    if not request.user.is_admin and not (request.user.is_firefighter or request.user.is_station_admin):raise PermissionDenied
    from .pdf import incident_pdf_response
    return incident_pdf_response(request,obj)
