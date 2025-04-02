document.getElementById('field-up-1-color').style.backgroundColor = 'red';
document.getElementById('field-up-2-color').style.backgroundColor = 'red';
document.getElementById('field-up-3-color').style.backgroundColor = 'red';

document.getElementById('field-up-6-color').style.backgroundColor = 'yellow';
document.getElementById('field-up-7-color').style.backgroundColor = 'yellow';
document.getElementById('field-up-9-color').style.backgroundColor = 'yellow';

document.getElementById('field-left-1-color').style.backgroundColor = 'orange';
document.getElementById('field-left-2-color').style.backgroundColor = 'orange';
document.getElementById('field-left-4-color').style.backgroundColor = 'orange';

document.getElementById('field-left-6-color').style.backgroundColor = 'purple';
document.getElementById('field-left-7-color').style.backgroundColor = 'purple';
document.getElementById('field-left-9-color').style.backgroundColor = 'purple';

document.getElementById('field-right-1-color').style.backgroundColor = 'green';
document.getElementById('field-right-2-color').style.backgroundColor = 'green';
document.getElementById('field-right-4-color').style.backgroundColor = 'green';

document.getElementById('field-right-7-color').style.backgroundColor = 'blue';
document.getElementById('field-right-9-color').style.backgroundColor = 'blue';

document.getElementById('field-down-1-color').style.backgroundColor = 'LightSkyBlue';
document.getElementById('field-down-2-color').style.backgroundColor = 'LightSkyBlue';
document.getElementById('field-down-4-color').style.backgroundColor = 'LightSkyBlue';

document.getElementById('field-down-7-color').style.backgroundColor = 'Sienna';
document.getElementById('field-down-9-color').style.backgroundColor = 'Sienna';



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