

const content_dir = 'contents/'
const config_file = 'config.yml'
const section_names = ['home', 'news', 'experience', 'publications', 'awards', 'friends']


window.addEventListener('DOMContentLoaded', event => {

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


    // Yaml
    fetch(content_dir + config_file)
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


    // Marked — load all sections, then typeset math ONCE (not per-section)
    marked.use({ mangle: false, headerIds: false })
    Promise.all(section_names.map(name =>
        fetch(content_dir + name + '.md')
            .then(response => response.text())
            .then(markdown => {
                const el = document.getElementById(name + '-md');
                if (el) el.innerHTML = marked.parse(markdown);
            })
            .catch(error => console.log(error))
    )).then(() => {
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
