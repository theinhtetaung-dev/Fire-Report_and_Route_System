(() => {
    const translate = () => {
        const language = localStorage.getItem('lang') === 'en' ? 'en' : 'my';
        document.querySelectorAll('[data-pg-en]').forEach(element => {
            element.textContent = element.dataset[language === 'en' ? 'pgEn' : 'pgMy'];
        });
    };
    document.addEventListener('change', event => {
        if (!event.target.matches('[data-pagination-size]')) return;
        const url = new URL(window.location.href);
        url.searchParams.set('per_page', event.target.value);
        url.searchParams.set('page', '1');
        window.location.assign(url);
    });
    translate();
    window.addEventListener('languageChanged', translate);
})();
