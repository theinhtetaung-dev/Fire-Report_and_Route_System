(() => {
    const source = document.getElementById('admin-chart-data');
    if (!source) return;
    const data = JSON.parse(source.textContent);
    const copy = {
        en: {
            trend: 'Incidents reported · last 14 days', workload: 'Open deployments by station',
            readiness: 'Vehicle availability by station', reported: 'Reported incidents', open: 'Open deployments',
            available: 'Available', committed: 'Reserved / deployed', unavailable: 'Maintenance / inactive',
            workloadNote: 'Ordered, accepted, departed or arrived deployments. Returned and cancelled orders excluded.',
            readinessNote: 'Available vehicles, reserved or deployed vehicles, and maintenance or inactive vehicles.',
            snapshot: 'Snapshot at page load. Refresh the dashboard for updated chart counts.',
            empty: 'No station records yet. Add stations to see their workload and vehicles.',
            error: 'Charts could not load. Check your connection and refresh the page.', loading: 'Loading chart…',
        },
        my: {
            trend: 'ပြီးခဲ့သည့် ၁၄ ရက်အတွင်း သတင်းပို့ဖြစ်စဉ်များ', workload: 'စခန်းအလိုက် လက်ရှိစေလွှတ်အမိန့်များ',
            readiness: 'စခန်းအလိုက် ယာဉ်အသင့်ရှိမှု', reported: 'သတင်းပို့ဖြစ်စဉ်', open: 'လက်ရှိစေလွှတ်အမိန့်',
            available: 'အသင့်ရှိ', committed: 'သီးသန့်ထား / စေလွှတ်ထား', unavailable: 'ပြုပြင်ဆဲ / အသုံးမပြု',
            workloadNote: 'အမိန့်ပေး၊ လက်ခံ၊ ထွက်ခွာနှင့် ရောက်ရှိအမိန့်များ။ ပြန်ရောက်နှင့် ပယ်ဖျက်အမိန့်များ မပါဝင်ပါ။',
            readinessNote: 'အသင့်ရှိယာဉ်၊ သီးသန့်ထား သို့မဟုတ် စေလွှတ်ထားယာဉ်နှင့် ပြုပြင်ဆဲ သို့မဟုတ် အသုံးမပြုယာဉ်များ။',
            snapshot: 'စာမျက်နှာဖွင့်ချိန် ဒေတာဖြစ်သည်။ နောက်ဆုံးအရေအတွက်အတွက် စာမျက်နှာကို ပြန်ဖွင့်ပါ။',
            empty: 'စခန်းမှတ်တမ်းမရှိသေးပါ။ စခန်းများကို ထည့်သွင်းပါ။',
            error: 'ဇယားများ မဖွင့်နိုင်ပါ။ ဆက်သွယ်မှုစစ်ဆေးပြီး စာမျက်နှာကို ပြန်ဖွင့်ပါ။', loading: 'ဇယားဖွင့်နေသည်…',
        },
    };
    let charts = [];
    function render() {
        charts.forEach(chart => chart.destroy());
        charts = [];
        const language = localStorage.getItem('lang') === 'en' ? 'en' : 'my';
        const text = copy[language];
        document.querySelectorAll('[data-chart-copy]').forEach(node => {
            node.textContent = text[node.dataset.chartCopy];
        });
        const ids = ['admin-incident-trend', 'admin-station-workload', 'admin-station-readiness'];
        if (!window.Highcharts) {
            ids.forEach(id => { document.getElementById(id).textContent = text.error; });
            return;
        }
        const style = getComputedStyle(document.documentElement);
        const foreground = style.getPropertyValue('--cad-text-main').trim();
        const muted = style.getPropertyValue('--cad-text-muted').trim();
        const border = style.getPropertyValue('--cad-border').trim();
        const base = {
            chart: { backgroundColor: 'transparent', animation: false, style: { fontFamily: 'inherit' } },
            title: { text: null }, credits: { enabled: true },
            accessibility: { enabled: true },
            legend: { itemStyle: { color: foreground, fontSize: '12px' } },
            xAxis: { lineColor: border, tickColor: border, labels: { style: { color: muted, fontSize: '12px' } } },
            yAxis: { min: 0, allowDecimals: false, title: { text: null }, gridLineColor: border,
                labels: { style: { color: muted, fontSize: '12px' } } },
            tooltip: { shared: true, backgroundColor: style.getPropertyValue('--cad-card-bg').trim(),
                borderColor: border, style: { color: foreground }, valueDecimals: 0 },
            plotOptions: { series: { animation: false } },
        };
        charts.push(Highcharts.chart(ids[0], Highcharts.merge(base, {
            chart: { type: 'column', height: 240 }, legend: { enabled: false },
            accessibility: { description: text.trend },
            xAxis: { categories: data.dates.map(date => date.split('-').reverse().join('-')) },
            series: [{ name: text.reported, data: data.reported, color: '#b91c1c' }],
        })));
        if (!data.stations.length) {
            ids.slice(1).forEach(id => { document.getElementById(id).textContent = text.empty; });
            return;
        }
        const workload = [...data.stations].sort((a, b) => b.open - a.open || a.name.localeCompare(b.name));
        charts.push(Highcharts.chart(ids[1], Highcharts.merge(base, {
            chart: { type: 'bar', height: Math.max(240, workload.length * 32 + 60) },
            legend: { enabled: false }, accessibility: { description: text.workload + '. ' + text.workloadNote },
            xAxis: { categories: workload.map(station => station.name) },
            series: [{ name: text.open, data: workload.map(station => station.open), color: '#b91c1c' }],
        })));
        charts.push(Highcharts.chart(ids[2], Highcharts.merge(base, {
            chart: { type: 'bar', height: Math.max(260, data.stations.length * 32 + 100) },
            accessibility: { description: text.readiness + '. ' + text.readinessNote },
            xAxis: { categories: data.stations.map(station => station.name) },
            plotOptions: { series: { stacking: 'normal' } },
            series: [
                { name: text.available, data: data.stations.map(station => station.available), color: '#15803d' },
                { name: text.committed, data: data.stations.map(station => station.committed), color: '#b45309' },
                { name: text.unavailable, data: data.stations.map(station => station.unavailable), color: '#64748b' },
            ],
        })));
    }
    render();
    window.addEventListener('languageChanged', render);
    new MutationObserver(render).observe(document.documentElement, {
        attributes: true, attributeFilter: ['data-theme'],
    });
})();
