(() => {
    const root = document.documentElement;
    const themeButtons = document.querySelectorAll('[data-theme-toggle]');

    const updateThemeControls = () => {
        const isDark = root.dataset.theme === 'dark';
        themeButtons.forEach((button) => {
            button.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
            button.setAttribute('aria-pressed', String(!isDark));
        });
    };

    themeButtons.forEach((button) => {
        button.addEventListener('click', () => {
            root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
            localStorage.setItem('portfolio-theme', root.dataset.theme);
            updateThemeControls();
        });
    });
    updateThemeControls();

    const menuButton = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const closeMenu = () => {
        if (!menuButton || !mobileMenu) return;
        mobileMenu.classList.add('hidden');
        menuButton.setAttribute('aria-expanded', 'false');
        menuButton.setAttribute('aria-label', 'Open navigation');
        menuButton.querySelector('i')?.classList.replace('bi-x-lg', 'bi-list');
    };

    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', () => {
            const willOpen = mobileMenu.classList.contains('hidden');
            mobileMenu.classList.toggle('hidden');
            menuButton.setAttribute('aria-expanded', String(willOpen));
            menuButton.setAttribute('aria-label', willOpen ? 'Close navigation' : 'Open navigation');
            const icon = menuButton.querySelector('i');
            icon?.classList.toggle('bi-list', !willOpen);
            icon?.classList.toggle('bi-x-lg', willOpen);
        });
        mobileMenu.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') closeMenu();
        });
    }

    const nav = document.getElementById('site-nav');
    const updateNav = () => nav?.classList.toggle('is-scrolled', window.scrollY > 16);
    window.addEventListener('scroll', updateNav, { passive: true });
    updateNav();

    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        const revealElements = document.querySelectorAll('.reveal-on-scroll');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });
        revealElements.forEach((element) => observer.observe(element));
    }
})();
