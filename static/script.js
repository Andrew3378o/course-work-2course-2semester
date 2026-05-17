(function() {
    const style = document.createElement('style');
    style.id = 'js-initial-hide';
    style.innerHTML = 'body { opacity: 0 !important; }';
    document.head.appendChild(style);

    const savedTheme = localStorage.getItem('theme');
    const savedWidth = localStorage.getItem('width');
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark-theme');
        const d = {'--bg-color':'#0d1117','--text-color':'#c9d1d9','--text-muted':'#8b949e','--border-color':'#30363d','--card-bg':'#161b22','--nav-bg':'#161b22'};
        for(let k in d) document.documentElement.style.setProperty(k, d[k]);
    }
    if (savedWidth === 'wide') {
        document.documentElement.classList.add('wide-layout');
        document.documentElement.style.setProperty('--container-width', '95%');
    } else {
        document.documentElement.classList.remove('wide-layout');
        document.documentElement.style.setProperty('--container-width', '1200px');
    }
})();

window.addEventListener('pageshow', (e) => {
    if (e.persisted) {
        document.body.style.opacity = '1';
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const initialHide = document.getElementById('js-initial-hide');
    if (initialHide) initialHide.remove();

    document.body.style.opacity = '0';
    animateStyle(document.body, 'opacity', 0, 1, 300);

    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            const target = this.getAttribute('target');
            if (href && !href.startsWith('#') && !href.startsWith('javascript') && target !== '_blank' && this.hostname === window.location.hostname) {
                if (this.classList.contains('category-main-link') && window.innerWidth <= 1000) {
                    const wrapper = this.closest('.category-item-wrapper');
                    const dropdown = wrapper ? wrapper.querySelector('.subcategories-dropdown') : null;
                    if (dropdown && dropdown.style.display !== 'block') {
                        return;
                    }
                }
                e.preventDefault();
                animateStyle(document.body, 'opacity', 1, 0, 250);
                setTimeout(() => { window.location.href = href; }, 250);
            }
        });
    });

    function lerp(start, end, amt) { return (1 - amt) * start + amt * end; }

    function animateVariables(startColors, endColors, duration) {
        let startTime = null;
        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            const progress = Math.min((timestamp - startTime) / duration, 1);
            for (const key in startColors) {
                const s = startColors[key];
                const e = endColors[key];
                const r = Math.round(lerp(s[0], e[0], progress));
                const g = Math.round(lerp(s[1], e[1], progress));
                const b = Math.round(lerp(s[2], e[2], progress));
                document.documentElement.style.setProperty(key, `rgb(${r}, ${g}, ${b})`);
            }
            if (progress < 1) window.requestAnimationFrame(step);
        }
        window.requestAnimationFrame(step);
    }

    function animateStyle(element, property, start, end, duration) {
        let startTime = null;
        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            const progress = Math.min((timestamp - startTime) / duration, 1);
            const current = start + (end - start) * progress;
            if (property === 'opacity') {
                element.style.opacity = current;
            } else if (property === 'translateY') {
                element.style.transform = `translateY(${current}px)`;
            }
            if (progress < 1) window.requestAnimationFrame(step);
        }
        window.requestAnimationFrame(step);
    }

    const lightThemeVars = {
        '--bg-color': [246, 248, 250], '--text-color': [36, 41, 47], '--text-muted': [87, 96, 106],
        '--border-color': [208, 215, 222], '--card-bg': [255, 255, 255], '--nav-bg': [255, 255, 255]
    };
    const darkThemeVars = {
        '--bg-color': [13, 17, 23], '--text-color': [201, 209, 217], '--text-muted': [139, 148, 158],
        '--border-color': [48, 54, 61], '--card-bg': [22, 27, 34], '--nav-bg': [22, 27, 34]
    };

    const savedTheme = localStorage.getItem('theme');
    const savedWidth = localStorage.getItem('width');
    const themeDarkRadio = document.getElementById('theme-dark');
    const themeLightRadio = document.getElementById('theme-light');
    if (themeDarkRadio && themeLightRadio) {
        if (savedTheme === 'dark') themeDarkRadio.checked = true;
        else themeLightRadio.checked = true;
    }

    const widthWideRadio = document.getElementById('width-wide');
    const widthStandardRadio = document.getElementById('width-standard');
    if (widthWideRadio && widthStandardRadio) {
        if (savedWidth === 'wide') widthWideRadio.checked = true;
        else widthStandardRadio.checked = true;
    }

    const cards = document.querySelectorAll('.article-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            animateStyle(card, 'translateY', 0, -3, 150);
            card.style.boxShadow = 'var(--shadow-md)';
        });
        card.addEventListener('mouseleave', () => {
            animateStyle(card, 'translateY', -3, 0, 150);
            card.style.boxShadow = 'none';
        });
    });

    const links = document.querySelectorAll('.nav-link, a:not(.btn-new-article):not(.category-main-link):not(.subcategory-link), .tag-badge');
    links.forEach(link => {
        if(!link.closest('.article-card') && link.className !== 'nav-logo' && !link.classList.contains('logout-btn') && !link.classList.contains('btn-danger-text')) {
            const isNavLink = link.classList.contains('nav-link');
            link.addEventListener('mouseenter', () => {
                if(isNavLink) {
                    link.style.backgroundColor = 'var(--bg-color)';
                    link.style.color = 'var(--primary-color)';
                } else { link.style.textDecoration = 'underline'; }
            });
            link.addEventListener('mouseleave', () => {
                if(isNavLink) {
                    link.style.backgroundColor = 'transparent';
                    link.style.color = 'var(--nav-text)';
                } else { link.style.textDecoration = 'none'; }
            });
        }
    });

    const mobileCatToggle = document.getElementById('mobile-cat-toggle');
    const categoriesList = document.getElementById('categories-list');
    if (mobileCatToggle && categoriesList) {
        mobileCatToggle.addEventListener('click', () => {
            categoriesList.classList.toggle('mobile-open');
            if (categoriesList.classList.contains('mobile-open')) {
                mobileCatToggle.innerHTML = 'Hide &#9652;';
                animateStyle(categoriesList, 'opacity', 0, 1, 200);
            } else {
                mobileCatToggle.innerHTML = 'Show &#9662;';
            }
        });
    }

    const categoryWrappers = document.querySelectorAll('.category-item-wrapper');
    categoryWrappers.forEach(wrapper => {
        const dropdown = wrapper.querySelector('.subcategories-dropdown');
        const mainLink = wrapper.querySelector('.category-main-link');
        
        if(dropdown) {
            wrapper.addEventListener('mouseenter', () => {
                if (window.innerWidth > 1000) {
                    dropdown.style.display = 'block';
                    animateStyle(dropdown, 'opacity', 0, 1, 150);
                    animateStyle(dropdown, 'translateY', -5, 0, 150);
                }
            });
            
            wrapper.addEventListener('mouseleave', () => {
                if (window.innerWidth > 1000) {
                    animateStyle(dropdown, 'opacity', 1, 0, 150);
                    animateStyle(dropdown, 'translateY', 0, -5, 150);
                    setTimeout(() => { dropdown.style.display = 'none'; }, 150);
                }
            });

            if (mainLink) {
                mainLink.addEventListener('click', (e) => {
                    if (window.innerWidth <= 1000) {
                        if (dropdown.style.display !== 'block') {
                            e.preventDefault();
                            document.querySelectorAll('.subcategories-dropdown').forEach(d => {
                                if (d !== dropdown) {
                                    d.style.opacity = 0;
                                    d.style.display = 'none';
                                }
                            });
                            dropdown.style.display = 'block';
                            animateStyle(dropdown, 'opacity', 0, 1, 150);
                            animateStyle(dropdown, 'translateY', -5, 0, 150);
                        }
                    }
                });
            }
        }
    });

    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('nav-menu');
    const spans = hamburger ? hamburger.querySelectorAll('span') : [];
    let menuOpen = false;

    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 1000) {
            if (!e.target.closest('.category-item-wrapper')) {
                document.querySelectorAll('.subcategories-dropdown').forEach(dropdown => {
                    if (dropdown.style.display === 'block') {
                        animateStyle(dropdown, 'opacity', 1, 0, 150);
                        animateStyle(dropdown, 'translateY', 0, -5, 150);
                        setTimeout(() => { dropdown.style.display = 'none'; }, 150);
                    }
                });
            }
        }
        
        if (menuOpen && hamburger && navMenu) {
            if (!e.target.closest('#nav-menu') && !e.target.closest('#hamburger')) {
                menuOpen = false;
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
                animateStyle(navMenu, 'opacity', 1, 0, 200);
                setTimeout(() => { navMenu.style.display = 'none'; }, 200);
            }
        }
    });

    const buttons = document.querySelectorAll('button:not(.hamburger):not(.search-btn):not(.tool-btn):not(.btn-danger-text):not(.btn-danger-full):not(.auth-tab):not(.mobile-cat-toggle), .btn-new-article');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', () => { btn.style.backgroundColor = 'var(--primary-hover)'; });
        btn.addEventListener('mouseleave', () => { btn.style.backgroundColor = 'var(--primary-color)'; });
    });

    const dangerButtons = document.querySelectorAll('.btn-danger-text, .btn-danger-full');
    dangerButtons.forEach(btn => {
        btn.addEventListener('mouseenter', () => { btn.style.textDecoration = 'underline'; });
        btn.addEventListener('mouseleave', () => { btn.style.textDecoration = 'none'; });
    });

    const toolBtns = document.querySelectorAll('.tool-btn');
    toolBtns.forEach(btn => {
        btn.addEventListener('mouseenter', () => { 
            btn.style.backgroundColor = 'var(--bg-color)'; 
            btn.style.borderColor = 'var(--primary-color)'; 
        });
        btn.addEventListener('mouseleave', () => { 
            btn.style.backgroundColor = 'var(--card-bg)';
            btn.style.borderColor = 'var(--border-color)'; 
            if(document.documentElement.classList.contains('dark-theme')){
                btn.style.backgroundColor = '#21262d';
                btn.style.borderColor = '#30363d';
            }
        });
    });

    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            menuOpen = !menuOpen;
            if (menuOpen) {
                spans[0].style.transform = 'translateY(8px) rotate(45deg)';
                spans[1].style.opacity = '0';
                spans[2].style.transform = 'translateY(-8px) rotate(-45deg)';
                navMenu.style.display = 'flex';
                animateStyle(navMenu, 'opacity', 0, 1, 200);
            } else {
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
                animateStyle(navMenu, 'opacity', 1, 0, 200);
                setTimeout(() => { navMenu.style.display = 'none'; }, 200);
            }
        });
    }

    const appearanceToggle = document.getElementById('appearance-toggle');
    const appearancePanel = document.getElementById('appearance-panel');
    let panelOpen = false;

    if (appearanceToggle && appearancePanel) {
        appearancePanel.style.overflow = 'hidden';
        appearanceToggle.addEventListener('click', (e) => {
            e.preventDefault();
            panelOpen = !panelOpen;
            if (panelOpen) {
                appearancePanel.style.display = 'block';
                const targetHeight = appearancePanel.scrollHeight;
                appearancePanel.style.height = '0px';
                appearancePanel.style.opacity = '0';
                
                let startTime = null;
                function slideDown(timestamp) {
                    if (!startTime) startTime = timestamp;
                    const progress = Math.min((timestamp - startTime) / 200, 1);
                    appearancePanel.style.height = `${progress * targetHeight}px`;
                    appearancePanel.style.opacity = progress;
                    if (progress < 1) window.requestAnimationFrame(slideDown);
                    else appearancePanel.style.height = 'auto';
                }
                window.requestAnimationFrame(slideDown);
            } else {
                const startHeight = appearancePanel.scrollHeight;
                appearancePanel.style.height = `${startHeight}px`;
                
                let startTime = null;
                function slideUp(timestamp) {
                    if (!startTime) startTime = timestamp;
                    const progress = Math.min((timestamp - startTime) / 200, 1);
                    appearancePanel.style.height = `${startHeight - (progress * startHeight)}px`;
                    appearancePanel.style.opacity = 1 - progress;
                    if (progress < 1) window.requestAnimationFrame(slideUp);
                    else {
                        appearancePanel.style.display = 'none';
                        appearancePanel.style.height = 'auto';
                    }
                }
                window.requestAnimationFrame(slideUp);
            }
        });
    }

    const themeRadios = document.querySelectorAll('input[name="theme"]');
    themeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'dark') {
                document.documentElement.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark');
                animateVariables(lightThemeVars, darkThemeVars, 250);
            } else {
                document.documentElement.classList.remove('dark-theme');
                localStorage.setItem('theme', 'light');
                animateVariables(darkThemeVars, lightThemeVars, 250);
            }
        });
    });

    const widthRadios = document.querySelectorAll('input[name="width"]');
    widthRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const container = document.querySelector('.container');
            const navContainer = document.querySelector('.nav-container');
            
            animateStyle(container, 'opacity', 1, 0, 250);
            if (navContainer) animateStyle(navContainer, 'opacity', 1, 0, 250);
            
            setTimeout(() => {
                if (e.target.value === 'wide') {
                    localStorage.setItem('width', 'wide');
                    document.documentElement.classList.add('wide-layout');
                    document.documentElement.style.setProperty('--container-width', '95%');
                } else {
                    localStorage.setItem('width', 'standard');
                    document.documentElement.classList.remove('wide-layout');
                    document.documentElement.style.setProperty('--container-width', '1200px');
                }
                animateStyle(container, 'opacity', 0, 1, 300);
                if (navContainer) animateStyle(navContainer, 'opacity', 0, 1, 300);
            }, 260);
        });
    });

    const editor = document.getElementById('editor');
    const preview = document.getElementById('preview');
    const imgUpload = document.getElementById('img-upload');
    
    if (editor && preview) {
        let timer;
        function updatePreview() {
            fetch('/api/preview', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content: editor.value})
            }).then(res => res.json()).then(data => { preview.innerHTML = data.html; });
        }
        updatePreview();
        editor.addEventListener('input', () => {
            clearTimeout(timer);
            timer = setTimeout(updatePreview, 300);
        });

        function insertText(before, after) {
            const start = editor.selectionStart;
            const end = editor.selectionEnd;
            const text = editor.value;
            const selected = text.substring(start, end);
            editor.value = text.substring(0, start) + before + selected + after + text.substring(end);
            editor.focus();
            editor.setSelectionRange(start + before.length, start + before.length + selected.length);
            updatePreview();
        }

        function insertLineStart(prefix) {
            const start = editor.selectionStart;
            const text = editor.value;
            const lineStart = text.lastIndexOf('\n', start - 1) + 1;
            editor.value = text.substring(0, lineStart) + prefix + text.substring(lineStart);
            editor.focus();
            editor.setSelectionRange(start + prefix.length, start + prefix.length);
            updatePreview();
        }

        function uploadImage(input) {
            if (!input.files || !input.files[0]) return;
            const formData = new FormData();
            formData.append('file', input.files[0]);
            fetch('/api/upload_image', { method: 'POST', body: formData })
            .then(res => res.json()).then(data => {
                if (data.url) { insertText('\n![Image](' + data.url + ')\n', ''); }
                input.value = '';
            });
        }

        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = btn.getAttribute('data-action');
                if (action === 'h1') insertLineStart('# ');
                else if (action === 'h2') insertLineStart('## ');
                else if (action === 'h3') insertLineStart('### ');
                else if (action === 'bold') insertText('**', '**');
                else if (action === 'italic') insertText('*', '*');
                else if (action === 'list') insertLineStart('- ');
                else if (action === 'numlist') insertLineStart('1. ');
                else if (action === 'wiki') insertText('[[', ']]');
                else if (action === 'link') insertText('[', '](url)');
                else if (action === 'image') imgUpload.click();
            });
        });

        if (imgUpload) imgUpload.addEventListener('change', function() { uploadImage(this); });
    }
});