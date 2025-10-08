document.addEventListener('DOMContentLoaded', () => {
    // Theme toggle
    const themeToggleBtn = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme') || 'light';

    if (currentTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }

    themeToggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');
        if (document.body.classList.contains('dark-theme')) {
            localStorage.setItem('theme', 'dark');
        } else {
            localStorage.setItem('theme', 'light');
        }
    });

    // Sales Entry Cart Functionality
    const menuItems = document.querySelectorAll('.menu-item');
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotalDisplay = document.getElementById('cart-total');
    const cartDataInput = document.getElementById('cart_data');

    let cart = [];

    function updateCartDisplay() {
        cartItemsContainer.innerHTML = '';
        if (cart.length === 0) {
            cartItemsContainer.innerHTML = '<p>No items in cart</p>';
            cartTotalDisplay.textContent = 'Total: KES 0.00';
            cartDataInput.value = '';
            return;
        }

        let total = 0;
        cart.forEach((item, index) => {
            const itemTotal = item.quantity * item.unit_price;
            total += itemTotal;

            const cartItemDiv = document.createElement('div');
            cartItemDiv.classList.add('cart-item');

            cartItemDiv.innerHTML = `
                <span>${item.name} (KES ${item.unit_price.toFixed(2)})</span>
                <input type="number" min="1" value="${item.quantity}" data-index="${index}" class="cart-quantity" style="width: 50px; margin: 0 10px;" />
                <span>KES ${itemTotal.toFixed(2)}</span>
                <button type="button" data-index="${index}" class="remove-item btn btn-danger" style="margin-left: 10px;">Remove</button>
            `;

            cartItemsContainer.appendChild(cartItemDiv);
        });

        cartTotalDisplay.textContent = `Total: KES ${total.toFixed(2)}`;
        cartDataInput.value = JSON.stringify(cart);
    }

    function addToCart(item) {
        const existingIndex = cart.findIndex(ci => ci.id === item.id);
        if (existingIndex !== -1) {
            cart[existingIndex].quantity += 1;
        } else {
            cart.push({...item, quantity: 1});
        }
        updateCartDisplay();
    }

    menuItems.forEach(menuItem => {
        menuItem.addEventListener('click', () => {
            const item = {
                id: parseInt(menuItem.getAttribute('data-id')),
                name: menuItem.getAttribute('data-name'),
                unit_price: parseFloat(menuItem.getAttribute('data-price'))
            };
            addToCart(item);
        });
    });

    cartItemsContainer.addEventListener('input', (e) => {
        if (e.target.classList.contains('cart-quantity')) {
            const index = parseInt(e.target.getAttribute('data-index'));
            let qty = parseInt(e.target.value);
            if (isNaN(qty) || qty < 1) {
                qty = 1;
                e.target.value = qty;
            }
            cart[index].quantity = qty;
            updateCartDisplay();
        }
    });

    cartItemsContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-item')) {
            const index = parseInt(e.target.getAttribute('data-index'));
            cart.splice(index, 1);
            updateCartDisplay();
        }
    });

    // Search menu items
    const menuSearchInput = document.getElementById('menu-search');
    menuSearchInput.addEventListener('input', () => {
        const filter = menuSearchInput.value.toLowerCase();
        menuItems.forEach(menuItem => {
            const name = menuItem.getAttribute('data-name').toLowerCase();
            if (name.includes(filter)) {
                menuItem.style.display = '';
            } else {
                menuItem.style.display = 'none';
            }
        });
    });

    // Initialize cart display
    updateCartDisplay();

    // Live update sale date and time in EAT (Africa/Nairobi, UTC+3)
    const saleDateInput = document.querySelector('input[name="sale_date"]');

    if (saleDateInput) {
        function updateSaleDateTime() {
            const now = new Date();

            // Get current time in EAT (Africa/Nairobi → UTC+3)
            const utc = now.getTime() + now.getTimezoneOffset() * 60000;
            const eat = new Date(utc + 3 * 60 * 60 * 1000);

            const year = eat.getFullYear();
            const month = String(eat.getMonth() + 1).padStart(2, '0');
            const day = String(eat.getDate()).padStart(2, '0');
            const hours = String(eat.getHours()).padStart(2, '0');  // 24-hour format
            const minutes = String(eat.getMinutes()).padStart(2, '0');

            // Format for datetime-local input
            const formatted = `${year}-${month}-${day}T${hours}:${minutes}:${String(eat.getSeconds()).padStart(2, '0')}`;
            saleDateInput.value = formatted;
        }

        updateSaleDateTime(); // initial call
        setInterval(updateSaleDateTime, 1000); // live update every second
    }
});
