function notify(message, type = "info", timeout = 3000) {
  const box = document.createElement("div");
  box.className = "notify " + type;
  box.innerText = message;

  document.getElementById("notify-container").appendChild(box);

  setTimeout(() => {
    box.style.opacity = "0";
    setTimeout(() => box.remove(), 300);
  }, timeout);
}
setTimeout(() => {
  el.classList.add("hide");
  setTimeout(() => el.remove(), 350);
}, 3500); // เวลาโชว์รวม
