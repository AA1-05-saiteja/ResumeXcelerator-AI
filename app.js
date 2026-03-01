document.getElementById("resumeForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const loading = document.getElementById("loading");
    const resultSection = document.getElementById("resultSection");

    loading.style.display = "block";
    resultSection.innerHTML = "";

    const formData = new FormData(this);

    const response = await fetch("/api/analyze-resume/", {
        method: "POST",
        body: formData
    });

    const data = await response.json();
    loading.style.display = "none";

    if (data.error) {
        resultSection.innerHTML = "<p style='color:red'>" + data.error + "</p>";
        return;
    }

    resultSection.innerHTML = `
        <div class="result-card">
            <h2>Match Score</h2>
            <div class="progress-bar">
                <div class="progress-fill" style="width:${data.match_percentage}%">
                    ${data.match_percentage}%
                </div>
            </div>

            <h2>Readiness Score</h2>
            <div class="progress-bar">
                <div class="progress-fill" style="width:${data.readiness_score}%">
                    ${data.readiness_score}%
                </div>
            </div>

            <h3>Matched Skills</h3>
            ${data.matched_skills.map(skill => `<span class="skill-tag">${skill}</span>`).join("")}

            <h3>Missing Skills</h3>
            ${data.missing_skills.map(skill => `<span class="skill-tag" style="background:#7f1d1d">${skill}</span>`).join("")}
        </div>
    `;
});
