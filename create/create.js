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