const friends = [
    "FriendOne", "FriendTwo", "FriendThree", "FriendFour", "FriendFive",
    "FriendSix", "FriendSeven", "FriendEight", "FriendNine", "FriendTen",
    "FriendEleven", "FriendTwelve", "FriendThirteen", "FriendFourteen",
    "FriendFifteen", "FriendSixteen"
  ];

  const modal = document.getElementById("editProfileModal");
  const closeModalBtn = document.getElementById("closeModalBtn");
  closeModalBtn.addEventListener("click", () => {
    modal.classList.remove('show');
    document.body.classList.remove('modal-open');
  });

  const editButton = document.querySelector(".btn-edit-profile");
  const confirmEditBtn = document.getElementById("confirmEdit");

  editButton.addEventListener("click", () => {
    modal.classList.add('show');
    document.body.classList.add('modal-open');
  });

  confirmEditBtn.addEventListener("click", () => {
    const nickname = document.getElementById("editNickname").value;
    const region = document.getElementById("editRegion").value;
    const password = document.getElementById("editPassword").value;
    const confirmPassword = document.getElementById("editConfirmPassword").value;

    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }

    alert(`Profile updated:\nNickname: ${nickname}\nRegion: ${region}`);
    modal.classList.remove('show');
    document.body.classList.remove('modal-open');
  });

  const itemsPerPage = 8;
  let currentPage = 1;
  function paginateFriends() {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = currentPage * itemsPerPage;
    const friendsToDisplay = friends.slice(startIndex, endIndex);

    const friendsContainer = document.getElementById('friendsContainer');
    friendsContainer.innerHTML = '';

    friendsToDisplay.forEach(friend => {
      const friendItem = document.createElement('div');
      friendItem.className = 'friend-item';
      friendItem.innerHTML = `<span>${friend}</span><button class="remove-friend-btn">Remove</button>`;
      friendsContainer.appendChild(friendItem);
    });

    updatePagination();
  }
  function updatePagination() {
    const totalPages = Math.ceil(friends.length / itemsPerPage);
    const pagination = document.getElementById('pagination');

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

  const tabs = document.querySelectorAll('.inv-btn');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active-tab'));
      tab.classList.add('active-tab');
      currentTab = tab.id.replace('Tab', '').toLowerCase();
    });
  });

  window.onload = function () {
    paginateFriends();
  };


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





  const buttons = document.querySelectorAll('.card-part-info-buttons button');
  const items = document.querySelectorAll('.card-part-el .item');

  let selectedCards = {
    top: null,
    right: null,
    bottom: null,
    left: null
  };

  let selectedButton = document.querySelector('.card-part-info-buttons button.active');

  buttons.forEach(button => {
    button.addEventListener('click', () => {
      selectedButton.classList.remove('active');

      selectedButton = button;
      selectedButton.classList.add('active');

      updateCardVisibility();
    });
  });

  items.forEach(item => {
    item.addEventListener('click', () => {
      const currentButtonId = selectedButton.id;

      if (item.classList.contains('selected') && selectedCards[currentButtonId] === item) {
        item.classList.remove('selected');
        selectedCards[currentButtonId] = null;
      } else {
        if (selectedCards[currentButtonId]) {
          selectedCards[currentButtonId].classList.remove('selected');
        }

        item.classList.add('selected');
        selectedCards[currentButtonId] = item;
      }

      updateCardVisibility();
    });
  });

  function updateCardVisibility() {
    items.forEach(item => {
      const cardId = item.dataset.id;
      const isSelected = Object.keys(selectedCards).some(key => selectedCards[key] && selectedCards[key].dataset.id === cardId);

      if (isSelected) {
        if (selectedCards[selectedButton.id] !== item) {
          item.style.display = 'none';
        } else {
          item.style.display = 'flex';
        }
      } else {
        item.style.display = 'flex';
      }
    });
  }

  const cubeItems = document.querySelectorAll('.cubes-part-el .item');
  let selectedCube = null;

  cubeItems.forEach(item => {
    item.addEventListener('click', () => {
      if (selectedCube === item) {
        item.classList.remove('selected');
        selectedCube = null;
      } else {
        if (selectedCube) {
          selectedCube.classList.remove('selected');
        }
        item.classList.add('selected');
        selectedCube = item;
      }
    });
  });


  document.querySelectorAll('.item-but').forEach((button, index) => {
    button.addEventListener('click', function () {
      const modal = document.getElementById('modal-cases');
      modal.style.display = 'flex';

      document.body.classList.add('modal-open');

      const modalTitle = document.getElementById('modal-title');
      const modalDescription = document.getElementById('modal-description');

      modalTitle.textContent = `Кейс ${index + 1}`;
      modalDescription.textContent = `Подробное описание для кейса номер ${index + 1}`;
    });
  });

  document.getElementById('close-modal-cases').addEventListener('click', function () {
    document.getElementById('modal-cases').style.display = 'none';
    document.body.classList.remove('modal-open');
  });


const removeButtons = document.querySelectorAll('.remove-overlay-btn');

removeButtons.forEach(button => {
button.addEventListener('click', function() {
  const overlay = button.closest('.overlay');
  overlay.style.display = 'none';
});
});


document.querySelector('.modal-cases-content-button button').addEventListener('click', function () {
const itemsContainer = document.querySelector('.modal-cases-content-items');
const items = Array.from(itemsContainer.children);

function animateScroll() {
  const firstItem = itemsContainer.firstElementChild;

  itemsContainer.appendChild(firstItem);

  items.forEach(item => {
    item.style.transition = 'none';
    item.style.transform = 'translateX(0)';
  });

  setTimeout(() => {
    items.forEach(item => {
      item.style.transition = 'transform 0.1s ease';
      item.style.transform = 'translateX(-100%)';
    });
  }, 50);
}

const animationInterval = setInterval(animateScroll, 250);

});




