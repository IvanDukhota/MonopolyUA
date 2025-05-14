const burgerBtn = document.querySelector('.burger-btn');
const sidebar = document.querySelector('.sidebar');
const closeBtn2 = document.querySelector('.close-btn');
const overlay = document.querySelector('.overlay');

burgerBtn.addEventListener('click', () => {
    sidebar.classList.add('open');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
});

closeBtn2.addEventListener('click', () => {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
});

document.querySelectorAll('.options-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const notification = e.target.closest('.notification-item');
        notification.classList.toggle('show-options');
    });
});

document.addEventListener('click', (e) => {
    document.querySelectorAll('.notification-item').forEach(notification => {
        if (!notification.contains(e.target)) {
            notification.classList.remove('show-options');
        }
    });
});



document.addEventListener('DOMContentLoaded', function () {
    const createBtn = document.getElementById('lobbyCreateBtn');
    const deleteBtn = document.getElementById('lobbyDeleteBtn');
    const lobbyBlock = document.querySelector('.game-create-lobby');
    const playersSelect = document.getElementById('playersAmount');
    const regionSelect = document.getElementById('regionPick');
    const lobbyNameInput = document.getElementById('lobbyNameInput');
    const lobbyMid = document.querySelector('.game-create-lobby-mid');
    const lobbyNameHeader = document.getElementById('lobbyNameHeader');
    const closedLobbySelector = document.getElementById('closedLobby');



    function validateForm() {
        const missing = [];

        if (!lobbyNameInput.value.trim()) {
            lobbyNameInput.style.border = '1px solid red';
            missing.push('Назва');
        } else {
            lobbyNameInput.style.border = '';
        }

        if (regionSelect.value === 'empty') {
            regionSelect.style.border = '1px solid red';
            missing.push('Регіон');
        } else {
            regionSelect.style.border = '';
        }

        if (playersSelect.value === 'empty') {
            playersSelect.style.border = '1px solid red';
            missing.push('Кількість гравців');
        } else {
            playersSelect.style.border = '';
        }

        if (missing.length > 0) {
            alert(`⚠️ Заповніть поля: (${missing.join(', ')})`);
            return false;
        }

        return true;
    }

    createBtn.addEventListener('click', () => {
        if (!validateForm()) return;

        lobbyNameHeader.textContent = lobbyNameInput.value.trim();
        lobbyBlock.style.opacity = '1';
        lobbyBlock.style.pointerEvents = 'auto';

        createBtn.disabled = true;
        createBtn.style.opacity = '0.5';
        createBtn.style.cursor = 'not-allowed';

        playersSelect.disabled = true;
        playersSelect.style.opacity = '0.5';
        playersSelect.style.cursor = 'not-allowed';

        regionSelect.disabled = true;
        regionSelect.style.opacity = '0.5';
        regionSelect.style.cursor = 'not-allowed';

        lobbyNameInput.disabled = true;
        lobbyNameInput.style.opacity = '0.5';
        lobbyNameInput.style.cursor = 'not-allowed';

        startSearchBtn.disabled = true;
        startSearchBtn.style.opacity = '0.5';
        startSearchBtn.style.cursor = 'not-allowed';

        closedLobbySelector.disabled = true;
        closedLobbySelector.style.opacity = '0.5';
        closedLobbySelector.style.cursor = 'not-allowed';
    });

    deleteBtn.addEventListener('click', () => {
        const confirmed = confirm('Ви впевнені, що хочете закрити лоббі?');
        if (confirmed) {
            lobbyBlock.style.opacity = '0';
            lobbyBlock.style.pointerEvents = 'none';

            createBtn.disabled = false;
            createBtn.style.opacity = '1';
            createBtn.style.cursor = 'pointer';

            playersSelect.disabled = false;
            playersSelect.style.opacity = '1';
            playersSelect.style.cursor = 'pointer';

            regionSelect.disabled = false;
            regionSelect.style.opacity = '1';
            regionSelect.style.cursor = 'pointer';

            lobbyNameInput.disabled = false;
            lobbyNameInput.style.opacity = '1';
            lobbyNameInput.style.cursor = 'pointer';

            startSearchBtn.disabled = false;
            startSearchBtn.style.opacity = '1';
            startSearchBtn.style.cursor = 'pointer';

            closedLobbySelector.disabled = false;
            closedLobbySelector.style.opacity = '1';
            closedLobbySelector.style.cursor = 'pointer';
        }
    });

    playersSelect.addEventListener('change', () => {
        const amount = parseInt(playersSelect.value);
        lobbyMid.innerHTML = '';

        if (!isNaN(amount) && amount >= 2 && amount <= 4) {
            for (let i = 0; i < amount; i++) {
                const userBox = document.createElement('div');
                userBox.classList.add('user-box');
                lobbyMid.appendChild(userBox);
            }
        }
    });

    const startSearchBtn = document.getElementById('startRatingGameSearch');
    const stopSearchBtn = document.getElementById('stopSearchGame');
    const searchContainer = document.querySelector('.rating-game-search');
    const timerDisplay = document.getElementById('searchTimer');

    let timerInterval;
    let secondsElapsed = 0;

    function formatTime(sec) {
        const minutes = Math.floor(sec / 60).toString().padStart(2, '0');
        const seconds = (sec % 60).toString().padStart(2, '0');
        return `${minutes}:${seconds}`;
    }

    function startTimer() {
        secondsElapsed = 0;
        timerDisplay.textContent = formatTime(secondsElapsed);
        timerInterval = setInterval(() => {
            secondsElapsed++;
            timerDisplay.textContent = formatTime(secondsElapsed);
        }, 1000);
    }

    function stopTimer() {
        clearInterval(timerInterval);
    }

    startSearchBtn.addEventListener('click', () => {
        searchContainer.style.opacity = '1';
        searchContainer.style.pointerEvents = 'auto';
        startTimer();

        startSearchBtn.disabled = true;
        startSearchBtn.style.opacity = '0.5';
        startSearchBtn.style.cursor = 'not-allowed';

        createBtn.disabled = true;
        createBtn.style.opacity = '0.5';
        createBtn.style.cursor = 'not-allowed';

        playersSelect.disabled = true;
        playersSelect.style.opacity = '0.5';
        playersSelect.style.cursor = 'not-allowed';

        regionSelect.disabled = true;
        regionSelect.style.opacity = '0.5';
        regionSelect.style.cursor = 'not-allowed';

        lobbyNameInput.disabled = true;
        lobbyNameInput.style.opacity = '0.5';
        lobbyNameInput.style.cursor = 'not-allowed';

        closedLobbySelector.disabled = true;
        closedLobbySelector.style.opacity = '0.5';
        closedLobbySelector.style.cursor = 'not-allowed';
    });

    stopSearchBtn.addEventListener('click', () => {
        const confirmed = confirm('Ви впевнені, що хочете припинити пошук?');
        if (confirmed) {
            searchContainer.style.opacity = '0';
            searchContainer.style.pointerEvents = 'none';
            stopTimer();

            startSearchBtn.disabled = false;
            startSearchBtn.style.opacity = '1';
            startSearchBtn.style.cursor = 'pointer';

            createBtn.disabled = false;
            createBtn.style.opacity = '1';
            createBtn.style.cursor = 'pointer';

            playersSelect.disabled = false;
            playersSelect.style.opacity = '1';
            playersSelect.style.cursor = 'pointer';

            regionSelect.disabled = false;
            regionSelect.style.opacity = '1';
            regionSelect.style.cursor = 'pointer';

            lobbyNameInput.disabled = false;
            lobbyNameInput.style.opacity = '1';
            lobbyNameInput.style.cursor = 'pointer';

            closedLobbySelector.disabled = false;
            closedLobbySelector.style.opacity = '1';
            closedLobbySelector.style.cursor = 'pointer';
        }
    });

});

