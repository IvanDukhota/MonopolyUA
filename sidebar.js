document.addEventListener('DOMContentLoaded', () => {
  const burgerBtn = document.querySelector('.burger-btn');
  const sidebar = document.querySelector('.sidebar');
  const closeBtn = document.querySelector('.close-btn');
  const overlay = document.querySelector('.overlay');
  const logoutBtn = document.querySelector('.logout-btn'); 

  if (burgerBtn && sidebar && closeBtn && overlay) {
    burgerBtn.addEventListener('click', () => {
      sidebar.classList.add('open');
      overlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    });

    closeBtn.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('active');
      document.body.style.overflow = '';
    });
  }

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

  const scrollBtn = document.querySelector('.scroll-to-rules');
  const rulesContainer = document.querySelector('.container-rules');

  if (scrollBtn && rulesContainer) {
    scrollBtn.addEventListener('click', function (e) {
      e.preventDefault();
      rulesContainer.scrollIntoView({
        behavior: 'smooth'
      });
    });
  }

  const token = localStorage.getItem('authToken'); 
  const gameCurrencyElement = document.getElementById('user-balance'); 

  if (token && gameCurrencyElement) {
    fetch('http://localhost:8000/profile/info/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      }
    })
    .then(response => response.json())
    .then(data => {
      const gameCurrency = data.game_currency;

      if (gameCurrency !== undefined) {
        gameCurrencyElement.textContent = `${gameCurrency}`;
      } else {
        console.error('Не вдалося отримати гейм валюту з відповіді');
      }
    })
    .catch(error => {
      console.error('Помилка при отриманні інформації про користувача:', error);
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      const confirmLogout = window.confirm("Ви точно хочете вийти?");
      
      if (confirmLogout) {
        localStorage.removeItem('authToken');
        
        window.location.replace('../Registration/registration.html');
      }
    });
  }
});
