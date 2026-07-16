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

    const supportsPointerEffects = window.matchMedia('(hover: hover) and (pointer: fine)').matches
        && !window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (supportsPointerEffects) {
        const cursor = document.querySelector('.creative-cursor');
        if (cursor) {
            document.body.classList.add('has-creative-cursor');
            window.addEventListener('pointermove', (event) => {
                cursor.style.setProperty('--cursor-x', `${event.clientX}px`);
                cursor.style.setProperty('--cursor-y', `${event.clientY}px`);
                cursor.classList.add('is-visible');
            }, { passive: true });
            document.addEventListener('pointerover', (event) => {
                cursor.classList.toggle('is-interactive', Boolean(event.target.closest('a, button, [role="button"], input, textarea, select, summary')));
            });
            document.addEventListener('pointerdown', () => cursor.classList.add('is-pressed'));
            document.addEventListener('pointerup', () => cursor.classList.remove('is-pressed'));
            document.documentElement.addEventListener('mouseleave', () => cursor.classList.remove('is-visible'));
            document.documentElement.addEventListener('mouseenter', () => cursor.classList.add('is-visible'));
        }

        let pointerFrame;
        window.addEventListener('pointermove', (event) => {
            if (pointerFrame) cancelAnimationFrame(pointerFrame);
            pointerFrame = requestAnimationFrame(() => {
                document.documentElement.style.setProperty('--pointer-x', `${event.clientX}px`);
                document.documentElement.style.setProperty('--pointer-y', `${event.clientY}px`);
            });
        }, { passive: true });

        const reactiveCards = document.querySelectorAll(
            '.project-card, .blog-card, .skill-card, .certification-card, .stat-card, .interest-card, .value-card, .timeline-card'
        );

        reactiveCards.forEach((card) => {
            card.classList.add('mouse-reactive');
            card.addEventListener('pointermove', (event) => {
                const rect = card.getBoundingClientRect();
                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;
                const rotateX = ((y / rect.height) - 0.5) * -5;
                const rotateY = ((x / rect.width) - 0.5) * 5;
                card.style.setProperty('--card-x', `${x}px`);
                card.style.setProperty('--card-y', `${y}px`);
                card.style.setProperty('--card-rx', `${rotateX}deg`);
                card.style.setProperty('--card-ry', `${rotateY}deg`);
            }, { passive: true });
            card.addEventListener('pointerleave', () => {
                card.style.setProperty('--card-rx', '0deg');
                card.style.setProperty('--card-ry', '0deg');
            });
        });
    }

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
