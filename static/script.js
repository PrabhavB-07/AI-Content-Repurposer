// ── Global raw result store ──
let rawResult = "";

window.onload = function () {
  const generateBtn = document.getElementById("generate-btn");
  const inputBox    = document.getElementById("content-url");
  const toneBox     = document.getElementById("tone");
  const loading     = document.getElementById("loading");

  generateBtn.addEventListener("click", async function () {
    const input = inputBox.value.trim();
    const tone  = toneBox.value;

    if (!input) {
      showToast("⚠️ Please enter a topic or URL first!", "warn");
      return;
    }

    generateBtn.disabled  = true;
    generateBtn.innerHTML = '<span class="spinner-inline"></span> Generating...';
    loading.style.display = "flex";
    hideAllCards();
    rawResult = ""; // reset

    try {
      const response = await fetch("/generate", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ url: input, tone: tone }),
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);

      const data = await response.json();
      rawResult  = data.result; // ← store raw AI response globally

      // ── Parse and fill cards ──
      const instagram = rawResult.match(/INSTAGRAM:(.*?)LINKEDIN:/s);
      const linkedin  = rawResult.match(/LINKEDIN:(.*?)TWITTER:/s);
      const twitter   = rawResult.match(/TWITTER:(.*?)BLOG:/s);
      const blog      = rawResult.match(/BLOG:(.*)/s);

      fillCard("instagram-card", "instagram-content", instagram);
      fillCard("linkedin-card",  "linkedin-content",  linkedin);
      fillCard("twitter-card",   "twitter-content",   twitter);
      fillCard("blog-card",      "blog-content",      blog);

      showToast("✅ Content generated!", "success");

      document.getElementById("result-box")
        .scrollIntoView({ behavior: "smooth", block: "start" });

    } catch (error) {
      showToast("❌ Error: " + error.message, "error");
    } finally {
      loading.style.display = "none";
      generateBtn.disabled  = false;
      generateBtn.innerHTML = "🚀 Generate Content";
    }
  });

  inputBox.addEventListener("keydown", function (e) {
    if (e.key === "Enter") generateBtn.click();
  });
};

// ── Helpers ──

function fillCard(cardId, contentId, match) {
  const card = document.getElementById(cardId);
  card.style.display = "block";
  document.getElementById(contentId).innerText =
    match ? match[1].trim() : "No content generated.";
}

function hideAllCards() {
  ["instagram-card", "linkedin-card", "twitter-card", "blog-card"]
    .forEach(id => document.getElementById(id).style.display = "none");
}

function copySection(id) {
  navigator.clipboard.writeText(document.getElementById(id).innerText);
  showToast("Copied!", "success");
}

function copyContent() {
  navigator.clipboard.writeText(document.getElementById("result-box").innerText);
  showToast("All content copied!", "success");
}

function downloadContent() {
  const b = new Blob([document.getElementById("result-box").innerText], { type: "text/plain" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(b);
  a.download = "generated-content.txt";
  a.click();
}

// ── Export PDF / DOCX — sends RAW result to backend ──
async function exportFile(format) {
  if (!rawResult) {
    showToast("⚠️ Generate content first!", "warn");
    return;
  }

  const btn  = document.getElementById("btn-" + format);
  const orig = btn.innerHTML;
  btn.innerHTML = "⏳ Exporting...";
  btn.disabled  = true;

  try {
    const res = await fetch("/export/" + format, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ content: rawResult }), // ← raw AI text with INSTAGRAM:/LINKEDIN: etc.
    });

    if (!res.ok) throw new Error("Export failed: " + res.status);

    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = format === "pdf" ? "generated-content.pdf" : "generated-content.docx";
    a.click();
    URL.revokeObjectURL(url);

    showToast(format.toUpperCase() + " downloaded! ✅", "success");

  } catch (e) {
    showToast("❌ Export error: " + e.message, "error");
  } finally {
    btn.innerHTML = orig;
    btn.disabled  = false;
  }
}

// ── Toast ──
function showToast(msg, type = "success") {
  const existing = document.getElementById("toast-msg");
  if (existing) existing.remove();

  const colors = {
    success: { bg: "rgba(16,185,129,.12)", border: "rgba(16,185,129,.3)",  color: "#6ee7b7" },
    warn:    { bg: "rgba(245,158,11,.10)", border: "rgba(245,158,11,.3)",  color: "#fcd34d" },
    error:   { bg: "rgba(239,68,68,.10)",  border: "rgba(239,68,68,.3)",   color: "#fca5a5" },
  };
  const c = colors[type] || colors.success;

  const toast = document.createElement("div");
  toast.id = "toast-msg";
  toast.innerText = msg;
  Object.assign(toast.style, {
    position:       "fixed",
    bottom:         "28px",
    right:          "28px",
    background:     c.bg,
    border:         `1px solid ${c.border}`,
    color:          c.color,
    padding:        "13px 22px",
    borderRadius:   "12px",
    fontSize:       "14px",
    fontFamily:     "'Space Grotesk', sans-serif",
    fontWeight:     "500",
    zIndex:         "9999",
    backdropFilter: "blur(12px)",
    boxShadow:      "0 8px 32px rgba(0,0,0,.3)",
  });

  if (!document.getElementById("toast-style")) {
    const s = document.createElement("style");
    s.id = "toast-style";
    s.textContent = `
      @keyframes toastIn  { from{opacity:0;transform:translateY(12px);}to{opacity:1;transform:translateY(0);} }
      @keyframes toastOut { from{opacity:1;transform:translateY(0);}to{opacity:0;transform:translateY(12px);} }
      .spinner-inline {
        display:inline-block;width:14px;height:14px;
        border:2px solid rgba(255,255,255,.2);border-top-color:#fff;
        border-radius:50%;animation:spin .7s linear infinite;
        vertical-align:middle;margin-right:6px;
      }
      @keyframes spin{to{transform:rotate(360deg);}}
    `;
    document.head.appendChild(s);
  }

  toast.style.animation = "toastIn .3s ease";
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = "toastOut .3s ease forwards";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}