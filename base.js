window.onload = function() {
	for (let elem of document.querySelectorAll("[data-show-localdate]")) {
		let sec = elem.getAttribute("data-time-sec");
		let date = new Date(parseFloat(sec) * 1000);
		elem.innerHTML = date.toLocaleString(undefined, {
			month: "long",
			year: "numeric",
			day: "numeric"
		});
	}
};
