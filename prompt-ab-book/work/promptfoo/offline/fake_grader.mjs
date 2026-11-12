// OFFLINE STAND-IN for an llm-rubric grader. It only checks that the
// output is one of the four labels and answers in the JSON shape
// promptfoo expects from a grader: {pass, score, reason}.
export default class FakeGrader {
  id() {
    return "fake-grader";
  }
  async callApi(prompt) {
    let text = String(prompt);
    try {
      const msgs = JSON.parse(text);   // chat-format grading prompt
      text = msgs.map((m) => m.content).join("\n");
    } catch {}
    // The grading prompt has worked examples first; the output
    // under test is the LAST <Output> block.
    const all = [...text.matchAll(/<Output>([\s\S]*?)<\/Output>/gi)];
    const out = (all.length ? all[all.length - 1][1] : "").trim().toLowerCase();
    const ok = ["refund", "delivery", "account", "other"].includes(out);
    return {
      output: JSON.stringify({
        pass: ok, score: ok ? 1 : 0,
        reason: ok ? "one valid label" : `not a label: ${out.slice(0, 40)}`,
      }),
    };
  }
}
