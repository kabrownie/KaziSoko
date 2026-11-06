const state = { jobs: [] };
const $ = (id) => document.getElementById(id);
const fields = ["query", "category", "location", "from", "to"];

function populate(id, values) {
  for (const value of [...new Set(values)].filter(Boolean).sort()) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    $(id).append(option);
  }
}

function render() {
  const query = $("query").value.trim().toLowerCase();
  const filtered = state.jobs.filter((job) => {
    const haystack = `${job.title} ${job.organisation} ${job.category} ${job.location}`.toLowerCase();
    return (!query || haystack.includes(query))
      && (!$("category").value || job.category === $("category").value)
      && (!$("location").value || job.location === $("location").value)
      && (!$("from").value || !job.deadline || job.deadline >= $("from").value)
      && (!$("to").value || !job.deadline || job.deadline <= $("to").value);
  });
  $("count").textContent = `${filtered.length} ${filtered.length === 1 ? "job" : "jobs"}`;
  $("empty").hidden = filtered.length !== 0;
  $("jobs").innerHTML = filtered.map((job) => `
    <article class="job">
      <div><p class="tag">${escapeHtml(job.category)}</p><h3>${escapeHtml(job.title)}</h3>
      <p class="organisation">${escapeHtml(job.organisation)} · ${escapeHtml(job.location || "Kenya")}</p></div>
      <div class="job-meta"><span>${job.deadline ? `Deadline ${escapeHtml(job.deadline)}` : "Deadline not stated"}</span>
      <a href="${safeUrl(job.source_url)}" target="_blank" rel="noopener">View original ↗</a></div>
    </article>`).join("");
}

function escapeHtml(value) {
  return String(value || "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char]));
}
function safeUrl(value) {
  try { const url = new URL(value); return ["http:", "https:"].includes(url.protocol) ? url.href : "#"; } catch { return "#"; }
}

async function init() {
  try {
    const response = await fetch("data/jobs.json");
    if (!response.ok) throw new Error(`Could not load jobs (${response.status})`);
    state.jobs = await response.json();
    populate("category", state.jobs.map((job) => job.category));
    populate("location", state.jobs.map((job) => job.location));
    render();
  } catch (error) {
    $("jobs").innerHTML = `<p class="empty">${escapeHtml(error.message)}. Please try again later.</p>`;
  }
}
fields.forEach((id) => $(id).addEventListener("input", render));
$("clear").addEventListener("click", () => { fields.forEach((id) => { $(id).value = ""; }); render(); });
document.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); $("query").focus(); }
});
init();
