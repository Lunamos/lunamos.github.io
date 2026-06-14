

const content_dir = 'contents/'
const section_names = ['home', 'news', 'experience', 'publications', 'awards', 'friends']

function getSiteLang() {
    var params = new URLSearchParams(location.search);
    if (params.has('lang')) {
        var l = params.get('lang');
        if (l === 'cn' || l === 'en') { localStorage.setItem('site-lang', l); return l; }
    }
    return localStorage.getItem('site-lang') || 'en';
}

window.addEventListener('DOMContentLoaded', event => {

    const lang = getSiteLang();
    const langSuffix = lang === 'cn' ? '.cn' : '';

    // Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            offset: 74,
        });
    };

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

    // Language toggle
    var langBtn = document.getElementById('langToggle');
    if (langBtn) {
        langBtn.textContent = lang === 'cn' ? 'EN' : '中文';
        langBtn.addEventListener('click', function () {
            var next = lang === 'cn' ? 'en' : 'cn';
            localStorage.setItem('site-lang', next);
            location.reload();
        });
    }

    // Yaml config (language-aware)
    var configFile = lang === 'cn' ? 'config.cn.yml' : 'config.yml';
    fetch(content_dir + configFile)
        .then(response => response.text())
        .then(text => {
            const yml = jsyaml.load(text);
            Object.keys(yml).forEach(key => {
                try {
                    document.getElementById(key).innerHTML = yml[key];
                } catch {
                    console.log("Unknown id and value: " + key + "," + yml[key].toString())
                }

            })
        })
        .catch(error => console.log(error));


    // Marked — load all sections (with language fallback)
    marked.use({ mangle: false, headerIds: false })

    function loadSection(name) {
        return fetch(content_dir + name + langSuffix + '.md')
            .then(function (r) {
                if (!r.ok) throw new Error('not found');
                return r.text();
            })
            .catch(function () {
                if (langSuffix) {
                    return fetch(content_dir + name + '.md').then(function (r) { return r.text(); });
                }
                return '';
            })
            .then(function (markdown) {
                var el = document.getElementById(name + '-md');
                if (el && markdown) el.innerHTML = marked.parse(markdown);
            })
            .catch(function (error) { console.log(error); });
    }

    Promise.all(section_names.map(loadSection)).then(() => {
        // Progressive (blur-up) loading for any opt-in <img class="prog"> in content.
        if (window.ProgImg) window.ProgImg.enhance(document);
        // Typeset math a single time; wait for MathJax if it is still loading.
        const doTypeset = () => { try { MathJax.typeset(); } catch (e) { } };
        if (window.MathJax) {
            if (MathJax.startup && MathJax.startup.promise) {
                MathJax.startup.promise.then(doTypeset);
            } else if (typeof MathJax.typeset === 'function') {
                doTypeset();
            }
        }
    });

});
