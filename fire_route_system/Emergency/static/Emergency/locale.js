/* UI copy only: stored values, addresses, names and form submissions stay intact. */
(() => {
    const pairs = [
        ['Command center','ကွပ်ကဲမှုဗဟို'], ['Command and dispatch','ကွပ်ကဲရေးနှင့် တာဝန်စေလွှတ်ခြင်း'],
        ['Stations and vehicles','စခန်းများနှင့် ယာဉ်ယန္တရားများ'], ['Staff and duties','ဝန်ထမ်းနှင့် တာဝန်စီမံမှု'],
        ['News and reports','သတင်းနှင့် အစီရင်ခံစာများ'], ['Report a fire','အရေးပေါ် မီးသတင်းပို့ရန်'],
        ['Incidents','မီးလောင်မှုဖြစ်စဉ်များ'], ['Review queue','စိစစ်ရန်ဖြစ်စဉ်များ'], ['Command map','ကွပ်ကဲမှုမြေပုံ'],
        ['Fire stations','မီးသတ်စခန်းများ'], ['Fire vehicles','မီးသတ်ယာဉ်များ'], ['Vehicle types','ယာဉ်အမျိုးအစားများ'],
        ['Response plans','မီးလောင်မှုအဆင့်အလိုက် အစီအစဉ်များ'], ['Plan vehicles','အစီအစဉ်အတွက် ယာဉ်စာရင်း'],
        ['Staff and accounts','ဝန်ထမ်းနှင့် အကောင့်များ'], ['Duties','တာဝန်ချိန်နှင့် တာဝန်များ'], ['Leave requests','ခွင့်စာများ'],
        ['News and education','သတင်းနှင့် အသိပညာပေး'], ['Manage posts','သတင်းစီမံရန်'], ['Export reports','အစီရင်ခံစာ ထုတ်ယူရန်'],
        ['Create citizen account','ပြည်သူ့အကောင့်ဖွင့်ရန်'], ['Sign in','အကောင့်ဝင်ရန်'], ['Sign out','အကောင့်ထွက်ရန်'],
        ['Overview','အခြေအနေအကျဉ်းချုပ်'], ['Incident records','ဖြစ်စဉ်မှတ်တမ်း'], ['Fire incidents','မီးလောင်ဖြစ်စဉ်များ'],
        ['Active incidents','လက်ရှိဖြစ်စဉ်'], ['Level 5 incidents','အဆင့် ၅ ဖြစ်စဉ်'], ['Ready stations','အသင့်ရှိစခန်း'],
        ["Today's dispatch orders",'ယနေ့စေလွှတ်အမိန့်'], ['My duties','မိမိတာဝန်ချိန်'], ['Notifications','အသိပေးချက်'],
        ['Recent incidents','နောက်ဆုံးဖြစ်စဉ်များ'], ['Stations and active incidents','စခန်းနှင့် လက်ရှိဖြစ်စဉ်မြေပုံ'],
        ['View full map','မြေပုံအပြည့်ကြည့်ရန်'], ['Mandalay Region Command · Fire emergency system','မန္တလေးတိုင်းဒေသကြီး ကွပ်ကဲမှုဗဟို · မီးဘေးအရေးပေါ်စနစ်'],
        ['Pending review and field operations','ဆိုင်းငံ့ / စိစစ်ဆဲနှင့် မြေပြင်ဖြစ်စဉ်'], ['Emergency severity','အရေးပေါ် မီးလောင်မှုအဆင့်'],
        ['Stations available for dispatch','စေလွှတ်နိုင်သောစခန်းများ'], ['For the associated incidents','သက်ဆိုင်ရာဖြစ်စဉ်များအတွက်'],
        ['No duties yet.','တာဝန်စာရင်းမရှိသေးပါ။'], ['No notifications.','အသိပေးချက်မရှိပါ။'], ['No incidents yet.','ဖြစ်စဉ်မရှိသေးပါ။'],
        ['Mark as read','ဖတ်ပြီး'], ['Marking as read does not accept the dispatch order.','ဖတ်ပြီးခြင်းသည် စေလွှတ်အမိန့်လက်ခံခြင်း မဟုတ်ပါ။'],
        ['Search','ရှာရန်'], ['Status','အခြေအနေ'], ['Fire level','မီးလောင်မှုအဆင့်'], ['Start date','စတင်ရက်'], ['End date','ပြီးဆုံးရက်'],
        ['Filter','စစ်ထုတ်ရန်'], ['All','အားလုံး'], ['Incident','ဖြစ်စဉ်'], ['Reported at','သတင်းပို့ချိန်'], ['Actions','လုပ်ဆောင်ရန်'],
        ['Manage','စီမံရန်'], ['View details','အသေးစိတ်ကြည့်ရန်'], ['Details','အသေးစိတ်'], ['Edit','ပြင်ရန်'], ['Add new','အသစ်ထည့်ရန်'],
        ['Records','စာရင်း'], ['Data source','ဒေတာရင်းမြစ်'], ['Sourced station records','ရင်းမြစ်ပါ စခန်းမှတ်တမ်း'],
        ['Previous page','ရှေ့စာမျက်နှာ'], ['Next page','နောက်စာမျက်နှာ'], ['Save','သိမ်းဆည်းရန်'], ['Submit fire report','မီးလောင်မှု သတင်းပို့ရန်'],
        ['Get current location','လက်ရှိတည်နေရာ ရယူရန်'], ['Name','အမည်'], ['Full name','အမည်အပြည့်အစုံ'], ['Phone number','ဖုန်းနံပါတ်'],
        ['National registration number','မှတ်ပုံတင်အမှတ်'], ['Email (optional)','အီးမေးလ် (မဖြည့်လည်းရသည်)'], ['Email','အီးမေးလ်'],
        ['Password','စကားဝှက်'], ['Confirm password','စကားဝှက် ထပ်ဖြည့်ပါ'], ['Password (only to change it)','စကားဝှက် (ပြင်မည်ဆိုမှဖြည့်ပါ)'],
        ['Username','အသုံးပြုသူအမည်'], ['Rank','ရာထူး'], ['Station','စခန်း'], ['Role','လုပ်ပိုင်ခွင့်'], ['Township','မြို့နယ်'],
        ['Address','လိပ်စာ'], ['Contact number','ဆက်သွယ်ရန်ဖုန်းနံပါတ်'], ['Latitude','လတ္တီတွဒ်'], ['Longitude','လောင်ဂျီတွဒ်'],
        ['Fire address','မီးလောင်ရာလိပ်စာ'], ['Fire latitude','မီးလောင်ရာလတ္တီတွဒ်'], ['Fire longitude','မီးလောင်ရာလောင်ဂျီတွဒ်'],
        ['Reporter latitude','သတင်းပို့သူ၏လတ္တီတွဒ်'], ['Reporter longitude','သတင်းပို့သူ၏လောင်ဂျီတွဒ်'],
        ['Home station','နယ်မြေခံစခန်း'], ['Lead station','ဦးဆောင်စခန်း'], ['Coordinates confirmed','မီးလောင်ရာတည်နေရာ အတည်ပြုပြီး'],
        ['Kind','အမျိုးအစား'], ['Registration','ယာဉ်မှတ်ပုံတင်အမှတ်'], ['Plan','အစီအစဉ်'], ['Quantity','အရေအတွက်'],
        ['Employee','ဝန်ထမ်း'], ['Starts at','စတင်ချိန်'], ['Ends at','ပြီးဆုံးချိန်'], ['Task','တာဝန်'], ['Reason','အကြောင်းပြချက်'],
        ['Title','ခေါင်းစဉ်'], ['Body','အကြောင်းအရာ'], ['Audience','ဖတ်ရှုနိုင်သူများ'], ['Published','ထုတ်ပြန်ပြီး'],
        ['Administrator','စနစ်အုပ်ချုပ်သူ'], ['Admin','စနစ်အုပ်ချုပ်သူ'], ['Station Admin','စခန်းတာဝန်ခံ'], ['Firefighter','မီးသတ်တပ်ဖွဲ့ဝင်'], ['Citizen','ပြည်သူ'],
        ['Available','အသင့်ရှိ'], ['Reserved','ကြိုတင်သတ်မှတ်ထား'], ['Deployed','စေလွှတ်ထား'], ['Maintenance','ပြုပြင်ထိန်းသိမ်းဆဲ'],
        ['Active','အသုံးပြုဆဲ'], ['Inactive','ပိတ်ထား'], ['Suspended','ယာယီရပ်ဆိုင်း'], ['Pending','ဆိုင်းငံ့ / စိစစ်ဆဲ'],
        ['Confirmed','အတည်ပြုပြီး'], ['Dispatched','တပ်ဖွဲ့စေလွှတ်ပြီး'], ['Under Control','မီးထိန်းချုပ်နိုင်ပြီ'], ['Resolved','ငြှိမ်းသတ်ပြီးစီး'], ['False Alarm','သတင်းမှား'],
        ['Approved','အတည်ပြုထား'], ['Rejected','ငြင်းပယ်ထား'], ['Submitted','တင်ပြပြီး'], ['Revision','ပြန်ပြင်ရန်'],
        ['Public','လူတိုင်း'], ['Staff','ဝန်ထမ်းအားလုံး'], ['My station','မိမိစခန်း'], ['Normal','နယ်မြေခံ'],
        ['Level 1','အဆင့် ၁'], ['Level 2','အဆင့် ၂'], ['Level 3','အဆင့် ၃'], ['Level 4','အဆင့် ၄'], ['Level 5','အဆင့် ၅'],
        ['Daily / monthly / yearly reports','နေ့ / လ / နှစ် အစီရင်ခံစာ'], ['Daily','နေ့အလိုက်'], ['Monthly','လအလိုက်'], ['Yearly','နှစ်အလိုက်'],
        ['Export CSV','ဇယားဖိုင် ထုတ်ရန်'], ['Export PDF','စာတမ်းဖိုင် ထုတ်ရန်'], ['Total incidents','ဖြစ်စဉ်စုစုပေါင်း'],
        ['Accept','လက်ခံ'], ['Reject','ငြင်းပယ်'], ['Note','မှတ်ချက်'], ['No replacement','မရွေးပါ'], ['Temporary station manager','ယာယီစခန်းတာဝန်ခံ'],
        ['Review / confirm','စိစစ် / အတည်ပြုရန်'], ['Review, level and station','စိစစ်ခြင်း၊ မီးလောင်မှုအဆင့်နှင့် စခန်းသတ်မှတ်ခြင်း'],
        ['Confirm and save','အတည်ပြု / သိမ်းရန်'], ['Review dispatch resources','စေလွှတ်မည့်စာရင်း စစ်ဆေးရန်'],
        ['Station / type','စခန်း / အမျိုးအစား'], ['Total required','စုစုပေါင်းလို'], ['Currently assigned','ပါဝင်ဆဲ'], ['Still needed','ထပ်လို'],
        ['Select ready or replacement vehicles','အသင့်ရှိယာဉ် / အစားထိုးရွေးရန်'], ['No vehicles available.','အသင့်ရှိယာဉ် မရှိပါ။'],
        ['Reason for an incomplete plan','အစီအစဉ်မပြည့်စုံပါက အကြောင်းပြချက်'], ['Reason for dispatch without a route','လမ်းကြောင်းမရဘဲ စေလွှတ်ရသည့်အကြောင်းပြချက်'],
        ['Approve and dispatch','အတည်ပြုပြီး စေလွှတ်ရန်'], ['Incident status','ဖြစ်စဉ်အခြေအနေ'], ['Change status','အခြေအနေပြောင်းရန်'],
        ['View route','လမ်းကြောင်းကြည့်ရန်'], ['Departure station','ထွက်ခွာစခန်း'], ['Assigned / nearest station','သတ်မှတ်စခန်း / အနီးဆုံးစခန်း'],
        ['Calculate route','လမ်းကြောင်းတွက်ရန်'], ['Viewing a route does not dispatch resources.','လမ်းကြောင်းကြည့်ခြင်းသည် စေလွှတ်အမိန့်မဟုတ်ပါ။'],
        ['Route and incident document','လမ်းကြောင်းနှင့် ဖြစ်စဉ်စာတမ်း'], ['Accept order','အမိန့်လက်ခံ'], ['Departed','ထွက်ခွာပြီး'], ['Arrived at fire','မီးလောင်ရာရောက်ရှိ'],
        ['Vehicles','ယာဉ်များ'], ['Staff members','ဝန်ထမ်းများ'], ['Select on-duty staff','တာဝန်ကျဝန်ထမ်းရွေးရန်'], ['Assign crew','လိုက်ပါရန် ရွေးပေး'],
        ['No staff selected.','မရွေးရသေးပါ။'], ['Release / replace staff','ပြန်လွှတ် / လူစားလဲရန်'], ['Field update','မြေပြင်အခြေအနေမှတ်တမ်း'],
        ['Post update','အခြေအနေတင်ရန်'], ['My station report','မိမိစခန်း အစီရင်ခံစာ'], ['Water used (gallons)','အသုံးပြုရေဂါလန်'],
        ['Incident narrative / operations','ဖြစ်ပွားပုံ / ဆောင်ရွက်မှု'], ['Submit station report','စခန်းအစီရင်ခံစာတင်ရန်'],
        ['Lead station final report','ဦးဆောင်စခန်း နောက်ဆုံးအစီရင်ခံစာ'], ['Narrative and consolidated report','ဖြစ်ပွားပုံနှင့် စုစည်းအစီရင်ခံချက်'],
        ['Submit consolidated reports','စခန်းစာရင်းများ စုစည်းပြီးတင်ရန်'], ['Review note','စိစစ်မှတ်ချက်'], ['Approve and close','အတည်ပြုပြီး စာရင်းပိတ်'],
        ['Request revision','ပြန်ပြင်ခိုင်း'], ['Status history','အခြေအနေမှတ်တမ်း'], ['No history yet.','မှတ်တမ်းမရှိပါ။'],
        ['No records yet.','စာရင်းမရှိသေးပါ။'], ['No records.','စာရင်းမရှိပါ။'], ['No posts yet.','သတင်းမရှိသေးပါ။'],
        ['View all incidents','ဖြစ်စဉ်အားလုံး ကြည့်ရန်'], ['No incidents to review.','စိစစ်ရန် ဖြစ်စဉ် မရှိပါ။'],
        ['View incident status and open its details.','ဖြစ်စဉ်အခြေအနေကို ကြည့်ရှုပြီး အသေးစိတ်ဖွင့်ပါ။'],
        ['No matching incidents. Try changing your search.','ပြသရန်ဖြစ်စဉ် မရှိပါ။ စစ်ထုတ်ထားပါက ရှာဖွေမှုကို ပြောင်းကြည့်ပါ။'],
        ['Fire location on the map','မြေပုံပေါ်ရှိ မီးလောင်ရာနေရာ'], ['Enter an address if location is unavailable.','တည်နေရာမရလျှင် လိပ်စာဖြင့် သတင်းပို့နိုင်ပါသည်။'],
        ['GPS shows your location. Select the fire location on the map, or report using an address.','တည်နေရာရယူခြင်းက သင့်လက်ရှိနေရာကို ပြပါမည်။ မီးလောင်ရာနေရာကို မြေပုံနှိပ်၍ ပြင်ပါ။ လိပ်စာဖြင့်လည်း သတင်းပို့နိုင်ပါသည်။'],
        ['Resource requirements','စခန်းနှင့်ယာဉ် လိုအပ်အရေအတွက်'], ['News posts','သတင်းနှင့် အသိပညာပေးစာများ'],
        ['Page','စာမျက်နှာ'], ['Total','စုစုပေါင်း'], ['records','ခု'],
        ['Review incidents','စိစစ်ရန်ဖြစ်စဉ်'], ['Closed','စာရင်းပိတ်ပြီး'], ['Notifications','အသိပေးချက်'], ['Check connection','ဆက်သွယ်မှု စစ်ဆေးပါ'],
        ['This field is required.','ဤအချက်အလက်ကို ဖြည့်ပါ။'], ['Enter a valid email address.','မှန်ကန်သော အီးမေးလ်လိပ်စာ ဖြည့်ပါ။'],
        ['Enter a number.','ကိန်းဂဏန်း ဖြည့်ပါ။'], ['Enter a whole number.','ကိန်းပြည့် ဖြည့်ပါ။'],
        ['Use the map coordinates for navigation.','တည်နေရာနှင့်လမ်းကြောင်းတွက်ရန်'],
        ['Station details','စခန်းအသေးစိတ်'], ['View stations','စခန်းများ ကြည့်ရန်'], ['Route from station to fire','စခန်းမှ မီးလောင်ရာသို့ လမ်းကြောင်း'],
        ['Route station','လမ်းကြောင်းကြည့်မည့် စခန်း'], ['Directions','လမ်းညွှန်ချက်'], ['Search station / incident','စခန်း / ဖြစ်စဉ် ရှာရန်'],
        ['Search area','နယ်မြေ ရှာရန်'], ['Map data source','မြေပုံဒေတာရင်းမြစ်'], ['Unverified demonstration record','စမ်းသပ်မှတ်တမ်း / ရင်းမြစ်မစစ်ဆေးရသေး'],
        ['Oldest reports appear first. Review the incident and issue dispatch orders separately.','စောစောသတင်းပို့ထားသည့် ဖြစ်စဉ်ကို အရင်ပြထားပါသည်။ စိစစ်အတည်ပြုခြင်းနှင့် စေလွှတ်အမိန့်ကို သီးခြားဆောင်ရွက်ပါ။'],
        ['Update the home station and fire level, then save. Check the response plan for its lead station.','နယ်မြေခံစခန်းနှင့် မီးလောင်မှုအဆင့်ကို ပြင်ပြီး သိမ်းပါ။ ဦးဆောင်စခန်းကို အစီအစဉ်စာရင်းမှ ကြည့်နိုင်ပါသည်။'],
        ['No available on-duty staff. Check the duty roster.','တာဝန်ကျပြီး အသင့်ရှိဝန်ထမ်းမရှိပါ။ တာဝန်စာရင်းကို စစ်ပါ။'],
        ['Confirm vehicle return / cancel','ယာဉ်ပြန်ရောက် အတည်ပြု / ရုတ်သိမ်း'], ['Cancellation reason','ရုတ်သိမ်းရသည့်အကြောင်းပြချက်'],
        ['Returned to station; vehicles and staff ready','စခန်းပြန်ရောက်၊ ယာဉ်/ဝန်ထမ်း အသင့်ဖြစ်'],
        ['day','နေ့'], ['month','လ'], ['year','နှစ်']
    ];
    const aliases = {
        'CAD ကွပ်ကဲမှုဗဟို':'Command center', 'CAD Dashboard':'Command center', 'စိစစ်ရန် ဖြစ်စဉ် Queue':'Review queue',
        'Level အလိုက် အစီအစဉ်များ':'Response plans', 'Plan ယာဉ်စာရင်း':'Plan vehicles', 'Post စီမံရန်':'Manage posts',
        'Citizen အကောင့်ဖွင့်ရန်':'Create citizen account', 'Email (မဖြည့်လည်းရသည်)':'Email (optional)',
        'မီးလောင်ရာ Latitude':'Fire latitude', 'မီးလောင်ရာ Longitude':'Fire longitude', 'သတင်းပို့သူ Latitude':'Reporter latitude',
        'သတင်းပို့သူ Longitude':'Reporter longitude', 'မီးလောင်ရာ Coordinate အတည်ပြုပြီး':'Coordinates confirmed',
        'Level':'Fire level', 'CSV ထုတ်ရန်':'Export CSV', 'PDF ထုတ်ရန်':'Export PDF', 'Post မရှိသေးပါ။':'No posts yet.',
        'စိစစ် / Level / စခန်းသတ်မှတ်ရန်':'Review, level and station', 'Route / ဖြစ်စဉ် PDF':'Route and incident document',
        'Route မရပါက manual စေလွှတ်ရသည့်အကြောင်းပြချက်':'Reason for dispatch without a route',
        'Admin အတည်ပြုပြီး စေလွှတ်ရန်':'Approve and dispatch', 'ယာယီတာဝန်ခံ (Station Admin ခွင့်အတွက်)':'Temporary station manager',
        'GPS မရှိလျှင် လိပ်စာသီးသန့်ဖြင့်တင်နိုင်ပါသည်။':'Enter an address if location is unavailable.',
        'မီးလောင်ရာ Map pin':'Fire location on the map',
        'GPS က သင့်လက်ရှိနေရာကို ပြပါမည်။ မီးလောင်ရာနေရာကို မြေပုံနှိပ်၍ ပြင်ပါ။ လိပ်စာဖြင့်လည်း သတင်းပို့နိုင်ပါသည်။':'GPS shows your location. Select the fire location on the map, or report using an address.',
        'အကောင့်ထွက်မည်':'Sign out', 'Logout':'Sign out', 'Officer Login':'Sign in', 'CAD Operational Console':'Command center',
        'သတင်းဦးစားပေး စိစစ်ရေး (Triage)':'Review queue', 'Triage Queue':'Review queue', 'Logistics & Fleet':'Stations and vehicles',
        'Command & Dispatch':'Command and dispatch', 'Intelligence & Admin':'News and reports', 'Report Portal':'Export reports',
        'User accounts':'Staff and accounts', 'Fire stations':'Fire stations',
        'စခန်း/ယာဉ် လိုအပ်အရေအတွက်':'Resource requirements', 'သတင်းနှင့် အသိပညာပေး Post များ':'News posts',
        'Full name':'Full name', 'Home station':'Home station', 'Lead station':'Lead station',
        'Fire scale':'Fire level', 'မီးသတင်းပေးပို့ရန်':'Report a fire',
        'OpenStreetMap ရင်းမြစ်':'Map data source', 'Demo / ရင်းမြစ် မစစ်ဆေးရသေးသော မှတ်တမ်း':'Unverified demonstration record',
        'နယ်မြေခံစခန်းနှင့် Level ကိုပြင်ပြီး သိမ်းပါ။ ကြိုသတ်မှတ်ထားသောဦးဆောင်စခန်းကို Plan စာရင်းမှကြည့်နိုင်ပါသည်။':'Update the home station and fire level, then save. Check the response plan for its lead station.'
    };
    const lookup = new Map();
    for (const pair of pairs) for (const text of pair) lookup.set(text.toLowerCase(), pair);
    for (const [text, key] of Object.entries(aliases)) lookup.set(text.toLowerCase(), lookup.get(key.toLowerCase()));
    const remembered = new WeakMap();
    const selectors = '[data-ui-copy],.cad-sidebar,.cad-breadcrumb,.cad-operator-badge > .badge,.page-heading,h1,h2,h3,th,label,button,option,summary,.helptext,.errorlist,.status-tag,.cad-kpi-label,.cad-kpi-trend,.cad-live-text,.cad-dash-subtitle,.pagination,.table-wrap td[colspan],.form-actions';
    window.consoleCopy = text => {
        const pair = lookup.get(text.toLowerCase());
        return pair ? pair[localStorage.getItem('lang') === 'en' ? 0 : 1] : text;
    };
    function apply() {
        const language = localStorage.getItem('lang') === 'en' ? 'en' : 'my';
        document.documentElement.lang = language;
        const visited = new Set();
        document.querySelectorAll(selectors).forEach(root => {
            const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
            let node;
            while ((node = walker.nextNode())) {
                if (visited.has(node) || node.parentElement.closest('script,style,input,textarea,#globalLangToggleBtn,#themeToggleBtn,.cad-operator-avatar,.location-item-card')) continue;
                visited.add(node);
                const option = node.parentElement.closest('option');
                if (option && option.value && option.closest('select[name="station"],select[name="home_station"],select[name="lead_station"],select[name="kind"],select[name="plan"],select[name="employee"],select[name="replacement"],select[name="township"],select[name="route_station"]')) continue;
                const raw = node.textContent, text = raw.trim(), hasColon = text.endsWith(':');
                const key = (hasColon ? text.slice(0,-1) : text).trim().toLowerCase();
                let pair = lookup.get(key);
                const old = remembered.get(node);
                if (!pair && old && old.rendered === raw) pair = old.pair;
                if (!pair) continue;
                const replacement = pair[language === 'en' ? 0 : 1] + (hasColon ? ':' : '');
                const rendered = raw.replace(text, replacement);
                remembered.set(node,{pair,rendered});
                if (raw !== rendered) node.textContent = rendered;
            }
        });
    }
    window.applyConsoleLanguage = apply;
    document.addEventListener('DOMContentLoaded', () => {
        apply();
        // New form fragments and polling updates use the same selected language.
        let pending = false;
        new MutationObserver(() => {
            if (pending) return;
            pending = true;
            queueMicrotask(() => { pending = false; apply(); });
        }).observe(document.body,{subtree:true,childList:true,characterData:true});
    });
    window.addEventListener('languageChanged', apply);
})();
