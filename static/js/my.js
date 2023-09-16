var nav = document.querySelector("nav");

window.addEventListener("scroll", function () {
  if (this.window.pageYOffset > 100) {
    nav.classList.add("warnavbar", "shadow");
  } else {
    nav.classList.remove("warnavbar", "shadow");
  }
});
