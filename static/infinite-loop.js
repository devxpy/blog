(function () {
for (let outer of document.querySelectorAll(".infinite-loop--outer")) {
    let content = outer.querySelector('.infinite-loop--content');
    repeatContent(content, outer.offsetWidth);

    let el = outer.querySelector('.infinite-loop');
    el.innerHTML = el.innerHTML + el.innerHTML;
}

function repeatContent(el, till) {
    let html = el.innerHTML;
    let counter = 0;
    while (el.offsetWidth < till || counter > 500) {
        el.innerHTML += html;
        counter += 1;
    }
}
})();

    let content = outer.querySelector('#content');
    repeatContent(content, outer.offsetWidth);

    let el = outer.querySelector('#loop');
    el.innerHTML = el.innerHTML + el.innerHTML;