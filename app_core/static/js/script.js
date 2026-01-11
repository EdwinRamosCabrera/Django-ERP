const hamburgerBtn = document.querySelector("hamburger-btn");
const mobileMenu = document.querySelector("mobile-menu");
const userMenuButton = document.querySelector("user-menu-button");
const userMenuDropdown = document.querySelector("user-menu-dropdown");

if(hamburgerBtn && mobileMenu){
  hamburgerBtn.addEventListener("click", () => {
    mobileMenu.classList.toggle("hidden");
  });
}

if(userMenuButton && userMenuDropdown){
  userMenuButton.addEventListener("click", (event) => {
    userMenuDropdown.classList.toggle("hidden");
    event.stopPropagation();
  });       
}

document.addEventListener("click", (event) => {
  if(userMenuButton && userMenuDropdown){
    if(!userMenuButton.contains(event.target) && !userMenuDropdown.contains(event.target)){
      userMenuDropdown.classList.add("hidden");
    }
  }
});

document.addEventListener("DOMContentLoaded", () => {
    if(userMenuDropdown){
        userMenuDropdown.classList.add("hidden");       
    }
});