var sha256 = require("@aws-crypto/sha256-browser")

let user_details;

const AvatarType = {
  "0": "default",
  "1": "url",
  "2": "gravatar",
  "3": "retro",
  "4": "identicon",
  "5": "monsterid",
  "6": "wavatar",
  "7": "robohash"
}

async function hash(email) {
  let s = new sha256.Sha256();
  s.update(email.toLowerCase().trim());
  let result = await s.digest();
  return Array.from(result).map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function setup() {
  try {
    user_details = await get_user_details(false);

    const avatar_box = document.getElementById("avatar_box");
    avatar_box.setAttribute("src",format("/avatar/{0}?size=320", user_details["name"]));
    format_element_text("avatar_for_h1", user_details["name"]);

  } catch (e) {
    show_popup("Failed to load user!", true, 5000);
    console.error(e);
  }

  const avatar_type_select = document.getElementById("avatar_type_select");
  const avatar_url_text = document.getElementById("avatar_url_text");
  const preview_avatar_box = document.getElementById("preview_avatar_box");
  let hashed_email = await hash(user_details["email"]);
  avatar_type_select.addEventListener("change", function(ev) {
    // Check if the option is 1 (URL)
    console.log(avatar_type_select.value)
    if (avatar_type_select.value === "1") {
      avatar_url_text.removeAttribute("disabled");
    } else {
      avatar_url_text.setAttribute("disabled",true);
      preview_avatar_box.setAttribute("src", format("/preview/{0}?size=320&style={1}", hashed_email, AvatarType[avatar_type_select.value]))
    }

  });

  preview_avatar_box.setAttribute("src", format("/preview/{0}?size=320&type={1}", hashed_email, AvatarType[avatar_type_select.value]))

  const set_avatar_button = document.getElementById("set_avatar_button");
  set_avatar_button.onclick = async function() { await set_avatar(set_avatar_button); }
}

async function set_avatar(button) {
  button.classList.add("is-loading");
  button.setAttribute("disabled",true);

  try {
    const avatar_type_select = document.getElementById("avatar_type_select");
    const avatar_url_text = document.getElementById("avatar_url_text");
    let packet = {
      "type": Number(avatar_type_select.value),
    }
    if (avatar_type_select.value === "1") {
      packet["url"] = avatar_url_text.value;
    }

    let request = await fetch("/api/user/set/", {
      "method": "POST",
      "body": JSON.stringify(packet),
      "headers": {
        "Authorization": "Bearer " + user_details["token"]
      }
    });

    if (request.status == 200) {
      show_popup("Set avatar!", false, 5000);
    } else {
      show_popup("Failed to set avatar. HTTP" + request.status, true, 5000);
    }
  } catch (e) {
    show_popup("Failed to set avatar! " + e, true, 5000);
    console.error(e);
  }

  button.classList.remove("is-loading");
  button.removeAttribute("disabled");
}

if (document.readyState == "loading") {
  document.addEventListener("DOMContentLoaded", setup);
} else {
  setup();
}