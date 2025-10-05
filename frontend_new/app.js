// Global state
const state = {
    currentStep: 1,
    location: { name: '', lat: 41.8781, lng: -87.6298 },
    profile: { type: '', name: '', details: {} },
    dates: { mode: 'single', start: '', end: '', time: '20:00' }
};

// API Configuration
// Will be overridden by azure-api-config.js in production
const API_URL = window.API_URL || 'http://localhost:8000';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    setMinDate();
    updateStep(1);
});

// Map initialization
let map, marker;

function initMap() {
    map = L.map('map').setView([state.location.lat, state.location.lng], 10);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    marker = L.marker([state.location.lat, state.location.lng], { draggable: true }).addTo(map);
    
    marker.on('dragend', function(e) {
        const pos = marker.getLatLng();
        state.location.lat = pos.lat;
        state.location.lng = pos.lng;
        updateLocationDisplay();
    });
    
    map.on('click', function(e) {
        marker.setLatLng(e.latlng);
        state.location.lat = e.latlng.lat;
        state.location.lng = e.latlng.lng;
        updateLocationDisplay();
    });
    
    // Default location
    state.location.name = 'Chicago, IL';
    updateLocationDisplay();
}

function updateLocationDisplay() {
    document.getElementById('location-name').textContent = state.location.name || 'Custom Location';
    document.getElementById('location-coords').textContent = 
        `${state.location.lat.toFixed(4)}° N, ${state.location.lng.toFixed(4)}° W`;
}

// Location search
document.getElementById('search-btn').addEventListener('click', searchLocation);
document.getElementById('location-search').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchLocation();
});

async function searchLocation() {
    const query = document.getElementById('location-search').value;
    if (!query) return;
    
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)},USA&limit=1`);
        const data = await response.json();
        
        if (data && data.length > 0) {
            const result = data[0];
            state.location.lat = parseFloat(result.lat);
            state.location.lng = parseFloat(result.lon);
            state.location.name = result.display_name;
            
            map.setView([state.location.lat, state.location.lng], 12);
            marker.setLatLng([state.location.lat, state.location.lng]);
            updateLocationDisplay();
        } else {
            alert('Location not found. Please try another search.');
        }
    } catch (error) {
        console.error('Search error:', error);
        alert('Error searching for location.');
    }
}

// Activity selection
function selectActivity(type) {
    // Remove previous selection
    document.querySelectorAll('.activity-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Select new activity
    event.target.closest('.activity-card').classList.add('selected');
    
    const profiles = {
        beach: { name: 'Beach Day', tempMin: 75, tempMax: 90, precip: 'none', wind: 15, clouds: 'clear', humidity: 70 },
        hiking: { name: 'Hiking', tempMin: 55, tempMax: 75, precip: 'none', wind: 20, clouds: 'light', humidity: 60 },
        skiing: { name: 'Skiing', tempMin: 20, tempMax: 40, precip: 'any', wind: 25, clouds: 'any', humidity: 50 },
        rain: { name: 'Rain Dancing', tempMin: 60, tempMax: 75, precip: 'any', wind: 15, clouds: 'cloudy', humidity: 90 },
        sailing: { name: 'Sailing', tempMin: 65, tempMax: 80, precip: 'drizzle', wind: 30, clouds: 'light', humidity: 65 }
    };
    
    if (type === 'custom') {
        document.getElementById('custom-profile-form').classList.remove('hidden');
        state.profile.type = 'custom';
        state.profile.name = 'Custom Profile';
    } else {
        document.getElementById('custom-profile-form').classList.add('hidden');
        state.profile.type = type;
        state.profile.name = profiles[type].name;
        state.profile.details = profiles[type];
    }
}

// Custom profile updates
function updateTempRange() {
    const min = document.getElementById('temp-min').value;
    const max = document.getElementById('temp-max').value;
    document.getElementById('temp-range-display').textContent = `${min}-${max}°F`;
    state.profile.details.tempMin = parseInt(min);
    state.profile.details.tempMax = parseInt(max);
}

function updateWindSpeed() {
    const wind = document.getElementById('wind-speed').value;
    document.getElementById('wind-display').textContent = `${wind} mph`;
    state.profile.details.wind = parseInt(wind);
}

function updateHumidity() {
    const humidity = document.getElementById('humidity').value;
    document.getElementById('humidity-display').textContent = `${humidity}%`;
    state.profile.details.humidity = parseInt(humidity);
}

function showPresets() {
    document.getElementById('custom-profile-form').classList.add('hidden');
    document.querySelectorAll('.activity-card').forEach(card => {
        card.classList.remove('selected');
    });
}

// Date selection
function setDateMode(mode) {
    state.dates.mode = mode;
    
    document.querySelectorAll('.btn-mode').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    if (mode === 'single') {
        document.getElementById('single-date-picker').classList.remove('hidden');
        document.getElementById('range-date-picker').classList.add('hidden');
        document.getElementById('general-date-options').classList.add('hidden');
    } else {
        document.getElementById('single-date-picker').classList.add('hidden');
        document.getElementById('range-date-picker').classList.remove('hidden');
    }
}

function showGeneralOptions() {
    document.getElementById('general-date-options').classList.remove('hidden');
}

function hideGeneralOptions() {
    document.getElementById('general-date-options').classList.add('hidden');
}

function setMinDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('single-date').min = today;
    document.getElementById('start-date').min = today;
    document.getElementById('end-date').min = today;
}

// Step navigation
function updateStep(step) {
    state.currentStep = step;
    
    // Update progress indicators
    document.querySelectorAll('.step').forEach((el, index) => {
        el.classList.remove('active', 'completed');
        if (index + 1 === step) {
            el.classList.add('active');
        } else if (index + 1 < step) {
            el.classList.add('completed');
        }
    });
    
    // Show/hide content
    document.querySelectorAll('.step-content').forEach(el => el.classList.add('hidden'));
    
    const contentMap = {
        1: 'content-location',
        2: 'content-profile',
        3: 'content-dates',
        4: 'content-confirm'
    };
    
    document.getElementById(contentMap[step]).classList.remove('hidden');
    
    // Update confirmation if on step 4
    if (step === 4) {
        updateConfirmation();
    }
}

function nextStep() {
    if (validateCurrentStep()) {
        updateStep(state.currentStep + 1);
    }
}

function prevStep() {
    if (state.currentStep > 1) {
        updateStep(state.currentStep - 1);
    }
}

function validateCurrentStep() {
    switch (state.currentStep) {
        case 1:
            if (!state.location.name) {
                alert('Please select a location');
                return false;
            }
            return true;
        case 2:
            if (!state.profile.type) {
                alert('Please select an activity profile');
                return false;
            }
            return true;
        case 3:
            if (state.dates.mode === 'single') {
                const date = document.getElementById('single-date').value;
                const time = document.getElementById('single-time').value;
                if (!date) {
                    alert('Please select a date');
                    return false;
                }
                state.dates.start = date;
                state.dates.time = time;
            } else {
                const start = document.getElementById('start-date').value;
                const end = document.getElementById('end-date').value;
                if (!start || !end) {
                    alert('Please select start and end dates');
                    return false;
                }
                if (new Date(end) < new Date(start)) {
                    alert('End date must be after start date');
                    return false;
                }
                state.dates.start = start;
                state.dates.end = end;
            }
            return true;
        default:
            return true;
    }
}

function updateConfirmation() {
    // Location
    document.getElementById('confirm-location').textContent = state.location.name;
    document.getElementById('confirm-coords').textContent = 
        `${state.location.lat.toFixed(4)}° N, ${state.location.lng.toFixed(4)}° W`;
    
    // Profile
    document.getElementById('confirm-profile-name').textContent = state.profile.name;
    const details = state.profile.details;
    document.getElementById('confirm-profile-details').innerHTML = `
        Temp: ${details.tempMin}-${details.tempMax}°F<br>
        Precipitation: ${details.precip || 'any'}<br>
        Maximum wind speed: ${details.wind || 30} mph<br>
        Cloud cover: ${details.clouds || 'any'}<br>
        Maximum humidity: ${details.humidity || 87}%
    `;
    
    // Dates
    if (state.dates.mode === 'single') {
        document.getElementById('confirm-dates').textContent = 
            `${state.dates.start} at ${state.dates.time}`;
    } else {
        document.getElementById('confirm-dates').textContent = 
            `${state.dates.start} - ${state.dates.end}`;
    }
}

// Generate report
async function generateReport() {
    // Show results page
    document.getElementById('content-confirm').classList.add('hidden');
    document.getElementById('content-results').classList.remove('hidden');
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results-container').classList.add('hidden');
    
    try {
        let weatherData;
        
        if (state.dates.mode === 'single') {
            // Single date/time prediction
            const hour = parseInt(state.dates.time.split(':')[0]);
            weatherData = await fetchHourlyWeather(state.dates.start, hour);
            displaySingleDayResults(weatherData);
        } else {
            // Date range prediction
            weatherData = await fetchRangeWeather(state.dates.start, state.dates.end);
            displayRangeResults(weatherData);
        }
        
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('results-container').classList.remove('hidden');
    } catch (error) {
        console.error('Error generating report:', error);
        document.getElementById('loading').innerHTML = `
            <p style="color: red;">Error generating report. Please make sure the backend server is running.</p>
            <p>Start the server with: <code>python backend/simple_server.py</code></p>
        `;
    }
}

async function fetchHourlyWeather(date, hour) {
    const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date, hour })
    });
    
    if (!response.ok) throw new Error('API request failed');
    return await response.json();
}

async function fetchRangeWeather(startDate, endDate) {
    const response = await fetch(`${API_URL}/predict-range`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start_date: startDate, end_date: endDate })
    });
    
    if (!response.ok) throw new Error('API request failed');
    return await response.json();
}

function displaySingleDayResults(data) {
    const container = document.getElementById('results-container');
    
    const suitability = checkSuitability(data);
    const breakdown = calculateScoreBreakdown(data);
    const avatar = getWeatherAvatar(data);
    
    container.innerHTML = `
        <div class="climatology-report">
            <div class="report-header">
                <div class="score-circle" style="border-color: ${suitability.color};">
                    <div class="score-number" style="color: ${suitability.color};">${suitability.score}</div>
                </div>
                <div class="report-title">
                    <h2>Climatology Report for ${state.profile.name}</h2>
                    <p class="report-subtitle">at ${state.location.name}</p>
                    <p class="report-date">on ${data.date} at ${data.hour}:00</p>
                    <p class="report-note">Score shown on the left. Weather conditions analyzed below.</p>
                </div>
            </div>
            
            <div class="score-breakdown">
                <div class="weather-avatar">
                    <div class="avatar-container">
                        ${avatar.html}
                        <p style="text-align: center; margin-top: 10px; font-size: 12px; color: #666;">${avatar.description}</p>
                    </div>
                </div>
                <div class="breakdown-bar">
                    <div class="bar-segment cloud-segment" style="height: ${breakdown.cloud}%">
                        <span class="segment-label">Cloud Cover — ${breakdown.cloud}%</span>
                    </div>
                    <div class="bar-segment uv-segment" style="height: ${breakdown.uv}%">
                        <span class="segment-label">Wind — ${breakdown.uv}%</span>
                    </div>
                    <div class="bar-segment aqi-segment" style="height: ${breakdown.aqi}%">
                        <span class="segment-label">AQI — ${breakdown.aqi}%</span>
                    </div>
                    <div class="bar-segment humidity-segment" style="height: ${breakdown.humidity}%">
                        <span class="segment-label">Humidity — ${breakdown.humidity}%</span>
                    </div>
                    <div class="bar-segment precip-segment" style="height: ${breakdown.precip}%">
                        <span class="segment-label">Precipitation — ${breakdown.precip}%</span>
                    </div>
                    <div class="bar-segment temp-segment" style="height: ${breakdown.temp}%">
                        <span class="segment-label">Temperature — ${breakdown.temp}%</span>
                    </div>
                </div>
            </div>
            
            <div class="weather-summary">
                <p><strong>Weather Details:</strong></p>
                <div class="summary-grid">
                    <div class="summary-item">
                        <span class="summary-icon">🌡️</span>
                        <span class="summary-label">Temperature:</span>
                        <span class="summary-value">${data.temperature_f}°F (${data.temperature_c}°C)</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-icon">🤔</span>
                        <span class="summary-label">Feels Like:</span>
                        <span class="summary-value">${data.feels_like_f}°F (${data.feels_like_c}°C)</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-icon">🌧️</span>
                        <span class="summary-label">Precipitation:</span>
                        <span class="summary-value">${data.precipitation_mm} mm</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-icon">💧</span>
                        <span class="summary-label">Humidity:</span>
                        <span class="summary-value">${data.humidity_percent}%</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-icon">☁️</span>
                        <span class="summary-label">Cloud Cover:</span>
                        <span class="summary-value">${data.cloud_cover_percent}%</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-icon">💨</span>
                        <span class="summary-label">Wind Speed:</span>
                        <span class="summary-value">${data.wind_speed_mph} mph</span>
                    </div>
                </div>
            </div>
            
            <div class="recommendation">
                <p><strong>${suitability.message}</strong></p>
                <p style="margin-top: 10px; color: #666;">${data.description}</p>
            </div>
            
            <div class="action-buttons">
                <button class="btn-check-date" onclick="resetApp()">Check another date</button>
                <button class="btn-export" onclick="exportReport()">📥 Export to CSV</button>
            </div>
        </div>
    `;
}

function calculateScoreBreakdown(data) {
    // Calculate contribution of each factor to the overall score
    const profile = state.profile.details;
    
    // Temperature contribution (30%)
    const temp = data.temperature_f || data.avg_temperature_f;
    let tempScore = 30;
    if (temp < profile.tempMin || temp > profile.tempMax) {
        const diff = Math.min(Math.abs(temp - profile.tempMin), Math.abs(temp - profile.tempMax));
        tempScore = Math.max(0, 30 - (diff * 0.6));
    }
    
    // Precipitation contribution (20%)
    const precip = data.precipitation_mm || data.total_precipitation_mm || 0;
    let precipScore = 20;
    if (profile.precip === 'none' && precip > 1) {
        precipScore = Math.max(0, 20 - (precip * 2));
    }
    
    // Humidity contribution (15%)
    const humidity = data.humidity_percent || data.avg_humidity_percent;
    let humidityScore = 15;
    if (humidity > profile.humidity) {
        humidityScore = Math.max(0, 15 - ((humidity - profile.humidity) * 0.15));
    }
    
    // AQI contribution (10%) - mock for now
    const aqiScore = 10;
    
    // Wind/UV contribution (15%)
    const wind = data.wind_speed_mph || data.avg_wind_speed_mph;
    let uvScore = 15;
    if (wind > profile.wind) {
        uvScore = Math.max(0, 15 - ((wind - profile.wind) * 0.3));
    }
    
    // Cloud cover contribution (10%)
    const clouds = data.cloud_cover_percent || data.avg_cloud_cover_percent;
    let cloudScore = 10;
    if (profile.clouds === 'clear' && clouds > 25) {
        cloudScore = Math.max(0, 10 - ((clouds - 25) * 0.1));
    }
    
    return {
        temp: Math.round(tempScore),
        precip: Math.round(precipScore),
        humidity: Math.round(humidityScore),
        aqi: Math.round(aqiScore),
        uv: Math.round(uvScore),
        cloud: Math.round(cloudScore)
    };
}

function getWeatherAvatar(data) {
    const temp = data.temperature_f || data.avg_temperature_f;
    const precip = data.precipitation_mm || data.total_precipitation_mm || 0;
    const wind = data.wind_speed_mph || data.avg_wind_speed_mph;
    const clouds = data.cloud_cover_percent || data.avg_cloud_cover_percent;
    
    let outfit = '';
    let accessories = '';
    let description = '';
    
    // Determine outfit based on temperature
    if (temp < 32) {
        // Freezing - Heavy winter clothes
        outfit = '🧥'; // Winter coat
        accessories = '🧣🧤'; // Scarf and gloves
        description = 'Bundle up! Heavy winter gear needed.';
    } else if (temp < 50) {
        // Cold - Jacket and layers
        outfit = '🧥';
        accessories = '🧣';
        description = 'Wear a warm jacket and scarf.';
    } else if (temp < 65) {
        // Cool - Light jacket
        outfit = '👔';
        accessories = '';
        description = 'Light jacket or sweater recommended.';
    } else if (temp < 75) {
        // Comfortable - Regular clothes
        outfit = '👕';
        accessories = '';
        description = 'Perfect weather! Regular clothes are fine.';
    } else if (temp < 85) {
        // Warm - Light clothes
        outfit = '👕';
        accessories = '🕶️';
        description = 'Wear light, breathable clothing.';
    } else {
        // Hot - Very light clothes
        outfit = '🩳';
        accessories = '🕶️🧢';
        description = 'Stay cool! Shorts and sun protection.';
    }
    
    // Add rain gear if precipitation
    if (precip > 5) {
        accessories += '☂️';
        description += ' Bring an umbrella!';
    } else if (precip > 1) {
        accessories += '🌂';
        description += ' Light rain possible.';
    }
    
    // Add wind protection
    if (wind > 25) {
        description += ' Windy conditions!';
    }
    
    // Add sun protection for clear days
    if (clouds < 30 && temp > 70) {
        accessories += '🧴';
        description += ' Use sunscreen!';
    }
    
    // Build avatar HTML
    const html = `
        <div style="font-size: 120px; text-align: center; position: relative;">
            <div style="margin-bottom: -20px;">😊</div>
            <div style="font-size: 100px;">${outfit}</div>
            ${accessories ? `<div style="font-size: 60px; margin-top: -10px;">${accessories}</div>` : ''}
        </div>
    `;
    
    return { html, description };
}

function exportReport() {
    alert('Export functionality coming soon! This will generate a CSV file with your weather report.');
}

function displayRangeResults(data) {
    const container = document.getElementById('results-container');
    
    // Calculate averages across all days
    const avgData = {
        avg_temperature_f: data.reduce((sum, d) => sum + d.avg_temperature_f, 0) / data.length,
        total_precipitation_mm: data.reduce((sum, d) => sum + d.total_precipitation_mm, 0) / data.length,
        avg_humidity_percent: data.reduce((sum, d) => sum + d.avg_humidity_percent, 0) / data.length,
        avg_cloud_cover_percent: data.reduce((sum, d) => sum + d.avg_cloud_cover_percent, 0) / data.length,
        avg_wind_speed_mph: data.reduce((sum, d) => sum + d.avg_wind_speed_mph, 0) / data.length,
        avg_temperature_c: data.reduce((sum, d) => sum + d.avg_temperature_c, 0) / data.length,
        avg_feels_like_f: data.reduce((sum, d) => sum + d.avg_feels_like_f, 0) / data.length,
        avg_feels_like_c: data.reduce((sum, d) => sum + d.avg_feels_like_c, 0) / data.length
    };
    
    const suitability = checkSuitability(avgData);
    const breakdown = calculateScoreBreakdown(avgData);
    const avatar = getWeatherAvatar(avgData);
    
    const startDate = data[0].date;
    const endDate = data[data.length - 1].date;
    
    container.innerHTML = `
        <div class="climatology-report">
            <div class="report-header">
                <div class="score-circle" style="border-color: ${suitability.color};">
                    <div class="score-number" style="color: ${suitability.color};">${suitability.score}</div>
                </div>
                <div class="report-title">
                    <h2>Climatology Report for ${state.profile.name}</h2>
                    <p class="report-subtitle">at ${state.location.name}</p>
                    <p class="report-date">from ${startDate} to ${endDate}</p>
                    <p class="report-note">Score shown on the left. Average conditions across ${data.length} days.</p>
                </div>
            </div>
            
            <div class="score-breakdown">
                <div class="weather-avatar">
                    <div class="avatar-container">
                        ${avatar.html}
                        <p style="text-align: center; margin-top: 10px; font-size: 12px; color: #666;">${avatar.description}</p>
                    </div>
                </div>
                <div class="breakdown-bar">
                    <div class="bar-segment cloud-segment" style="height: ${breakdown.cloud}%">
                        <span class="segment-label">Cloud Cover — ${breakdown.cloud}%</span>
                    </div>
                    <div class="bar-segment uv-segment" style="height: ${breakdown.uv}%">
                        <span class="segment-label">Wind — ${breakdown.uv}%</span>
                    </div>
                    <div class="bar-segment aqi-segment" style="height: ${breakdown.aqi}%">
                        <span class="segment-label">AQI — ${breakdown.aqi}%</span>
                    </div>
                    <div class="bar-segment humidity-segment" style="height: ${breakdown.humidity}%">
                        <span class="segment-label">Humidity — ${breakdown.humidity}%</span>
                    </div>
                    <div class="bar-segment precip-segment" style="height: ${breakdown.precip}%">
                        <span class="segment-label">Precipitation — ${breakdown.precip}%</span>
                    </div>
                    <div class="bar-segment temp-segment" style="height: ${breakdown.temp}%">
                        <span class="segment-label">Temperature — ${breakdown.temp}%</span>
                    </div>
                </div>
            </div>
            
            <div class="weather-summary">
                <p><strong>Average Weather Conditions (${data.length} days):</strong></p>
                <div class="summary-grid">
                    <div class="summary-item">
                        <span class="summary-icon">🌡️</span>
                        <span class="summary-label">Avg Temperature:</span>
                        <span class="summary-value">${avgData.avg_temperature_f.toFixed(1)}°F (${avgData.avg_temperature_c.toFixed(1)}°C)</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-icon">🤔</span>
                        <span class="summary-label">Avg Feels Like:</span>
                        <span class="summary-value">${avgData.avg_feels_like_f.toFixed(1)}°F (${avgData.avg_feels_like_c.toFixed(1)}°C)</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-icon">🌧️</span>
                        <span class="summary-label">Avg Precipitation:</span>
                        <span class="summary-value">${avgData.total_precipitation_mm.toFixed(2)} mm/day</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-icon">💧</span>
                        <span class="summary-label">Avg Humidity:</span>
                        <span class="summary-value">${avgData.avg_humidity_percent.toFixed(1)}%</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-icon">☁️</span>
                        <span class="summary-label">Avg Cloud Cover:</span>
                        <span class="summary-value">${avgData.avg_cloud_cover_percent.toFixed(1)}%</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-icon">💨</span>
                        <span class="summary-label">Avg Wind Speed:</span>
                        <span class="summary-value">${avgData.avg_wind_speed_mph.toFixed(1)} mph</span>
                    </div>
                </div>
            </div>
            
            <div class="recommendation ${suitability.score < 60 ? (suitability.score < 40 ? 'danger' : 'warning') : ''}">
                <p><strong>${suitability.message}</strong></p>
                <p style="margin-top: 10px; color: #666;">Based on ${data.length} days of weather predictions</p>
            </div>
            
            <div class="daily-breakdown" style="margin-top: 30px;">
                <h3 style="margin-bottom: 15px; color: #b8a76f;">📅 Daily Breakdown</h3>
                <div style="display: grid; gap: 15px;">
                    ${data.map(day => {
                        const daySuitability = checkSuitability(day);
                        return `
                            <div class="weather-day" style="border-left-color: ${daySuitability.color};">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                    <h4 style="margin: 0;">${day.date}</h4>
                                    <div style="background: ${daySuitability.color}; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 14px;">
                                        ${daySuitability.score}%
                                    </div>
                                </div>
                                <div style="display: flex; gap: 20px; flex-wrap: wrap; font-size: 14px;">
                                    <span>🌡️ ${day.avg_temperature_f.toFixed(1)}°F</span>
                                    <span>🌧️ ${day.total_precipitation_mm.toFixed(1)}mm</span>
                                    <span>💧 ${day.avg_humidity_percent.toFixed(0)}%</span>
                                    <span>☁️ ${day.avg_cloud_cover_percent.toFixed(0)}%</span>
                                    <span>💨 ${day.avg_wind_speed_mph.toFixed(1)}mph</span>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
            
            <div class="action-buttons">
                <button class="btn-check-date" onclick="resetApp()">Check another date</button>
                <button class="btn-export" onclick="exportReport()">📥 Export to CSV</button>
            </div>
        </div>
    `;
}

function checkSuitability(weather) {
    const profile = state.profile.details;
    let score = 100;
    let reasons = [];
    
    // Check temperature
    const temp = weather.temperature_f || weather.avg_temperature_f;
    if (temp < profile.tempMin || temp > profile.tempMax) {
        const diff = Math.min(Math.abs(temp - profile.tempMin), Math.abs(temp - profile.tempMax));
        score -= Math.min(diff * 2, 40);
        reasons.push('temperature outside ideal range');
    }
    
    // Check precipitation
    const precip = weather.precipitation_mm || weather.total_precipitation_mm || 0;
    if (profile.precip === 'none' && precip > 1) {
        score -= 20;
        reasons.push('unwanted precipitation');
    }
    
    // Check wind
    const wind = weather.wind_speed_mph || weather.avg_wind_speed_mph;
    if (wind > profile.wind) {
        score -= Math.min((wind - profile.wind) * 2, 20);
        reasons.push('wind too strong');
    }
    
    // Check humidity
    const humidity = weather.humidity_percent || weather.avg_humidity_percent;
    if (humidity > profile.humidity) {
        score -= Math.min((humidity - profile.humidity) / 2, 15);
        reasons.push('humidity too high');
    }
    
    score = Math.max(0, Math.round(score));
    
    let message, color;
    if (score >= 80) {
        message = '✅ Excellent conditions for your activity!';
        color = '#28a745';
    } else if (score >= 60) {
        message = '👍 Good conditions, minor issues: ' + reasons.join(', ');
        color = '#ffc107';
    } else if (score >= 40) {
        message = '⚠️ Fair conditions, some concerns: ' + reasons.join(', ');
        color = '#fd7e14';
    } else {
        message = '❌ Poor conditions: ' + reasons.join(', ');
        color = '#dc3545';
    }
    
    return { score, message, color };
}

function resetApp() {
    state.currentStep = 1;
    state.location = { name: '', lat: 41.8781, lng: -87.6298 };
    state.profile = { type: '', name: '', details: {} };
    state.dates = { mode: 'single', start: '', end: '', time: '20:00' };
    
    document.querySelectorAll('.activity-card').forEach(card => card.classList.remove('selected'));
    document.getElementById('custom-profile-form').classList.add('hidden');
    
    updateStep(1);
}


// Chatbot functionality
let conversationHistory = [];
let chatbotMinimized = false;

// Initialize chatbot
document.addEventListener('DOMContentLoaded', () => {
    const chatToggle = document.getElementById('chatbot-toggle');
    const chatSend = document.getElementById('chat-send');
    const chatInput = document.getElementById('chat-input');
    const chatbotHeader = document.querySelector('.chatbot-header');
    
    // Toggle chatbot
    chatToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleChatbot();
    });
    
    chatbotHeader.addEventListener('click', () => {
        toggleChatbot();
    });
    
    // Send message
    chatSend.addEventListener('click', () => sendChatMessage());
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });
    
    // Check chatbot status
    checkChatbotStatus();
});

function toggleChatbot() {
    const container = document.getElementById('chatbot-container');
    const toggle = document.getElementById('chatbot-toggle');
    chatbotMinimized = !chatbotMinimized;
    
    if (chatbotMinimized) {
        container.classList.add('minimized');
        toggle.textContent = '+';
    } else {
        container.classList.remove('minimized');
        toggle.textContent = '−';
    }
}

async function checkChatbotStatus() {
    try {
        const response = await fetch(`${API_URL}/chat-status`);
        const data = await response.json();
        
        if (!data.available) {
            addBotMessage("⚠️ AI chatbot is currently not configured. The backend needs Azure OpenAI credentials to enable this feature.");
        }
    } catch (error) {
        console.error('Error checking chatbot status:', error);
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addUserMessage(message);
    input.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Prepare context
    const chatRequest = {
        message: message,
        location: state.location.name ? {
            name: state.location.name,
            lat: state.location.lat,
            lng: state.location.lng
        } : null,
        dates: state.dates.start ? {
            start: state.dates.start,
            end: state.dates.end || state.dates.start
        } : null,
        weather_data: window.lastWeatherData || null,
        conversation_history: conversationHistory
    };
    
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(chatRequest)
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Add bot response
        addBotMessage(data.response);
        
        // Show events if available
        if (data.events && data.events.length > 0) {
            addEventsToChat(data.events, data.recommendations);
        }
        
        // Update conversation history
        conversationHistory.push(
            { role: 'user', content: message },
            { role: 'assistant', content: data.response }
        );
        
        // Keep only last 10 messages
        if (conversationHistory.length > 10) {
            conversationHistory = conversationHistory.slice(-10);
        }
        
    } catch (error) {
        removeTypingIndicator();
        addBotMessage("Sorry, I encountered an error. Please make sure the backend is running and try again.");
        console.error('Chat error:', error);
    }
}

function addUserMessage(message) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message user-message';
    messageDiv.innerHTML = `<div class="message-content">${escapeHtml(message)}</div>`;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function addBotMessage(message) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message bot-message';
    
    // Convert markdown-style formatting to HTML
    let formattedMessage = escapeHtml(message);
    formattedMessage = formattedMessage.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formattedMessage = formattedMessage.replace(/\n/g, '<br>');
    
    messageDiv.innerHTML = `<div class="message-content">${formattedMessage}</div>`;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function addEventsToChat(events, recommendations) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message bot-message';
    
    let eventsHtml = '<div class="message-content"><strong>📅 Local Events:</strong><br>';
    
    events.forEach((event, index) => {
        const rec = recommendations?.find(r => r.event === event.name);
        const suitabilityBadge = rec ? 
            `<span class="recommendation-badge ${rec.suitable ? 'suitable' : 'not-suitable'}">
                ${rec.suitable ? '✓ Suitable' : '⚠ Check Weather'}
            </span>` : '';
        
        eventsHtml += `
            <div class="event-card">
                <h4>${event.name}</h4>
                <p><strong>Type:</strong> ${event.type}</p>
                <p><strong>Location:</strong> ${event.location}</p>
                <p>${event.description}</p>
                ${suitabilityBadge}
                ${rec && !rec.suitable ? `<p style="font-size: 12px; color: #666;">${rec.reason}</p>` : ''}
            </div>
        `;
    });
    
    eventsHtml += '</div>';
    messageDiv.innerHTML = eventsHtml;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message bot-message';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="message-content typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    messagesContainer.appendChild(typingDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

function scrollToBottom() {
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Store weather data for chatbot context
function storeWeatherDataForChat(weatherData) {
    window.lastWeatherData = weatherData;
}

// Update the generateReport function to store weather data
const originalGenerateReport = window.generateReport;
if (originalGenerateReport) {
    window.generateReport = async function() {
        const result = await originalGenerateReport();
        // Store the weather data for chatbot
        if (result && result.weather) {
            storeWeatherDataForChat(result.weather);
        }
        return result;
    };
}
