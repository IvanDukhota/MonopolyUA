const seasonPlayers = [
  { rank: 1, name: "PlayerOne", games: 120, wins: 80, winrate: "66%", points: 3500 },
  { rank: 2, name: "PlayerTwo", games: 90, wins: 50, winrate: "55%", points: 2000 },
  { rank: 3, name: "PlayerThree", games: 75, wins: 45, winrate: "60%", points: 1800 },
  { rank: 4, name: "PlayerFour", games: 80, wins: 60, winrate: "75%", points: 2500 },
  { rank: 5, name: "PlayerFive", games: 100, wins: 70, winrate: "70%", points: 3000 },
  { rank: 6, name: "PlayerSix", games: 100, wins: 70, winrate: "70%", points: 3000 },
  { rank: 7, name: "PlayerSeven", games: 100, wins: 70, winrate: "70%", points: 3000 },
  { rank: 8, name: "PlayerEight", games: 100, wins: 70, winrate: "70%", points: 3000 },
  { rank: 9, name: "PlayerNine", games: 100, wins: 70, winrate: "70%", points: 3000 },
  { rank: 10, name: "PlayerTen", games: 100, wins: 70, winrate: "70%", points: 3000 },
  { rank: 11, name: "PlayerEleven", games: 100, wins: 70, winrate: "70%", points: 3000 },
  { rank: 12, name: "PlayerTwelve", games: 100, wins: 70, winrate: "70%", points: 3000 },
];

const allTimePlayers = [
  { rank: 1, name: "LegendaryJoe", games: 500, wins: 300, winrate: "60%", points: 9000 },
  { rank: 2, name: "OldMaster", games: 450, wins: 250, winrate: "55%", points: 7500 },
  { rank: 3, name: "StarPlayer", games: 400, wins: 200, winrate: "50%", points: 6500 },
  { rank: 4, name: "PlayerOne", games: 120, wins: 80, winrate: "66%", points: 3500 },
  { rank: 5, name: "PlayerTwo", games: 100, wins: 50, winrate: "50%", points: 2000 },
  { rank: 6, name: "PlayerSix", games: 100, wins: 70, winrate: "70%", points: 3000 },
  { rank: 7, name: "PlayerSeven", games: 100, wins: 70, winrate: "70%", points: 3000 },
  { rank: 8, name: "PlayerEight", games: 100, wins: 70, winrate: "70%", points: 3000 },
  { rank: 9, name: "PlayerNine", games: 100, wins: 70, winrate: "70%", points: 3000 },
  { rank: 10, name: "PlayerTen", games: 100, wins: 70, winrate: "70%", points: 3000 },
  { rank: 11, name: "PlayerEleven", games: 100, wins: 70, winrate: "70%", points: 3000 },
  { rank: 12, name: "PlayerTwelve", games: 100, wins: 70, winrate: "70%", points: 3000 },
];

function renderPlayers(players, page = 1, playersPerPage = 10, modalId) {
  const startIdx = (page - 1) * playersPerPage;
  const endIdx = startIdx + playersPerPage;
  const paginatedPlayers = players.slice(startIdx, endIdx);
  const tbody = document.querySelector(`#${modalId} .top-players-table tbody`);
  tbody.innerHTML = "";

  paginatedPlayers.forEach(player => {
    const tr = document.createElement("tr");
    tr.classList.add("fade-in");
    tr.innerHTML = `
      <td>${player.rank}</td>
      <td>${player.name}</td>
      <td>${player.games}</td>
      <td>${player.wins}</td>
      <td>${player.winrate}</td>
      <td>${player.points}</td>
    `;
    tbody.appendChild(tr);
  });

  updatePagination(players.length, page, playersPerPage, modalId);
}



function updatePagination(totalPlayers, currentPage, playersPerPage, modalId) {
  const paginationContainer = document.querySelector(`#${modalId} .table-pagination`);
  const totalPages = Math.ceil(totalPlayers / playersPerPage);

  paginationContainer.innerHTML = "";
  for (let i = 1; i <= totalPages; i++) {
    const span = document.createElement("span");
    span.classList.add("page-num");
    if (i === currentPage) span.classList.add("active");
    span.textContent = i;
    span.addEventListener("click", () => {
      renderPlayers(seasonPlayers, i, 10, modalId);
    });
    paginationContainer.appendChild(span);
  }
}

const seasonTopBtn = document.getElementById('seasonTopBtn');
const closeSeasonModal = document.getElementById('closeSeasonModal');
const seasonModal = document.getElementById('seasonModal');

seasonTopBtn.addEventListener('click', () => {
  seasonModal.style.display = 'block';
  renderPlayers(seasonPlayers, 1, 10, 'seasonModal');
});

closeSeasonModal.addEventListener('click', () => {
  seasonModal.style.display = 'none';
});

const allTimeTopBtn = document.getElementById('allTimeTopBtn');
const closeAllTimeModal = document.getElementById('closeAllTimeModal');
const allTimeModal = document.getElementById('allTimeModal');

allTimeTopBtn.addEventListener('click', () => {
  allTimeModal.style.display = 'block';
  renderPlayers(allTimePlayers, 1, 10, 'allTimeModal');
});

closeAllTimeModal.addEventListener('click', () => {
  allTimeModal.style.display = 'none';
});


function renderPlayersInTable(players, tableId, limit = 10) {
  const tbody = document.querySelector(`#${tableId} tbody`);
  tbody.innerHTML = "";

  const playersToRender = players.slice(0, limit);

  playersToRender.forEach(player => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${player.rank}</td>
      <td>${player.name}</td>
      <td>${player.games}</td>
      <td>${player.wins}</td>
      <td>${player.winrate}</td>
      <td>${player.points}</td>
    `;
    tbody.appendChild(tr);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  renderPlayersInTable(seasonPlayers, "seasonTopTable", 10);
  renderPlayersInTable(allTimePlayers, "allTimeTopTable", 10);
});


const showVideoBtn = document.getElementById('showVideoBtn');
const videoContainer = document.getElementById('videoContainer');
const videoElement = document.getElementById('monopolyVideo');

let isVideoVisible = false;

showVideoBtn.addEventListener('click', () => {
  isVideoVisible = !isVideoVisible;
  videoContainer.classList.toggle('collapsed');

  if (isVideoVisible) {
    showVideoBtn.textContent = 'Hide video';
  } else {
    videoElement.pause();
    videoElement.currentTime = 0;
    showVideoBtn.textContent = 'Show video guide';
  }
});


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



