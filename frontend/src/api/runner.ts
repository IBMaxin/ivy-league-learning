// Coding execution concern only. No network, no UI.
export interface RunResult {
  output: string;
}

export function runJavaScript(code: string): RunResult {
  const logs: string[] = [];
  const sandboxConsole = { log: (...a: unknown[]) => logs.push(a.map(String).join(" ")) };
  try {
    const fn = new Function("console", `"use strict";\n${code}\n`);
    const t = setTimeout(() => {
      throw new Error("timeout");
    }, 2000);
    const ret = fn(sandboxConsole) as unknown;
    clearTimeout(t);
    if (ret !== undefined) logs.push(String(ret));
    return { output: logs.join("\n") || "(no output)" };
  } catch (e) {
    return { output: `Error: ${(e as Error).message}` };
  }
}

export function analyzePython(code: string): RunResult {
  // Browser-safe: emulate print("...") / arithmetic only, explain the rest.
  const out: string[] = [];
  for (const line of code.split("\n")) {
    const m = line.match(/^\s*print\((.*)\)\s*$/);
    if (m) {
      try {
        const val = new Function(`"use strict";return (${m[1]});`)() as unknown;
        out.push(typeof val === "string" ? val : JSON.stringify(val));
      } catch {
        out.push(m[1]);
      }
    }
  }
  if (out.length > 0) return { output: out.join("\n") };
  return {
    output: [
      "Python runs server-side in an isolated sandbox (see backend /api/code/run).",
      "Browser preview shows print() output only.",
    ].join("\n"),
  };
}

export function analyzeRust(code: string): RunResult {
  const lines = code.split("\n").length;
  const hasUnsafe = /\bunsafe\b/.test(code);
  return {
    output: [
      `Rust: ${lines} lines received.`,
      hasUnsafe ? "Contains `unsafe` — review ownership rules." : "No `unsafe` detected.",
      "Compile with `cargo run` locally or paste into the Rust Playground.",
    ].join("\n"),
  };
}
