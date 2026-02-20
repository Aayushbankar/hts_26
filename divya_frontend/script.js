document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    lucide.createIcons();

    const startBtn = document.getElementById('start-btn');
    const landingPage = document.getElementById('landing-page');
    const chatPage = document.getElementById('chat-page');
    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');

    // Page Switching Logic
    startBtn.addEventListener('click', () => {
        landingPage.classList.remove('active');
        chatPage.classList.add('active');
    });

    // Basic Input Logic
    function handleSend() {
        if(userInput.value.trim() !== "") {
            console.log
            ("Message Encrypted & Sent: " + userInput.value);
            userInput.value = "";
        }
    }

    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });
});