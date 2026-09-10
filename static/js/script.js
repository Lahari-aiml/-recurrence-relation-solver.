/**
 * Recurrence Relation Solver - Client-Side Interactive Script
 */

document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initPresetCards();
    initMobileNav();
    initFormValidation();
    initPrintButton();
});

/**
 * Dark / Light Theme Toggle with LocalStorage persistence
 */
function initThemeToggle() {
    const toggleBtn = document.getElementById('themeToggleBtn');
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');

    // Retrieve saved theme or default to light
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        });
    }

    function setTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
            if (themeIcon) themeIcon.textContent = '☀️';
            if (themeText) themeText.textContent = 'Light Mode';
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            if (themeIcon) themeIcon.textContent = '🌙';
            if (themeText) themeText.textContent = 'Dark Mode';
            localStorage.setItem('theme', 'light');
        }
    }
}

/**
 * Automatically populates input fields when an example preset card is clicked.
 */
function initPresetCards() {
    const presetCards = document.querySelectorAll('.preset-card');
    const recInput = document.getElementById('recurrence');
    const baseInput = document.getElementById('base_case');

    presetCards.forEach(card => {
        card.addEventListener('click', () => {
            const formula = card.getAttribute('data-formula');
            const baseCase = card.getAttribute('data-base') || 'T(1) = 1';

            if (recInput && formula) {
                recInput.value = formula;
            }
            if (baseInput) {
                baseInput.value = baseCase;
            }

            // Smooth focus & scroll to input
            recInput.focus();
            recInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
    });
}

/**
 * Mobile navigation hamburger menu toggle
 */
function initMobileNav() {
    const navToggle = document.getElementById('mobileNavToggle');
    const navLinks = document.getElementById('navLinks');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('show');
        });
    }
}

/**
 * Form submission validation
 */
function initFormValidation() {
    const solverForm = document.getElementById('solverForm');
    const recInput = document.getElementById('recurrence');
    const errorMsg = document.getElementById('formClientError');

    if (solverForm && recInput) {
        solverForm.addEventListener('submit', (e) => {
            if (!recInput.value.strip ? !recInput.value.trim() : recInput.value === '') {
                e.preventDefault();
                if (errorMsg) {
                    errorMsg.textContent = 'Please enter a recurrence relation before submitting.';
                    errorMsg.style.display = 'block';
                } else {
                    alert('Please enter a recurrence relation.');
                }
                recInput.focus();
            } else {
                if (errorMsg) errorMsg.style.display = 'none';
            }
        });
    }
}

/**
 * Solution print action button
 */
function initPrintButton() {
    const printBtn = document.getElementById('printSolutionBtn');
    if (printBtn) {
        printBtn.addEventListener('click', () => {
            window.print();
        });
    }
}
