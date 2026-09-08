const { WebSocketServer } = require("ws");

const wss = new WebSocketServer({ port: 8765 });
console.log("Mock WebSocket server running on ws://localhost:8765");

const EVENTS = [
  { task_id: "demo", step: "classify", payload: { task_type: "drafting", confidence: 0.94 }, timestamp: "2026-09-07T14:32:01Z" },
  { task_id: "demo", step: "plan", payload: { summary: "Extract fields, verify, draft note" }, timestamp: "2026-09-07T14:32:02Z" },
  { task_id: "demo", step: "tool_call", payload: { tool_name: "extract_from_image", input: { image_path: "uploads/scan_001.jpg" } }, timestamp: "2026-09-07T14:32:03Z" },
  { task_id: "demo", step: "verify_pass", payload: { tool_name: "verify_numeric", detail: "within tolerance" }, timestamp: "2026-09-07T14:32:04Z" },
  { task_id: "demo", step: "done", payload: { artifacts: [{ type: "docx", filename: "approval_note_unit2.docx", path: "outputs/approval_note_unit2.docx" }], summary: "Extracted 6 fields from scan, verified 5, drafted approval note." }, timestamp: "2026-09-07T14:32:05Z" }
];

wss.on("connection", (ws) => {
  console.log("Frontend connected to mock stream");
  EVENTS.forEach((event, index) => {
    setTimeout(() => {
      if (ws.readyState === ws.OPEN) {
        ws.send(JSON.stringify(event));
      }
    }, (index + 1) * 1200);
  });
});