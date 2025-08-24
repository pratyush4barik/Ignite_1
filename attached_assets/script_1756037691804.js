// ------------------- Mobile navigation toggle -------------------
document.addEventListener('DOMContentLoaded', function () {
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('nav-menu');

    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function () {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });

        document.addEventListener('click', function (event) {
            const isClickInsideNav = navMenu.contains(event.target);
            const isClickOnHamburger = hamburger.contains(event.target);

            if (!isClickInsideNav && !isClickOnHamburger) {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            }
        });
    }
});

// ------------------- Smooth scrolling -------------------
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        if (this.id === "ai-assessment-btn") {
            e.preventDefault(); // prevent scroll for chatbot
            return;
        }

        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// ------------------- Navbar scroll effects -------------------
let lastScrollTop = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', function () {
    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    if (scrollTop > lastScrollTop) {
        navbar.style.top = '-100px';
        navbar.style.opacity = '0';
    } else {
        navbar.style.top = '20px';
        navbar.style.opacity = '1';
    }

    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
});

// ------------------- Animate elements on scroll -------------------
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', function () {
    const animatedElements = document.querySelectorAll('.department-card, .about-content');

    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// ------------------- View All Departments Toggle -------------------
document.addEventListener("DOMContentLoaded", function () {
    const viewAllBtn = document.getElementById("viewAllBtn");
    const hiddenCards = document.querySelectorAll(".department-card.hidden");

    viewAllBtn?.addEventListener("click", function () {
        hiddenCards.forEach(card => card.classList.remove("hidden"));
        viewAllBtn.style.display = "none";
    });
});

// ------------------- Button ripple effect -------------------
document.querySelectorAll('button').forEach(button => {
    button.addEventListener('click', function (e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(255, 255, 255, 0.3)';
        ripple.style.transform = 'scale(0)';
        ripple.style.animation = 'ripple 0.6s linear';
        ripple.style.pointerEvents = 'none';

        this.style.position = 'relative';
        this.style.overflow = 'hidden';
        this.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    });
});

// ------------------- Add ripple + chatbot CSS dynamically -------------------
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .hamburger.active .bar:nth-child(2) {
        opacity: 0;
    }
    .hamburger.active .bar:nth-child(1) {
        transform: translateY(8px) rotate(45deg);
    }
    .hamburger.active .bar:nth-child(3) {
        transform: translateY(-8px) rotate(-45deg);
    }

    #chatbot-modal {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }
    #chatbot-messages {
        background: rgba(255, 255, 255, 0.8);
        padding: 10px;
        border-radius: 8px;
        color: #000;
        max-height: 300px;
        overflow-y: auto;
    }
`;
document.head.appendChild(style);

// ------------------- CTA buttons -------------------
document.querySelector('.cta-button')?.addEventListener('click', function () {
    document.querySelector('#about')?.scrollIntoView({ behavior: 'smooth' });
});

document.querySelector('.read-more-btn')?.addEventListener('click', function () {
    alert('Read more functionality is not implemented in this demo.');
});

// ------------------- Loading animation -------------------
window.addEventListener('load', function () {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease';
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);
});

// ------------------- Chatbot Modal Handling -------------------
let chatHistory = [];

document.addEventListener("DOMContentLoaded", () => {
    const chatbotBtn = document.getElementById("ai-assessment-btn");
    const chatbotModal = document.getElementById("chatbot-modal");
    const closeChatbot = document.getElementById("close-chatbot");
    const userInput = document.getElementById("user-input");
    const messages = document.getElementById("chatbot-messages");
    const form = document.getElementById("chatbot-form");

    // Hide modal initially
    if (chatbotModal) chatbotModal.style.display = "none";

    const createMessage = (text, sender = "bot") => {
        const wrapper = document.createElement("div");
        wrapper.classList.add(sender === "user" ? "user-msg" : "bot-msg");

        if (sender === "bot") {
            const logo = document.createElement("img");
            logo.src = "healthbot-logo.png";
            logo.classList.add("msg-logo");
            wrapper.appendChild(logo);
        }

        const bubble = document.createElement("div");
        bubble.classList.add("msg-bubble");
        bubble.textContent = text;

        wrapper.appendChild(bubble);
        messages.appendChild(wrapper);
        messages.scrollTop = messages.scrollHeight;
    };

    const showTyping = () => {
        const typingDiv = document.createElement("div");
        typingDiv.classList.add("bot-msg", "typing");
        typingDiv.innerHTML = `
            <img src="healthbot-logo.png" class="msg-logo">
            <div class="typing-dots"><span></span><span></span><span></span></div>
        `;
        messages.appendChild(typingDiv);
        messages.scrollTop = messages.scrollHeight;
        return typingDiv;
    };

    // Greeting
    const greetUser = () => {
        chatbotModal.style.display = "flex";
        messages.innerHTML = "";
        chatHistory = [];
        createMessage("👋 Hello! I'm your AI Health Assistant. Please describe your health concern.");
    };

    chatbotBtn?.addEventListener("click", greetUser);

    closeChatbot?.addEventListener("click", () => {
        chatbotModal.style.display = "none";
        messages.innerHTML = "";
        userInput.value = "";
        chatHistory = [];
    });

    // Handle form submission
    form?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

        createMessage(text, "user");
        userInput.value = "";

        if (text.toLowerCase().includes("start new assessment")) {
            greetUser();
            return;
        }

        const typingDiv = showTyping();

        try {
            const res = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text, history: chatHistory })
            });

            const data = await res.json();
            typingDiv.remove();
            createMessage(data.response, "bot");

            chatHistory = data.history || chatHistory;
        } catch (err) {
            typingDiv.remove();
            createMessage("⚠️ Error connecting to the assistant.", "bot");
        }
    });

    // Quick reply buttons
    document.querySelectorAll('.quick-btn').forEach(button => {
        button.addEventListener('click', () => {
            const value = button.getAttribute('data-value');
            userInput.value = value;
            form.dispatchEvent(new Event('submit'));
        });
    });
});
