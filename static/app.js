const schema = [
  ["website_name", "Website Name"],
  ["company_name", "Company Name"],
  ["address", "Address"],
  ["mobile_number", "Mobile Number"],
  ["mail", "Mail"],
  ["core_service", "Core Service"],
  ["target_customer", "Target Customer"],
  ["probable_pain_point", "Probable Pain Point"],
  ["outreach_opener", "Outreach Opener"],
];

const form = document.querySelector("#enrichForm");
const statusEl = document.querySelector("#status");
const latestResult = document.querySelector("#latestResult");
const allResults = document.querySelector("#allResults");
const resultCount = document.querySelector("#resultCount");
const enrichBtn = document.querySelector("#enrichBtn");
const showResultsBtn = document.querySelector("#showResultsBtn");

function displayValue(value) {
  if (Array.isArray(value)) {
    return value.length ? value.join(", ") : "N/A";
  }
  return value || "N/A";
}

function normalizeRecord(record) {
  return Object.fromEntries(schema.map(([key]) => [key, displayValue(record?.[key])]));
}

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

function renderProfile(record, target) {
  const normalized = normalizeRecord(record);
  target.innerHTML = `
    <div class="profile-grid">
      ${schema
        .map(([key, label]) => {
          const wide = ["core_service", "probable_pain_point", "outreach_opener", "address"].includes(key);
          return `
            <div class="field ${wide ? "wide" : ""}">
              <strong>${label}</strong>
              <span>${escapeHtml(normalized[key])}</span>
            </div>
          `;
        })
        .join("")}
    </div>
  `;
}

function renderTable(records) {
  resultCount.textContent = `${records.length} ${records.length === 1 ? "record" : "records"}`;

  if (!records.length) {
    allResults.innerHTML = '<div class="empty">No saved companies yet.</div>';
    return;
  }

  allResults.innerHTML = `
    <table>
      <thead>
        <tr>${schema.map(([, label]) => `<th>${label}</th>`).join("")}</tr>
      </thead>
      <tbody>
        ${records
          .map((record) => {
            const normalized = normalizeRecord(record);
            return `<tr>${schema.map(([key]) => `<td>${escapeHtml(normalized[key])}</td>`).join("")}</tr>`;
          })
          .join("")}
      </tbody>
    </table>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus("Enriching website...");
  enrichBtn.disabled = true;

  const payload = {
    website_name: document.querySelector("#websiteName").value.trim(),
    url: document.querySelector("#companyUrl").value.trim(),
  };

  try {
    const response = await fetch("/enrich", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    renderProfile(data, latestResult);
    setStatus("Enrichment complete.");
  } catch (error) {
    setStatus(error.message || "Unable to enrich this website.", true);
  } finally {
    enrichBtn.disabled = false;
  }
});

showResultsBtn.addEventListener("click", async () => {
  showResultsBtn.disabled = true;

  try {
    const response = await fetch("/results");
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }
    renderTable(await response.json());
  } catch (error) {
    allResults.innerHTML = `<div class="empty">${escapeHtml(error.message || "Unable to load results.")}</div>`;
  } finally {
    showResultsBtn.disabled = false;
  }
});
