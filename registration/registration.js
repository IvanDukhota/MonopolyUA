const form = document.getElementById('registrationForm');
const switchModeLink = document.getElementById('switchModeLink');
const formTitleSpan = document.querySelector('.form-title span');
const submitBtn = document.getElementById('submitBtn');

const nicknameBlock = document.getElementById('nicknameBlock');
const genderBlock   = document.getElementById('genderBlock');

const nickname   = document.getElementById('nickname');
const genderMale = genderBlock.querySelector('input[value="male"]');
const genderFem  = genderBlock.querySelector('input[value="female"]');

let isLoginMode = false;

form.addEventListener('submit', function (e) {
  e.preventDefault();

  if (isLoginMode) {
    const emailValue = document.getElementById('email').value;
    const passwordValue = document.getElementById('password').value;
    alert(`Вход с данными: ${emailValue} / ${passwordValue}`);
    
    fetch('http://localhost:8000/api/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: emailValue,
        password: passwordValue
      }),
    })
    .then(response => response.json())
    .then(data => {
      alert('Вход успешен');
      console.log(data);
    })
    .catch(error => {
      alert('Ошибка входа');
      console.error(error);
    });

    return;
  }

  const password = document.getElementById('password').value;
  const repeatPassword = document.getElementById('repeatPassword').value;

  if (password !== repeatPassword) {
    alert('Пароли не совпадают!');
    return;
  }

  const nicknameValue = nickname.value;
  const genderValue = genderMale.checked ? 'male' : 'female';
  const emailValue = document.getElementById('email').value;

  fetch('http://localhost:8000/api/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: emailValue,
      password: password,
      nickname: nicknameValue,
      gender: genderValue
    }),
  })
  .then(response => response.json())
  .then(data => {
    alert('Регистрация прошла успешно!');
    form.reset();
    console.log(data);
  })
  .catch(error => {
    alert('Ошибка регистрации');
    console.error(error);
  });
});


switchModeLink.addEventListener('click', function(e) {
  e.preventDefault();
  toggleMode();
});

function toggleMode() {
  if (!isLoginMode) {
    switchToLogin();
  } else {
    switchToRegistration();
  }
}

function switchToLogin() {
  isLoginMode = true;
  formTitleSpan.textContent = 'Login';
  switchModeLink.textContent = 'No account? Create it here';
  submitBtn.textContent = 'Login';

  nicknameBlock.style.display = 'none';
  genderBlock.style.display   = 'none';

  nickname.removeAttribute('required');
  genderMale.removeAttribute('required');
  genderFem.removeAttribute('required');
}

function switchToRegistration() {
  isLoginMode = false;
  formTitleSpan.textContent = 'Registration';
  switchModeLink.textContent = 'Have an account? Join here';
  submitBtn.textContent = 'Registration';

  nicknameBlock.style.display = 'block';
  genderBlock.style.display   = 'flex';

  nickname.setAttribute('required', 'true');
  genderMale.setAttribute('required', 'true');
  genderFem.setAttribute('required', 'true');
}
