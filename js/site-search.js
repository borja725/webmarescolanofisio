/*
 * Site search
 * -----------
 * Client-side search for a static site with no build step and no backend.
 *
 * The whole feature is self-contained: this file injects its own styles and
 * its own markup into the navigation bar. Adding it to a page only requires
 * a single <script> tag, and removing it only requires deleting that tag.
 *
 * To add a new destination, append an entry to INDEX below.
 */
(function () {
    'use strict';

    /* ------------------------------------------------------------------
     * Search index
     *
     * url      site-root-relative path of the destination
     * title    label shown in the results list
     * keywords alternative terms a visitor may type; accents are ignored,
     *          so "ecografia" already matches "Ecografía"
     * ------------------------------------------------------------------ */
    var INDEX = [
        {
            url: 'index.html',
            title: 'Inicio',
            keywords: ['inicio', 'home', 'principal', 'portada', 'mar escolano', 'fisioterapia gandia', 'clinica']
        },
        {
            url: 'conocenos.html',
            title: 'Conócenos',
            keywords: ['conocenos', 'sobre nosotros', 'quienes somos', 'equipo', 'historia', 'mar escolano']
        },
        {
            url: 'servicios.html',
            title: 'Servicios',
            keywords: ['servicios', 'prestaciones', 'que hacemos', 'especialidades']
        },
        {
            url: 'servicios/fisioterapia.html',
            title: 'Fisioterapia',
            keywords: ['fisioterapia', 'fisio', 'terapia', 'fisioterapeuta']
        },
        {
            url: 'servicios/rehabilitacion.html',
            title: 'Rehabilitación',
            keywords: ['rehabilitacion', 'rehab', 'recuperacion', 'lesion', 'lesiones', 'postoperatorio']
        },
        {
            url: 'servicios/entrenamientos.html',
            title: 'Entrenamientos',
            keywords: ['entrenamiento', 'entrenamientos', 'entreno', 'ejercicio', 'ejercicios', 'readaptacion', 'ejercicio terapeutico']
        },
        {
            url: 'servicios/nutricion.html',
            title: 'Nutrición',
            keywords: ['nutricion', 'dieta', 'alimentacion', 'nutricionista', 'dietista', 'peso']
        },
        {
            url: 'servicios/psicologia.html',
            title: 'Psicología',
            keywords: ['psicologia', 'psicologo', 'psicologa', 'salud mental', 'ansiedad', 'terapia psicologica']
        },
        {
            url: 'tratamientos.html',
            title: 'Tratamientos',
            keywords: ['tratamientos', 'tecnicas', 'terapias', 'todos los tratamientos']
        },
        {
            url: 'tratamientos/ecografia.html',
            title: 'Ecografía',
            keywords: ['ecografia', 'ecografo', 'ecografia musculoesqueletica', 'ultrasonido', 'ultrasonidos', 'ecoguiada', 'ecoguiado', 'imagen', 'diagnostico por imagen']
        },
        {
            url: 'tratamientos/diatermia.html',
            title: 'Diatermia',
            keywords: ['diatermia', 'tecarterapia', 'tecar', 'radiofrecuencia', 'corrientes', 'calor profundo']
        },
        {
            url: 'tratamientos/puncion-seca.html',
            title: 'Punción seca',
            keywords: ['puncion seca', 'puncion', 'aguja', 'agujas', 'punto gatillo', 'puntos gatillo', 'contractura', 'contracturas', 'dry needling']
        },
        {
            url: 'tratamientos/electro-puncion.html',
            title: 'Electropunción',
            keywords: ['electropuncion', 'electro puncion', 'electroterapia', 'epi', 'electrolisis', 'tendinopatia']
        },
        {
            url: 'tratamientos/presoterapia.html',
            title: 'Presoterapia',
            keywords: ['presoterapia', 'drenaje', 'drenaje linfatico', 'circulacion', 'piernas cansadas', 'retencion de liquidos']
        },
        {
            url: 'atm.html',
            title: 'ATM',
            keywords: ['atm', 'mandibula', 'mandibular', 'articulacion temporomandibular', 'bruxismo', 'dolor de mandibula', 'chasquido']
        },
        {
            url: 'tratamientos/atm.html',
            title: 'ATM (tratamiento)',
            keywords: ['atm tratamiento', 'tratamiento atm', 'mandibula tratamiento']
        },
        {
            url: 'tratamientos/terapia-manual.html',
            title: 'Terapia manual',
            keywords: ['terapia manual', 'manual', 'masaje', 'movilizacion', 'manos', 'osteopatia']
        },
        {
            url: 'tratamientos/ganchos.html',
            title: 'Ganchos',
            keywords: ['ganchos', 'ganchoterapia', 'fibrolisis', 'fibrolisis diacutanea', 'diacutanea', 'adherencias']
        },
        {
            url: 'tratamientos/manipulaciones-vertebrales.html',
            title: 'Manipulaciones vertebrales',
            keywords: ['manipulaciones', 'manipulacion', 'vertebral', 'vertebrales', 'columna', 'espalda', 'cervicales', 'cervical', 'lumbar', 'lumbares', 'dorsal', 'quiropraxia']
        },
        {
            url: 'instalaciones.html',
            title: 'Instalaciones',
            keywords: ['instalaciones', 'clinica', 'centro', 'sala', 'gimnasio', 'fotos', 'como es la clinica']
        },
        {
            url: 'contacto.html',
            title: 'Contacto',
            keywords: ['contacto', 'cita', 'coger cita', 'pedir cita', 'reservar', 'telefono', 'email', 'correo', 'direccion', 'horario', 'horarios', 'donde estamos', 'como llegar', 'ubicacion']
        }
    ];

    var MAX_RESULTS = 6;

    /* ------------------------------------------------------------------
     * Resolve the site root from this script's own URL.
     *
     * Pages reference the file as "js/", "./js/" or "../js/" depending on
     * their depth, but the browser resolves src to an absolute URL, so
     * stripping the known suffix always yields the site root.
     * ------------------------------------------------------------------ */
    function siteRoot() {
        var el = document.currentScript;

        if (!el) {
            var all = document.getElementsByTagName('script');
            for (var i = all.length - 1; i >= 0; i--) {
                if (all[i].src && all[i].src.indexOf('site-search.js') > -1) {
                    el = all[i];
                    break;
                }
            }
        }

        return el ? el.src.replace(/js\/site-search\.js(\?.*)?$/, '') : '';
    }

    var ROOT = siteRoot();

    /* ------------------------------------------------------------------
     * Text normalisation: lowercase, strip accents, drop punctuation.
     * Lets "Ecografía", "ecografia" and "ECOGRAFIA" all match each other.
     *
     * Unicode combining diacritical marks (U+0300-U+036F) are matched via
     * escape sequences rather than literal characters, so the pattern does
     * not depend on how this file is encoded on disk. Stripping them has to
     * happen before punctuation is removed: NFD splits "í" into "i" plus a
     * combining accent, and the punctuation rule would otherwise turn that
     * accent into a space and break the word in two.
     * ------------------------------------------------------------------ */
    var COMBINING_MARKS = new RegExp('[\\u0300-\\u036F]', 'g');

    function normalize(value) {
        return String(value)
            .toLowerCase()
            .normalize('NFD')
            .replace(COMBINING_MARKS, '')
            .replace(/[^a-z0-9\s]/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
    }

    // Precompute the normalised forms once, at load time.
    INDEX.forEach(function (entry) {
        entry.nTitle = normalize(entry.title);
        entry.nKeywords = entry.keywords.map(normalize);
    });

    /*
     * Score a single entry against a normalised query.
     * Higher is better; 0 means "no match".
     */
    function scoreTerm(entry, term) {
        if (!term) {
            return 0;
        }

        if (entry.nTitle === term) {
            return 100;
        }
        if (entry.nTitle.indexOf(term) === 0) {
            return 80;
        }

        var best = 0;

        for (var i = 0; i < entry.nKeywords.length; i++) {
            var keyword = entry.nKeywords[i];

            if (keyword === term) {
                best = Math.max(best, 70);
            } else if (keyword.indexOf(term) === 0) {
                best = Math.max(best, 55);
            } else if (keyword.indexOf(term) > -1) {
                best = Math.max(best, 35);
            }
        }

        if (entry.nTitle.indexOf(term) > -1) {
            best = Math.max(best, 50);
        }

        return best;
    }

    function search(rawQuery) {
        var query = normalize(rawQuery);

        if (!query) {
            return [];
        }

        var terms = query.split(' ');

        return INDEX
            .map(function (entry) {
                // Score the full query first: "puncion seca" should beat the
                // average of "puncion" and "seca" scored separately.
                var value = scoreTerm(entry, query);

                if (!value && terms.length > 1) {
                    var total = 0;
                    var matched = 0;

                    terms.forEach(function (term) {
                        var termScore = scoreTerm(entry, term);
                        if (termScore) {
                            total += termScore;
                            matched++;
                        }
                    });

                    // Require every term to match so unrelated pages do not
                    // surface on a single incidental word.
                    value = matched === terms.length ? total / terms.length : 0;
                }

                return { entry: entry, score: value };
            })
            .filter(function (hit) {
                return hit.score > 0;
            })
            .sort(function (a, b) {
                return b.score - a.score;
            })
            .slice(0, MAX_RESULTS)
            .map(function (hit) {
                return hit.entry;
            });
    }

    /* ------------------------------------------------------------------
     * Styles
     *
     * The navbar is transparent over the hero image and turns white once
     * the page scrolls, so the field keeps a solid white background and a
     * visible border in order to stay readable in both states.
     * ------------------------------------------------------------------ */
    var CSS = [
        '.site-search{position:relative;display:flex;align-items:center;margin-left:14px}',
        // bootsnav ships `.navbar-nav > li{position:inherit}` so its dropdowns can
        // span the full navbar. That selector outranks a bare `.site-search`, which
        // would leave this item static and anchor the results panel to the navbar
        // container instead of the field. Match its specificity to win it back.
        '.navbar-nav > li.site-search{position:relative}',
        '.site-search__form{position:relative;display:flex;align-items:center;height:34px;padding:0}',
        // The field paints no background of its own so the hero image shows
        // through, and it takes the navbar's own text colour instead of a fixed
        // one. `line-height` stays at `normal` on purpose: an explicit value
        // taller than the content box (height minus the two borders) lifts the
        // placeholder off the magnifier's centre line.
        // `margin:0` is load-bearing, not tidiness. The theme gives every input a
        // bottom margin for stacked forms; inside this centred flex wrapper that
        // margin counts as part of the item's outer box, so the field gets pushed
        // half of it upwards and the placeholder drifts off the magnifier's line.
        // 140px leaves a little slack in the navbar row so the item never sits
        // right on the wrapping threshold.
        '.site-search__input{width:140px;height:34px;margin:0;padding:0 32px 0 14px;',
        'border:1px solid rgba(35,35,35,.35);border-radius:17px;background:transparent;',
        'color:#232323;font-size:12px;font-weight:600;line-height:normal;outline:none;',
        'transition:border-color .25s ease;-webkit-appearance:none;appearance:none}',
        '.site-search__input::-webkit-search-cancel-button{-webkit-appearance:none}',
        '.site-search__input::placeholder{color:#232323;opacity:.7}',
        // The width must not change on focus. `.navbar-nav` is a flex row with
        // `flex-wrap: wrap` and the items already fill it almost exactly, so
        // widening the field on focus overflows the row and drops the search
        // box onto a second line. Focus is signalled with the border instead.
        '.site-search__input:focus{border-color:rgba(35,35,35,.85)}',
        '.site-search__icon{position:absolute;right:13px;top:50%;transform:translateY(-50%);',
        'color:#232323;opacity:.7;font-size:12px;pointer-events:none}',
        // bootsnav marks the light-over-photo navbar with `.white-link` (the home
        // page) and leaves it off everywhere else. Mirroring that flag is what
        // keeps the field readable on both, instead of white-on-white.
        '.white-link .site-search__input{color:#fff;border-color:rgba(255,255,255,.55)}',
        '.white-link .site-search__input::placeholder{color:#fff;opacity:.8}',
        '.white-link .site-search__input:focus{border-color:#fff}',
        '.white-link .site-search__icon{color:#fff;opacity:.9}',
        '.site-search__results{position:absolute;top:calc(100% + 8px);left:0;z-index:1050;',
        'min-width:250px;max-height:320px;overflow-y:auto;margin:0;padding:6px 0;list-style:none;',
        'background:#fff;border:1px solid #e4e4e4;border-radius:6px;box-shadow:0 8px 24px rgba(0,0,0,.14);',
        'display:none;text-align:left}',
        '.site-search__results.is-open{display:block}',
        '.site-search__results li{margin:0;padding:0;border:0}',
        '.site-search__results a{display:block;padding:9px 16px;color:#232323;font-size:12px;',
        'line-height:1.4;text-transform:none;text-decoration:none;white-space:nowrap;',
        'overflow:hidden;text-overflow:ellipsis}',
        '.site-search__results a:hover,.site-search__results li.is-active a{background:#f4f4f4;color:#000}',
        '.site-search__empty{padding:9px 16px;color:#9a9a9a;font-size:12px}',
        // Inside the collapsed mobile menu the field spans the full width.
        '@media (max-width:991px){',
        '.site-search{margin:8px 0 4px;padding:0 15px;width:100%}',
        '.site-search__form{width:100%}',
        '.site-search__input,.site-search__input:focus{width:100%}',
        '.site-search__results{left:15px;right:15px;min-width:0}',
        '}'
    ].join('');

    function injectStyles() {
        var style = document.createElement('style');
        style.setAttribute('data-site-search', '');
        style.appendChild(document.createTextNode(CSS));
        document.head.appendChild(style);
    }

    /* ------------------------------------------------------------------
     * Markup
     * ------------------------------------------------------------------ */
    function buildWidget() {
        var item = document.createElement('li');
        item.className = 'site-search';

        item.innerHTML =
            '<div class="site-search__form" role="search">' +
                '<input type="search" class="site-search__input" placeholder="Buscar..."' +
                    ' aria-label="Buscar en la web" autocomplete="off" role="combobox"' +
                    ' aria-expanded="false" aria-controls="site-search-results">' +
                '<i class="fas fa-search site-search__icon" aria-hidden="true"></i>' +
            '</div>' +
            '<ul class="site-search__results" id="site-search-results" role="listbox"></ul>';

        return item;
    }

    function init() {
        // The Contacto item is the last one in the main menu, so the search
        // field is appended right after it.
        var menu = document.querySelector('.navbar-nav');

        if (!menu || menu.querySelector('.site-search')) {
            return;
        }

        injectStyles();

        var widget = buildWidget();
        menu.appendChild(widget);

        var input = widget.querySelector('.site-search__input');
        var list = widget.querySelector('.site-search__results');
        var current = [];
        var activeIndex = -1;

        function close() {
            list.classList.remove('is-open');
            input.setAttribute('aria-expanded', 'false');
            activeIndex = -1;
        }

        function highlight(index) {
            var items = list.querySelectorAll('li');

            for (var i = 0; i < items.length; i++) {
                items[i].classList.toggle('is-active', i === index);
            }

            activeIndex = index;
        }

        function go(entry) {
            window.location.href = ROOT + entry.url;
        }

        function render(results) {
            list.innerHTML = '';
            activeIndex = -1;

            if (!results.length) {
                var empty = document.createElement('li');
                empty.className = 'site-search__empty';
                empty.textContent = 'Sin resultados';
                list.appendChild(empty);
            } else {
                results.forEach(function (entry, index) {
                    var li = document.createElement('li');
                    var link = document.createElement('a');

                    link.href = ROOT + entry.url;
                    link.textContent = entry.title;
                    link.setAttribute('role', 'option');

                    link.addEventListener('mouseenter', function () {
                        highlight(index);
                    });

                    li.appendChild(link);
                    list.appendChild(li);
                });
            }

            list.classList.add('is-open');
            input.setAttribute('aria-expanded', 'true');
        }

        input.addEventListener('input', function () {
            var value = input.value.trim();

            if (!value) {
                close();
                current = [];
                return;
            }

            current = search(value);
            render(current);
        });

        input.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                close();
                input.blur();
                return;
            }

            if (!current.length) {
                return;
            }

            if (event.key === 'ArrowDown') {
                event.preventDefault();
                highlight((activeIndex + 1) % current.length);
            } else if (event.key === 'ArrowUp') {
                event.preventDefault();
                highlight(activeIndex <= 0 ? current.length - 1 : activeIndex - 1);
            } else if (event.key === 'Enter') {
                event.preventDefault();
                go(current[activeIndex > -1 ? activeIndex : 0]);
            }
        });

        input.addEventListener('focus', function () {
            if (current.length) {
                list.classList.add('is-open');
                input.setAttribute('aria-expanded', 'true');
            }
        });

        document.addEventListener('click', function (event) {
            if (!widget.contains(event.target)) {
                close();
            }
        });

        // Bootsnav binds its own handlers to the menu; keep clicks inside the
        // field from bubbling up and toggling the mobile navigation.
        widget.addEventListener('click', function (event) {
            event.stopPropagation();
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}());
