"use strict";
const $ = (id) => document.getElementById(id);
const tabs = ["agents", "guardian", "about"];
for (const button of document.querySelectorAll("[data-tab]")) {
  button.addEventListener("click", () => {
    const tab = button.dataset.tab;
    for (const name of tabs) $(name).classList.toggle("hidden", name !== tab);
    for (const b of document.querySelectorAll("[data-tab]")) b.classList.toggle("active", b.dataset.tab === tab);
    $("heading").textContent = ({agents:"Agent workspace",guardian:"Code Guardian",about:"About & security"})[tab];
    $("crumb").textContent = tab.toUpperCase();
  });
}
function renderCard(parent, title, body) {
  const card = document.createElement("article");
  card.className = "result";
  const heading = document.createElement("h3");
  heading.textContent = title;
  const pre = document.createElement("pre");
  pre.textContent = body;
  card.append(heading, pre);
  parent.append(card);
}
async function post(url, data) {
  const response = await fetch(url, {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
  const payload = await response.json();
  if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "Request failed");
  return payload;
}
$("run-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = $("run-btn"); button.disabled = true;
  $("run-status").textContent = "Running…"; $("run-output").replaceChildren();
  try {
    const data = await post("/api/run", {goal:$("goal").value,mode:$("mode").value,model:$("model").value});
    for (const step of data.steps) renderCard($("run-output"), step.role.toUpperCase(), step.output);
    $("run-status").textContent = data.mode === "offline" ? "Offline demo completed — no LLM used." : "Provider response received.";
  } catch (error) { $("run-status").textContent = "Error: " + error.message; }
  finally {button.disabled = false;}
});
$("review-form").addEventListener("submit", async (event) => {
  event.preventDefault(); $("review-status").textContent = "Reviewing…"; $("review-output").replaceChildren();
  try {
    const data = await post("/api/guardian", {diff:$("diff").value});
    $("review-status").textContent = data.count + " possible finding(s). Heuristic review only.";
    for (const finding of data.findings) renderCard($("review-output"), finding.severity.toUpperCase()+" · "+finding.rule, finding.path+":"+finding.line+" — "+finding.message);
  } catch (error) {$("review-status").textContent = "Error: " + error.message;}
});
