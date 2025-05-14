let currentSlide = 0;
const slides = document.querySelector('.slides');
const totalSlides = 6;
let slideInterval = startSlideInterval();

function startSlideInterval() {
  return setInterval(() => {
    moveSlide(1);
  }, 10000);
}

function moveSlide(step) {
  currentSlide = (currentSlide + step + totalSlides) % totalSlides;
  updateSlide();
}

function updateSlide() {
  slides.style.transform = `translateX(-${currentSlide * 100}%)`;
}

function nextSlide() {
  clearInterval(slideInterval);
  moveSlide(1);
  slideInterval = startSlideInterval();
}

function prevSlide() {
  clearInterval(slideInterval);
  moveSlide(-1);
  slideInterval = startSlideInterval();
}

document.querySelector('.next').addEventListener('click', nextSlide);
document.querySelector('.prev').addEventListener('click', prevSlide);


const watchBtn = document.querySelector('.watch-video-btn');
const closeBtn = document.querySelector('.close-video-btn');
const containerVideo = document.querySelector('.container-video');

watchBtn.addEventListener('click', () => {
  containerVideo.classList.add('active');

  setTimeout(() => {
    containerVideo.classList.add('show-video');
  }, 1000);
});

closeBtn.addEventListener('click', () => {
  containerVideo.classList.remove('show-video');

  setTimeout(() => {
    containerVideo.classList.remove('active');
  }, 300);
});



const seasonPlayers = [
  { name: 'Іван', games: 50, wins: 30, points: 1200 },
  { name: 'Олег', games: 45, wins: 27, points: 1100 },
  { name: 'Марія', games: 60, wins: 40, points: 1500 },
  { name: 'Андрій', games: 55, wins: 35, points: 1300 },
  { name: 'Катерина', games: 40, wins: 22, points: 950 },
  { name: 'Петро', games: 70, wins: 45, points: 1600 },
  { name: 'Оксана', games: 48, wins: 28, points: 1150 },
  { name: 'Юрій', games: 38, wins: 18, points: 850 },
  { name: 'Наталя', games: 52, wins: 30, points: 1250 },
  { name: 'Богдан', games: 47, wins: 25, points: 1000 },
  { name: 'Людмила', games: 36, wins: 20, points: 800 }
];

const allTimePlayers = [
  { name: 'Максим', games: 200, wins: 150, points: 5000 },
  { name: 'Олена', games: 180, wins: 120, points: 4500 },
  { name: 'Тарас', games: 220, wins: 160, points: 5300 },
  { name: 'Світлана', games: 210, wins: 140, points: 4900 },
  { name: 'Руслан', games: 190, wins: 130, points: 4700 },
  { name: 'Ірина', games: 170, wins: 110, points: 4300 },
  { name: 'Дмитро', games: 230, wins: 170, points: 5500 },
  { name: 'Ганна', games: 175, wins: 115, points: 4400 },
  { name: 'Степан', games: 160, wins: 100, points: 4000 },
  { name: 'Аліна', games: 185, wins: 125, points: 4600 },
  { name: 'Віктор', games: 195, wins: 135, points: 4800 }
];

function renderTable(players, tableId) {
  const tableBody = document.getElementById(tableId).querySelector('tbody');

  players.sort((a, b) => b.points - a.points);

  players.slice(0, 10).forEach((player, index) => {
    const winRate = player.games > 0 ? ((player.wins / player.games) * 100).toFixed(1) : '0';

    const row = `
        <tr>
          <td>${index + 1}</td>
          <td>${player.name}</td>
          <td>${player.games}</td>
          <td>${player.wins}</td>
          <td>${winRate}%</td>
          <td>${player.points}</td>
        </tr>
      `;
    tableBody.innerHTML += row;
  });
}

renderTable(seasonPlayers, 'season-table');
renderTable(allTimePlayers, 'alltime-table');


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

document.querySelector('.scroll-to-rules').addEventListener('click', function (e) {
  e.preventDefault();

  document.querySelector('.container-rules').scrollIntoView({
    behavior: 'smooth'
  });
});
