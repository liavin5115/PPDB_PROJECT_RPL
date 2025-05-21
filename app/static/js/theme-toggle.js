document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    const currentTheme = localStorage.getItem('theme');
    
    // Set initial theme
    function setTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        updateThemeIcon(theme === 'dark');
        
        // Trigger DataTables redraw if exists
        if (typeof $.fn !== 'undefined' && $.fn.dataTable) {
            $('.dataTable').DataTable().draw();
        }
    }
    
    // Initialize theme
    if (currentTheme) {
        setTheme(currentTheme);
    } else {
        const isDark = prefersDarkScheme.matches;
        setTheme(isDark ? 'dark' : 'light');
    }
    
    // Theme toggle handler
    themeToggle.addEventListener('click', function() {
        const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
        const newTheme = isDark ? 'light' : 'dark';
        
        localStorage.setItem('theme', newTheme);
        setTheme(newTheme);
    });

    // Listen for system theme changes
    prefersDarkScheme.addEventListener('change', function(e) {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });

    // Update icon based on theme
    function updateThemeIcon(isDark) {
        const icon = themeToggle.querySelector('i');
        if (isDark) {
            icon.classList.remove('bi-sun-fill');
            icon.classList.add('bi-moon-fill');
            icon.setAttribute('title', 'Switch to Light Mode');
        } else {
            icon.classList.remove('bi-moon-fill');
            icon.classList.add('bi-sun-fill');
            icon.setAttribute('title', 'Switch to Dark Mode');
        }
    }
});
