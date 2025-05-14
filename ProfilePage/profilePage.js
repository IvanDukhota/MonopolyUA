

// User Profile Manage

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("authToken");

    const nameInput = document.getElementById("nameInput");
    const regionInput = document.getElementById("regionInput");
    const passInput = document.getElementById("passInput");
    const repeatPassInput = document.getElementById("repeatPassInput");
    const avatar = document.getElementById("avatar");
    const editBtn = document.getElementById("acceptChange");
    const cancelBtn = document.getElementById("cancelChange");

    let editing = false;
    let originalName = "";
    let originalRegion = "";

    function applyDisabledStyles() {
        [nameInput, regionInput].forEach(input => {
            input.style.cursor = "default";
            input.classList.add("no-hover");
        });
    }

    function removeDisabledStyles() {
        [nameInput, regionInput].forEach(input => {
            input.style.cursor = "text";
            input.classList.remove("no-hover");
        });
    }

    fetch("http://localhost:8000/profile/info/", {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        avatar.src = data.avatar;
        nameInput.value = data.username;
        regionInput.value = data.region || "";

        originalName = data.username;
        originalRegion = data.region || "";

        nameInput.disabled = true;
        regionInput.disabled = true;
        applyDisabledStyles();
    })
    .catch(err => {
        console.error("Помилка отримання профілю:", err);
        alert("Не вдалося завантажити профіль");
    });


    fetch("http://localhost:8000/profile/stat/", {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + localStorage.getItem("authToken"), 
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Не вдалося отримати статистику");
        }
        return response.json();
    })
    .then(data => {
        document.getElementById("stat-games").textContent = data.games;
        document.getElementById("stat-wins").textContent = data.wins;
        document.getElementById("stat-loses").textContent = data.lose;
        document.getElementById("stat-percentage").textContent = data.percentage + "%";
        document.getElementById("stat-points").textContent = data.points;
    })
    .catch(error => {
        console.error("Помилка при завантаженні статистики:", error);
    });

    editBtn.addEventListener("click", () => {
        if (!editing) {
            editing = true;
            nameInput.disabled = false;
            regionInput.disabled = false;

            removeDisabledStyles();

            passInput.style.opacity = "1";
            repeatPassInput.style.opacity = "1";
            passInput.style.pointerEvents = "auto";
            repeatPassInput.style.pointerEvents = "auto";

            cancelBtn.style.opacity = "1";
            cancelBtn.style.pointerEvents = "auto";

            editBtn.textContent = "Зберегти";
        } else {
            if (passInput.value !== repeatPassInput.value) {
                alert("Паролі не співпадають!");
                return;
            }

            fetch("http://localhost:8000/profile/update/", {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    username: nameInput.value,
                    region: regionInput.value,
                    password: passInput.value || undefined
                })
            })
            .then(response => {
                if (!response.ok) throw new Error("Заповніть всі необхідні поля");
                return response.json();
            })
            .then(data => {
                nameInput.disabled = true;
                regionInput.disabled = true;
                applyDisabledStyles();

                passInput.style.opacity = "0";
                repeatPassInput.style.opacity = "0";
                passInput.style.pointerEvents = "none";
                repeatPassInput.style.pointerEvents = "none";

                cancelBtn.style.opacity = "0";
                cancelBtn.style.pointerEvents = "none";

                editBtn.textContent = "Редагувати";
                editing = false;

                originalName = data.username;
                originalRegion = data.region || "";

                alert("Профіль оновлено");
            })
            .catch(error => {
                alert(error.message);
            });
        }
    });

    cancelBtn.addEventListener("click", () => {
        nameInput.value = originalName;
        regionInput.value = originalRegion;

        nameInput.disabled = true;
        regionInput.disabled = true;
        applyDisabledStyles();

        passInput.value = "";
        repeatPassInput.value = "";

        passInput.style.opacity = "0";
        repeatPassInput.style.opacity = "0";
        passInput.style.pointerEvents = "none";
        repeatPassInput.style.pointerEvents = "none";

        cancelBtn.style.opacity = "0";
        cancelBtn.style.pointerEvents = "none";

        editBtn.textContent = "Редагувати";
        editing = false;
    });



    document.getElementById("changePictureBtn").addEventListener("click", function () {
        document.getElementById("uploadInput").click();
    });
    
    document.getElementById("uploadInput").addEventListener("change", function () {
        const file = this.files[0];
        if (!file) return;
    
        const formData = new FormData();
        formData.append("avatar", file);
    
        fetch("http://localhost:8000/profile/avatar/", {
            method: "PATCH",
            headers: {
                Authorization: `Bearer ${localStorage.getItem("authToken")}` 
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Не вдалося оновити фото");
            }
            return response.json();
        })
        .then(data => {
            document.getElementById("avatar").src = data.avatar;
        })
        .catch(error => {
            alert(error.message);
        });
    });


});






// User Profile Manage end



// Change avatar




// End Avatar Change

const friends = [];
const token = localStorage.getItem('authToken'); 
fetch('http://localhost:8000/friends/user-friends/', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  }
})
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok ' + response.statusText);
    }
    return response.json();
  })
  .then(data => {
    console.log("Friends:", data);

    data.forEach(friend => {
      friends.push(friend); 
    });
    renderFriends(currentPage);

    console.log("Friends array:", friends);
  })
  .catch(error => {
    console.error('Error:', error);
  });


const friendsListMid = document.querySelector('.friends-list-mid');
const friendsListBot = document.querySelector('.friends-list-bot');

const itemsPerPage = 9;
let currentPage = 1;

function renderFriends(page) {
  friendsListMid.innerHTML = '';
  const start = (page - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  const pageFriends = friends.slice(start, end);

  pageFriends.forEach((friend, index) => {
      const friendItem = document.createElement('div');
      friendItem.className = 'friend-item';

      friendItem.innerHTML = `
          <span>${friend.username}</span>
          <button class="remove-friend-btn" onclick="removeFriend(${start + index}, ${friend.id})">Видалити</button>
      `;

      friendsListMid.appendChild(friendItem);
  });
}

function renderPagination() {
  friendsListBot.innerHTML = '';
  const pageCount = Math.ceil(friends.length / itemsPerPage);

  for (let i = 1; i <= pageCount; i++) {
      const pageBtn = document.createElement('span');
      pageBtn.className = 'page-num' + (i === currentPage ? ' active' : '');
      pageBtn.innerText = i;
      pageBtn.addEventListener('click', () => {
          currentPage = i;
          renderFriends(currentPage);
          renderPagination();
      });
      friendsListBot.appendChild(pageBtn);
  }
}

function removeFriend(index, id) {
  const confirmed = confirm("Ви впевнені, що хочете видалити цього друга?");
  if (!confirmed) return;

  const token = localStorage.getItem('authToken');

  fetch('http://localhost:8000/friends/delete-friend/', {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ friend_id: id })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Не вдалося видалити друга.');
    }
    friends.splice(index, 1);
    if (currentPage > Math.ceil(friends.length / itemsPerPage)) {
      currentPage--;
    }
    renderFriends(currentPage);
    renderPagination();
  })
  .catch(error => {
    console.error('Помилка при видаленні:', error);
    alert('Сталася помилка при видаленні друга.');
  });
}


renderFriends(currentPage);
renderPagination();




//INVENTORY SECTION//

const cubesBtn = document.getElementById('cubesBtn');
const cardsBtn = document.getElementById('cardsBtn');
const casesBtn = document.getElementById('casesBtn');
const inventorySection = document.querySelector('.player-inventory-data');

const items = [
    { id: 1, type: 'cube', name: 'Звичайний куб', price: 120, rarity: 'common', imageUrl: '../images/cubes.png' },
    { id: 2, type: 'card', name: 'Компанія "Реал Мідрід"', price: 200, rarity: 'rare', imageUrl: '../images/realmadrid.png' },
    { id: 3, type: 'case', name: 'Кейс Фенікс', price: 300, rarity: 'legendary', imageUrl: '../images/fenix.png' },
    { id: 4, type: 'cube', name: 'Куб вічності', price: 150, rarity: 'epic', imageUrl: '../images/galaxy.png' },
    { id: 5, type: 'card', name: 'Компанія "Люфтганза"', price: 250, rarity: 'legendary', imageUrl: '../images/lufthansa.png' },
    { id: 6, type: 'case', name: 'Кейс Кошмар', price: 350, rarity: 'epic', imageUrl: '../images/casess.png' },

    { id: 7, type: 'cube', name: 'Куб магії', price: 180, rarity: 'rare', imageUrl: '../images/magic_cube.png' },
    { id: 8, type: 'cube', name: 'Куб часу', price: 220, rarity: 'legendary', imageUrl: '../images/time_cube.png' },
    { id: 9, type: 'cube', name: 'Куб сили', price: 300, rarity: 'epic', imageUrl: '../images/power_cube.png' },
    { id: 10, type: 'cube', name: 'Куб світла', price: 250, rarity: 'epic', imageUrl: '../images/light_cube.png' },
    { id: 11, type: 'cube', name: 'Куб тіні', price: 190, rarity: 'common', imageUrl: '../images/shadow_cube.png' },
    { id: 12, type: 'cube', name: 'Куб безмежності', price: 400, rarity: 'legendary', imageUrl: '../images/infinity_cube.png' },

    { id: 13, type: 'card', name: 'Компанія "Баварія"', price: 180, rarity: 'common', imageUrl: '../images/bayern.png' },
    { id: 14, type: 'card', name: 'Компанія "Барселона"', price: 220, rarity: 'rare', imageUrl: '../images/barcelona.png' },
    { id: 15, type: 'card', name: 'Компанія "Ювентус"', price: 250, rarity: 'legendary', imageUrl: '../images/juventus.png' },
    { id: 16, type: 'card', name: 'Компанія "ПСЖ"', price: 230, rarity: 'epic', imageUrl: '../images/psg.png' },
    { id: 17, type: 'card', name: 'Компанія "Манчестер Юнайтед"', price: 270, rarity: 'epic', imageUrl: '../images/manunited.png' },
    { id: 18, type: 'card', name: 'Компанія "Челсі"', price: 200, rarity: 'common', imageUrl: '../images/chelsea.png' },

    { id: 19, type: 'case', name: 'Кейс Золото', price: 320, rarity: 'legendary', imageUrl: '../images/gold_case.png' },
    { id: 20, type: 'case', name: 'Кейс Срібло', price: 200, rarity: 'common', imageUrl: '../images/silver_case.png' },
    { id: 21, type: 'case', name: 'Кейс Магія', price: 250, rarity: 'rare', imageUrl: '../images/magic_case.png' },
    { id: 22, type: 'case', name: 'Кейс Привид', price: 180, rarity: 'epic', imageUrl: '../images/ghost_case.png' },
    { id: 23, type: 'case', name: 'Кейс Молнія', price: 270, rarity: 'epic', imageUrl: '../images/thunder_case.png' },
    { id: 24, type: 'case', name: 'Кейс Вулкан', price: 350, rarity: 'legendary', imageUrl: '../images/volcano_case.png' }
];

let selectedCubeId = null;
let selectedCards = {};
let currentType = 'cubes';

function clearActiveButtons() {
    document.querySelectorAll('.type-buttons').forEach(btn => btn.classList.remove('active'));
}

function saveToLocalStorage() {
    const data = {
        selectedCubeId,
        selectedCards
    };
    localStorage.setItem('playerInventory', JSON.stringify(data));
}

function loadFromLocalStorage() {
    return JSON.parse(localStorage.getItem('playerInventory')) || { selectedCubeId: null, selectedCards: {} };
}

function renderItems(type) {
    inventorySection.innerHTML = '';
    const savedData = loadFromLocalStorage();
    selectedCubeId = savedData.selectedCubeId;
    selectedCards = savedData.selectedCards || {};

    const data = items.filter(item => item.type === type.slice(0, -1));

    data.forEach((itemData) => {
        const item = document.createElement('div');
        item.className = 'item';
        item.dataset.id = itemData.id;
        item.dataset.type = itemData.type;
        item.innerHTML = `
            <img src="${itemData.imageUrl}" alt="${itemData.name}">
            <h3>${itemData.name}</h3>
            <p>Ціна: ${itemData.price}</p>
            <p>Рідкість: ${itemData.rarity}</p>
        `;

        if (itemData.type === 'cube' && savedData.selectedCubeId == itemData.id) {
            item.style.border = '1px solid limegreen';
        }

        if (itemData.type === 'card' && selectedCards[itemData.id]) {
            item.style.border = '1px solid limegreen';
        }

        if (itemData.type === 'cube') {
            item.addEventListener('click', () => {
                document.querySelectorAll('.item').forEach(el => el.style.border = 'none');
                item.style.border = '1px solid limegreen';
                selectedCubeId = itemData.id;
                saveToLocalStorage();
            });
        }

        if (itemData.type === 'case') {
            item.addEventListener('dblclick', () => {
                window.location.href = '../CaseOpeningPage/caseOpeningPage.html';
            });
        }

        if (itemData.type === 'card') {
            let optionsMenu = null;

            item.addEventListener('click', (e) => {
                if (optionsMenu) {
                    optionsMenu.remove();
                    optionsMenu = null;
                }

                optionsMenu = document.createElement('div');
                optionsMenu.style.position = 'absolute';
                optionsMenu.style.top = (item.getBoundingClientRect().top + window.scrollY) + 'px';
                optionsMenu.style.left = (item.getBoundingClientRect().right + 10) + 'px';
                optionsMenu.style.background = '#222';
                optionsMenu.style.border = '1px solid #555';
                optionsMenu.style.padding = '10px';
                optionsMenu.style.borderRadius = '8px';
                optionsMenu.style.display = 'flex';
                optionsMenu.style.flexDirection = 'column';
                optionsMenu.style.zIndex = '1000';

                ['Вверх', 'Вниз', 'Вліво', 'Вправо'].forEach(direction => {
                    const btn = document.createElement('button');
                    btn.textContent = direction;
                    btn.style.marginBottom = '5px';
                    btn.style.backgroundColor = (selectedCards[itemData.id] === direction) ? 'limegreen' : '#444';
                    btn.style.color = 'white';
                    btn.style.border = 'none';
                    btn.style.borderRadius = '5px';
                    btn.style.padding = '5px 10px';
                    btn.style.cursor = 'pointer';

                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                    
                        const alreadySelectedCardId = Object.entries(selectedCards).find(([id, dir]) => dir === direction);
                    
                        if (alreadySelectedCardId) {
                            const [conflictingId] = alreadySelectedCardId;
                            delete selectedCards[conflictingId];
                            const oldCard = document.querySelector(`.item[data-id="${conflictingId}"]`);
                            if (oldCard) oldCard.style.border = 'none';
                        }
                    
                        if (!selectedCards[itemData.id] && Object.keys(selectedCards).length >= 4) {
                            alert('Можна вибрати максимум 4 карти');
                            optionsMenu.remove();
                            optionsMenu = null;
                            return;
                        }
                    
                        selectedCards[itemData.id] = direction;
                        item.style.border = '1px solid limegreen';
                        saveToLocalStorage();
                        optionsMenu.remove();
                        optionsMenu = null;
                    });

                    optionsMenu.appendChild(btn);
                });

                document.body.appendChild(optionsMenu);

        
                setTimeout(() => {
                    document.addEventListener('click', function handler(e) {
                        if (!optionsMenu.contains(e.target) && e.target !== item) {
                            optionsMenu?.remove();
                            optionsMenu = null;
                            document.removeEventListener('click', handler);
                        }
                    });
                }, 0);
            });

            item.addEventListener('dblclick', () => {
                if (currentType === 'cards' && selectedCards[itemData.id]) {
                    delete selectedCards[itemData.id]; 
                    item.style.border = 'none';
                    saveToLocalStorage();
                }
            });
        }

        inventorySection.appendChild(item);
    });
}

cubesBtn.addEventListener('click', () => {
    clearActiveButtons();
    cubesBtn.classList.add('active');
    currentType = 'cubes';
    renderItems(currentType);
});

cardsBtn.addEventListener('click', () => {
    clearActiveButtons();
    cardsBtn.classList.add('active');
    currentType = 'cards';
    renderItems(currentType);
});

casesBtn.addEventListener('click', () => {
    clearActiveButtons();
    casesBtn.classList.add('active');
    currentType = 'cases';
    renderItems(currentType);
});

renderItems(currentType);