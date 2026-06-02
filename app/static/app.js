const form = document.getElementById("moderationForm");
const textInput = document.getElementById("text");
const userIdInput = document.getElementById("user_id");
const surfaceInput = document.getElementById("surface");
const localeInput = document.getElementById("locale");
const submitButton = document.getElementById("submitButton");
const fillExampleButton = document.getElementById("fillExample");
const sampleButtons = document.querySelectorAll(".sample-chip");

const emptyState = document.getElementById("emptyState");
const resultState = document.getElementById("resultState");
const decisionBadge = document.getElementById("decisionBadge");
const maxScore = document.getElementById("maxScore");
const reasonsList = document.getElementById("reasonsList");
const categoryTags = document.getElementById("categoryTags");
const scoreBars = document.getElementById("scoreBars");
const normalizedText = document.getElementById("normalizedText");

const samples = {
  safe: {
    text: "Thanks everyone for joining today. Please keep the conversation respectful.",
    surface: "chat",
  },
  toxic: {
    text: "You are disgusting and worthless.",
    surface: "chat",
  },
  violent: {
    text: "I will kill you",
    surface: "signup",
  },
  spam: {
    text: "Free money click here www.scam.test buy now buy now",
    surface: "comment",
  },
};

function setSample(key) {
  const sample = samples[key];
  if (!sample) {
    return;
  }
  textInput.value = sample.text;
  surfaceInput.value = sample.surface;
}

function setDecision(decision) {
  decisionBadge.textContent = decision.toUpperCase();
  decisionBadge.className = `decision-badge ${decision}`;
}

function renderReasons(reasons) {
  reasonsList.innerHTML = "";
  reasons.forEach((reason) => {
    const item = document.createElement("li");
    item.textContent = reason;
    reasonsList.appendChild(item);
  });
}

function renderCategories(categories) {
  categoryTags.innerHTML = "";
  if (!categories.length) {
    const tag = document.createElement("span");
    tag.className = "tag";
    tag.textContent = "No categories matched";
    categoryTags.appendChild(tag);
    return;
  }

  categories.forEach((category) => {
    const tag = document.createElement("span");
    tag.className = "tag";
    tag.textContent = category.replace("_", " ");
    categoryTags.appendChild(tag);
  });
}

function renderScores(scores) {
  scoreBars.innerHTML = "";

  Object.entries(scores)
    .sort((a, b) => b[1] - a[1])
    .forEach(([category, score]) => {
      const row = document.createElement("div");
      row.className = "score-row";

      const label = document.createElement("label");
      label.textContent = category.replace("_", " ");

      const track = document.createElement("div");
      track.className = "score-track";

      const fill = document.createElement("div");
      fill.className = "score-fill";
      fill.style.width = `${Math.max(score * 100, 4)}%`;

      const value = document.createElement("strong");
      value.textContent = score.toFixed(2);

      track.appendChild(fill);
      row.appendChild(label);
      row.appendChild(track);
      row.appendChild(value);
      scoreBars.appendChild(row);
    });
}

function showResult(data) {
  emptyState.classList.add("hidden");
  resultState.classList.remove("hidden");
  setDecision(data.decision);
  maxScore.textContent = data.max_score.toFixed(2);
  renderReasons(data.reasons);
  renderCategories(data.matched_categories);
  renderScores(data.scores);
  normalizedText.textContent = data.normalized_text;
}

async function moderateContent(event) {
  event.preventDefault();
  submitButton.disabled = true;
  submitButton.textContent = "Analyzing...";

  try {
    const payload = {
      text: textInput.value.trim(),
      user_id: userIdInput.value.trim() || null,
      surface: surfaceInput.value,
      locale: localeInput.value.trim() || "en",
    };

    const response = await fetch("/moderate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("The moderation request failed.");
    }

    const data = await response.json();
    showResult(data);
  } catch (error) {
    emptyState.classList.remove("hidden");
    resultState.classList.add("hidden");
    emptyState.innerHTML = `
      <h3>Request failed</h3>
      <p>${error.message} Make sure the server is running and try again.</p>
    `;
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Analyze Content";
  }
}

form.addEventListener("submit", moderateContent);
fillExampleButton.addEventListener("click", () => setSample("toxic"));
sampleButtons.forEach((button) => {
  button.addEventListener("click", () => setSample(button.dataset.sample));
});
