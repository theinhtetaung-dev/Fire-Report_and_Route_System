(() => {
    window.formatDateTime = value => {
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return '';
        const parts = Object.fromEntries(new Intl.DateTimeFormat('en-GB', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Yangon',
        }).formatToParts(date).map(part => [part.type, part.value]));
        return `${parts.day}-${parts.month}-${parts.year} ${parts.hour}:${parts.minute} ${parts.dayPeriod.toUpperCase()}`;
    };
    const selector = '[data-datepicker], input[type="date"], input[type="datetime-local"]';
    function initialize(root = document) {
        const fields = [...root.querySelectorAll(selector)];
        if (root.matches?.(selector)) fields.unshift(root);
        fields.forEach(input => {
            if (input._flatpickr) return;
            const nativeType = input.type;
            const withTime = input.dataset.datepicker === 'datetime' || nativeType === 'datetime-local';
            const value = input.value;
            const options = {
                dateFormat: withTime ? 'd-m-Y G:i K' : 'd-m-Y',
                enableTime: withTime,
                time_24hr: false,
                minuteIncrement: 1,
                disableMobile: true,
                allowInput: true,
            };
            if (nativeType === 'date' || nativeType === 'datetime-local') {
                const sourceFormat = nativeType === 'date' ? 'Y-m-d' : 'Y-m-d\\TH:i';
                if (value) options.defaultDate = flatpickr.parseDate(value, sourceFormat);
                if (input.min) options.minDate = flatpickr.parseDate(input.min, sourceFormat);
                if (input.max) options.maxDate = flatpickr.parseDate(input.max, sourceFormat);
                input.type = 'text';
                input.value = '';
            }
            input.placeholder = withTime ? 'dd-mm-yyyy hh:mm AM/PM' : 'dd-mm-yyyy';
            flatpickr(input, options);
        });
    }
    window.initializeDatepickers = initialize;
    document.addEventListener('DOMContentLoaded', () => {
        initialize();
        new MutationObserver(records => {
            records.forEach(record => record.addedNodes.forEach(node => {
                if (node.nodeType === Node.ELEMENT_NODE) initialize(node);
            }));
        }).observe(document.body, { childList: true, subtree: true });
    });
})();
