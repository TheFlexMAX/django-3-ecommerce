//FIXME: Добавить рендер на событие нажатий кнопок покупки товара
let updateButtons = document.getElementsByClassName('update-cart');


for (let i = 0; i < updateButtons.length; i++) {
    updateButtons[i].addEventListener('click', () => {
        let btn = updateButtons[i];
        let productId = btn.dataset.goods_id;
        let action = btn.dataset.action;

        if (user === 'AnonymousUser') {
            addCookieItem(productId, action);
        }
    });
}

function addCookieItem(productId, action) {

    if (action === 'addToCart') {
        if (cart[productId] === undefined) {
            cart[productId] = {'qty': 1};
        } else {
            cart[productId]['qty'] += 1;
        }
    }

    if (action === 'remove') {
        cart[productId]['qty'] -= 1;

        if (cart[productId]['qty'] <= 0) {
            delete cart[productId];
        }
    }

    document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";
    location.reload();
}
