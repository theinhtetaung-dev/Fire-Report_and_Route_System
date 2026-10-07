(() => {
    const url = document.currentScript.dataset.pollUrl;
    const interval = 10000;
    let timer, inFlight = false, stopped = false, delay = interval, snapshot;

    window.applyEmergencyUpdate = data => {
        document.getElementById('notice-count').textContent = data.unread > 99 ? '99+' : String(data.unread);
        const next = JSON.stringify(data);
        if (next !== snapshot) {
            snapshot = next;
            window.dispatchEvent(new CustomEvent('emergency-update', {detail: data}));
        }
    };

    window.poll = async () => {
        clearTimeout(timer);
        if (document.hidden || inFlight || stopped) return;
        inFlight = true;
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 15000);
        try {
            const response = await fetch(url, {signal: controller.signal});
            if (response.status === 401 || response.status === 403) {
                stopped = true;
                return;
            }
            if (!response.ok) throw new Error('Refresh failed');
            window.applyEmergencyUpdate(await response.json());
            delay = interval;
        } catch (error) {
            delay = Math.min(delay * 2, 60000);
        } finally {
            clearTimeout(timeout);
            inFlight = false;
            if (!document.hidden && !stopped) timer = setTimeout(window.poll, delay);
        }
    };

    document.addEventListener('visibilitychange', () => {
        clearTimeout(timer);
        if (!document.hidden) window.poll();
    });
    window.poll();
})();
