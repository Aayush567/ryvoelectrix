// Intersection Observer for scroll animations
document.addEventListener("DOMContentLoaded", () => {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Initial load animations
    setTimeout(() => {
        document.querySelectorAll('.fade-up, .fade-in').forEach(el => {
            if (el.getBoundingClientRect().top < window.innerHeight) {
                el.classList.add('visible');
            } else {
                observer.observe(el);
            }
        });
    }, 100);

    // Make Navbar slightly opaque on scroll
    const nav = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.style.background = 'rgba(11, 15, 25, 0.95)';
            nav.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.5)';
        } else {
            nav.style.background = 'rgba(11, 15, 25, 0.8)';
            nav.style.boxShadow = 'none';
        }
    });

    // Slider Logic
    const slides = document.querySelectorAll('.slide');
    if (slides.length > 0) {
        let currentSlide = 0;
        const dotsContainer = document.querySelector('.slider-dots');

        slides.forEach((_, idx) => {
            let dot = document.createElement('div');
            dot.classList.add('dot');
            if (idx === 0) dot.classList.add('active');
            dot.addEventListener('click', () => goToSlide(idx));
            dotsContainer.appendChild(dot);
        });
        const dots = document.querySelectorAll('.dot');

        function goToSlide(n) {
            dots.forEach(d => d.classList.remove('active'));
            slides.forEach(s => s.classList.remove('active'));
            currentSlide = (n + slides.length) % slides.length;
            document.querySelector('.slides-container').style.transform = `translateX(-${currentSlide * 100}%)`;
            dots[currentSlide].classList.add('active');
            slides[currentSlide].classList.add('active');
        }

        document.getElementById('nextSlide')?.addEventListener('click', () => goToSlide(currentSlide + 1));
        document.getElementById('prevSlide')?.addEventListener('click', () => goToSlide(currentSlide - 1));

        setInterval(() => {
            goToSlide(currentSlide + 1);
        }, 5000);
    }

    // Stats Counter Animation
    const statNumbers = document.querySelectorAll('.stat-number[data-target]');
    if (statNumbers.length > 0) {
        const statsObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    const target = parseInt(el.getAttribute('data-target'));
                    const duration = 2000;
                    const step = target / (duration / 16);
                    let current = 0;
                    const timer = setInterval(() => {
                        current += step;
                        if (current >= target) {
                            el.textContent = target.toLocaleString();
                            clearInterval(timer);
                        } else {
                            el.textContent = Math.floor(current).toLocaleString();
                        }
                    }, 16);
                    statsObserver.unobserve(el);
                }
            });
        }, { threshold: 0.5 });
        statNumbers.forEach(el => statsObserver.observe(el));
    }

    // Mobile Menu Toggle Logic
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            const icon = navToggle.querySelector('i');
            if (navLinks.classList.contains('active')) {
                icon.setAttribute('data-lucide', 'x');
            } else {
                icon.setAttribute('data-lucide', 'menu');
            }
            if (window.lucide) window.lucide.createIcons();
        });

        // Close menu when clicking links
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                const icon = navToggle.querySelector('i');
                icon.setAttribute('data-lucide', 'menu');
                if (window.lucide) window.lucide.createIcons();
            });
        });
    }
});

function openTestRideModal(modelValue) {
    const modal = document.getElementById('testRideModal');
    if (modal) {
        modal.style.display = 'block';
        if (modelValue) {
            const selectField = document.getElementById('modalModelSelect');
            if (selectField) selectField.value = modelValue;
        }
    }
}

function showToast(message, isError = false) {
    let toast = document.getElementById('customToast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'customToast';
        toast.className = 'toast-notification';
        document.body.appendChild(toast);
    }

    const icon = isError ? 'alert-circle' : 'check-circle';
    const color = isError ? '#ff4757' : 'var(--primary)';
    toast.style.borderLeftColor = color;

    toast.innerHTML = `
        <div class="toast-icon" style="color: ${color}; background: ${isError ? 'rgba(255,71,87,0.1)' : 'rgba(0,240,255,0.1)'}">
            <i data-lucide="${icon}"></i>
        </div>
        <div style="display:flex; flex-direction:column; gap:4px; text-align:left;">
            <strong style="font-size:1.1rem; color:white;">${isError ? 'Error!' : 'Success!'}</strong>
            <span style="color:var(--text-muted); font-size:0.95rem; line-height:1.4;">${message}</span>
        </div>
    `;

    if (window.lucide) window.lucide.createIcons();
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => toast.classList.remove('show'), 5000);
}

async function submitForm(event, queryType) {
    event.preventDefault();
    const form = event.target;
    const inputs = form.querySelectorAll('input, select, textarea');
    let payload = {};

    inputs.forEach(el => {
        let labelNode = el.previousElementSibling;
        let label = labelNode ? labelNode.innerText.replace(' (Optional)', '') : (el.placeholder || el.name || 'Field');
        if (el.value) payload[label] = el.value;
    });

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerText;
    submitBtn.innerText = "Sending...";
    submitBtn.disabled = true;

    try {
        const response = await fetch('/api/submit-query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: queryType, payload: payload })
        });
        if (response.ok) {
            showToast('Your details have been submitted. Our team will contact you shortly.');
            form.reset();
            const modal = document.getElementById('testRideModal');
            if (modal && modal.style.display === 'block') modal.style.display = 'none';
        } else {
            showToast('Failed to submit application. Server error.', true);
        }
    } catch (e) {
        showToast('Network error! Try refreshing the page.', true);
    } finally {
        submitBtn.innerText = originalText;
        submitBtn.disabled = false;
    }
}


