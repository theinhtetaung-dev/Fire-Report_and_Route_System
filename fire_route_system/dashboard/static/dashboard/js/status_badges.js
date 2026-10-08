/* Use textContent so status labels from APIs cannot inject markup. */
(() => {
    function set(element, status, label = status) {
        if (!element) return;
        element.dataset.status = status || 'Unknown';
        element.textContent = label || status || 'Unknown';
        return element;
    }
    function create(status, label = status) {
        return set(document.createElement('span'), status, label);
    }
    window.FireRouteStatus = {set, create, html: (status, label = status) => create(status, label).outerHTML};
})();
