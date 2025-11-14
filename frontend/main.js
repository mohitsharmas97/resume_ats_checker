// ---------------------------
// API BASE URL
// ---------------------------
const API_BASE_URL = "http://127.0.0.1:5000";

console.log("Loaded main.js");

// Global variable for template selection
let selectedTemplate = 'modern'; 

// ---------------------------
// Upload Resume API Wrapper
// ---------------------------
async function uploadResumeAPI(file) {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch(`${API_BASE_URL}/api/upload`, {
            method: "POST",
            body: formData
        });

        return await res.json();
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ---------------------------
// Manual Entry API
// ---------------------------
async function manualEntryAPI(data) {
    try {
        const res = await fetch(`${API_BASE_URL}/api/manual-entry`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });

        return await res.json();
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ---------------------------
// Enhance Resume API
// ---------------------------
async function enhanceResumeAPI(data, jobDesc="") {
    try {
        const res = await fetch(`${API_BASE_URL}/api/enhance`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                resume_data: data,
                job_description: jobDesc
            })
        });

        return await res.json();
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ---------------------------
// Generate Resume API
// ---------------------------
async function generateResumeAPI(data, template="modern") {
    try {
        const res = await fetch(`${API_BASE_URL}/api/generate`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                resume_data: data,
                template
            })
        });

        return await res.json();
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ---------------------------
// Load Templates UI
// ---------------------------
async function loadTemplates() {
    const templates = [
        { id: "modern", name: "Modern Professional", image: "images/templates/modern.png", desc: "Clean & ATS Friendly" },
        { id: "classic", name: "Classic ATS", image: "images/templates/classic.png", desc: "Traditional & Corporate" },
        { id: "creative", name: "Creative Professional", image: "images/templates/creative.png", desc: "Modern & Bold" }
    ];

    const grid = document.getElementById('templateGrid');
    if (!grid) return; // Guard clause in case element doesn't exist on page
    
    grid.innerHTML = ''; // Clear existing

    templates.forEach(template => {
        const card = document.createElement('div');
        card.className = 'template-card';
        if (template.id === selectedTemplate) card.classList.add('selected');
        
        card.innerHTML = `
            <div class="template-preview">
                <img src="${template.image}" alt="${template.name}" onerror="this.src='https://via.placeholder.com/150?text=${template.name}'">
            </div>
            <h4>${template.name}</h4>
            <p>${template.desc}</p>
            <button class="btn btn-secondary" onclick="selectTemplate('${template.id}', this)">
                Select
            </button>
        `;
        grid.appendChild(card);
    });
}

// ---------------------------
// Handle Template Selection
// ---------------------------
function selectTemplate(templateId, button) {
    selectedTemplate = templateId;
    
    // Remove 'selected' class from all cards
    document.querySelectorAll('.template-card').forEach(card => {
        card.classList.remove('selected');
    });

    // Add 'selected' class to the clicked card (parent of the button)
    button.closest('.template-card').classList.add('selected');
    
    console.log("Selected Template:", selectedTemplate);
}

// ---------------------------
// Build Download Link
// ---------------------------
function getDownloadLink(filename) {
    return `${API_BASE_URL}/api/download/${filename}`;
}