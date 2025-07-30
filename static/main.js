document.addEventListener('DOMContentLoaded', () => {
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
