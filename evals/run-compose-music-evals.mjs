#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const DEFAULT_PROMPTS = join(ROOT, "evals", "compose-music.prompts.csv");
const DEFAULT_CHECKS = join(ROOT, "evals", "compose-music.checks.json");
const DEFAULT_ARTIFACTS = join(ROOT, "evals", "artifacts");

function parseArgs(argv) {
  const args = {
    prompts: DEFAULT_PROMPTS,
    checks: DEFAULT_CHECKS,
    artifacts: DEFAULT_ARTIFACTS,
    answersDir: DEFAULT_ARTIFACTS,
    runCodex: false,
    dryRun: false
  };
  for (let index = 2; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === "--run-codex") args.runCodex = true;
    else if (value === "--dry-run") args.dryRun = true;
    else if (value === "--prompts") args.prompts = argv[++index];
    else if (value === "--checks") args.checks = argv[++index];
    else if (value === "--artifacts") {
      args.artifacts = argv[++index];
      args.answersDir = args.artifacts;
    } else if (value === "--answers-dir") args.answersDir = argv[++index];
    else throw new Error(`unsupported argument: ${value}`);
  }
  return args;
}

function parseCsvLine(line) {
  const fields = [];
  let current = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === '"' && line[index + 1] === '"') {
      current += '"';
      index += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      fields.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  fields.push(current);
  return fields;
}

function loadPrompts(path) {
  const lines = readFileSync(path, "utf8").trim().split(/\r?\n/);
  const header = parseCsvLine(lines.shift());
  return lines.map((line) => {
    const fields = parseCsvLine(line);
    return Object.fromEntries(header.map((key, index) => [key, fields[index] ?? ""]));
  });
}

function runCodex(prompt, id, artifactsDir) {
  const fullPrompt = `Use $compose-music. ${prompt}`;
  const result = spawnSync("codex", ["exec", "--json", fullPrompt], { encoding: "utf8" });
  writeFileSync(join(artifactsDir, `${id}.trace.jsonl`), result.stdout + result.stderr);
  if (result.status !== 0) {
    return `codex exec failed with status ${result.status}\n${result.stderr}`;
  }
  const finalLines = result.stdout
    .trim()
    .split(/\r?\n/)
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    })
    .filter(Boolean);
  const final = [...finalLines].reverse().find((item) => typeof item.message === "string" || typeof item.output === "string");
  return final?.message || final?.output || result.stdout;
}

function extractCompositionSpec(text) {
  const fenced = [...text.matchAll(/```(?:json)?\s*([\s\S]*?)```/g)].map((match) => match[1]);
  const candidates = fenced.length ? fenced : [text];
  for (const candidate of candidates) {
    const trimmed = candidate.trim();
    try {
      const parsed = JSON.parse(trimmed);
      if (parsed?.composition_spec) return parsed.composition_spec;
      if (parsed?.version === "1.0" && parsed?.tracks && parsed?.sections) return parsed;
    } catch {
      // Continue with lightweight extraction below.
    }
  }
  return null;
}

function validateCompositionSpec(spec) {
  if (!spec) return { ok: false, errors: ["composition_spec not found"] };
  const result = spawnSync("python3", ["compose-music/scripts/validate_composition_spec.py", "-"], {
    cwd: ROOT,
    input: JSON.stringify(spec),
    encoding: "utf8"
  });
  try {
    return JSON.parse(result.stdout);
  } catch {
    return { ok: false, errors: [result.stderr || result.stdout || "validator did not return JSON"] };
  }
}

function hasAll(text, keywords) {
  const lower = text.toLowerCase();
  return keywords.every((keyword) => lower.includes(String(keyword).toLowerCase()));
}

function hasAny(text, keywords) {
  const lower = text.toLowerCase();
  return keywords.some((keyword) => lower.includes(String(keyword).toLowerCase()));
}

function sectionSumOk(text, expectedBars, spec) {
  if (spec?.brief?.length_bars === expectedBars) {
    const total = (spec.sections || []).reduce((sum, section) => sum + Number(section.length_bars || 0), 0);
    return total === expectedBars;
  }
  const lower = text.toLowerCase();
  return lower.includes(`${expectedBars}-bar`) || lower.includes(`${expectedBars} bar`) || lower.includes(`${expectedBars} bars`);
}

function fullTemplatePresent(text) {
  return hasAll(text, ["Composition Brief", "Pattern Grid", "Harmony Map", "Section Plan", "Ableton Execution Notes", "Finish Checklist"]);
}

function checkOutput(prompt, output, checksConfig) {
  const spec = extractCompositionSpec(output);
  const checks = [];
  const add = (id, ok, message) => checks.push({ id, ok, message });

  for (const check of checksConfig.global_checks) {
    if (check.type === "absence_regex") {
      const regex = new RegExp(check.pattern, "im");
      add(check.id, !regex.test(output), check.description);
    } else if (check.type === "max_regex_count") {
      const regex = new RegExp(check.pattern, "g");
      const count = [...output.matchAll(regex)].length;
      add(check.id, count <= check.max, `${check.description} Count: ${count}`);
    } else if (check.type === "conditional_keywords") {
      const shouldCheck = hasAll(output, check.when_all);
      add(check.id, !shouldCheck || hasAny(output, check.any), check.description);
    }
  }

  if (prompt.narrow === "true") {
    add("narrow_no_full_template", !fullTemplatePresent(output), "Narrow request must not emit the full song-sketch template.");
  }
  if (prompt.requires_spec === "true") {
    const validation = validateCompositionSpec(spec);
    add("composition_spec_valid", validation.ok, validation.ok ? "composition_spec validates." : validation.errors.join("; "));
  }
  if (prompt.requested_length_bars) {
    add(
      "requested_section_sum",
      sectionSumOk(output, Number(prompt.requested_length_bars), spec),
      `Requested length should be ${prompt.requested_length_bars} bars.`
    );
  }

  for (const check of checksConfig.prompt_checks[prompt.id] || []) {
    if (check.type === "all_keywords") add(check.id, hasAll(output, check.keywords), `Needs all keywords: ${check.keywords.join(", ")}`);
    else if (check.type === "any_keywords") add(check.id, hasAny(output, check.keywords), `Needs one keyword: ${check.keywords.join(", ")}`);
    else if (check.type === "forbid_full_template") add(check.id, !fullTemplatePresent(output), "Must not include the full template.");
    else if (check.type === "requires_composition_spec") {
      const validation = validateCompositionSpec(spec);
      add(check.id, validation.ok, validation.ok ? "composition_spec validates." : validation.errors.join("; "));
    } else if (check.type === "section_sum") {
      add(check.id, sectionSumOk(output, check.expected_bars, spec), `Section sum should be ${check.expected_bars}.`);
    }
  }

  const failures = checks.filter((check) => !check.ok).map((check) => check.id);
  return {
    prompt_id: prompt.id,
    score: checks.length ? (checks.length - failures.length) / checks.length : 0,
    checks,
    failures
  };
}

function main() {
  const args = parseArgs(process.argv);
  const prompts = loadPrompts(args.prompts);
  const checksConfig = JSON.parse(readFileSync(args.checks, "utf8"));
  mkdirSync(args.artifacts, { recursive: true });
  if (args.dryRun) {
    const summary = { prompts: prompts.length, global_checks: checksConfig.global_checks.length };
    console.log(JSON.stringify(summary, null, 2));
    return;
  }

  const results = [];
  for (const prompt of prompts) {
    let output;
    if (args.runCodex) {
      output = runCodex(prompt.prompt, prompt.id, args.artifacts);
      writeFileSync(join(args.artifacts, `${prompt.id}.final.txt`), output);
    } else {
      const finalPath = join(args.answersDir, `${prompt.id}.final.txt`);
      output = existsSync(finalPath) ? readFileSync(finalPath, "utf8") : "";
    }
    const rubric = checkOutput(prompt, output, checksConfig);
    writeFileSync(join(args.artifacts, `${prompt.id}.rubric.json`), `${JSON.stringify(rubric, null, 2)}\n`);
    results.push(rubric);
  }
  const failed = results.filter((result) => result.failures.length > 0);
  const summary = {
    ok: failed.length === 0,
    total: results.length,
    failed: failed.map((result) => ({ prompt_id: result.prompt_id, failures: result.failures }))
  };
  writeFileSync(join(args.artifacts, "summary.json"), `${JSON.stringify(summary, null, 2)}\n`);
  console.log(JSON.stringify(summary, null, 2));
  if (!summary.ok) process.exitCode = 1;
}

main();
