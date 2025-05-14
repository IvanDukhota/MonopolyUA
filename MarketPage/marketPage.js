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


//Market//
const items = [
    { id: 1, type: 'cube', name: 'Червоні кубики', price: 120, rarity: 'common', amount: 10, imageUrl: '../images/cubes/red-cubes.png' },
    { id: 2, type: 'card', name: 'Компанія "Адідас"', price: 200, rarity: 'rare', amount: 5, imageUrl: '../images/logos/adidas.png' },
    { id: 3, type: 'case', name: 'Кейс Фенікс', price: 300, rarity: 'legendary', amount: 3, imageUrl: '../images/cases/fenix.png' },
    { id: 4, type: 'cube', name: 'Сині кубики', price: 150, rarity: 'epic', amount: 7, imageUrl: '../images/cubes/blue-cubes.png' },
    { id: 5, type: 'card', name: 'Компанія "Американські авіалінії"', price: 250, rarity: 'legendary', amount: 2, imageUrl: '../images/logos/american.png' },
    { id: 6, type: 'case', name: 'Кейс Кошмар', price: 350, rarity: 'epic', amount: 4, imageUrl: '../images/cases/nightmare.png' },

    { id: 7, type: 'cube', name: 'Золоті кубики', price: 180, rarity: 'rare', amount: 6, imageUrl: '../images/cubes/gold-cubes.png' },
    { id: 8, type: 'cube', name: 'Зелені кубики', price: 220, rarity: 'legendary', amount: 4, imageUrl: '../images/cubes/green-cubes.png' },
    { id: 9, type: 'cube', name: 'Лавові кубики', price: 300, rarity: 'epic', amount: 3, imageUrl: '../images/cubes/lava-cubes.png' },
    { id: 10, type: 'cube', name: 'Магічні куби', price: 250, rarity: 'epic', amount: 5, imageUrl: '../images/cubes/magic_cube.png' },
    { id: 11, type: 'cube', name: 'Рожеві куби', price: 190, rarity: 'common', amount: 8, imageUrl: '../images/cubes/pink-cubes.png' },
    { id: 12, type: 'cube', name: 'Фіолетові куби', price: 400, rarity: 'legendary', amount: 2, imageUrl: '../images/cubes/purple-cubes.png' },
    
    { id: 13, type: 'card', name: 'Компанія "Apple"', price: 180, rarity: 'common', amount: 9, imageUrl: '../images/logos/apple.png' },
    { id: 14, type: 'card', name: 'Компанія "Asus"', price: 220, rarity: 'rare', amount: 7, imageUrl: '../images/logos/asus.png' },
    { id: 15, type: 'card', name: 'Компанія "Барселона"', price: 250, rarity: 'legendary', amount: 5, imageUrl: '../images/logos/barcelona.png' },
    { id: 16, type: 'card', name: 'Компанія "Burger King"', price: 230, rarity: 'epic', amount: 4, imageUrl: '../images/logos/burger-king.png' },
    { id: 17, type: 'card', name: 'Компанія "Discord"', price: 270, rarity: 'epic', amount: 3, imageUrl: '../images/logos/discord.png' },
    { id: 18, type: 'card', name: 'Компанія "Dynamo"', price: 200, rarity: 'common', amount: 6, imageUrl: '../images/logos/dynamo.png' },
    
    { id: 19, type: 'case', name: 'Кейс gallery', price: 320, rarity: 'legendary', amount: 4, imageUrl: '../images/cases/gallery.png' },
    { id: 20, type: 'case', name: 'Кейс kilowatt', price: 200, rarity: 'common', amount: 10, imageUrl: '../images/cases/kilowatt.png' },
    { id: 21, type: 'case', name: 'Кейс recoil', price: 250, rarity: 'rare', amount: 8, imageUrl: '../images/cases/recoil.png' },
    { id: 22, type: 'case', name: 'Кейс revolution', price: 180, rarity: 'epic', amount: 6, imageUrl: '../images/cases/revolution.png' },
    { id: 23, type: 'case', name: 'Кейс case1', price: 270, rarity: 'epic', amount: 4, imageUrl: '../images/cases/case1.png' },
    { id: 24, type: 'case', name: 'Кейс case2', price: 350, rarity: 'legendary', amount: 3, imageUrl: '../images/cases/case2.png' }
];


let activeType = null;
const itemDisplayMid = document.querySelector('.item-display-mid');
const searchNameInput = document.getElementById('search-name');
const typeButtons = document.querySelectorAll('.type-btn');
const priceFromInput = document.getElementById('price-from');
const priceToInput = document.getElementById('price-to');
const raritySelect = document.getElementById('rarity-select');
const amountInput = document.getElementById('amount');

function createItemElement(item) {
    const itemElement = document.createElement('div');
    itemElement.classList.add('item');
    itemElement.innerHTML = `
        <h3>${item.name}</h3>
        <p>Ціна: ${item.price}</p>
        <p>Рідкість: ${item.rarity}</p>
        <p>Кількість: ${item.amount}</p>
        <img src="${item.imageUrl}" alt="${item.name}">
    `;
    return itemElement;
}

function updateItems() {
    const nameFilter = searchNameInput.value.toLowerCase();
    const priceMin = parseInt(priceFromInput.value) || 0;
    const priceMax = parseInt(priceToInput.value) || Infinity;
    const rarityFilter = raritySelect.value;
    const amountFilter = parseInt(amountInput.value) || 0;

    itemDisplayMid.innerHTML = '';

    const filteredItems = items.filter(item => {
        const matchesName = item.name.toLowerCase().includes(nameFilter);
        const matchesPrice = item.price >= priceMin && item.price <= priceMax;
        const matchesRarity = rarityFilter === 'all' || item.rarity === rarityFilter;
        const matchesAmount = item.amount >= amountFilter;

        const matchesType = !activeType || item.type === activeType;

        return matchesName && matchesPrice && matchesRarity && matchesAmount && matchesType;
    });

    filteredItems.forEach(item => {
        const itemElement = createItemElement(item);
        itemDisplayMid.appendChild(itemElement);
    });
}

searchNameInput.addEventListener('input', updateItems);

typeButtons.forEach(button => {
    button.addEventListener('click', () => {
        if (activeType === button.dataset.type) {
            activeType = null;
            button.classList.remove('active');
        } else {
            activeType = button.dataset.type;
            typeButtons.forEach(b => b.classList.remove('active'));
            button.classList.add('active');
        }

        updateItems();
    });
});

priceFromInput.addEventListener('input', updateItems);
priceToInput.addEventListener('input', updateItems);
raritySelect.addEventListener('change', updateItems);
amountInput.addEventListener('input', updateItems);

updateItems();
