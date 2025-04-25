const loginBtn = document.querySelector('.login-btn');
const sidebar = document.getElementById('sidebar');
const closeSidebar = document.getElementById('closeSidebar');

loginBtn.addEventListener('click', () => {
  if (sidebar.style.right === '0px') {
    sidebar.style.right = '-300px';
    document.body.classList.remove('sidebar-open');
  } else {
    sidebar.style.right = '0';
    document.body.classList.add('sidebar-open');
  }
});
closeSidebar.addEventListener('click', () => {
  sidebar.style.right = '-300px';
  document.body.classList.remove('sidebar-open');
});


let timerInterval;
let seconds = 0;
let minutes = 0;
let hours = 0;
let isRunning = false;

function startTimer() {
    if (isRunning) return; 

    isRunning = true;
    timerInterval = setInterval(updateTime, 1000);
}

function updateTime() {
    seconds++;
    if (seconds >= 60) {
        seconds = 0;
        minutes++;
    }
    if (minutes >= 60) {
        minutes = 0;
        hours++;
    }

    document.getElementById("timer").textContent = 
        formatTime(hours) + ":" + formatTime(minutes) + ":" + formatTime(seconds);
}

function formatTime(time) {
    return time < 10 ? "0" + time : time;
}





document.querySelector('.create-game-button button').addEventListener('click', function () {
  const lobbyName = document.querySelector('.create-input').value.trim();
  const squares = document.querySelectorAll('.player-square');
  const lobbyInfo = document.querySelector('.create-game-settings-result-info');
  const button = this;

  if (lobbyName !== '') {
    squares.forEach(square => {
      square.style.opacity = '1';
      square.style.visibility = 'visible';
    });

    lobbyInfo.style.opacity = '1';
    lobbyInfo.style.visibility = 'visible';

    button.textContent = 'GO';
  } else {
    alert('Please enter the name of the lobby!');
  }
});

document.querySelector('.create-game-settings-result-info button').addEventListener('click', function () {
  const confirmDelete = confirm("Are you sure you want to delete this lobby?");
  if (!confirmDelete) return;

  const squares = document.querySelectorAll('.player-square');
  const lobbyInfo = document.querySelector('.create-game-settings-result-info');
  const createButton = document.querySelector('.create-game-button button');

  squares.forEach(square => {
    square.style.opacity = '0';
    square.style.visibility = 'hidden';
  });
  lobbyInfo.style.opacity = '0';
  lobbyInfo.style.visibility = 'hidden';
  createButton.textContent = 'Create';
});

const friends = [
  "FriendOne", "FriendTwo", "FriendThree", "FriendFour", "FriendFive",
  "FriendSix", "FriendSeven", "FriendEight", "FriendNine", "FriendTen",
  "FriendEleven", "FriendTwelve", "FriendThirteen", "FriendFourteen",
  "FriendFifteen", "FriendSixteen"
];

const itemsPerPage = 8;
let currentPage = 1;
let selectedSquare = null;
let interactionStarted = false;

const modal = document.getElementById('friendsModal');
const friendsContainer = document.getElementById('friendsContainer');
const pagination = document.getElementById('pagination');
const createGameButton = document.querySelector('.create-game-button button');

let invitedPlayers = [];

function paginateFriends() {
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = currentPage * itemsPerPage;
  const friendsToDisplay = friends.slice(startIndex, endIndex);

  friendsContainer.innerHTML = '';

  friendsToDisplay.forEach(friend => {
    const friendItem = document.createElement('div');
    friendItem.className = 'friend-item';
    friendItem.innerHTML = `<span>${friend}</span><button class="invite-btn">Invite</button>`;

    friendItem.querySelector('button').addEventListener('click', () => {
      modal.style.display = 'none';
      if (selectedSquare) {
        if (invitedPlayers.includes(friend)) {
          alert(`${friend} has already been invited.`);
        } else {
          selectedSquare.textContent = friend;
          selectedSquare.setAttribute('data-invited', 'true');
          invitedPlayers.push(friend);
          alert(`Invitation sent to ${friend}`);
        }
      }
    });

    friendsContainer.appendChild(friendItem);
  });

  updatePagination();
}

function updatePagination() {
  const totalPages = Math.ceil(friends.length / itemsPerPage);
  pagination.innerHTML = '';

  for (let i = 1; i <= totalPages; i++) {
    const pageNum = document.createElement('span');
    pageNum.classList.add('page-num');
    if (i === currentPage) {
      pageNum.classList.add('active');
    }
    pageNum.textContent = i;
    pagination.appendChild(pageNum);

    pageNum.addEventListener('click', () => {
      currentPage = i;
      paginateFriends();
    });
  }
}

window.onload = () => {
  const squares = document.querySelectorAll('.player-square');
  
  squares.forEach(square => {
    square.addEventListener('click', () => {
      interactionStarted = true;
      if (square.classList.contains('disabled')) return;

      if (square.getAttribute('data-invited') === 'true') {
        const confirmKick = confirm('Kick this player?');
        if (confirmKick) {
          invitedPlayers = invitedPlayers.filter(player => player !== square.textContent);
          square.textContent = '';
          square.removeAttribute('data-invited');
        }
      } else {
        selectedSquare = square;
        modal.style.display = 'flex';
      }
    });
  });

  squaresInitialized = true; 
  paginateFriends();
};


window.addEventListener('click', function (e) {
  if (e.target === modal) {
    modal.style.display = 'none';
  }
});


createGameButton.addEventListener('click', () => {
  if (!interactionStarted) return; 

  if (invitedPlayers.length === 0) {
    alert('Invite at least one player!');
  } else {
    window.location.href = '../board/board.html';
  }
});




