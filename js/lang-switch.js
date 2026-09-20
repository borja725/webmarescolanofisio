/*
 * Language switcher - tap and click support
 * -----------------------------------------
 * The dropdown already opens on :hover and :focus-within, which covers mouse
 * and keyboard and keeps working with JavaScript disabled. iOS Safari does
 * not reliably move focus to a bare <button> on tap, so on a phone the menu
 * could stay unreachable - and most of this clinic's traffic is mobile.
 *
 * This adds an explicit toggle on top of that CSS, never replacing it.
 */
(function () {
    'use strict';

    var OPEN = 'is-open';

    function init() {
        var boxes = document.querySelectorAll('.lang-switch');

        for (var i = 0; i < boxes.length; i++) {
            wire(boxes[i]);
        }

        // a tap or click anywhere else closes any open menu
        document.addEventListener('click', function (event) {
            for (var i = 0; i < boxes.length; i++) {
                if (!boxes[i].contains(event.target)) {
                    close(boxes[i]);
                }
            }
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' || event.keyCode === 27) {
                for (var i = 0; i < boxes.length; i++) {
                    close(boxes[i]);
                }
            }
        });
    }

    function wire(box) {
        var button = box.querySelector('.lang-switch__toggle');

        if (!button) {
            return;
        }

        button.setAttribute('aria-expanded', 'false');

        button.addEventListener('click', function (event) {
            event.preventDefault();
            event.stopPropagation();

            if (box.classList.contains(OPEN)) {
                close(box);
            } else {
                box.classList.add(OPEN);
                button.setAttribute('aria-expanded', 'true');
            }
        });
    }

    function close(box) {
        if (!box.classList.contains(OPEN)) {
            return;
        }

        box.classList.remove(OPEN);

        var button = box.querySelector('.lang-switch__toggle');

        if (button) {
            button.setAttribute('aria-expanded', 'false');
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}());
