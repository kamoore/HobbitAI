// This single script now handles all interactivity for the page.
// It runs after the DOM is fully loaded to prevent errors.
document.addEventListener('DOMContentLoaded', () => {

    // --- THEME TOGGLE LOGIC (Consolidated & Corrected) ---
    const themeToggleBtn = document.getElementById('theme-toggle');
    const darkIcon = document.getElementById('theme-toggle-dark-icon');
    const lightIcon = document.getElementById('theme-toggle-light-icon');
    const htmlEl = document.documentElement;

    const setAndApplyTheme = (theme) => {
        if (theme === 'light') {
            htmlEl.classList.remove('dark');
            localStorage.setItem('theme', 'light');
            darkIcon.classList.remove('hidden');
            lightIcon.classList.add('hidden');
        } else {
            // Default to dark
            htmlEl.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            darkIcon.classList.add('hidden');
            lightIcon.classList.remove('hidden');
        }
    };

    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = localStorage.getItem('theme') || 'dark';
        setAndApplyTheme(currentTheme === 'dark' ? 'light' : 'dark');
    });

    // Initial theme setup on page load
    const initialTheme = localStorage.getItem('theme') || 'dark';
    setAndApplyTheme(initialTheme);


    // --- FEATURE CARD TOGGLE ---
    const featuresGrid = document.getElementById('features-grid');
    if (featuresGrid) {
        featuresGrid.addEventListener('click', (e) => {
            const card = e.target.closest('.feature-card');
            if (card) {
                featuresGrid.querySelectorAll('.feature-card.active').forEach(activeCard => {
                    if (activeCard !== card) activeCard.classList.remove('active');
                });
                card.classList.toggle('active');
            }
        });
    }


    // --- CHAT SIMULATION ---
    const chatWindow = document.getElementById('chat-window');
    const simulateBtn = document.getElementById('simulate-command-btn');
    if (chatWindow && simulateBtn) {
        let isSimulating = false;
        const chatSteps = [
            { user: 'ModUser', text: '!aicmd add_memo SomeChatter their dog is named Sparky', userColor: 'text-orange-400' },
            { user: 'HobbitAI_Bot', text: '✅ Memo added for SomeChatter.', userColor: 'text-green-400' }
        ];

        const addLine = (line, delay) => new Promise(resolve => {
            setTimeout(() => {
                const lineEl = document.createElement('div');
                lineEl.className = 'chat-line-item';
                lineEl.innerHTML = `<span class="${line.userColor} font-bold">[${line.user}]</span>: ${line.text}`;
                chatWindow.appendChild(lineEl);
                setTimeout(() => lineEl.style.opacity = '1', 50);
                chatWindow.scrollTop = chatWindow.scrollHeight;
                resolve();
            }, delay);
        });

        simulateBtn.addEventListener('click', async () => {
            if (isSimulating) return;
            isSimulating = true;
            simulateBtn.disabled = true;
            simulateBtn.classList.add('opacity-50');
            chatWindow.innerHTML = '';
            await addLine(chatSteps[0], 100);
            await addLine(chatSteps[1], 600);
            isSimulating = false;
            simulateBtn.disabled = false;
            simulateBtn.classList.remove('opacity-50');
        });
    }
});
