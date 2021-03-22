document.addEventListener( 'DOMContentLoaded', () => {
    let filterBtn = document.getElementsByClassName('filter-btn')[0];
    filterBtn.addEventListener('click', () => {
        showElement('filter-form');
    })

    let hideFilterBtn = document.getElementsByClassName('close__filter-btn')[0];
    hideFilterBtn.addEventListener('click', () => {
        hideElement('filter-form');
    })
});


function hideElement(elementClassName) {
    let element = document.getElementsByClassName(elementClassName)[0];
    element.style.visibility = 'hidden';
}

function showElement(elementClassName) {
    let element = document.getElementsByClassName(elementClassName)[0];
    element.style.visibility = 'visible';
}

