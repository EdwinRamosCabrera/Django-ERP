const hamburgerBtn = document.getElementById("hamburger-btn");
const mobileMenu = document.getElementById("mobile-menu");
const userMenuButton = document.getElementById("user-menu-button");
const userMenuDropdown = document.getElementById("user-menu-dropdown");

// Toggle mobile menu
if(hamburgerBtn && mobileMenu){
  hamburgerBtn.addEventListener("click", () => {
    mobileMenu.classList.toggle("hidden");
  });
}

// Toggle user menu dropdown
if(userMenuButton && userMenuDropdown){
  userMenuButton.addEventListener("click", (event) => {
    userMenuDropdown.classList.toggle("hidden");
    event.stopPropagation();
  });       
}

// Close the user menu if clicking outside of it 
document.addEventListener("click", (event) => {
  if(userMenuButton && userMenuDropdown){
    if(!userMenuButton.contains(event.target) && !userMenuDropdown.contains(event.target)){
      userMenuDropdown.classList.add("hidden");
    }
  }
});

// Ensure the user menu is hidden on initial load
document.addEventListener("DOMContentLoaded", () => {
    if(userMenuDropdown){
        userMenuDropdown.classList.add("hidden");       
    }
});