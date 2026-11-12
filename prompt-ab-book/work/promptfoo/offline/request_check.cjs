// Captures the request promptfoo would send to the real endpoint,
// WITHOUT any network: fetch is disabled and messages.create is stubbed.
globalThis.fetch = async () => { throw new Error("network disabled in test"); };
const { loadApiProvider } = require("promptfoo"); // NODE_PATH must point at a local install
(async () => {
  for (const base of [undefined, "http://127.0.0.1:9"]) {
    const config = { max_tokens: 1024, effort: "low" };
    if (base) config.apiBaseUrl = base;
    const p = await loadApiProvider("anthropic:messages:claude-haiku-5-5", { options: { config } });
    let sent = null;
    const stub = async (params) => { sent = params; return {
      id: "x", type: "message", role: "assistant", model: params.model,
      content: [{ type: "text", text: "refund" }], stop_reason: "end_turn",
      usage: { input_tokens: 1, output_tokens: 1 } }; };
    p.anthropic.messages.create = stub;
    const prompt = JSON.stringify([{ role: "system", content: "S" }, { role: "user", content: "U" }]);
    const r = await p.callApi(prompt);
    console.log("baseURL:", p.anthropic.baseURL, "| output:", r.output, r.error ?? "");
    const { messages, system, ...rest } = sent;
    console.log("  sent:", JSON.stringify(rest));
  }
})();
