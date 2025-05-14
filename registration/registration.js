const form = document.getElementById('registrationForm');
const switchModeLink = document.getElementById('switchModeLink');
const formTitleSpan = document.querySelector('.form-title span');
const submitBtn = document.getElementById('submitBtn');

const nicknameBlock = document.getElementById('nicknameBlock');
const genderBlock = document.getElementById('genderBlock');

const nickname = document.getElementById('nickname');
const genderMale = genderBlock.querySelector('input[value="male"]');
const genderFem = genderBlock.querySelector('input[value="female"]');

let isLoginMode = false;

form.addEventListener('submit', function (e) {
  e.preventDefault();

  if (isLoginMode) {
    const emailValue = document.getElementById('email').value;
    const passwordValue = document.getElementById('password').value;

    fetch('http://127.0.0.1:8000/auth/login/', {
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
        if (data.access) {
          localStorage.setItem('authToken', data.access);
          window.location.href = '../MainPage/mainPage.html';
          console.log(data);
        } else {
          alert('Токен не получен');
        }
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
    showFieldError("repeatPassword", 'Пароли не совпадают!')
    return;
  }

  const nicknameValue = nickname.value;
  const genderValue = genderMale.checked ? 'male' : 'female';
  const emailValue = document.getElementById('email').value;

  fetch('http://127.0.0.1:8000/auth/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: emailValue,
      password: password,
      username: nicknameValue,
      gender: genderValue
    }),
  })
    .then(response => response.json())
    .then(data => {
      if (data.access) {
        localStorage.setItem('authToken', data.access);
        window.location.href = '../MainPage/mainPage.html';
        form.reset();
        console.log(data);
      }
      else if (data.username || data.email) {
        console.log(data);
        if (data.username) {
          showFieldError("nickname", data.username)
        }
        if (data.email) {
          showFieldError("email", data.email)
        }
      }
      else {
        alert('Токен не получен');
      }
    })
    .catch(error => {
      alert('Ошибка регистрации');
      console.error(error);
    });
});

switchModeLink.addEventListener('click', function (e) {
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
  genderBlock.style.display = 'none';

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
  genderBlock.style.display = 'flex';

  nickname.setAttribute('required', 'true');
  genderMale.setAttribute('required', 'true');
  genderFem.setAttribute('required', 'true');
}

function showFieldError(fieldId, message) {
  const input = document.getElementById(fieldId);
  const errorDiv = document.getElementById(fieldId + 'Error');

  if (!input || !errorDiv) return;

  input.classList.add('input-error');
  errorDiv.textContent = message;
  errorDiv.style.display = 'block';

  input.addEventListener('input', function clearError() {
    input.classList.remove('input-error');
    errorDiv.style.display = 'none';
    input.removeEventListener('input', clearError);
  });
}