const DEVICE_ID = "motor_01";

function update() {
  fetch("/api/latest")
    .then(r => r.json())
    .then(d => {
      if (d.status === "NO_DATA") return;

      document.getElementById("voltage").innerText =
        d.U.map(v => v.toFixed(1)).join(" | ");

      document.getElementById("current").innerText =
        d.I.map(i => i.toFixed(2)).join(" | ");

      let status = "NORMAL";
      let cls = "ok";

      if (d.fault.length > 0) {
        status = d.fault.join(", ");
        cls = d.fault.includes("Mất pha") ? "crit" : "warn";
      }

      document.getElementById("status").innerHTML =
        `<span class="${cls}">${status}</span>`;
    });
}

function cutPower() {
  fetch(`/api/manual_cut/${DEVICE_ID}`, { method: "POST" })
    .then(() => alert("Đã gửi lệnh NGẮT TẢI"));
}

setInterval(update, 2000);
update();
