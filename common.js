document.addEventListener('DOMContentLoaded', function () {

    let currentLang = 'ja'; 

    fetch('/header.html') 
        .then(response => response.ok ? response.text() : Promise.reject('File not found'))
        .then(data => {
            document.getElementById('header-placeholder').innerHTML = data;
            initializeHeaderScripts(); 
        })
        .catch(error => console.error('Error loading header:', error));

    fetch('/footer.html') 
        .then(response => response.ok ? response.text() : Promise.reject('File not found'))
        .then(data => {
            document.getElementById('footer-placeholder').innerHTML = data;
            updateLanguageDisplay();
        })
        .catch(error => console.error('Error loading footer:', error));

    function initializeHeaderScripts() {
        const hamburgerBtn = document.getElementById('hamburger-btn');
        const mainNav = document.getElementById('main-nav');
        const dropdowns = document.querySelectorAll('.navbar .dropdown'); 
        const langToggleBtn = document.getElementById('lang-toggle');
        const header = document.getElementById('header');

        if (hamburgerBtn && mainNav) {
            hamburgerBtn.addEventListener('click', function() {
                mainNav.classList.toggle('open');
            });
        }

        dropdowns.forEach(function (dropdown) {
            const submenu = dropdown.querySelector('ul');
            const triggerLinks = dropdown.querySelectorAll(':scope > a');

            triggerLinks.forEach(function(link) {
                link.addEventListener('click', function (event) {
                    if (this.getAttribute('href') === '#') {
                        event.preventDefault();
                        event.stopPropagation();
                        const isCurrentlyOpen = submenu.classList.contains('show');
                        closeOtherDropdowns(null);
                        if (!isCurrentlyOpen) {
                            submenu.classList.add('show');
                            triggerLinks.forEach(a => a.classList.add('submenu-open'));
                        }
                    }
                });
            });
            
            dropdown.addEventListener('mouseenter', function() {
                if (window.getComputedStyle(hamburgerBtn).display === 'none') {
                    const submenu = this.querySelector('ul');
                    if (submenu) {
                        closeOtherDropdowns(submenu);
                        submenu.classList.add('show');
                        this.querySelectorAll(':scope > a').forEach(a => a.classList.add('submenu-open'));
                    }
                }
            });

            dropdown.addEventListener('mouseleave', function() {
                if (window.getComputedStyle(hamburgerBtn).display === 'none') {
                    const submenu = this.querySelector('ul');
                    if (submenu) {
                        submenu.classList.remove('show');
                        this.querySelectorAll(':scope > a').forEach(a => a.classList.remove('submenu-open'));
                    }
                }
            });
        });

        if (langToggleBtn) {
            langToggleBtn.addEventListener('click', function () {
                currentLang = (currentLang === 'ja') ? 'en' : 'ja';
                updateLanguageDisplay(); 
                closeOtherDropdowns(null); 
            });
        }

        let lastScrollTop = 0;
        if (header) {
            window.addEventListener('scroll', function() {
                let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                if (scrollTop > lastScrollTop && scrollTop > header.offsetHeight){
                    header.classList.add('header-hidden');
                } else {
                    header.classList.remove('header-hidden');
                }
                lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
            }, false);
        }

        document.addEventListener('click', function (event) {
            if (mainNav && mainNav.classList.contains('open') && !mainNav.contains(event.target) && hamburgerBtn && !hamburgerBtn.contains(event.target)) {
                mainNav.classList.remove('open');
            }
            if (!event.target.closest('.navbar')) {
                closeOtherDropdowns(null);
            }
        });
        updateLanguageDisplay();
    }
    
    // --- 3. 共通のヘルパー関数 ---
    function closeOtherDropdowns(exceptThis) {
        document.querySelectorAll('.navbar .dropdown ul').forEach(function (submenu) {
            if (submenu !== exceptThis) {
                submenu.classList.remove('show');
                if (submenu.parentElement) {
                    submenu.parentElement.querySelectorAll(':scope > a').forEach(a => a.classList.remove('submenu-open'));
                }
            }
        });
    }

    function updateLanguageDisplay() {
        const langToggleBtn = document.getElementById('lang-toggle');
        if (langToggleBtn) {
            langToggleBtn.textContent = currentLang === 'ja' ? 'English' : '日本語';
        }
        document.querySelectorAll('.lang-ja').forEach(el => {
            el.style.display = currentLang === 'ja' ? '' : 'none';
        });
        document.querySelectorAll('.lang-en').forEach(el => {
            el.style.display = currentLang === 'en' ? '' : 'none';
        });
    }
});
