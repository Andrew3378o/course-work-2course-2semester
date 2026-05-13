document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('nav-menu');
    const themeToggle = document.getElementById('theme-toggle');

    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        document.querySelectorAll('.nav-link').forEach(n => {
            if(n.id !== 'theme-toggle') {
                n.addEventListener('click', () => {
                    hamburger.classList.remove('active');
                    navMenu.classList.remove('active');
                });
            }
        });
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', (e) => {
            e.preventDefault();
            document.body.classList.toggle('dark-theme');
            if (document.body.classList.contains('dark-theme')) {
                localStorage.setItem('theme', 'dark');
            } else {
                localStorage.setItem('theme', 'light');
            }
        });
    }

    const editor = document.getElementById('editor');
    const preview = document.getElementById('preview');
    
    if (editor && preview) {
        let timer;
        
        function updatePreview() {
            fetch('/api/preview', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content: editor.value})
            }).then(res => res.json()).then(data => {
                preview.innerHTML = data.html;
            });
        }

        updatePreview();

        editor.addEventListener('input', () => {
            clearTimeout(timer);
            timer = setTimeout(updatePreview, 300);
        });

        window.insertText = function(before, after) {
            const start = editor.selectionStart;
            const end = editor.selectionEnd;
            const text = editor.value;
            const selected = text.substring(start, end);
            editor.value = text.substring(0, start) + before + selected + after + text.substring(end);
            editor.focus();
            editor.setSelectionRange(start + before.length, start + before.length + selected.length);
            updatePreview();
        };

        window.insertLineStart = function(prefix) {
            const start = editor.selectionStart;
            const text = editor.value;
            const lineStart = text.lastIndexOf('\n', start - 1) + 1;
            editor.value = text.substring(0, lineStart) + prefix + text.substring(lineStart);
            editor.focus();
            editor.setSelectionRange(start + prefix.length, start + prefix.length);
            updatePreview();
        };

        window.uploadImage = function(input) {
            if (!input.files || !input.files[0]) return;
            const formData = new FormData();
            formData.append('file', input.files[0]);
            fetch('/api/upload_image', {
                method: 'POST',
                body: formData
            }).then(res => res.json()).then(data => {
                if (data.url) {
                    insertText('\n![Image](' + data.url + ')\n', '');
                }
                input.value = '';
            });
        };
    }
});