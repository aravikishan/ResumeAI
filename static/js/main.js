/* ResumeAI -- client-side logic
 * Handles file drag-and-drop, progress bars, chart rendering,
 * resume parsing, job matching, and results display.
 */

const CATEGORY_CSS = {
    "Programming": "skill-programming",
    "Frameworks": "skill-frameworks",
    "Cloud": "skill-cloud",
    "Data": "skill-data",
    "Databases": "skill-databases",
    "Soft Skills": "skill-soft-skills",
};

const LEVEL_CSS = {
    "Entry": "level-entry",
    "Mid": "level-mid",
    "Senior": "level-senior",
    "Lead": "level-lead",
    "Unknown": "",
};

const BREAKDOWN_LABELS = {
    contact_email: "Email present",
    contact_phone: "Phone present",
    skills_count: "Skills listed",
    skill_diversity: "Skill diversity",
    education: "Education",
    experience: "Experience",
    formatting: "Formatting & quality",
};

let lastParsedResult = null;
let currentMatchJobId = null;

/* ── Initialization ───────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
    initDropZone();
    initCharCount();
    initNavToggle();
    loadStoredResult();
});

/* ── Navigation Toggle (mobile) ───────────────────────────────────── */
function initNavToggle() {
    const toggle = document.getElementById("navToggle");
    const links = document.getElementById("navLinks");
    if (toggle && links) {
        toggle.addEventListener("click", () => {
            links.classList.toggle("active");
        });
    }
}

/* ── Character Count ──────────────────────────────────────────────── */
function initCharCount() {
    const textarea = document.getElementById("resumeText");
    const counter = document.getElementById("charCount");
    if (textarea && counter) {
        textarea.addEventListener("input", () => {
            counter.textContent = textarea.value.length;
        });
    }
}

/* ── Drag & Drop File Upload ──────────────────────────────────────── */
function initDropZone() {
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    if (!dropZone || !fileInput) return;

    // Prevent default drag behaviors on the whole page
    ["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Visual feedback
    ["dragenter", "dragover"].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add("drag-over");
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove("drag-over");
        });
    });

    // Handle dropped files
    dropZone.addEventListener("drop", (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) handleFile(files[0]);
    });

    // Handle file input change
    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    // Click to upload
    dropZone.addEventListener("click", (e) => {
        if (e.target.tagName !== "INPUT" && !e.target.closest(".file-label")) {
            fileInput.click();
        }
    });
}

function handleFile(file) {
    if (!file.name.endsWith(".txt")) {
        alert("Only .txt files are supported.");
        return;
    }
    if (file.size > 2 * 1024 * 1024) {
        alert("File too large (max 2MB).");
        return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
        const textarea = document.getElementById("resumeText");
        if (textarea) {
            textarea.value = e.target.result;
            const counter = document.getElementById("charCount");
            if (counter) counter.textContent = textarea.value.length;
        }
    };
    reader.readAsText(file);
}

/* ── Parse Resume ─────────────────────────────────────────────────── */
async function parseResume() {
    const textarea = document.getElementById("resumeText");
    const text = textarea ? textarea.value.trim() : "";
    if (!text) {
        alert("Please paste your resume text or upload a file first.");
        return;
    }
    if (text.length < 10) {
        alert("Resume text is too short. Please provide more content.");
        return;
    }

    showProgress(true);
    try {
        // Simulate progress stages
        updateProgress(20, "Extracting sections...");
        const resp = await fetch("/api/parse", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });

        updateProgress(60, "Analyzing skills...");

        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || "Parse failed");
        }

        updateProgress(80, "Calculating ATS score...");
        const data = await resp.json();
        lastParsedResult = data;

        updateProgress(100, "Complete!");

        // Store result and navigate to results page
        sessionStorage.setItem("resumeResult", JSON.stringify(data));
        setTimeout(() => {
            window.location.href = "/results";
        }, 400);
    } catch (e) {
        showProgress(false);
        alert("Error: " + e.message);
    }
}

/* ── Load Stored Result ───────────────────────────────────────────── */
function loadStoredResult() {
    // Results page
    const resultData = sessionStorage.getItem("resumeResult");
    if (resultData && document.getElementById("resultsContainer")) {
        const data = JSON.parse(resultData);
        lastParsedResult = data;
        displayResults(data);
    }
}

/* ── Display Results ──────────────────────────────────────────────── */
function displayResults(data) {
    // Contact Info
    setText("resultName", data.name || "Not found");
    setText("resultEmail", data.email || "Not found");
    setText("resultPhone", data.phone || "Not found");

    // Experience Level
    const levelEl = document.getElementById("resultLevel");
    if (levelEl) {
        const level = data.experience_level || "Unknown";
        levelEl.textContent = level;
        levelEl.className = "contact-value level-badge " + (LEVEL_CSS[level] || "");
    }

    // ATS Score
    animateScore(data.ats_score || 0);
    renderBreakdown(data.ats_breakdown || {});

    // Skills
    renderSkills(data.skills || {});

    // Experience & Education
    setText("resultExperience",
        data.experience_years ? data.experience_years + " years" : "Not detected");
    setText("resultEducation", data.education || "Not detected");

    // Sections
    renderSections(data.sections || {});

    // Suggestions
    renderSuggestions(data.suggestions || []);
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

/* ── ATS Score Animation ──────────────────────────────────────────── */
function animateScore(target) {
    const circle = document.getElementById("atsScoreCircle");
    const valueEl = document.getElementById("atsScoreValue");
    if (!circle || !valueEl) return;

    let current = 0;
    const step = Math.max(1, Math.ceil(target / 50));

    function tick() {
        current = Math.min(current + step, target);
        valueEl.textContent = current;
        circle.style.setProperty("--score", current);

        // Color based on score
        if (current >= 70) {
            circle.style.setProperty("--accent", "#059669");
        } else if (current >= 40) {
            circle.style.setProperty("--accent", "#d97706");
        } else {
            circle.style.setProperty("--accent", "#dc2626");
        }

        if (current < target) requestAnimationFrame(tick);
    }
    tick();
}

function renderBreakdown(breakdown) {
    const container = document.getElementById("atsBreakdown");
    if (!container) return;
    container.innerHTML = "";
    for (const [key, value] of Object.entries(breakdown)) {
        const item = document.createElement("div");
        item.className = "ats-breakdown-item";
        const label = BREAKDOWN_LABELS[key] || key;
        item.innerHTML = `<span>${label}</span><span><strong>+${value}</strong></span>`;
        container.appendChild(item);
    }
}

/* ── Skills Rendering ─────────────────────────────────────────────── */
function renderSkills(skills) {
    const container = document.getElementById("skillsContainer");
    if (!container) return;
    container.innerHTML = "";

    const categories = Object.entries(skills);
    if (categories.length === 0) {
        container.innerHTML = '<p style="color:var(--text-muted)">No skills detected. Make sure your resume includes technical and soft skills.</p>';
        return;
    }

    let totalSkills = 0;
    for (const [category, items] of categories) {
        totalSkills += items.length;
        const div = document.createElement("div");
        div.className = "skill-category";
        const cssClass = CATEGORY_CSS[category] || "skill-programming";
        div.innerHTML = `<h4>${category} (${items.length})</h4><div class="skill-tags">${
            items.map(s => `<span class="skill-badge ${cssClass}">${s}</span>`).join("")
        }</div>`;
        container.appendChild(div);
    }

    // Summary
    const summary = document.createElement("p");
    summary.style.cssText = "margin-top:0.75rem;font-size:0.85rem;color:var(--text-muted);";
    summary.textContent = `${totalSkills} skills detected across ${categories.length} categories.`;
    container.appendChild(summary);
}

/* ── Sections Rendering ───────────────────────────────────────────── */
function renderSections(sections) {
    const container = document.getElementById("sectionsContainer");
    if (!container) return;
    container.innerHTML = "";

    const sectionNames = Object.keys(sections);
    if (sectionNames.length === 0) {
        container.innerHTML = '<p style="color:var(--text-muted)">No sections detected. Use clear headings like "Experience", "Education", "Skills".</p>';
        return;
    }

    for (const name of sectionNames) {
        const item = document.createElement("div");
        item.className = "section-item";
        item.innerHTML = `<span class="section-check">&#10003;</span><span>${capitalize(name)}</span>`;
        container.appendChild(item);
    }
}

/* ── Suggestions Rendering ────────────────────────────────────────── */
function renderSuggestions(suggestions) {
    const container = document.getElementById("suggestionsContainer");
    if (!container) return;
    container.innerHTML = "";

    if (suggestions.length === 0) {
        container.innerHTML = '<p style="color:var(--text-muted)">No suggestions -- your resume looks great!</p>';
        return;
    }

    for (const suggestion of suggestions) {
        const item = document.createElement("div");
        item.className = "suggestion-item";
        item.innerHTML = `<span class="suggestion-icon">&#128161;</span><span>${suggestion}</span>`;
        container.appendChild(item);
    }
}

/* ── Load Sample ──────────────────────────────────────────────────── */
async function loadSample() {
    try {
        const resp = await fetch("/api/sample");
        const data = await resp.json();
        const textarea = document.getElementById("resumeText");
        if (textarea) {
            textarea.value = data.text;
            const counter = document.getElementById("charCount");
            if (counter) counter.textContent = textarea.value.length;
        }
    } catch (e) {
        alert("Failed to load sample: " + e.message);
    }
}

/* ── Job Matching ─────────────────────────────────────────────────── */
function matchJob(jobId) {
    currentMatchJobId = jobId;
    // If we have parsed text stored, use it
    const storedResult = sessionStorage.getItem("resumeResult");
    if (storedResult) {
        const data = JSON.parse(storedResult);
        if (data && data.name) {
            submitMatchWithStored(jobId);
            return;
        }
    }
    // Otherwise show modal
    const modal = document.getElementById("matchModal");
    if (modal) modal.style.display = "flex";
}

async function loadSampleForMatch() {
    try {
        const resp = await fetch("/api/sample");
        const data = await resp.json();
        const ta = document.getElementById("matchResumeText");
        if (ta) ta.value = data.text;
    } catch (e) {
        alert("Failed to load sample: " + e.message);
    }
}

function closeModal() {
    const modal = document.getElementById("matchModal");
    if (modal) modal.style.display = "none";
}

async function submitMatch() {
    const text = document.getElementById("matchResumeText").value.trim();
    if (!text) { alert("Paste your resume first."); return; }
    closeModal();
    await submitMatchDirect(text, currentMatchJobId);
}

async function submitMatchWithStored(jobId) {
    const storedResult = sessionStorage.getItem("resumeResult");
    if (!storedResult) return;
    // We need the original text; fall back to modal if not available
    const modal = document.getElementById("matchModal");
    if (modal) modal.style.display = "flex";
}

async function submitMatchDirect(text, jobId) {
    showLoading(true);
    try {
        const resp = await fetch("/api/match", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ resume_text: text, job_id: jobId }),
        });
        if (!resp.ok) throw new Error("Match request failed");
        const data = await resp.json();
        displayMatchResult(data);
    } catch (e) {
        alert("Error: " + e.message);
    } finally {
        showLoading(false);
    }
}

function displayMatchResult(data) {
    const panel = document.getElementById("matchResultPanel");
    if (!panel) return;
    panel.style.display = "block";

    setText("matchJobTitle", data.job_title || "Unknown");
    const companyEl = document.getElementById("matchJobCompany");
    if (companyEl) companyEl.textContent = data.job_company || "";

    setText("matchRecommendation", data.recommendation || "");

    const pct = data.match_percentage || 0;
    const circle = document.getElementById("matchPercentCircle");
    const valueEl = document.getElementById("matchPercentValue");
    if (circle && valueEl) {
        circle.style.setProperty("--pct", pct);
        valueEl.textContent = Math.round(pct);
    }

    const matchedContainer = document.getElementById("matchedSkills");
    const missingContainer = document.getElementById("missingSkills");
    if (matchedContainer) {
        matchedContainer.innerHTML = (data.matched_skills || [])
            .map(s => `<span class="skill-badge skill-matched">${s}</span>`).join("");
        if (data.matched_skills && data.matched_skills.length === 0) {
            matchedContainer.innerHTML = '<span style="color:var(--text-muted)">None</span>';
        }
    }
    if (missingContainer) {
        missingContainer.innerHTML = (data.missing_skills || [])
            .map(s => `<span class="skill-badge skill-missing">${s}</span>`).join("");
        if (data.missing_skills && data.missing_skills.length === 0) {
            missingContainer.innerHTML = '<span style="color:var(--text-muted)">None -- perfect match!</span>';
        }
    }

    // Scroll to results
    panel.scrollIntoView({ behavior: "smooth", block: "start" });
}

/* ── Progress Bar ─────────────────────────────────────────────────── */
function showProgress(show) {
    const bar = document.getElementById("progressBar");
    if (bar) bar.style.display = show ? "block" : "none";
    if (!show) {
        updateProgress(0, "");
    }
}

function updateProgress(percent, text) {
    const fill = document.getElementById("progressFill");
    const label = document.getElementById("progressText");
    if (fill) fill.style.width = percent + "%";
    if (label) label.textContent = text;
}

/* ── Loading Overlay ──────────────────────────────────────────────── */
function showLoading(show) {
    const el = document.getElementById("loadingOverlay");
    if (el) el.style.display = show ? "flex" : "none";
}

/* ── Utility ──────────────────────────────────────────────────────── */
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
