// ===== Kyūreki App JavaScript =====

// --- Image toggle functions ---
function showOriginal() {
    const original = document.getElementById('original');
    const dithered = document.getElementById('dithered');
    original.classList.add('active');
    dithered.classList.remove('active');
    document.getElementById('btnOriginal').classList.add('active');
    document.getElementById('btnDithered').classList.remove('active');
}

function showDithered() {
    const original = document.getElementById('original');
    const dithered = document.getElementById('dithered');
    dithered.classList.add('active');
    original.classList.remove('active');
    document.getElementById('btnDithered').classList.add('active');
    document.getElementById('btnOriginal').classList.remove('active');
}

// --- Load Kyūreki data from data.json ---
async function loadKyurekiData() {
    try {
        const res = await fetch('data.json');
        const data = await res.json();

        // Update date and rokuyo
        document.getElementById('date').textContent = data.date;
        document.getElementById('rokuyo').textContent = `六曜: ${data.rokuyo}`;

        // Update images
        document.getElementById('original').src = data.image;
        document.getElementById('dithered').src = data.dithered_image;

        // Show dithered by default
        showDithered();
    } catch (err) {
        console.error("Failed to load Kyūreki data:", err);
    }
}

// --- Load weather using user's location ---
async function loadWeather() {
    const weatherDiv = document.getElementById("weather-strip");

    if (!navigator.geolocation) {
        weatherDiv.textContent = "Geolocation not supported by your browser";
        return;
    }

    navigator.geolocation.getCurrentPosition(async (position) => {
        try {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            const url = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current_weather=true`;

            const res = await fetch(url);
            const data = await res.json();

            const weather = data.current_weather;
            const temp = weather.temperature;
            const wind = weather.windspeed;

            weatherDiv.textContent = `🌤️ Temperature: ${temp}°C, Wind: ${wind} km/h`;

        } catch (err) {
            console.error("Failed to fetch weather:", err);
            weatherDiv.textContent = "Weather info unavailable";
        }
    }, (error) => {
        console.error("Geolocation error:", error);
        weatherDiv.textContent = "Unable to get your location";
    });
}

// --- Initialize everything on page load ---
window.addEventListener("load", () => {
    loadKyurekiData();
    loadWeather();
});
