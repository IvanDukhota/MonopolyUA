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


//Case opening animation

const button = document.getElementById('caseOpen');
const dropLine = document.querySelector('.drop-line');

let isAnimating = false;

button.addEventListener('click', () => {
  if (isAnimating) return;
  isAnimating = true;
  button.disabled = true;

  const moveTime = 50;
  const duration = 5000;
  const itemWidth = dropLine.firstElementChild.offsetWidth + 20;

  dropLine.style.transition = `transform ${moveTime}ms ease-in-out`;

  const shuffleInsert = (element) => {
    const children = Array.from(dropLine.children);
    const randomIndex = Math.floor(Math.random() * children.length);
    dropLine.insertBefore(element, dropLine.children[randomIndex]);
  };

  const animate = () => {
    dropLine.style.transform = `translateX(-${itemWidth}px)`;

    setTimeout(() => {
      dropLine.style.transition = 'none';
      dropLine.style.transform = 'translateX(0)';

      const first = dropLine.firstElementChild;
      shuffleInsert(first);

      void dropLine.offsetWidth;
      dropLine.style.transition = `transform ${moveTime}ms ease-in-out`;

      if (isAnimating) requestAnimationFrame(animate);
    }, moveTime);
  };

  animate();

  setTimeout(() => {
    isAnimating = false;
    button.disabled = false;
  }, duration);
});


