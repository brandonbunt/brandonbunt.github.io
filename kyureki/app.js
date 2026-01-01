// Local date (viewer’s timezone)
const dateEl = document.getElementById("date");
const today = new Date();

dateEl.textContent = today.toLocaleDateString(undefined, {
  weekday: "long",
  year: "numeric",
  month: "long",
  day: "numeric"
});

// Rokuyo from generated data
fetch("data.json")
  .then(res => res.json())
  .then(data => {
    document.getElementById("rokuyo").textContent =
      `六曜: ${data.rokuyo}`;
  })
  .catch(() => {
    document.getElementById("rokuyo").textContent =
      "六曜: —";
  });
