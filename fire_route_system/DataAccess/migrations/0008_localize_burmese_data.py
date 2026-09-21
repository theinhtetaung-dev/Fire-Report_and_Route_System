from django.db import migrations

def apply_burmese_localization(apps, schema_editor):
    FireStation = apps.get_model('DataAccess', 'FireStation')
    Location = apps.get_model('DataAccess', 'Location')
    Role = apps.get_model('DataAccess', 'Role')
    Dispatch = apps.get_model('DataAccess', 'Dispatch')
    FireReport = apps.get_model('DataAccess', 'FireReport')

    # 1. Localize Fire Stations (Mandalay Region)
    station_updates = {
        4: {
            'name': 'မန္တလေးတိုင်းဒေသကြီး မီးသတ်ဦးစီးဌာန (ပင်မ)',
            'address': '၇၈ လမ်း၊ ၂၆ လမ်းနှင့် ၂၇ လမ်းကြား၊ ချမ်းအေးသာဇံမြို့နယ်၊ မန္တလေးမြို့',
        },
        5: {
            'name': 'အမရပူရမြို့နယ် မီးသတ်စခန်း',
            'address': 'စစ်ကိုင်း-မန္တလေးလမ်းမကြီး၊ အမရပူရမြို့နယ်၊ မန္တလေးမြို့',
        },
        6: {
            'name': 'ချမ်းမြသာစည်မြို့နယ် မီးသတ်စခန်း',
            'address': '၈၄ လမ်း၊ ချမ်းမြသာစည်မြို့နယ်၊ မန္တလေးမြို့',
        },
        7: {
            'name': 'မန္တလေးမြို့ ဗဟိုမီးသတ်စခန်း (အမှတ် ၁)',
            'address': '၈၄ လမ်းနှင့် ၂၆ လမ်းထောင့်၊ မဟာအောင်မြေမြို့နယ်၊ မန္တလေးမြို့',
        },
        8: {
            'name': 'ချမ်းအေးသာဇံမြို့နယ် မီးသတ်စခန်း (အမှတ် ၂)',
            'address': '၆၉ လမ်းနှင့် ၃၅ လမ်းထောင့်၊ ချမ်းအေးသာဇံမြို့နယ်၊ မန္တလေးမြို့',
        },
        9: {
            'name': 'ချမ်းမြသာစည်မြို့နယ် မီးသတ်စခန်း (အမှတ် ၃)',
            'address': 'ကန်တော်ကြီးပတ်လမ်း၊ ချမ်းမြသာစည်မြို့နယ်၊ မန္တလေးမြို့',
        },
        10: {
            'name': 'ပြည်ကြီးတံခွန်မြို့နယ် မီးသတ်စခန်း (အမှတ် ၄)',
            'address': 'မန္တလေး-လားရှိုးလမ်းမကြီး၊ ပြည်ကြီးတံခွန်မြို့နယ်၊ မန္တလေးမြို့',
        },
        11: {
            'name': 'မဟာအောင်မြေမြို့နယ် မီးသတ်စခန်း (အမှတ် ၅)',
            'address': '၃၅ လမ်းနှင့် ၇၈ လမ်းထောင့်၊ မဟာအောင်မြေမြို့နယ်၊ မန္တလေးမြို့',
        },
        12: {
            'name': 'ပုသိမ်ကြီးမြို့နယ် မီးသတ်စခန်း (အမှတ် ၆)',
            'address': 'မန္တလေး-မတ္တရာလမ်းမကြီး၊ ပုသိမ်ကြီးမြို့နယ်၊ မန္တလေးမြို့',
        },
        13: {
            'name': 'အမရပူရမြို့နယ် မီးသတ်စခန်း (အမှတ် ၇)',
            'address': 'မန္တလေး-အမရပူရလမ်းမကြီး၊ အမရပူရမြို့နယ်၊ မန္တလေးမြို့',
        },
        14: {
            'name': 'အောင်မြေသာဇံမြို့နယ် မီးသတ်စခန်း (အမှတ် ၈)',
            'address': '၃၅ လမ်းနှင့် ၈၅ လမ်းထောင့်၊ အောင်မြေသာဇံမြို့နယ်၊ မန္တလေးမြို့',
        },
        15: {
            'name': 'တံတားဦးမြို့နယ် မီးသတ်စခန်း (အမှတ် ၉)',
            'address': 'မန္တလေး-မုံရွာလမ်းမကြီး၊ တံတားဦးမြို့နယ်၊ မန္တလေးတိုင်းဒေသကြီး',
        },
        16: {
            'name': 'စဉ့်ကိုင်မြို့နယ် မီးသတ်စခန်း (အမှတ် ၁၀)',
            'address': 'ရန်ကုန်-မန္တလေးလမ်းဟောင်း၊ စဉ့်ကိုင်မြို့နယ်၊ မန္တလေးတိုင်းဒေသကြီး',
        },
        17: {
            'name': 'ချမ်းအေးသာစံ နယ်မြေမီးသတ်စခန်း',
            'address': '၁၀၇ လမ်း၊ ချမ်းအေးသာစံမြို့နယ်၊ မန္တလေးမြို့',
        }
    }

    for st_id, data in station_updates.items():
        FireStation.objects.filter(station_id=st_id).update(
            name=data['name'],
            address=data['address']
        )

    # Clean any other station names containing English parentheticals
    for st in FireStation.objects.all():
        updated = False
        new_name = st.name
        if '(' in new_name and ')' in new_name:
            # Strip English inside brackets if Burmese exists before it
            burmese_part = new_name.split('(')[0].strip()
            if burmese_part:
                new_name = burmese_part
                updated = True
        if updated:
            st.name = new_name
            st.save()

    # 2. Localize Location (Mandalay Region landmarks)
    location_updates = {
        11: {
            'name': 'မန္တလေး နန်းတော်',
            'description': '၁၈၅၀ ပြည့်လွန်နှစ်များ နှောင်းပိုင်းတွင် တည်ဆောက်ခဲ့သော ကျုံးနှင့် မြို့ရိုးကာရံထားသည့် ကုန်းဘောင်ခေတ် နောက်ဆုံးနန်းတော်ဟောင်း။'
        },
        12: {
            'name': 'မန္တလေးတောင်',
            'description': 'မန္တလေးမြို့ အရှေ့မြောက်ဘက်တွင် တည်ရှိသော အမြင့် ၂၄၀ မီတာရှိ သမိုင်းဝင် တောင်တော်ဖြစ်ပြီး စေတီပုထိုး၊ ဘုန်းတော်ကြီးကျောင်းများနှင့် ရှုခင်းကောင်းများ တည်ရှိရာနေရာ။'
        },
        13: {
            'name': 'မဟာမုနိဘုရားကြီး',
            'description': 'ရွှေသင်္ကန်းအထပ်ထပ် ကပ်လှူပူဇော်ထားသည့် ဗုဒ္ဓဘာသာဝင်တို့၏ အထွတ်အမြတ်ထားရာ သမိုင်းဝင် မဟာမုနိ ရုပ်ရှင်တော်မြတ်ကြီး ကိန်းဝပ်တော်မူရာ ဌာန။'
        },
        14: {
            'name': 'ကုသိုလ်တော်ဘုရား',
            'description': 'ပိဋကတ်သုံးပုံ ပါဠိတော်များကို ကျောက်ထက်အက္ခရာ တင်ထားသည့် ကျောက်စာချပ်ပေါင်း ၇၂၉ ချပ် တည်ရှိသော ကမ္ဘာ့အကြီးဆုံး စာအုပ်အဖြစ် ထင်ရှားသည့် စေတီတော်။'
        },
        15: {
            'name': 'ဦးပိန်တံတား',
            'description': '၁၈၅၀ ပြည့်နှစ်ခန့်တွင် တောင်သမန်အင်းကို ဖြတ်သန်းတည်ဆောက်ခဲ့ပြီး ကမ္ဘာ့သက်တမ်းအရင့်ဆုံးနှင့် အရှည်ဆုံး ကျွန်းသစ်တံတားအဖြစ် ထင်ရှားသော ၁.၂ ကီလိုမီတာရှည် သမိုင်းဝင်တံတား။'
        },
        16: {
            'name': 'ဈေးချိုတော်',
            'description': 'မန္တလေးမြို့၏ သမိုင်းအရှည်ကြာဆုံး ဗဟိုဈေးကြီးဖြစ်ပြီး ဒေသထွက်ကုန်၊ အထည်အလိပ်နှင့် လူသုံးကုန်ပစ္စည်းများ စုံလင်စွာ ရောင်းဝယ်ဖောက်ကားရာ အဓိကနေရာ။'
        },
        17: {
            'name': 'ရွှေကျောင်းတော် (ရွှေနန်းတော်ကျောင်း)',
            'description': 'နန်းတွင်းလက်ရာ သစ်သားပန်းပု လက်ရာမြောက် အနုပညာများဖြင့် စနစ်တကျ တည်ဆောက်ထားသည့် သမိုင်းဝင် ကျွန်းကျောင်းတော်ကြီး။'
        }
    }

    for loc_id, data in location_updates.items():
        Location.objects.filter(id=loc_id).update(
            name=data['name'],
            description=data['description']
        )

    # 3. Localize Role descriptions
    role_desc_map = {
        'administrator': 'အကောင့်များနှင့် စနစ်ဆက်တင်များကို အပြည့်အဝ စီမံခန့်ခွဲနိုင်သော စနစ်အုပ်ချုပ်သူ',
        'admin': 'အကောင့်များနှင့် စနစ်ဆက်တင်များကို အပြည့်အဝ စီမံခန့်ခွဲနိုင်သော စနစ်အုပ်ချုပ်သူ',
        'dispatcher': 'အရေးပေါ်ဖုန်းခေါ်ဆိုမှုများ လက်ခံစိစစ်ခြင်းနှင့် မီးသတ်တပ်ဖွဲ့များ စေလွှတ်ခြင်းကို ကိုင်တွယ်သည့် အရေးပေါ်ကွပ်ကဲရေးအရာရှိ',
        'operator': 'အရေးပေါ်ဖုန်းခေါ်ဆိုမှုများ လက်ခံစိစစ်ခြင်းနှင့် မီးသတ်တပ်ဖွဲ့များ စေလွှတ်ခြင်းကို ကိုင်တွယ်သည့် အရေးပေါ်ကွပ်ကဲရေးအရာရှိ',
        'firefighter': 'မီးလောင်ရာ မြေပြင်သို့ သွားရောက်ငြှိမ်းသတ်ပြီး အခြေအနေသတင်းပို့သော မြေပြင်မီးသတ်တပ်ဖွဲ့ဝင်',
        'responder': 'မီးလောင်ရာ မြေပြင်သို့ သွားရောက်ငြှိမ်းသတ်ပြီး အခြေအနေသတင်းပို့သော မြေပြင်မီးသတ်တပ်ဖွဲ့ဝင်',
        'citizen': 'အရေးပေါ် မီးလောင်မှုများကို အချိန်နှင့်တစ်ပြေးညီ သတင်းပေးပို့တိုင်ကြားသူ ပြည်သူလူထု',
        'reporter': 'အရေးပေါ် မီးလောင်မှုများကို အချိန်နှင့်တစ်ပြေးညီ သတင်းပေးပို့တိုင်ကြားသူ ပြည်သူလူထု',
    }

    for role in Role.objects.all():
        desc = role_desc_map.get(role.role_name.lower().strip())
        if desc:
            role.description = desc
            role.save()

    # 4. Localize Dispatch resources_deployed
    for disp in Dispatch.objects.all():
        if disp.resources_deployed:
            text = disp.resources_deployed
            if 'Fire Engine' in text or 'Water Tender' in text or 'Personnel' in text:
                disp.resources_deployed = 'မီးသတ်ယာဉ် ၂ စီး၊ ရေသယ်ယာဉ် ၁ စီး၊ မီးသတ်တပ်ဖွဲ့ဝင် ၈ ဦး'
                disp.save()

    # 5. Localize FireReport Addresses (Mandalay Region)
    report_address_map = {
        18: '၇၃ လမ်း၊ ၁၀၇ x ၁၀၈ လမ်းကြား၊ MIIT အနီး၊ ချမ်းမြသာစည်မြို့နယ်၊ မန္တလေးမြို့',
        20: '၁၂၃ လမ်း၊ မဟာအောင်မြေမြို့နယ်၊ မန္တလေးမြို့',
        21: '၆၂ လမ်းနှင့် သိပ္ပံလမ်းထောင့်၊ မဟာအောင်မြေမြို့နယ်၊ မန္တလေးမြို့',
        29: '၇၃ လမ်းနှင့် ၁၀၇ လမ်းထောင့်၊ ချမ်းမြသာစည်မြို့နယ်၊ မန္တလေးမြို့',
    }
    for rep_id, addr in report_address_map.items():
        FireReport.objects.filter(id=rep_id).update(address=addr)


def revert_burmese_localization(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('DataAccess', '0007_user_last_login'),
    ]

    operations = [
        migrations.RunPython(apply_burmese_localization, revert_burmese_localization),
    ]
