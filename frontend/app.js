const $ = (selector) => document.querySelector(selector);
const form = $("#leave-form");
const dateInput = $("#leave-date");
const feedback = $("#feedback");
const submitButton = $("#submit-button");

function showFeedback(message, type = "") {
  feedback.textContent = message;
  feedback.className = "feedback" + (type ? " " + type : "");
}

async function loadRules() {
  const response = await fetch("/api/rules");
  if (!response.ok) throw new Error("Could not load the leave date rule.");
  const rules = await response.json();
  $("#eligible-date").textContent = rules.eligible_date;
  $("#today-label").textContent = "Today in India: " + rules.today + " · " + rules.days_ahead + " days ahead";
  dateInput.min = rules.eligible_date;
  dateInput.max = rules.eligible_date;
  dateInput.value = rules.eligible_date;
}

async function loadJobs() {
  const container = $("#jobs");
  try {
    const response = await fetch("/api/jobs");
    if (!response.ok) throw new Error("Request history unavailable.");
    const data = await response.json();
    if (!data.jobs.length) {
      container.innerHTML = '<p class="muted">No requests yet. Prepare a test request to see it here.</p>';
      return;
    }
    container.replaceChildren();
    for (const job of data.jobs) {
      const card = document.createElement("article");
      card.className = "job";
      const top = document.createElement("div");
      top.className = "job-top";
      const title = document.createElement("strong");
      title.textContent = "Request #" + job.id + " · " + job.leave_type + " · " + job.leave_date;
      const status = document.createElement("span");
      status.className = "status";
      status.textContent = job.status;
      top.append(title, status);
      const message = document.createElement("p");
      message.textContent = job.message;
      card.append(top, message);
      container.append(card);
    }
  } catch (error) {
    container.textContent = error.message;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  submitButton.disabled = true;
  showFeedback("Preparing a simulation record…");
  try {
    const response = await fetch("/api/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ leave_date: dateInput.value, leave_type: $("#leave-type").value })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Could not prepare the request.");
    showFeedback(data.message, "success");
    await loadJobs();
  } catch (error) {
    showFeedback(error.message, "error");
  } finally {
    submitButton.disabled = false;
  }
});

$("#refresh-button").addEventListener("click", loadJobs);
Promise.all([loadRules(), loadJobs()]).catch((error) => showFeedback(error.message, "error"));
