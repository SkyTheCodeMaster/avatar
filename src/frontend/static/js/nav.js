fetch("/sup/navbar")
.then(res => res.text())
.then(text => {
  let oldelem = document.querySelector("script#replace_with_navbar");
  let newelem = document.createElement("div");
  newelem.innerHTML = text;
  oldelem.replaceWith(newelem);
  get_user_area();
});
fetch("/sup/footer")
.then(res => res.text())
.then(text => {
  let oldelem = document.querySelector("div#replace_with_footer");
  let newelem = document.createElement("div");
  newelem.innerHTML = text;
  oldelem.replaceWith(newelem);

  // Now that footer exists, we can fill in the details
  fetch("/api/srv/get/")
    .then(res => res.json())
    .then(data => {
      const footer_frontend_p = document.getElementById("footer_frontend_p");
      const footer_backend_p = document.getElementById("footer_backend_p");
      footer_frontend_p.innerText = format(footer_frontend_p.innerText, data["frontend_version"]);
      footer_backend_p.innerText = format(footer_backend_p.innerText, data["api_version"]);
    })
})

// Toggle button for navbar.
function toggle_navmenu(burger) {
  let navbar_menu = document.getElementById("navbar_menu");
  navbar_menu.classList.toggle("is-active");
  burger.classList.toggle("is-active");
}

function get_user_area() {
  fetch("https://auth.skystuff.cc/api/user/get/", { credentials: "include" })
    .then(res => {
      if (res.status == 200) {
        res.json().then( json => {
          const navbar_username = document.getElementById("navbar_username");
          const navbar_avatar = document.getElementById("navbar_avatar");

          navbar_username.innerText = json["name"];
          navbar_avatar.setAttribute("src", "/avatar/" + json["name"] + "?size=48");
        });
      } else {
        // User isn't logged in
        window.location.assign("https://auth.skystuff.cc/login?r=https%3A%2F%2Favatar.skystuff.cc%2F");
      }
    }).catch(err => {
      window.location.assign("https://auth.skystuff.cc/login?r=https%3A%2F%2Favatar.skystuff.cc%2F");
    });
}