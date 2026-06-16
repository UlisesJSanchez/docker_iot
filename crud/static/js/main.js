
const btnDelete= document.querySelectorAll('.btn-borrar');
if(btnDelete) {
  const btnArray = Array.from(btnDelete);
  btnArray.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      if(!confirm('¿Está seguro de querer borrar?')){
        e.preventDefault();
      }
    });
  })
}

document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("theme-toggle");
    const themeStyle = document.getElementById("theme-style");
    
    const lightThemeUrl = "https://bootswatch.com/5/cosmo/bootstrap.min.css";
    const darkThemeUrl = "https://bootswatch.com/5/darkly/bootstrap.min.css";

    const savedTheme = localStorage.getItem("theme") || "light";

    const applyTheme = (theme) => {
        if (theme === "dark") {
            themeStyle.setAttribute("href", darkThemeUrl);
            themeToggle.className = "btn btn-light me-4";
            themeToggle.textContent = "Light";
        } else {
            themeStyle.setAttribute("href", lightThemeUrl);
            themeToggle.className = "btn btn-dark me-4";
            themeToggle.textContent = "Dark";
        }
    };

    applyTheme(savedTheme);

    themeToggle.addEventListener("click", () => {
        const currentTheme = themeStyle.getAttribute("href") === lightThemeUrl ? "light" : "dark";
        const newTheme = currentTheme === "light" ? "dark" : "light";
        
        applyTheme(newTheme);
        localStorage.setItem("theme", newTheme);
    });
});