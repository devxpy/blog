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
        while (el.offsetWidth < till && counter < 100) {
            el.innerHTML += html;
            console.log(el.offsetWidth, till);
            counter += 1;
        }
    }
})();