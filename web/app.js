fetch("/api/data")
  .then(r => r.json())
  .then(d => {
    document.getElementById("status").innerHTML =
      d.fault.length ? "⚠️ " + d.fault.join(", ") : "✅ Normal";
  });
