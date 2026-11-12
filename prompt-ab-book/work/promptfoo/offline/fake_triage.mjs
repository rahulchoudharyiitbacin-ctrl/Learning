// OFFLINE STAND-IN for the model. No network, no key, no cost.
// A keyword rule, deliberately imperfect, so some tests fail.
// Its accuracy numbers mean NOTHING about Claude or the prompts.
// Use:  npx promptfoo eval -r file://offline/fake_triage.mjs
const RULES = [
  ["refund", ["refund", "money back", "charged"]],
  ["account", ["log in", "password", "account", "phone number"]],
  ["delivery", ["driver", "late", "delivered", "address"]],
];

export default class FakeTriage {
  id() {
    return "fake-triage";
  }
  async callApi(prompt) {
    let system = "";
    let user = prompt;
    try {
      const msgs = JSON.parse(prompt);
      system = msgs.find((m) => m.role === "system")?.content ?? "";
      user = msgs.find((m) => m.role === "user")?.content ?? "";
    } catch {}
    const text = user.toLowerCase();
    // Pretend the few-shot prompt (v2) knows one extra word.
    const extra = system.includes("Examples:") ? ["reimbursed"] : [];
    let label = "other";
    for (const [name, words] of RULES) {
      if (words.some((w) => text.includes(w))) { label = name; break; }
    }
    if (label === "other" && extra.some((w) => text.includes(w))) {
      label = "refund";
    }
    return { output: label };
  }
}
