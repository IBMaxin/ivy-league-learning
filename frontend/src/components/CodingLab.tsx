import { useState } from "react";
import { analyzePython, analyzeRust, runJavaScript } from "../api/runner";
import { api, authErrorMessage, getUser } from "../api/client";

type Lang = "javascript" | "python" | "rust";
const STARTER: Record<Lang, string> = {
  javascript: 'console.log("hello ivy");\nconsole.log(2 + 3 * 2);',
  python: 'print("hello ivy")\nprint(2 + 3 * 2)',
  rust: 'fn main() {\n    println!("hello ivy");\n}',
};

export default function CodingLab() {
  const [lang, setLang] = useState<Lang>("javascript");
  const [code, setCode] = useState(STARTER.javascript);
  const [out, setOut] = useState("");
  const [serverOut, setServerOut] = useState("");

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
      <h2>Coding Lab</h2>
      <select value={lang} onChange={(e) => {
        const l = e.target.value as Lang;
        setLang(l);
        setCode(STARTER[l]);
      }}>
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
