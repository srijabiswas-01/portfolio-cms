(() => {
    const form = document.getElementById('adminLoginForm');
    if (!form) return;
    const button = form.querySelector('[type="submit"]');
    const error = document.getElementById('loginRequestError');
    let pending = false;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (pending) return;
        pending = true;
        button.disabled = true;
        error.hidden = true;
        try {
            // A login in another tab can rotate the cookie after this form was opened.
            const response = await fetch(form.dataset.csrfUrl, {
                credentials: 'same-origin', cache: 'no-store',
                headers: { Accept: 'application/json' },
            });
            if (!response.ok) throw new Error('Token refresh failed');
            const data = await response.json();
            if (typeof data.csrfToken !== 'string' || !/^[a-zA-Z0-9]{64}$/.test(data.csrfToken)) {
                throw new Error('Invalid token response');
            }
            form.querySelector('[name="csrfmiddlewaretoken"]').value = data.csrfToken;
            HTMLFormElement.prototype.submit.call(form);
        } catch {
            error.textContent = 'Unable to connect. Please try signing in again.';
            error.hidden = false;
            pending = false;
            button.disabled = false;
        }
    });

    window.addEventListener('pageshow', () => {
        pending = false;
        button.disabled = false;
    });
})();
