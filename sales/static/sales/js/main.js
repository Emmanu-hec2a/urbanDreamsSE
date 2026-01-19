document.addEventListener('DOMContentLoaded', () => {

    /* =========================
       MOBILE NAV TOGGLE
    ========================== */
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const navMenu = document.getElementById('nav-menu');

    if (mobileMenuToggle && navMenu) {
        mobileMenuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            navMenu.classList.toggle('nav-open');
        });

        document.addEventListener('click', (e) => {
            if (
                navMenu.classList.contains('nav-open') &&
                !navMenu.contains(e.target) &&
                e.target !== mobileMenuToggle
            ) {
                navMenu.classList.remove('nav-open');
            }
        });
    }

    /* =========================
       THEME TOGGLE
    ========================== */
    const themeToggleBtn = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme') || 'light';

    if (currentTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            document.body.classList.toggle('dark-theme');
            localStorage.setItem(
                'theme',
                document.body.classList.contains('dark-theme') ? 'dark' : 'light'
            );
        });
    }

    /* =========================
       SALES CART FUNCTIONALITY
    ========================== */
    const menuItems = document.querySelectorAll('.menu-item');
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotalDisplay = document.getElementById('cart-total');
    const cartDataInput = document.getElementById('cart_data');

    let cart = [];

    if (cartItemsContainer && cartTotalDisplay && cartDataInput) {

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
                    <input type="number" min="1" value="${item.quantity}"
                           data-index="${index}" class="cart-quantity"
                           style="width: 50px; margin: 0 10px;" />
                    <span>KES ${itemTotal.toFixed(2)}</span>
                    <button type="button" data-index="${index}"
                            class="remove-item btn btn-danger"
                            style="margin-left: 10px;">Remove</button>
                `;

                cartItemsContainer.appendChild(cartItemDiv);
            });

            cartTotalDisplay.textContent = `Total: KES ${total.toFixed(2)}`;
            cartDataInput.value = JSON.stringify(cart);
        }

        function addToCart(item) {
            const existingItem = cart.find(ci => ci.id === item.id);
            existingItem ? existingItem.quantity++ : cart.push({ ...item, quantity: 1 });
            updateCartDisplay();
        }

        menuItems.forEach(menuItem => {
            menuItem.addEventListener('click', () => {
                const item = {
                    id: parseInt(menuItem.dataset.id),
                    name: menuItem.dataset.name,
                    unit_price: parseFloat(menuItem.dataset.price)
                };
                addToCart(item);
            });
        });

        cartItemsContainer.addEventListener('input', (e) => {
            if (e.target.classList.contains('cart-quantity')) {
                const index = parseInt(e.target.dataset.index);
                cart[index].quantity = Math.max(1, parseInt(e.target.value) || 1);
                updateCartDisplay();
            }
        });

        cartItemsContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-item')) {
                const index = parseInt(e.target.dataset.index);
                cart.splice(index, 1);
                updateCartDisplay();
            }
        });

        updateCartDisplay();
    }

    /* =========================
       MENU SEARCH
    ========================== */
    const menuSearchInput = document.getElementById('menu-search');

    if (menuSearchInput) {
        menuSearchInput.addEventListener('input', () => {
            const filter = menuSearchInput.value.toLowerCase();
            menuItems.forEach(menuItem => {
                const name = menuItem.dataset.name.toLowerCase();
                menuItem.style.display = name.includes(filter) ? '' : 'none';
            });
        });
    }

    /* =========================
       SALE DATE (EAT TIMEZONE)
    ========================== */
    const saleDateInput = document.querySelector('input[name="sale_date"]');

    if (saleDateInput) {
        function updateSaleDateTime() {
            const now = new Date();
            const utc = now.getTime() + now.getTimezoneOffset() * 60000;
            const eat = new Date(utc + 3 * 60 * 60 * 1000);

            const formatted = `${eat.getFullYear()}-${String(eat.getMonth() + 1).padStart(2, '0')}-${String(eat.getDate()).padStart(2, '0')}T${String(eat.getHours()).padStart(2, '0')}:${String(eat.getMinutes()).padStart(2, '0')}:${String(eat.getSeconds()).padStart(2, '0')}`;
            saleDateInput.value = formatted;
        }

        updateSaleDateTime();
        setInterval(updateSaleDateTime, 1000);
    }

});
