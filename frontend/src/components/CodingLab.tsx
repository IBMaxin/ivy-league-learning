import { useState } from "react";
import { analyzePython, analyzeRust, runJavaScript } from "../api/runner";
import { api, authErrorMessage, getUser } from "../api/client";

type Lang = "javascript" | "python" | "rust";
const STARTER: Record<Lang, string> = {
  javascript: 'console.log("hello ivy");\nconsole.log(2 + 3 * 2);',
  python: 'print("hello ivy")\nprint(2 + 3 * 2)',
  rust: 'fn main() {\n    println!("hello ivy");\n}',
};

interface LabResult {
  input: string;
  expected: unknown;
  actual?: unknown;
  passed: boolean;
  error?: string;
}

const LABS: { id: string; label: string }[] = [
  { id: "py-101", label: "Python Basics: Square" },
  { id: "algs-101", label: "Algorithms: Palindrome" },
  { id: "ds-101", label: "Data Structures: Stack Top" },
];

export default function CodingLab() {
  // Lab challenge state (server-validated).
  const [lesson, setLesson] = useState("py-101");
  const [prompt, setPrompt] = useState("");
  const [labCode, setLabCode] = useState("");
  const [results, setResults] = useState<LabResult[]>([]);
  const [labStatus, setLabStatus] = useState("");

  // Playground state (local runner + server sandbox).
  const [lang, setLang] = useState<Lang>("javascript");
  const [code, setCode] = useState(STARTER.javascript);
  const [out, setOut] = useState("");
  const [serverOut, setServerOut] = useState("");

  async function loadLab() {
    try {
      const d = await api.getLab(lesson);
      setPrompt(d.prompt);
      setLabCode("");
      setResults([]);
      setLabStatus("");
    } catch (e) {
      setLabStatus(authErrorMessage(e));
    }
  }

  async function submitLab() {
    if (!getUser()) {
      setLabStatus("Login required — sign in above.");
      return;
    }
    setLabStatus("Validating…");
    try {
      const r = await api.submitLab({ lesson_id: lesson, code: labCode });
      setResults(r.results);
      setLabStatus(r.success ? "Challenge complete!" : "Some tests failed. Keep trying!");
    } catch (e) {
      setLabStatus(authErrorMessage(e));
    }
  }

  function run() {
    if (lang === "javascript") setOut(runJavaScript(code).output);
    else if (lang === "python") setOut(analyzePython(code).output);
    else setOut(analyzeRust(code).output);
  }

  async function sendServer() {
    if (!getUser()) {
      setServerOut("Login required — sign in above.");
      return;
    }
    setServerOut("Sending…");
    try {
      const r = await api.runCode(lang, code);
      setServerOut(r.output);
    } catch (e) {
      setServerOut(authErrorMessage(e));
    }
  }

  return (
    <section>
      <h2>Interactive Coding Labs</h2>
      <div style={{ marginBottom: 16 }}>
        <select value={lesson} onChange={(e) => setLesson(e.target.value)}>
          {LABS.map((l) => (
            <option key={l.id} value={l.id}>
              {l.label}
            </option>
          ))}
        </select>{" "}
        <button onClick={() => void loadLab()}>Load Challenge</button>
      </div>

      {prompt && (
        <div
          style={{
            background: "#f9f9f9",
            padding: 12,
            borderRadius: 8,
            marginBottom: 12,
            border: "1px solid #ddd",
          }}
        >
          <strong>Challenge:</strong> {prompt}
        </div>
      )}

      <textarea
        value={labCode}
        onChange={(e) => setLabCode(e.target.value)}
        rows={8}
        style={{ width: "100%", fontFamily: "monospace", marginBottom: 12 }}
        placeholder="Write your function here…"
      />
      <br />
      <button onClick={() => void submitLab()} disabled={!prompt}>
        Submit to Validator
      </button>

      <p aria-live="polite" style={{ fontWeight: "bold", margin: "12px 0" }}>
        {labStatus}
      </p>

      {results.length > 0 && (
        <div style={{ marginTop: 16, marginBottom: 24 }}>
          <h3>Test Results</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {results.map((res, i) => (
              <div
                key={i}
                style={{
                  padding: 8,
                  border: "1px solid #ddd",
                  borderRadius: 4,
                  backgroundColor: res.passed ? "#e6ffed" : "#ffeef0",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>
                    Test {i + 1}: {res.input}
                  </span>
                  <span>{res.passed ? "Pass" : "Fail"}</span>
                </div>
                {!res.passed && (
                  <div style={{ fontSize: "0.9em", color: "#d73a49", marginTop: 4 }}>
                    Expected: {JSON.stringify(res.expected)} | Actual:{" "}
                    {JSON.stringify(res.actual ?? res.error)}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <hr />
      <h2>Playground</h2>
      <select
        value={lang}
        onChange={(e) => {
          const l = e.target.value as Lang;
          setLang(l);
          setCode(STARTER[l]);
        }}
      >
        <option value="javascript">JavaScript (runs in browser)</option>
        <option value="python">Python (preview + server sandbox)</option>
        <option value="rust">Rust (analysis)</option>
      </select>
      <textarea value={code} onChange={(e) => setCode(e.target.value)} rows={10} cols={60} />
      <br />
      <button onClick={run}>Run locally</button>{" "}
      <button onClick={() => void sendServer()}>Send to server sandbox</button>
      <pre aria-live="polite">{out}</pre>
      {serverOut && <pre aria-live="polite">Server: {serverOut}</pre>}
    </section>
  );
}
