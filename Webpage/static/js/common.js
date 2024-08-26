document.addEventListener('DOMContentLoaded', () => {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const floatingNavButton = document.createElement('button');

    floatingNavButton.innerHTML = '☰';
    floatingNavButton.classList.add('floating-nav-button');
    document.body.appendChild(floatingNavButton);

    floatingNavButton.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });

    navToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        navToggle.classList.toggle('active');
    });

    // Close the nav menu when a link is clicked (for mobile view)
    document.querySelectorAll('.floating-nav a').forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
            navToggle.classList.remove('active');
        });
    });
});
