/* Cookie consent banner for marescolanofisioterapia.com
 *
 * Works together with the Google Consent Mode v2 block that sits inline in the
 * <head> of every page. That inline block is what actually matters for
 * compliance: it denies analytics storage before gtag.js loads, so no analytics
 * cookie is written until the visitor says yes. This file only draws the
 * banner and flips the switch.
 *
 * It replaces a third-party widget that exposed no callback on acceptance and
 * relied on `beforescriptexecute`, a Firefox-only event.
 */
(function () {
    'use strict';

    var KEY = 'mef-cookie-consent';
    var GRANTED = 'granted';
    var DENIED = 'denied';

    var TEXTS = {
        es: {
            text: 'Usamos cookies necesarias para que la web funcione y cookies de analítica de ' +
                  'Google para saber qué contenidos resultan útiles. Las analíticas solo se ' +
                  'activan si las aceptas.',
            link: 'Política de cookies',
            href: '/politica-cookies.html',
            accept: 'Aceptar',
            reject: 'Rechazar',
            label: 'Aviso de cookies'
        },
        va: {
            text: 'Utilitzem galetes necessàries perquè la web funcione i galetes d\'analítica ' +
                  'de Google per a saber quins continguts resulten útils. Les analítiques només ' +
                  's\'activen si les acceptes.',
            link: 'Política de galetes',
            href: '/va/politica-cookies.html',
            accept: 'Acceptar',
            reject: 'Rebutjar',
            label: 'Avís de galetes'
        },
        en: {
            text: 'We use essential cookies to make the site work and Google analytics cookies to ' +
                  'understand which content is useful. Analytics are only enabled if you accept.',
            link: 'Cookie policy',
            href: '/en/politica-cookies.html',
            accept: 'Accept',
            reject: 'Reject',
            label: 'Cookie notice'
        }
    };

    /* The language comes from the URL, not from a stored preference: a link
       shared over WhatsApp must speak the language of whoever opens it. This
       matches how js/site-search.js already decides. */
    function currentLang() {
        var path = window.location.pathname;
        if (path.indexOf('/va/') === 0) { return 'va'; }
        if (path.indexOf('/en/') === 0) { return 'en'; }
        return 'es';
    }

    function read() {
        try {
            return window.localStorage.getItem(KEY);
        } catch (e) {
            /* Private browsing, blocked storage. Treat as "not decided yet". */
            return null;
        }
    }

    function write(value) {
        try {
            window.localStorage.setItem(KEY, value);
        } catch (e) {
            /* Nothing to do: the choice simply will not survive this session. */
        }
    }

    function applyConsent(value) {
        if (typeof window.gtag !== 'function') { return; }
        window.gtag('consent', 'update', {
            analytics_storage: value === GRANTED ? GRANTED : DENIED
        });
    }

    /* Deleting the cookies Google already wrote, in case consent is withdrawn
       after having been given. Without this, rejecting would leave the previous
       cookies in place and the rejection would be cosmetic. */
    function clearAnalyticsCookies() {
        var host = window.location.hostname;
        var domains = ['', host, '.' + host];
        var parts = host.split('.');
        if (parts.length > 2) { domains.push('.' + parts.slice(-2).join('.')); }

        document.cookie.split(';').forEach(function (raw) {
            var name = raw.split('=')[0].trim();
            if (name.indexOf('_ga') !== 0 && name.indexOf('_gid') !== 0) { return; }
            domains.forEach(function (domain) {
                document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/' +
                    (domain ? '; domain=' + domain : '');
            });
        });
    }

    var banner = null;

    function close() {
        if (banner) { banner.setAttribute('data-open', 'false'); }
    }

    function decide(value) {
        write(value);
        applyConsent(value);
        if (value === DENIED) { clearAnalyticsCookies(); }
        close();
    }

    function build(t) {
        var el = document.createElement('div');
        el.id = 'mef-cc';
        el.setAttribute('role', 'dialog');
        el.setAttribute('aria-live', 'polite');
        el.setAttribute('aria-label', t.label);

        var inner = document.createElement('div');
        inner.className = 'mef-cc__inner';

        var p = document.createElement('p');
        p.className = 'mef-cc__text';
        p.appendChild(document.createTextNode(t.text + ' '));
        var a = document.createElement('a');
        a.href = t.href;
        a.textContent = t.link;
        p.appendChild(a);
        p.appendChild(document.createTextNode('.'));

        var actions = document.createElement('div');
        actions.className = 'mef-cc__actions';

        /* Reject comes first in the DOM so keyboard and screen-reader users
           reach it at least as easily as accept. */
        var reject = document.createElement('button');
        reject.type = 'button';
        reject.className = 'mef-cc__btn';
        reject.textContent = t.reject;
        reject.addEventListener('click', function () { decide(DENIED); });

        var accept = document.createElement('button');
        accept.type = 'button';
        accept.className = 'mef-cc__btn';
        accept.textContent = t.accept;
        accept.addEventListener('click', function () { decide(GRANTED); });

        actions.appendChild(reject);
        actions.appendChild(accept);
        inner.appendChild(p);
        inner.appendChild(actions);
        el.appendChild(inner);
        return el;
    }

    function open() {
        if (!banner) {
            banner = build(TEXTS[currentLang()] || TEXTS.es);
            document.body.appendChild(banner);
        }
        banner.setAttribute('data-open', 'true');
    }

    function init() {
        var stored = read();

        /* A stored "granted" is already applied by the inline head block, so
           returning visitors are measured from the first page view. Re-applying
           here is harmless and covers the case where storage was readable only
           after the head ran. */
        if (stored === GRANTED || stored === DENIED) {
            applyConsent(stored);
        } else {
            open();
        }

        /* Anything marked data-cookie-settings reopens the banner. Used by the
           cookie policy pages, which promise the visitor can change their mind. */
        Array.prototype.forEach.call(
            document.querySelectorAll('[data-cookie-settings]'),
            function (trigger) {
                trigger.addEventListener('click', function (ev) {
                    ev.preventDefault();
                    open();
                });
            }
        );

        initMaps();
    }

    /* ---------------------------------------------------------------- map
       The embedded Google map is third-party content: loading it hands the
       visitor's IP to Google. It waits for an explicit click, deliberately not
       for the banner's accept button, since the banner only asks about
       analytics. */

    var MAP_TEXTS = {
        es: {
            text: 'El mapa lo proporciona Google. Al cargarlo, tu dirección IP y otros datos de ' +
                  'tu navegador se envían a sus servidores.',
            button: 'Ver el mapa',
            alt: 'O abrir la ubicación en Google Maps',
            title: 'Mapa de la clínica'
        },
        va: {
            text: 'El mapa el proporciona Google. En carregar-lo, la teua adreça IP i altres dades ' +
                  'del teu navegador s\'envien als seus servidors.',
            button: 'Veure el mapa',
            alt: 'O obrir la ubicació en Google Maps',
            title: 'Mapa de la clínica'
        },
        en: {
            text: 'The map is provided by Google. Loading it sends your IP address and other ' +
                  'browser data to their servers.',
            button: 'Show the map',
            alt: 'Or open the location in Google Maps',
            title: 'Clinic map'
        }
    };

    function loadMap(holder) {
        var frame = document.createElement('iframe');
        frame.src = holder.getAttribute('data-map-src');
        frame.width = '100%';
        frame.height = holder.getAttribute('data-map-height') || '450';
        frame.title = (MAP_TEXTS[currentLang()] || MAP_TEXTS.es).title;
        frame.style.border = '0';
        frame.setAttribute('allowfullscreen', '');
        frame.setAttribute('loading', 'lazy');
        frame.setAttribute('referrerpolicy', 'no-referrer-when-downgrade');
        holder.replaceWith(frame);
    }

    function initMaps() {
        var t = MAP_TEXTS[currentLang()] || MAP_TEXTS.es;

        Array.prototype.forEach.call(document.querySelectorAll('.mef-map'), function (holder) {
            var p = document.createElement('p');
            p.className = 'mef-map__text';
            p.textContent = t.text;

            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'mef-map__btn';
            btn.textContent = t.button;
            btn.addEventListener('click', function () { loadMap(holder); });

            var alt = document.createElement('p');
            alt.className = 'mef-map__alt';
            var link = document.createElement('a');
            link.href = holder.getAttribute('data-map-link') ||
                        'https://www.google.com/maps/search/?api=1&query=Mar+Escolano+Fisioterapia+Gandia';
            link.target = '_blank';
            link.rel = 'noopener';
            link.textContent = t.alt;
            alt.appendChild(link);

            holder.appendChild(p);
            holder.appendChild(btn);
            holder.appendChild(alt);
        });
    }

    window.MEFCookieConsent = { open: open, reset: function () { decide(DENIED); } };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}());
