// ===== Kyūreki App JS =====

// --- Image toggle ---
function showOriginal() {
    document.getElementById('original').classList.add('active');
    document.getElementById('dithered').classList.remove('active');
    document.getElementById('btnOriginal').classList.add('active');
    document.getElementById('btnDithered').classList.remove('active');
}

function showDithered() {
    document.getElementById('dithered').classList.add('active');
    document.getElementById('original').classList.remove('active');
    document.getElementById('btnDithered').classList.add('active');
    document.getElementById('btnOriginal').classList.remove('active');
}

// --- Load Kyūreki data ---
async function loadKyurekiData() {
    try {
        const res = await fetch(`data.json?v=${Date.now()}`);
        const data = await res.json();

        document.getElementById('date').textContent = data.date;
        document.getElementById('rokuyo').textContent = `六曜: ${data.rokuyo}`;
        document.getElementById('original').src = `${data.image}?v=${Date.now()}`;
        document.getElementById('dithered').src = `${data.dithered_image}?v=${Date.now()}`;

        showDithered();
    } catch (err) {
        console.error("Failed to load Kyūreki data:", err);
    }
}

// --- Background based on local time ---
function updateBackground() {
    const hour = new Date().getHours();
    let bg = '#f5f5f5', text = '#333';

    if (hour >= 6 && hour < 12) { // Morning
        bg = '#fff8dc'; text = '#333';
    } else if (hour >= 12 && hour < 18) { // Afternoon
        bg = '#e0f7ff'; text = '#333';
    } else if (hour >= 18 && hour < 21) { // Evening
        bg = '#ffdab9'; text = '#fff';
    } else { // Night
        bg = '#2c3e50'; text = '#fff';
    }

    document.body.style.backgroundColor = bg;
    document.body.style.color = text;
}

// --- Load weather with scrollable hourly forecast ---
async function loadWeather() {
    const weatherDiv = document.getElementById("weather-strip");

    if (!navigator.geolocation) {
        weatherDiv.textContent = "Geolocation not supported";
        return;
    }

    navigator.geolocation.getCurrentPosition(async (pos) => {
        try {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&hourly=temperature_2m,weathercode&current_weather=true&timezone=auto`;
            const res = await fetch(url);
            const data = await res.json();

            const now = new Date();
            const currentHour = now.getHours();
            let stripHTML = `🌡️ ${data.current_weather.temperature}°C `;

            for (let i = currentHour - 3; i <= currentHour + 12; i++) {
                const hourIndex = (i + 24) % 24;
                const temp = data.hourly.temperature_2m[hourIndex];
                const code = data.hourly.weathercode[hourIndex];
                let icon = '🌤️';

                if ([0].includes(code)) icon = '☀️';
                else if ([1,2].includes(code)) icon = '🌤️';
                else if ([3].includes(code)) icon = '☁️';
                else if ([61,63,65].includes(code)) icon = '🌧️';
                else if ([71,73,75].includes(code)) icon = '❄️';

                stripHTML += `<span>${hourIndex}: ${temp}°C ${icon}</span>`;
            }

            weatherDiv.innerHTML = stripHTML;

        } catch (err) {
            console.error("Weather fetch failed:", err);
            weatherDiv.textContent = "Weather info unavailable";
        }
    }, (err) => {
        console.error("Geolocation error:", err);
        weatherDiv.textContent = "Unable to get your location";
    });
}

// --- Auto-refresh every hour ---
setInterval(loadKyurekiData, 60 * 60 * 1000);
setInterval(loadWeather, 60 * 60 * 1000);

// --- Initialize ---
window.addEventListener("load", () => {
    updateBackground();
    loadKyurekiData();
    loadWeather();
});
