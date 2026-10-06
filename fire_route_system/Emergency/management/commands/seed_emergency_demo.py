from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from DataAccess.models import Role,User,FireStation
from Emergency.models import VehicleType,Vehicle,ResponsePlan,PlanRequirement,Duty,Post


class Command(BaseCommand):
    help='Seed clearly labelled demo accounts, vehicles and response plans without resetting passwords.'
    @transaction.atomic
    def handle(self,*args,**options):
        roles={name:Role.objects.get_or_create(role_name=name)[0] for name in ['Administrator','Station Admin','Firefighter','Citizen']}
        stations=list(FireStation.objects.filter(status='Active').order_by('pk'))
        if not stations:
            stations=[FireStation.objects.create(name='Demo မန္တလေးစခန်း',address='Demo နေရာ',contact_number='020000000',latitude=21.975,longitude=96.083)]
        kinds=[VehicleType.objects.get_or_create(name=n)[0] for n in ['မီးငြှိမ်းသတ်ယာဉ်','ရေသယ်ယာဉ်','ကယ်ဆယ်ရေးယာဉ်']]
        for i,station in enumerate(stations):
            for k,kind in enumerate(kinds):
                for number in [1,2]:Vehicle.objects.get_or_create(registration=f'DEMO-{station.pk}-{k}-{number}',defaults={'station':station,'kind':kind})
            for level in range(6):
                plan,created=ResponsePlan.objects.get_or_create(home_station=station,level=level,defaults={'lead_station':station})
                if created:
                    for n,target in enumerate(stations[:min(len(stations),level+1)]):
                        target=station if n==0 else (target if target!=station else stations[-1])
                        PlanRequirement.objects.get_or_create(plan=plan,station=target,kind=kinds[0],defaults={'quantity':1 if level==0 else 2})
                    PlanRequirement.objects.get_or_create(plan=plan,station=station,kind=kinds[1],defaults={'quantity':1 if level<3 else 2})
        demo=[('demo_admin','Administrator','09900000001',None),('demo_station','Station Admin','09900000002',stations[0]),('demo_firefighter','Firefighter','09900000003',stations[0]),('demo_citizen','Citizen','09900000004',None)]
        for username,role,phone,station in demo:
            user,created=User.objects.get_or_create(username=username,defaults={'role':roles[role],'phone_number':phone,'email':None,'station':station,'full_name':username+' (Demo)','nrc':'Demo NRC','rank':'Demo တပ်သား' if role=='Firefighter' else ''})
            if created:user.set_password('DemoFire2026!');user.save()
            if role=='Firefighter' and not Duty.objects.filter(employee=user,ends_at__gt=timezone.now()).exists():
                Duty.objects.create(employee=user,starts_at=timezone.now()-timedelta(hours=1),ends_at=timezone.now()+timedelta(hours=24),task='Demo မီးလောင်မှုလိုက်ပါရန်')
        Post.objects.get_or_create(title='Demo စနစ်အသုံးပြုခြင်း',defaults={'author':User.objects.get(username='demo_admin'),'body':'ယာဉ်နှင့် စေလွှတ်အစီအစဉ်များသည် သရုပ်ပြဒေတာသာဖြစ်သည်။','audience':'Public'})
        self.stdout.write(self.style.SUCCESS('Demo seed complete. New demo accounts only: DemoFire2026! Existing passwords and plans preserved.'))
