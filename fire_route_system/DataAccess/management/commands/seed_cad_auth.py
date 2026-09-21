import os
import sqlite3
from django.core.management.base import BaseCommand
from django.conf import settings
from DataAccess.models import Role, User, FireStation, Location, FireReport, Dispatch, Tbl_Notification

class Command(BaseCommand):
    help = 'Seeds CAD roles, standard accounts, and migrates existing SQLite data to MySQL'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing CAD Authentication & Roles..."))

        # 1. Ensure Standard Roles
        roles_data = [
            ("Administrator", "အကောင့်များနှင့် စနစ်ဆက်တင်များကို အပြည့်အဝ စီမံခန့်ခွဲနိုင်သော စနစ်အုပ်ချုပ်သူ"),
            ("Dispatcher", "အရေးပေါ်ဖုန်းခေါ်ဆိုမှုများ လက်ခံစိစစ်ခြင်းနှင့် မီးသတ်တပ်ဖွဲ့များ စေလွှတ်ခြင်းကို ကိုင်တွယ်သည့် အရေးပေါ်ကွပ်ကဲရေးအရာရှိ"),
            ("Firefighter", "မီးလောင်ရာ မြေပြင်သို့ သွားရောက်ငြှိမ်းသတ်ပြီး အခြေအနေသတင်းပို့သော မြေပြင်မီးသတ်တပ်ဖွဲ့ဝင်"),
            ("Citizen", "အရေးပေါ် မီးလောင်မှုများကို အချိန်နှင့်တစ်ပြေးညီ သတင်းပေးပို့တိုင်ကြားသူ ပြည်သူလူထု"),
        ]

        role_objs = {}
        for r_name, r_desc in roles_data:
            role_obj, created = Role.objects.get_or_create(
                role_name=r_name,
                defaults={'description': r_desc}
            )
            if not created and role_obj.description != r_desc:
                role_obj.description = r_desc
                role_obj.save()
            role_objs[r_name] = role_obj
            status_str = "Created" if created else "Exists"
            self.stdout.write(f"  Role '{r_name}': {status_str}")

        # Also preserve legacy alias roles if existing
        admin_role = role_objs["Administrator"]
        dispatcher_role = role_objs["Dispatcher"]
        firefighter_role = role_objs["Firefighter"]
        citizen_role = role_objs["Citizen"]

        # 2. Ensure Standard Users
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@fireroute.gov',
                'password': 'adminpass',
                'phone': '091234567',
                'role': admin_role,
            },
            {
                'username': 'operator_hnin',
                'email': 'hnin@fireroute.gov',
                'password': 'operatorpass',
                'phone': '097771112',
                'role': dispatcher_role,
            },
            {
                'username': 'firefighter_zaw',
                'email': 'zaw@fireroute.gov',
                'password': 'firefighter123',
                'phone': '098882223',
                'role': firefighter_role,
            },
            {
                'username': 'citizen_kyaw',
                'email': 'kyaw@gmail.com',
                'password': 'citizen123',
                'phone': '099993334',
                'role': citizen_role,
            },
        ]

        for u_info in users_data:
            user = User.objects.filter(username=u_info['username']).first()
            if not user:
                user = User(
                    username=u_info['username'],
                    email=u_info['email'],
                    phone_number=u_info['phone'],
                    role=u_info['role'],
                    status='Active'
                )
                user.set_password(u_info['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"  User '{user.username}' created."))
            else:
                user.role = u_info['role']
                user.set_password(u_info['password'])
                user.save()
                self.stdout.write(f"  User '{user.username}' updated.")

        # 3. Migrate SQLite Data if MySQL tables are empty
        sqlite_path = settings.BASE_DIR / 'db.sqlite3'
        if os.path.exists(sqlite_path):
            self.stdout.write(self.style.NOTICE("Checking SQLite data for migration to MySQL..."))
            try:
                sq_conn = sqlite3.connect(sqlite_path)
                sq_cur = sq_conn.cursor()

                # Migrate FireStations
                if FireStation.objects.count() == 0:
                    sq_cur.execute("SELECT station_id, name, address, contact_number, latitude, longitude, status, created_at FROM fire_stations")
                    st_rows = sq_cur.fetchall()
                    for r in st_rows:
                        FireStation.objects.create(
                            station_id=r[0],
                            name=r[1],
                            address=r[2],
                            contact_number=r[3],
                            latitude=r[4],
                            longitude=r[5],
                            status=r[6]
                        )
                    self.stdout.write(self.style.SUCCESS(f"  Migrated {len(st_rows)} Fire Stations from SQLite."))

                # Migrate Locations
                if Location.objects.count() == 0:
                    sq_cur.execute("SELECT id, name, latitude, longitude, description, created_at FROM DataAccess_location")
                    loc_rows = sq_cur.fetchall()
                    for r in loc_rows:
                        Location.objects.create(
                            id=r[0],
                            name=r[1],
                            latitude=r[2],
                            longitude=r[3],
                            description=r[4]
                        )
                    self.stdout.write(self.style.SUCCESS(f"  Migrated {len(loc_rows)} Locations from SQLite."))

                # Migrate FireReports
                if FireReport.objects.count() == 0:
                    sq_cur.execute("SELECT id, user_id, reporter_phone, latitude, longitude, fire_scale, photo_url, status, reported_at, address FROM DataAccess_firereport")
                    rep_rows = sq_cur.fetchall()
                    for r in rep_rows:
                        FireReport.objects.create(
                            id=r[0],
                            user_id=r[1],
                            reporter_phone=r[2],
                            latitude=r[3],
                            longitude=r[4],
                            fire_scale=r[5],
                            photo_url=r[6],
                            status=r[7],
                            address=r[9]
                        )
                    self.stdout.write(self.style.SUCCESS(f"  Migrated {len(rep_rows)} Fire Reports from SQLite."))

                # Migrate Notifications
                if Tbl_Notification.objects.count() == 0:
                    sq_cur.execute("SELECT id, is_read, created_at, report_id FROM tbl_notifications")
                    notif_rows = sq_cur.fetchall()
                    for r in notif_rows:
                        rep = FireReport.objects.filter(id=r[3]).first()
                        if rep:
                            Tbl_Notification.objects.create(
                                id=r[0],
                                is_read=bool(r[1]),
                                report=rep
                            )
                    self.stdout.write(self.style.SUCCESS(f"  Migrated {len(notif_rows)} Notifications from SQLite."))

                # Migrate Dispatches
                if Dispatch.objects.count() == 0:
                    sq_cur.execute("SELECT id, dispatched_at, resolved_at, resources_deployed, operator_id, report_id, station_id FROM DataAccess_dispatch")
                    disp_rows = sq_cur.fetchall()
                    for r in disp_rows:
                        rep = FireReport.objects.filter(id=r[5]).first()
                        st = FireStation.objects.filter(station_id=r[6]).first()
                        op = User.objects.filter(id=r[4]).first() or admin_role
                        if rep and st and op:
                            res = r[3]
                            if res and ('Fire Engine' in res or 'Personnel' in res):
                                res = 'မီးသတ်ယာဉ် ၂ စီး၊ ရေသယ်ယာဉ် ၁ စီး၊ မီးသတ်တပ်ဖွဲ့ဝင် ၈ ဦး'
                            Dispatch.objects.create(
                                id=r[0],
                                resources_deployed=res,
                                operator=op,
                                report=rep,
                                station=st
                            )
                    self.stdout.write(self.style.SUCCESS(f"  Migrated {len(disp_rows)} Dispatches from SQLite."))

                sq_conn.close()
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"SQLite migration notice: {e}"))

        self.stdout.write(self.style.SUCCESS("CAD Authentication and Data Initialization Complete."))
