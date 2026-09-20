// =============================================
// STATE MANAGEMENT
// =============================================

// Initialize state variables first
let currentUser = null;
let selectedSymptoms = [];
let chatHistory = [];
let consultationHistory = [];
let consultationCount = 0;
let symptomCheckCount = 0;
let map = null;
let recognition = null;

// =============================================
// INITIALIZATION
// =============================================

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Check for saved theme
    if (localStorage.getItem('darkMode') === 'true') {
        document.documentElement.classList.add('dark');
        updateThemeIcons();
    }

    // Initialize symptom tags
    renderSymptomTags();

    // Initialize speech recognition if available
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('chatInput').value = transcript;
        };

        recognition.onend = function() {
            document.getElementById('voiceBtn').classList.remove('listening');
        };
    }

    // Load saved data
    loadSavedData();
}

// =============================================
// AUTHENTICATION
// =============================================

function switchAuthTab(tab) {
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    if (tab === 'login') {
        loginTab.style.background = 'var(--accent-primary)';
        loginTab.style.color = 'white';
        registerTab.style.background = 'transparent';
        registerTab.style.color = 'var(--fg-muted)';
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    } else {
        registerTab.style.background = 'var(--accent-primary)';
        registerTab.style.color = 'white';
        loginTab.style.background = 'transparent';
        loginTab.style.color = 'var(--fg-muted)';
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
    }
}

function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    // Check for admin login
    if (email === 'admin@medassist.com' && password === 'admin123') {
        currentUser = { name: 'Administrator', email: email, isAdmin: true };
        showAdminDashboard();
        return;
    }

    // Simulate login
    currentUser = {
        name: email.split('@')[0].charAt(0).toUpperCase() + email.split('@')[0].slice(1),
        email: email,
        isAdmin: false
    };

    showDashboard();
}

function handleRegister(event) {
    event.preventDefault();
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const language = document.getElementById('regLanguage').value;

    currentUser = { name: name, email: email, language: language, isAdmin: false };
    showDashboard();
}

function demoLogin() {
    currentUser = { name: 'Demo User', email: 'demo@medassist.com', isAdmin: false };
    showDashboard();
}

function handleLogout() {
    currentUser = null;
    document.getElementById('authScreen').classList.remove('hidden');
    document.getElementById('dashboardScreen').classList.add('hidden');
    document.getElementById('adminScreen').classList.add('hidden');
}

// =============================================
// VIEW MANAGEMENT
// =============================================

function showDashboard() {
    document.getElementById('authScreen').classList.add('hidden');
    document.getElementById('dashboardScreen').classList.remove('hidden');
    document.getElementById('adminScreen').classList.add('hidden');

    // Update user info
    document.getElementById('userName').textContent = currentUser.name;
    document.getElementById('userEmail').textContent = currentUser.email;
    document.getElementById('userAvatar').textContent = currentUser.name.charAt(0);
    document.getElementById('profileName').value = currentUser.name;
    document.getElementById('profileEmail').value = currentUser.email;

    // Don't initialize map until hospitals view is opened (for better performance)

    // Set random health tip
    document.getElementById('healthTip').textContent = healthTips[Math.floor(Math.random() * healthTips.length)];
}

function showAdminDashboard() {
    document.getElementById('authScreen').classList.add('hidden');
    document.getElementById('dashboardScreen').classList.add('hidden');
    document.getElementById('adminScreen').classList.remove('hidden');

    // Initialize analytics chart
    setTimeout(initializeAnalyticsChart, 500);
}

function switchView(view) {
    // Hide all views
    document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));

    // Show selected view
    document.getElementById(view + 'View').classList.remove('hidden');

    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.style.color = 'var(--fg-secondary)';
        item.classList.remove('active');
    });

    if (event && event.target) {
        event.target.style.color = 'var(--fg-primary)';
        event.target.classList.add('active');
    }

    // Update mobile nav
    document.querySelectorAll('.mobile-nav-item').forEach(item => {
        item.style.background = 'var(--bg-tertiary)';
        item.style.color = 'var(--fg-secondary)';
    });

    if (view === 'hospitals') {
        setTimeout(() => {
            initializeMap();
            showNotification('Hospitals View', 'Loading nearby healthcare facilities', 'info');
        }, 300);
    } else if (view === 'history') {
        updateHistoryView();
    } else if (view === 'symptoms') {
        showNotification('Symptom Checker', 'Select your symptoms for analysis', 'info');
    }
}

// =============================================
// CHAT FUNCTIONALITY
// =============================================

function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    // Add user message
    addChatMessage(message, 'user');
    input.value = '';

    // Show typing indicator
    showTypingIndicator();

    // Process and respond
    setTimeout(() => {
        removeTypingIndicator();
        const response = processUserMessage(message);
        addChatMessage(response, 'bot');

        // Update stats
        consultationCount++;
        document.getElementById('chatCount').textContent = consultationCount;
        addToRecentActivity(message);
    }, 1000 + Math.random() * 1000);
}

function sendQuickMessage(message) {
    document.getElementById('chatInput').value = message;
    sendMessage(new Event('submit'));
}

function addChatMessage(message, sender) {
    const chatContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex gap-3 fade-in ${sender === 'user' ? 'justify-end' : ''}`;

    if (sender === 'user') {
        messageDiv.innerHTML = `
            <div class="chat-bubble-user rounded-2xl rounded-tr-sm p-4 max-w-md">
                <p>${escapeHtml(message)}</p>
            </div>
            <div class="w-8 h-8 rounded-full accent-gradient flex-shrink-0 flex items-center justify-center text-white font-semibold text-sm">
                ${currentUser ? currentUser.name.charAt(0) : 'U'}
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="w-8 h-8 rounded-full accent-gradient flex-shrink-0 flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
            </div>
            <div class="chat-bubble-bot rounded-2xl rounded-tl-sm p-4 max-w-md">
                ${message}
            </div>
        `;
    }

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Save to history
    chatHistory.push({ message, sender, timestamp: new Date() });
}

function processUserMessage(message) {
    const lowerMessage = message.toLowerCase();

    // Check for emergency keywords
    if (lowerMessage.includes('emergency') || lowerMessage.includes('help me') || lowerMessage.includes('ambulance')) {
        triggerEmergency();
        return `<p>Emergency mode activated. Please stay calm. Help is on the way.</p>
                <p class="mt-2"><strong>Emergency Numbers:</strong></p>
                <p>Ambulance: 108 | Emergency: 112</p>`;
    }

    // Check for hospital request
    if (lowerMessage.includes('hospital') || lowerMessage.includes('doctor') || lowerMessage.includes('clinic')) {
        const hospitalList = hospitals.slice(0, 3).map(h =>
            `<div class="p-2 rounded-lg mt-2" style="background: var(--bg-tertiary);">
                <strong>${h.name}</strong><br>
                <span class="text-sm">${h.city} | ${h.type}</span>
            </div>`
        ).join('');

        return `<p>Here are nearby healthcare facilities:</p>${hospitalList}
                <p class="mt-2 text-sm" style="color: var(--fg-muted);">Visit the Hospitals section for more details and directions.</p>`;
    }

    // Check for symptoms
    const detectedSymptoms = symptomList.filter(s => lowerMessage.includes(s));
    if (detectedSymptoms.length > 0) {
        const predictions = predictDisease(detectedSymptoms);
        let response = `<p>I detected these symptoms: <strong>${detectedSymptoms.join(', ')}</strong></p>`;
        response += `<p class="mt-2">Based on your symptoms, here are possible conditions:</p>`;
        response += '<div class="space-y-2 mt-2">';

        predictions.forEach(p => {
            response += `<div class="p-2 rounded-lg" style="background: var(--bg-tertiary);">
                <div class="flex justify-between items-center">
                    <strong>${p.disease}</strong>
                    <span class="text-sm px-2 py-1 rounded-full" style="background: ${getProbabilityColor(p.probability)}20; color: ${getProbabilityColor(p.probability)};">${p.probability}%</span>
                </div>
                <p class="text-sm mt-1" style="color: var(--fg-muted);">${diseases[p.disease].description}</p>
            </div>`;
        });

        response += '</div>';
        response += `<p class="mt-3 text-xs" style="color: var(--fg-muted);">This is not a medical diagnosis. Please consult a healthcare professional.</p>`;

        return response;
    }

    // Check for greetings
    if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
        return `<p>${translations[currentLanguage].welcome}</p>
                <p class="mt-2">How can I help you today? You can tell me about your symptoms or ask about nearby hospitals.</p>`;
    }

    // Default response
    return `<p>I understand you're asking about "${escapeHtml(message)}".</p>
            <p class="mt-2">I can help you with:</p>
            <ul class="list-disc list-inside mt-1 text-sm">
                <li>Symptom analysis and disease prediction</li>
                <li>Finding nearby hospitals and clinics</li>
                <li>Health tips and precautions</li>
                <li>Emergency assistance</li>
            </ul>
            <p class="mt-2">Please describe your symptoms or ask a specific health question.</p>`;
}

function showTypingIndicator() {
    const chatContainer = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'flex gap-3 fade-in';
    typingDiv.innerHTML = `
        <div class="w-8 h-8 rounded-full accent-gradient flex-shrink-0 flex items-center justify-center">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2-2v10a2 2 0 002 2z"></path>
            </svg>
        </div>
        <div class="chat-bubble-bot rounded-2xl rounded-tl-sm p-4">
            <div class="typing-indicator flex gap-1">
                <span class="w-2 h-2 rounded-full bg-gray-400"></span>
                <span class="w-2 h-2 rounded-full bg-gray-400"></span>
                <span class="w-2 h-2 rounded-full bg-gray-400"></span>
            </div>
        </div>
    `;
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

function clearChat() {
    if (chatHistory.length <= 1) {
        showNotification('Chat Empty', 'No messages to clear', 'info');
        return;
    }

    if (confirm('Are you sure you want to clear the chat history?')) {
        const chatContainer = document.getElementById('chatMessages');
        chatContainer.innerHTML = `
            <div class="flex gap-3 fade-in">
                <div class="w-8 h-8 rounded-full accent-gradient flex-shrink-0 flex items-center justify-center">
                    <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2-2v10a2 2 0 002 2z"></path>
                    </svg>
                </div>
                <div class="chat-bubble-bot rounded-2xl rounded-tl-sm p-4 max-w-md">
                    <p class="mb-2">Chat cleared. How can I assist you today?</p>
                </div>
            </div>
        `;
        chatHistory = [];
        showNotification('Chat Cleared', 'Conversation history has been cleared', 'success');
    }
}

// =============================================
// SYMPTOM CHECKER
// =============================================

function renderSymptomTags() {
    const container = document.getElementById('symptomTags');
    container.innerHTML = '';

    symptomList.forEach(symptom => {
        const tag = document.createElement('button');
        tag.className = 'symptom-tag px-3 py-1.5 rounded-full text-sm border transition-all';
        tag.style.borderColor = 'var(--border-color)';
        tag.style.color = 'var(--fg-secondary)';
        tag.textContent = symptom;
        tag.onclick = () => toggleSymptom(symptom, tag);
        container.appendChild(tag);
    });
}

function filterSymptoms(query) {
    const tags = document.querySelectorAll('#symptomTags .symptom-tag');
    const lowerQuery = query.toLowerCase();

    tags.forEach(tag => {
        if (tag.textContent.toLowerCase().includes(lowerQuery)) {
            tag.style.display = 'inline-flex';
        } else {
            tag.style.display = 'none';
        }
    });
}

function toggleSymptom(symptom, element) {
    const index = selectedSymptoms.indexOf(symptom);

    if (index === -1) {
        selectedSymptoms.push(symptom);
        element.classList.add('selected');
    } else {
        selectedSymptoms.splice(index, 1);
        element.classList.remove('selected');
    }

    updateSelectedSymptoms();
}

function updateSelectedSymptoms() {
    const container = document.getElementById('selectedSymptoms');
    const noMsg = document.getElementById('noSymptomsMsg');

    if (selectedSymptoms.length === 0) {
        container.innerHTML = '<p class="text-sm" style="color: var(--fg-muted);" id="noSymptomsMsg">Click on symptoms above to add them</p>';
    } else {
        container.innerHTML = selectedSymptoms.map(s =>
            `<span class="px-3 py-1.5 rounded-full text-sm" style="background: var(--accent-primary); color: white;">${s}
                <button onclick="removeSymptom('${s}')" class="ml-2 hover:text-red-200">&times;</button>
            </span>`
        ).join('');
    }
}

function removeSymptom(symptom) {
    selectedSymptoms = selectedSymptoms.filter(s => s !== symptom);
    updateSelectedSymptoms();

    // Update tag state
    const tags = document.querySelectorAll('#symptomTags .symptom-tag');
    tags.forEach(tag => {
        if (tag.textContent === symptom) {
            tag.classList.remove('selected');
        }
    });
}

function analyzeSymptoms() {
    if (selectedSymptoms.length === 0) {
        showNotification('No Symptoms Selected', 'Please select at least one symptom to analyze', 'error');
        return;
    }

    // Show loading state
    const resultsContainer = document.getElementById('predictionResults');
    resultsContainer.innerHTML = `
        <div class="text-center py-12">
            <div class="spinner mx-auto mb-4"></div>
            <p style="color: var(--fg-muted);">Analyzing your symptoms...</p>
        </div>
    `;

    // Simulate analysis delay for better UX
    setTimeout(() => {
        const predictions = predictDisease(selectedSymptoms);
        const duration = document.getElementById('symptomDuration').value;
        const severity = document.getElementById('symptomSeverity').value;

        // Update stats
        symptomCheckCount++;
        document.getElementById('symptomCount').textContent = symptomCheckCount;

        // Update health score based on severity
        updateHealthScore(severity, predictions);

        // Save to consultation history
        consultationHistory.push({
            symptoms: [...selectedSymptoms],
            predictions: predictions,
            duration: duration,
            severity: severity,
            timestamp: new Date()
        });

        // Save to localStorage
        saveData();

        // Display results
        displayPredictionResults(predictions);

        // Show success notification
        showNotification('Analysis Complete', `Found ${predictions.length} possible condition(s) based on your symptoms`, 'success');
    }, 1500);
}

function updateHealthScore(severity, predictions) {
    let score = 85; // Base score

    if (severity === 'severe') score -= 20;
    else if (severity === 'moderate') score -= 10;

    if (predictions.length > 0 && predictions[0].probability > 70) {
        score -= 5;
    }

    score = Math.max(50, Math.min(100, score));
    document.getElementById('healthScore').textContent = score;
}

function predictDisease(symptoms) {
    const results = [];

    for (const [diseaseName, diseaseData] of Object.entries(diseases)) {
        let matchCount = 0;
        symptoms.forEach(s => {
            if (diseaseData.symptoms.some(ds => ds.toLowerCase().includes(s.toLowerCase()) || s.toLowerCase().includes(ds.toLowerCase()))) {
                matchCount++;
            }
        });

        if (matchCount > 0) {
            const probability = Math.round((matchCount / diseaseData.symptoms.length) * 100 * (0.7 + Math.random() * 0.3));
            results.push({
                disease: diseaseName,
                probability: Math.min(probability, 95),
                severity: diseaseData.severity
            });
        }
    }

    return results.sort((a, b) => b.probability - a.probability).slice(0, 4);
}

function displayPredictionResults(predictions) {
    const container = document.getElementById('predictionResults');

    if (predictions.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8" style="color: var(--fg-muted);">
                <p>No matching conditions found. Please try different symptoms.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = predictions.map((p, index) => `
        <div class="p-4 rounded-xl slide-up" style="background: var(--bg-tertiary); animation-delay: ${index * 0.1}s;">
            <div class="flex items-center justify-between mb-2">
                <h4 class="font-semibold" style="color: var(--fg-primary);">${p.disease}</h4>
                <span class="text-sm px-2 py-1 rounded-full font-medium" style="background: ${getProbabilityColor(p.probability)}20; color: ${getProbabilityColor(p.probability)};">
                    ${p.probability}%
                </span>
            </div>
            <div class="w-full h-2 rounded-full bg-gray-200 dark:bg-gray-700 mb-2">
                <div class="h-full rounded-full transition-all duration-500" style="width: ${p.probability}%; background: ${getProbabilityColor(p.probability)};"></div>
            </div>
            <p class="text-sm" style="color: var(--fg-muted);">${diseases[p.disease].description}</p>
            <div class="mt-3 flex flex-wrap gap-1">
                ${diseases[p.disease].precautions.slice(0, 2).map(pre =>
                    `<span class="text-xs px-2 py-1 rounded-full" style="background: var(--accent-light); color: var(--accent-primary);">${pre}</span>`
                ).join('')}
            </div>
        </div>
    `).join('') + `
        <div class="p-4 rounded-xl border" style="border-color: var(--warning); background: rgba(245, 158, 11, 0.1);">
            <p class="text-sm" style="color: var(--fg-primary);">
                <strong>Disclaimer:</strong> This is not a medical diagnosis. Please consult a healthcare professional for proper evaluation.
            </p>
        </div>
    `;
}

function getProbabilityColor(probability) {
    if (probability >= 70) return '#10b981';
    if (probability >= 40) return '#f59e0b';
    return '#6b7280';
}

// =============================================
// HOSPITALS & MAP
// =============================================

function initializeMap() {
    const mapContainer = document.getElementById('map');
    if (!mapContainer) return;

    // Clear existing map
    if (map) {
        map.remove();
        map = null;
    }

    // Reset container with explicit dimensions
    mapContainer.innerHTML = '';
    mapContainer.style.height = '400px';
    mapContainer.style.width = '100%';

    try {
        // Check if Leaflet is loaded
        if (typeof L === 'undefined') {
            throw new Error('Leaflet library not loaded');
        }

        // Initialize map centered on India
        map = L.map('map', {
            center: [22.5937, 78.9629],
            zoom: 5,
            zoomControl: true,
            scrollWheelZoom: true,
            preferCanvas: true
        });

        // Add CartoDB Positron tiles (more developer-friendly, less likely to be blocked)
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreet.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19,
            errorOverlayUrl: '',
            opacity: 1
        }).addTo(map);

        // Custom hospital icon with improved styling
        const hospitalIcon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="background: #0d9488; width: 36px; height: 36px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); display: flex; align-items: center; justify-content: center; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                    <svg style="width: 18px; height: 18px; color: white; transform: rotate(45deg);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                    </svg>
                   </div>`,
            iconSize: [36, 36],
            iconAnchor: [18, 36],
            popupAnchor: [0, -36]
        });

        // Add hospital markers with individual error handling
        const markersAdded = [];
        hospitals.forEach((hospital, index) => {
            try {
                const marker = L.marker([hospital.lat, hospital.lng], { icon: hospitalIcon }).addTo(map);

                marker.bindPopup(`
                    <div style="min-width: 250px; max-width: 300px;">
                        <h3 style="font-weight: 600; margin-bottom: 12px; color: #0d9488; font-size: 18px;">${hospital.name}</h3>
                        <div style="display: grid; gap: 8px; font-size: 14px; color: #555;">
                            <div><strong>Type:</strong> ${hospital.type}</div>
                            <div><strong>City:</strong> ${hospital.city}</div>
                            <div><strong>Rating:</strong> ⭐ ${hospital.rating}/5.0</div>
                            <div><strong>Phone:</strong> <a href="tel:${hospital.phone}" style="color: #0d9488; text-decoration: none;">${hospital.phone}</a></div>
                        </div>
                        <a href="https://www.google.com/maps/dir/?api=1&destination=${hospital.lat},${hospital.lng}" target="_blank" style="display: inline-block; margin-top: 12px; padding: 8px 16px; background: #0d9488; color: white; text-decoration: none; border-radius: 8px; font-size: 14px; font-weight: 500; transition: all 0.3s ease;">Get Directions</a>
                    </div>
                `);

                markersAdded.push(marker);
            } catch (markerError) {
                console.error(`Error adding marker for ${hospital.name}:`, markerError);
                // Continue with other markers
            }
        });

        // Fit the map view to show all hospitals across India
        if (markersAdded.length > 0) {
            const group = L.featureGroup(markersAdded);
            map.fitBounds(group.getBounds().pad(0.15));
        }

        // Add scale control
        L.control.scale({ imperial: false }).addTo(map);

        // Force map to update its size with better timing
        if (map) {
            setTimeout(() => {
                try {
                    map.invalidateSize();
                    // Show success notification after map loads
                    showNotification('Map Loaded', `${hospitals.length} hospitals across India displayed`, 'success');
                } catch (sizeError) {
                    console.error('Error updating map size:', sizeError);
                }
            }, 500);
        }

        renderHospitalList();
    } catch (error) {
        console.error('Map initialization error:', error);
        mapContainer.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; background: var(--bg-tertiary); border-radius: 12px; padding: 20px;">
                <div style="text-align: center; margin-bottom: 16px;">
                    <svg style="width: 56px; height: 56px; margin: 0 auto 12px; color: var(--emergency);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
                    </svg>
                    <h4 style="color: var(--fg-primary); margin-bottom: 8px;">Map Loading Error</h4>
                    <p style="color: var(--fg-muted); margin-bottom: 16px; max-width: 280px; line-height: 1.5;">
                        Unable to load the map. This might be due to connectivity issues or Leaflet library not loading properly.
                    </p>
                    <button onclick="refreshMap()" class="w-full py-2 px-4 rounded-xl btn-primary font-medium transition-all hover:scale-105">
                        Retry Loading Map
                    </button>
                </div>
            </div>
        `;
    }
}

function filterHospitals(query) {
    renderHospitalList(query);
}

function renderHospitalList(filterQuery = '') {
    const container = document.getElementById('hospitalList');
    if (!container) return;

    const query = filterQuery.toLowerCase().trim();
    const filtered = query
        ? hospitals.filter(h =>
            h.name.toLowerCase().includes(query) ||
            h.city.toLowerCase().includes(query) ||
            h.type.toLowerCase().includes(query))
        : hospitals;

    const countEl = document.getElementById('hospitalCount');
    if (countEl) {
        countEl.textContent = `${filtered.length} ${filtered.length === 1 ? 'facility' : 'facilities'} found`;
    }

    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="p-6 rounded-xl text-center" style="background: var(--bg-tertiary);">
                <p class="text-2xl mb-2">🔍</p>
                <p class="text-sm" style="color: var(--fg-muted);">No hospitals match "${filterQuery}"</p>
            </div>
        `;
        return;
    }

    container.innerHTML = filtered.map(h => `
        <div class="hospital-card p-4 rounded-xl border cursor-pointer group" style="border-color: var(--border-color);" onclick="focusHospital(${h.lat}, ${h.lng}, ${h.id})">
            <div class="flex items-start justify-between mb-3">
                <div class="flex gap-3">
                    <div class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style="background: var(--accent-light);">
                        <svg class="w-6 h-6" style="color: var(--accent-primary);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2-2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                        </svg>
                    </div>
                    <div>
                        <h4 class="font-semibold mb-1 group-hover:text-teal-500 transition-colors" style="color: var(--fg-primary);">${h.name}</h4>
                        <div class="flex items-center gap-2 mb-1">
                            <span class="text-xs px-2 py-0.5 rounded-full" style="background: var(--accent-light); color: var(--accent-primary);">${h.type}</span>
                            <span class="text-sm font-semibold" style="color: var(--accent-primary);">📍 ${h.city}</span>
                        </div>
                        <p class="text-xs" style="color: var(--fg-muted);">${h.address}</p>
                    </div>
                </div>
                <div class="flex items-center justify-between pt-3 border-t" style="border-color: var(--border-color);">
                    <div class="flex items-center gap-1">
                        <svg class="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                        </svg>
                        <span class="text-sm font-medium" style="color: var(--fg-primary);">${h.rating}</span>
                        <span class="text-xs" style="color: var(--fg-muted);">/5.0</span>
                    </div>
                    <a href="tel:${h.phone}" onclick="event.stopPropagation()" class="text-sm font-medium flex items-center gap-1 px-3 py-1.5 rounded-lg transition-all hover:bg-teal-50 dark:hover:bg-teal-900/20" style="color: var(--accent-primary);">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                        </svg>
                        Call
                    </a>
                </div>
            </div>
    `).join('');
}

function refreshMap() {
    showNotification('Refreshing', 'Reloading map data...', 'info');
    initializeMap();
}

function focusHospital(lat, lng, id) {
    if (map) {
        map.setView([lat, lng], 16);
        // Find and open the popup for this hospital
        map.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                const pos = layer.getLatLng();
                if (pos.lat === lat && pos.lng === lng) {
                    layer.openPopup();
                }
            }
        });
        const hospital = hospitals.find(h => h.id === id);
        showNotification('Hospital Selected', `Showing ${hospital ? hospital.name : 'hospital'} on map`, 'success');
    }
}

function locateHospitals() {
    if (!navigator.geolocation) {
        showNotification('Location Not Supported', 'Your browser does not support geolocation', 'error');
        return;
    }

    showNotification('Locating...', 'Finding your current location', 'info');

    navigator.geolocation.getCurrentPosition(
        (position) => {
            if (map) {
                const userLocation = [position.coords.latitude, position.coords.longitude];
                map.setView(userLocation, 15);

                // Custom user location icon
                const userIcon = L.divIcon({
                    className: 'user-location-marker',
                    html: `<div style="width: 20px; height: 20px; background: #3b82f6; border: 4px solid white; border-radius: 50%; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>`,
                    iconSize: [20, 20],
                    iconAnchor: [10, 10]
                });

                L.marker(userLocation, { icon: userIcon })
                    .addTo(map)
                    .bindPopup('<strong style="color: #3b82f6;">📍 Your Location</strong>')
                    .openPopup();

                showNotification('Location Found', 'Showing nearby hospitals from your location', 'success');
            }
        },
        (error) => {
            let message = 'Unable to get your location.';
            if (error.code === 1) {
                message = 'Location access denied. Please enable location permissions.';
            } else if (error.code === 2) {
                message = 'Location information unavailable.';
            } else if (error.code === 3) {
                message = 'Location request timed out.';
            }
            showNotification('Location Error', message, 'error');
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

// =============================================
// EMERGENCY
// =============================================

function triggerEmergency() {
    const modal = document.getElementById('emergencyModal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');

    // Populate emergency hospitals
    const container = document.getElementById('emergencyHospitals');
    container.innerHTML = hospitals.slice(0, 3).map(h => `
        <div class="p-3 rounded-xl text-left" style="background: var(--bg-tertiary);">
            <div class="flex items-center justify-between">
                <div>
                    <strong style="color: var(--fg-primary);">${h.name}</strong>
                    <p class="text-sm" style="color: var(--fg-muted);">${h.city}</p>
                </div>
                <a href="tel:${h.phone}" class="px-3 py-1.5 rounded-lg bg-teal-500 text-white text-sm font-medium">Call</a>
            </div>
        </div>
    `).join('');
}

function closeEmergency() {
    const modal = document.getElementById('emergencyModal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

// =============================================
// VOICE INPUT
// =============================================

function toggleVoice() {
    if (!recognition) {
        alert('Speech recognition is not supported in your browser.');
        return;
    }

    const voiceBtn = document.getElementById('voiceBtn');

    if (voiceBtn.classList.contains('listening')) {
        recognition.stop();
        voiceBtn.classList.remove('listening');
    } else {
        recognition.start();
        voiceBtn.classList.add('listening');
    }
}

// =============================================
// HISTORY
// =============================================

function clearHistory() {
    if (consultationHistory.length === 0) {
        showNotification('No History', 'There is no consultation history to clear', 'info');
        return;
    }

    if (confirm('Are you sure you want to clear all consultation history? This cannot be undone.')) {
        consultationHistory = [];
        localStorage.removeItem('consultationHistory');
        updateHistoryView();
        showNotification('History Cleared', 'All consultation history has been deleted', 'success');
    }
}

function addToRecentActivity(message) {
    const container = document.getElementById('recentActivity');
    const activityItem = document.createElement('div');
    activityItem.className = 'flex items-start gap-2 fade-in';
    activityItem.innerHTML = `
        <div class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0" style="background: var(--accent-light);">
            <svg class="w-3 h-3" style="color: var(--accent-primary);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
            </svg>
        </div>
        <div class="flex-1 min-w-0">
            <p class="text-sm truncate" style="color: var(--fg-primary);">${escapeHtml(message.substring(0, 50))}${message.length > 50 ? '...' : ''}</p>
            <p class="text-xs" style="color: var(--fg-muted);">Just now</p>
        </div>
    `;

    container.insertBefore(activityItem, container.firstChild);

    // Keep only last 5
    while (container.children.length > 5) {
        container.removeChild(container.lastChild);
    }
}

// =============================================
// THEME & UI
// =============================================

function toggleTheme() {
    document.documentElement.classList.toggle('dark');
    const isDark = document.documentElement.classList.contains('dark');
    localStorage.setItem('darkMode', isDark);
    updateThemeIcons();
}

function updateThemeIcons() {
    const isDark = document.documentElement.classList.contains('dark');
    document.getElementById('sunIcon').classList.toggle('hidden', !isDark);
    document.getElementById('moonIcon').classList.toggle('hidden', isDark);
}

function toggleUserMenu() {
    const menu = document.getElementById('userMenu');
    menu.classList.toggle('hidden');
}

function changeLanguage(lang) {
    currentLanguage = lang;
    document.getElementById('languageSelect').value = lang;
}

// =============================================
// PROFILE
// =============================================

function updateProfile(event) {
    event.preventEvent();
    const name = document.getElementById('profileName').value;
    const language = document.getElementById('profileLanguage').value;
    const age = document.getElementById('profileAge').value;
    const conditions = document.getElementById('profileConditions').value;

    if (!name.trim()) {
        showNotification('Invalid Name', 'Please enter a valid name', 'error');
        return;
    }

    currentUser.name = name;
    currentUser.language = language;
    currentUser.age = age;
    currentUser.medicalConditions = conditions;

    document.getElementById('userName').textContent = name;
    document.getElementById('userAvatar').textContent = name.charAt(0);

    // Save to localStorage
    localStorage.setItem('currentUser', JSON.stringify(currentUser));

    showNotification('Profile Updated', 'Your profile has been updated successfully!', 'success');
}

// =============================================
// ANALYTICS CHART (Admin)
// =============================================

function initializeAnalyticsChart() {
    const ctx = document.getElementById('analyticsChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
            datasets: [{
                label: 'Consultations',
                data: [420, 580, 650, 720, 890, 1050, 1280],
                borderColor: '#0d9488',
                backgroundColor: 'rgba(13, 148, 136, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Symptom Checks',
                data: [280, 350, 420, 510, 620, 780, 920],
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// =============================================
// UTILITIES
// =============================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function loadSavedData() {
    // Load any saved preferences
    const savedLang = localStorage.getItem('language');
    if (savedLang) {
        currentLanguage = savedLang;
        document.getElementById('languageSelect').value = savedLang;
    }

    // Load consultation history from localStorage
    const savedHistory = localStorage.getItem('consultationHistory');
    if (savedHistory) {
        try {
            consultationHistory = JSON.parse(savedHistory);
            updateHistoryView();
        } catch(e) {
            console.error('Error loading history:', e);
        }
    }
}

function saveData() {
    // Save consultation history
    localStorage.setItem('consultationHistory', JSON.stringify(consultationHistory));
}

function rotateHealthTip() {
    const tip = healthTips[Math.floor(Math.random() * healthTips.length)];
    const tipEl = document.getElementById('healthTip');
    tipEl.style.opacity = '0';
    setTimeout(() => {
        tipEl.textContent = tip;
        tipEl.style.opacity = '1';
    }, 200);
}

function exportHealthData() {
    const data = {
        user: currentUser ? {name: currentUser.name, email: currentUser.email} : null,
        consultationCount: consultationCount,
        symptomCheckCount: symptomCheckCount,
        consultationHistory: consultationHistory,
        exportDate: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `medassist-health-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showNotification('Success', 'Health data exported successfully!', 'success');
}

function showNotification(title, message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = 'notification slide-in-right glass-card p-4 rounded-xl';

    const iconColor = type === 'success' ? 'var(--success)' : type === 'error' ? 'var(--emergency)' : 'var(--accent-primary)';
    const icon = type === 'success' ?
        '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>' :
        '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>';

    notification.innerHTML = `
        <div class="flex items-start gap-3">
            <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0" style="background: ${iconColor}20;">
                <svg class="w-5 h-5" style="color: ${iconColor};" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    ${icon}
                </svg>
            </div>
            <div class="flex-1">
                <h4 class="font-semibold text-sm" style="color: var(--fg-primary);">${title}</h4>
                <p class="text-xs mt-1" style="color: var(--fg-muted);">${message}</p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="text-gray-400 hover:text-gray-600">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

function updateHistoryView() {
    const container = document.getElementById('historyList');
    if (!container) return;

    if (consultationHistory.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12" style="color: var(--fg-muted);">
                <svg class="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <p>No consultation history yet</p>
                <p class="text-sm mt-2">Start by checking your symptoms or chatting with the AI assistant</p>
            </div>
        `;
        return;
    }

    container.innerHTML = consultationHistory.slice().reverse().map((item, index) => {
        const date = new Date(item.timestamp);
        const timeAgo = getTimeAgo(date);

        return `
            <div class="glass-card rounded-xl p-4 fade-in">
                <div class="flex items-start justify-between mb-3">
                    <div>
                        <h4 class="font-medium" style="color: var(--fg-primary);">Consultation #${consultationHistory.length - index}</h4>
                        <p class="text-xs" style="color: var(--fg-muted);">${timeAgo} - ${date.toLocaleString()}</p>
                    </div>
                    <span class="badge badge-${getSeverityBadge(item.severity)}">${item.severity || 'mild'}</span>
                </div>
                <div class="mb-3">
                    <p class="text-sm font-medium mb-2" style="color: var(--fg-secondary);">Symptoms:</p>
                    <div class="flex flex-wrap gap-1">
                        ${item.symptoms.map(s =>
                            `<span class="text-xs px-2 py-1 rounded-full" style="background: var(--bg-tertiary); color: var(--fg-primary);">${s}</span>`
                        ).join('')}
                    </div>
                </div>
                ${item.predictions && item.predictions.length > 0 ? `
                    <div>
                        <p class="text-sm font-medium mb-2" style="color: var(--fg-secondary);">Predictions:</p>
                        <div class="space-y-1">
                            ${item.predictions.slice(0, 3).map(p =>
                                `<div class="flex items-center justify-between text-sm">
                                    <span style="color: var(--fg-primary);">${p.disease}</span>
                                    <span class="text-xs px-2 py-1 rounded-full" style="background: ${getProbabilityColor(p.probability)}20; color: ${getProbabilityColor(p.probability)};">${p.probability}%</span>
                                </div>`
                            ).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    if (seconds < 60) return 'Just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
}

function getSeverityBadge(severity) {
    if (severity === 'severe') return 'danger';
    if (severity === 'moderate') return 'warning';
    return 'success';
}

// Close menus when clicking outside
document.addEventListener('click', function(event) {
    const userMenu = document.getElementById('userMenu');
    const userBtn = event.target.closest('[onclick="toggleUserMenu()"]');

    if (!userBtn && userMenu && !userMenu.contains(event.target)) {
        userMenu.classList.add('hidden');
    }
});

// Keyboard accessibility
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeEmergency();
        document.getElementById('userMenu').classList.add('hidden');
    }
});