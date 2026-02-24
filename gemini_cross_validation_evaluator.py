import argparse
import getpass
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from google import genai
from google.genai import types


@dataclass
class EvalConfig:
    model: str = "gemini-2.5-flash"
    temperature: float = 0.0
    max_output_tokens: int = 800
    input_json_path: Path = Path("personality_validation_20251228_090433.json")
    output_dir: Path = Path(".")
    sleep_seconds: float = 0.2
    max_retries: int = 3


PERSONALITY_DEFINITIONS: Dict[str, str] = {
    "average": (
        "Average (Gerlach et al., 2018): moderate/balanced Big Five profile. "
        "Language tends to be practical, non-extreme, nuanced, uses qualifiers (e.g., 'it depends', 'sometimes'). "
        "Avoids absolutist statements, avoids extreme emotionality."
    ),
    "role_model": (
        "Role Model (Gerlach et al., 2018): low neuroticism, high extraversion, high openness, "
        "high agreeableness, high conscientiousness. Language is upbeat, confident, prosocial, "
        "organized, constructive, goal-oriented, cooperative, emotionally stable."
    ),
    "self_centred": (
        "Self-Centred (Gerlach et al., 2018): relatively higher neuroticism and extraversion, "
        "low openness, low agreeableness, low conscientiousness. Language is self-focused, competitive, "
        "status/advantage seeking, blunt, low empathy, conventional, impatient with teamwork; may reject cooperation."
    ),
    "reserved": (
        "Reserved (Gerlach et al., 2018): low neuroticism, low extraversion, low openness, "
        "moderate agreeableness, moderate conscientiousness. Language is calm, brief, conventional, "
        "prefers routine, polite but distant, avoids novelty and high social energy."
    ),
}


GEMINI_RESPONSE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "expected_personality": {"type": "string"},
        "predicted_personality": {
            "type": "string",
            "enum": ["average", "role_model", "self_centred", "reserved"],
        },
        "match_score": {"type": "integer"},
        "pass": {"type": "boolean"},
        "big_five_estimates": {
            "type": "object",
            "properties": {
                "N": {"type": "integer"},
                "E": {"type": "integer"},
                "O": {"type": "integer"},
                "A": {"type": "integer"},
                "C": {"type": "integer"},
            },
            "required": ["N", "E", "O", "A", "C"],
        },
        "strengths": {"type": "array", "items": {"type": "string"}},
        "concerns": {"type": "array", "items": {"type": "string"}},
        "evidence_quotes": {"type": "array", "items": {"type": "string"}},
        "reasoning": {"type": "string"},
    },
    "required": [
        "expected_personality",
        "predicted_personality",
        "match_score",
        "pass",
        "big_five_estimates",
        "strengths",
        "concerns",
        "evidence_quotes",
        "reasoning",
    ],
}


def _safe_json_extract(text: str) -> Dict[str, Any]:
    text = text.strip()

    # Common Gemini behavior: wrap JSON in fenced code blocks.
    if "```" in text:
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
        if fence_match:
            text = fence_match.group(1).strip()

    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    # If it looks like JSON but is missing a closing brace, treat as truncated output.
    if text.startswith("{") and "}" not in text:
        raise ValueError("Model returned truncated JSON (missing closing brace)")

    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        raise ValueError("No JSON object found in model output")

    return json.loads(m.group(0))


def _now_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _load_validation_dataset(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_eval_prompt(expected_personality: str, question: str, claude_response: str) -> Tuple[str, str]:
    system = (
        "You are an independent evaluator performing a blind audit of an AI assistant's personality behavior. "
        "You MUST evaluate whether the response matches the intended personality type described below. "
        "Do NOT assume the response is correct; judge based only on the text. "
        "You must return a single JSON object only."
    )

    definitions_block = "\n\n".join([f"- {k}: {v}" for k, v in PERSONALITY_DEFINITIONS.items()])

    user = (
        "BLIND PERSONALITY VALIDATION (Mode B)\n\n"
        "Goal: Determine whether the RESPONSE matches the TARGET personality.\n\n"
        f"TARGET personality key: {expected_personality}\n"
        f"TARGET personality definition: {PERSONALITY_DEFINITIONS[expected_personality]}\n\n"
        "For your reference, here are the 4 possible personality definitions:\n"
        f"{definitions_block}\n\n"
        "QUESTION (prompt asked to the assistant):\n"
        f"{question}\n\n"
        "RESPONSE (text to evaluate):\n"
        f"{claude_response}\n\n"
        "Return a JSON object with these keys:\n"
        "- expected_personality: string (the TARGET key you were given)\n"
        "- predicted_personality: string (one of: average, role_model, self_centred, reserved)\n"
        "- match_score: integer 0-100 (how well RESPONSE matches TARGET)\n"
        "- pass: boolean (true if match_score >= 70 AND predicted_personality == expected_personality)\n"
        "- big_five_estimates: object with keys N,E,O,A,C each integer 1-5 (your estimate from the response text)\n"
        "- strengths: array of 2-5 short strings (evidence supporting match)\n"
        "- concerns: array of 0-5 short strings (evidence against match / inconsistencies)\n"
        "- evidence_quotes: array of 2-5 short direct quotes from RESPONSE\n"
        "- reasoning: string (brief audit-style rationale, 3-8 sentences)\n"
        "OUTPUT RULES:\n"
        "- Output ONLY the JSON object.\n"
        "- Do NOT include markdown.\n"
        "- Do NOT include code fences.\n"
        "- The first character MUST be '{' and the last character MUST be '}'."
    )

    return system, user


def _call_gemini_text(
    client: genai.Client,
    cfg: EvalConfig,
    system: str,
    user: str,
) -> str:
    resp = client.models.generate_content(
        model=cfg.model,
        contents=user,
        config={
            "system_instruction": system,
            "temperature": cfg.temperature,
            "max_output_tokens": cfg.max_output_tokens,
            "response_mime_type": "application/json",
            "response_schema": GEMINI_RESPONSE_SCHEMA,
        },
    )

    parsed = getattr(resp, "parsed", None)
    if parsed is not None:
        return json.dumps(parsed, ensure_ascii=False)

    text = getattr(resp, "text", None)
    if text is None:
        text = json.dumps(getattr(resp, "model_dump", lambda: resp)(), indent=2)  # type: ignore[misc]
    text = str(text)
    if not text.strip():
        raise RuntimeError("Gemini returned empty text output")
    return text


def evaluate_one(
    client: genai.Client,
    cfg: EvalConfig,
    item: Dict[str, Any],
) -> Dict[str, Any]:
    expected = str(item.get("personality_type") or "").strip()
    prompt = str(item.get("prompt") or "")
    claude_response = str(item.get("response") or "")

    if expected not in PERSONALITY_DEFINITIONS:
        raise ValueError(f"Unexpected personality_type in dataset: {expected}")

    system, user = _build_eval_prompt(expected, prompt, claude_response)

    last_err: Optional[Exception] = None
    raw_text: str = ""
    parsed: Dict[str, Any]

    def _repair_prompt(bad_output: str) -> Tuple[str, str]:
        repair_system = (
            "You are an independent evaluator. You must output a single VALID JSON object only. "
            "No markdown, no code fences, no extra text."
        )
        repair_user = (
            "Your previous output was invalid or truncated JSON. Re-emit the FULL JSON object according to the required schema.\n\n"
            "Partial/invalid output (for reference):\n"
            f"{bad_output[:4000]}\n\n"
            "Now output ONLY the corrected JSON object."
        )
        return repair_system, repair_user

    for _ in range(cfg.max_retries):
        try:
            raw_text = _call_gemini_text(client, cfg, system, user)
            parsed = _safe_json_extract(raw_text)
            break
        except Exception as e:
            last_err = e

            # If Gemini returned partial JSON, attempt a one-shot repair request before sleeping.
            if raw_text.strip().startswith("{"):
                try:
                    rs, ru = _repair_prompt(raw_text)
                    raw_text = _call_gemini_text(client, cfg, rs, ru)
                    parsed = _safe_json_extract(raw_text)
                    break
                except Exception as e2:
                    last_err = e2

            time.sleep(max(cfg.sleep_seconds, 0.1))
    else:
        try:
            cfg.output_dir.mkdir(parents=True, exist_ok=True)
            fail_path = cfg.output_dir / f"gemini_parse_failure_{_now_ts()}.txt"
            with open(fail_path, "w", encoding="utf-8") as f:
                f.write(raw_text)
        except Exception:
            fail_path = None

        suffix = f" (raw saved to: {fail_path})" if fail_path else ""
        raise RuntimeError(f"Gemini call/parsing failed after retries: {last_err}{suffix}")

    predicted = parsed.get("predicted_personality")
    match_score = parsed.get("match_score")

    try:
        score_int = int(match_score)
    except Exception:
        score_int = 0

    parsed["expected_personality"] = expected
    parsed["pass"] = bool(score_int >= 70 and predicted == expected)

    return {
        "expected_personality": expected,
        "category": item.get("category"),
        "prompt": prompt,
        "claude_response": claude_response,
        "gemini_raw": raw_text,
        "gemini_parsed": parsed,
    }


def summarize(evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
    per_personality: Dict[str, Dict[str, Any]] = {}
    confusion: Dict[str, Dict[str, int]] = {
        k: {k2: 0 for k2 in PERSONALITY_DEFINITIONS.keys()} for k in PERSONALITY_DEFINITIONS.keys()
    }

    overall_scores: List[int] = []

    for ev in evaluations:
        expected = ev.get("expected_personality")
        parsed = ev.get("gemini_parsed", {})
        predicted = parsed.get("predicted_personality")
        score = parsed.get("match_score")
        passed = bool(parsed.get("pass"))

        try:
            score_int = int(score)
        except Exception:
            score_int = 0

        overall_scores.append(score_int)

        if expected not in per_personality:
            per_personality[expected] = {"count": 0, "scores": [], "passes": 0}

        per_personality[expected]["count"] += 1
        per_personality[expected]["scores"].append(score_int)
        per_personality[expected]["passes"] += 1 if passed else 0

        if expected in confusion and predicted in confusion[expected]:
            confusion[expected][predicted] += 1

    for p, stats in per_personality.items():
        scores = stats.get("scores", [])
        count = int(stats.get("count", 0))
        passes = int(stats.get("passes", 0))
        per_personality[p] = {
            "count": count,
            "avg_score": sum(scores) / len(scores) if scores else 0.0,
            "pass_rate": (passes / count) if count else 0.0,
        }

    return {
        "overall": {
            "count": len(evaluations),
            "avg_score": sum(overall_scores) / len(overall_scores) if overall_scores else 0.0,
        },
        "per_personality": per_personality,
        "confusion_matrix": confusion,
    }


def render_markdown_report(
    cfg: EvalConfig,
    input_dataset: Dict[str, Any],
    summary: Dict[str, Any],
    output_json_path: Path,
    evaluations: List[Dict[str, Any]],
) -> str:
    lines: List[str] = []
    lines.append("# Gemini Blind Validation Report (Mode B)")
    lines.append("")
    lines.append(f"**Evaluator Model:** `{cfg.model}`")
    lines.append(f"**Temperature:** `{cfg.temperature}`")
    lines.append(f"**Input Dataset:** `{cfg.input_json_path.name}`")
    lines.append(f"**Output Evaluations:** `{output_json_path.name}`")
    lines.append("")

    session = input_dataset.get("session_info", {})
    lines.append("## Scope")
    lines.append("")
    lines.append(
        "This report evaluates **Claude-generated** responses from the existing validation session dated "
        f"`{session.get('date', 'unknown')}`. `{cfg.model}` acted as an **independent judge** (Mode B), meaning it did not "
        "use our internal marker lists and instead judged the responses against high-level Gerlach personality definitions."
    )
    lines.append("")

    lines.append("## Inputs (What Gemini is validating)")
    lines.append("")
    lines.append(f"- **Input dataset:** `{cfg.input_json_path.name}`")
    lines.append(f"- **Total items:** {summary['overall']['count']}")
    lines.append("- **Unit of evaluation:** one (prompt, Claude response) pair")
    lines.append("")
    lines.append(
        "Each dataset item includes the intended personality (`personality_type`), the test category (`category`), "
        "the prompt (`prompt`), and Claude’s generated response (`response`). The evaluator does not regenerate Claude responses; "
        "it only judges the fixed text in the dataset."
    )
    lines.append("")

    lines.append("## Personality definitions used by Gemini (Mode B rubric)")
    lines.append("")
    lines.append("Gemini is instructed to classify each response as exactly one of:")
    lines.append("")
    lines.append("1. **Average**: balanced, practical, moderate; uses qualifiers; avoids absolutes")
    lines.append("2. **Role Model**: upbeat, prosocial, cooperative, organized; emotionally stable")
    lines.append("3. **Self-Centred**: self-focused, competitive, blunt, low empathy; may reject teamwork")
    lines.append("4. **Reserved**: calm, brief, conventional; prefers routine; low social energy")
    lines.append("")

    lines.append("## Step-by-step validation procedure (repeatable)")
    lines.append("")
    lines.append("### Step 1: Prepare environment")
    lines.append("")
    lines.append("- Install dependencies: `pip install -r requirements.txt`")
    lines.append("- Set your API key: `GEMINI_API_KEY` environment variable")
    lines.append("")

    lines.append("### Step 2: Run the evaluator")
    lines.append("")
    lines.append("Example command used for this report:")
    lines.append("")
    lines.append("```bash")
    lines.append(
        f"python gemini_cross_validation_evaluator.py --model {cfg.model} --input {cfg.input_json_path.name} --output-dir {str(cfg.output_dir).replace('\\\\', '/')}"
    )
    lines.append("```")
    lines.append("")
    lines.append("Outputs:")
    lines.append(f"- **Raw evaluations JSON:** `{output_json_path.name}`")
    lines.append("- **Summary report (this file):** `gemini_validation_report_<timestamp>.md`")
    lines.append("")

    lines.append("### Step 3: What is sent to Gemini for each evaluation")
    lines.append("")
    lines.append(
        "For each item, the evaluator sends Gemini: (a) the target personality key, (b) the target definition, "
        "(c) all four possible personality definitions, (d) the prompt, and (e) the Claude response text."
    )
    lines.append("")

    lines.append("### Step 4: What Gemini must return (strict JSON)")
    lines.append("")
    lines.append("Gemini is required to return a single JSON object with:")
    lines.append("- `predicted_personality` (one of: average, role_model, self_centred, reserved)")
    lines.append("- `match_score` (0–100)")
    lines.append("- `pass` (boolean)")
    lines.append("- `big_five_estimates` (N,E,O,A,C on a 1–5 scale)")
    lines.append("- `strengths`, `concerns`, `evidence_quotes`, `reasoning`")
    lines.append("")
    lines.append(
        "The evaluator then applies the pass/fail rule stored in the output JSON metadata: "
        "`pass if match_score >= 70 and predicted_personality == expected_personality`."
    )
    lines.append("")

    lines.append("### Step 5: Aggregation")
    lines.append("")
    lines.append(
        "After all items are scored, the script computes per-personality average scores, pass rates, and a confusion matrix "
        "(expected vs Gemini predicted)."
    )
    lines.append("")

    lines.append("## Overall Summary")
    lines.append("")
    lines.append(f"- **Total items evaluated:** {summary['overall']['count']}")
    lines.append(f"- **Average match score (0-100):** {summary['overall']['avg_score']:.2f}")
    lines.append("")

    lines.append("## Per-Personality Results")
    lines.append("")
    lines.append("| Personality | Items | Avg Gemini Match Score | Pass Rate |")
    lines.append("|---|---:|---:|---:|")
    for p in ["average", "role_model", "self_centred", "reserved"]:
        stats = summary["per_personality"].get(p, {"count": 0, "avg_score": 0.0, "pass_rate": 0.0})
        lines.append(
            f"| {p.replace('_', ' ').title()} | {stats['count']} | {stats['avg_score']:.2f} | {stats['pass_rate']*100:.1f}% |"
        )
    lines.append("")

    lines.append("## Confusion Matrix (Expected vs Gemini Predicted)")
    lines.append("")
    header = "| Expected \\ Predicted | " + " | ".join([p.replace("_", " ").title() for p in PERSONALITY_DEFINITIONS.keys()]) + " |"
    sep = "|---|" + "---:|" * len(PERSONALITY_DEFINITIONS)
    lines.append(header)
    lines.append(sep)
    cm = summary["confusion_matrix"]
    for expected in PERSONALITY_DEFINITIONS.keys():
        row = [str(cm.get(expected, {}).get(pred, 0)) for pred in PERSONALITY_DEFINITIONS.keys()]
        lines.append("| " + expected.replace("_", " ").title() + " | " + " | ".join(row) + " |")
    lines.append("")

    def _pick_example(expected_key: str) -> Optional[Dict[str, Any]]:
        for ev in evaluations:
            if ev.get("expected_personality") == expected_key:
                return ev
        return None

    lines.append("## Worked examples (from the dataset)")
    lines.append("")
    lines.append(
        "These examples are taken directly from the raw evaluations JSON to show how the independent evaluator justified its decisions."
    )
    lines.append("")

    for expected_key, title in [
        ("average", "Average (balanced, non-extreme)"),
        ("role_model", "Role Model (upbeat, prosocial, organized)"),
        ("self_centred", "Self-Centred (self-focused, blunt, low empathy)"),
        ("reserved", "Reserved (calm, brief, routine-oriented)"),
    ]:
        ev = _pick_example(expected_key)
        if not ev:
            continue

        parsed = ev.get("gemini_parsed", {})
        lines.append(f"### Example: {title}")
        lines.append("")
        lines.append(f"- **Prompt:** {ev.get('prompt','')}")
        lines.append(f"- **Gemini predicted:** `{parsed.get('predicted_personality')}`")
        score = parsed.get("match_score")
        verdict = "PASS" if parsed.get("pass") else "FAIL"
        lines.append(f"- **Match score:** {score} ({verdict})")
        lines.append("- **Evidence quotes (Claude):**")
        for q in (parsed.get("evidence_quotes") or [])[:4]:
            lines.append(f"  - \"{q}\"")
        lines.append(f"- **Reasoning (Gemini):** {parsed.get('reasoning','')}")
        lines.append("")

    lines.append("## How this supports the mission")
    lines.append("")
    lines.append(
        "The mission of this validation study is to demonstrate that the four Gerlach personality types are "
        "(1) authentically expressed and (2) distinguishable. A blind Gemini evaluation provides external evidence "
        "that the personalities 'stand up' even when judged by an independent model family. The confusion matrix "
        "directly tests distinguishability (whether the evaluator can correctly identify the intended type), and "
        "the match scores/pass rates quantify authenticity."
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"))
    parser.add_argument(
        "--input",
        default=os.environ.get("GEMINI_VALIDATION_INPUT", "personality_validation_20251228_090433.json"),
        help="Path to personality_validation_*.json (Claude dataset)",
    )
    parser.add_argument(
        "--output-dir",
        default=os.environ.get("GEMINI_VALIDATION_OUTPUT_DIR", "."),
        help="Directory to write gemini_validation_*.json and gemini_validation_report_*.md",
    )
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key.strip().lower().startswith("your_") or len(api_key.strip()) < 20:
        api_key = getpass.getpass("Enter GEMINI_API_KEY (input hidden): ")
    api_key = (api_key or "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required.")

    cfg = EvalConfig()
    cfg.model = str(args.model)
    cfg.input_json_path = Path(str(args.input))
    cfg.output_dir = Path(str(args.output_dir))

    if not cfg.input_json_path.exists():
        raise FileNotFoundError(f"Input dataset not found: {cfg.input_json_path}")

    dataset = _load_validation_dataset(cfg.input_json_path)
    items = dataset.get("detailed_results", [])
    if not isinstance(items, list) or not items:
        raise RuntimeError("Input dataset has no detailed_results to evaluate")

    client = genai.Client(api_key=api_key)

    ts = _now_ts()
    out_json = cfg.output_dir / f"gemini_validation_{ts}.json"
    out_md = cfg.output_dir / f"gemini_validation_report_{ts}.md"

    evaluations: List[Dict[str, Any]] = []

    print("=" * 80)
    print("GEMINI BLIND PERSONALITY VALIDATION (Mode B)")
    print("=" * 80)
    print(f"Model: {cfg.model}")
    print(f"Input dataset: {cfg.input_json_path}")
    print(f"Total items: {len(items)}")

    for idx, item in enumerate(items, 1):
        expected = item.get("personality_type")
        prompt = item.get("prompt", "")

        print(f"\n[{idx}/{len(items)}] Evaluating {expected}: {str(prompt)[:70]}...")
        ev = evaluate_one(client, cfg, item)
        parsed = ev["gemini_parsed"]
        print(
            f"  Gemini predicted={parsed.get('predicted_personality')} score={parsed.get('match_score')} pass={parsed.get('pass')}"
        )

        evaluations.append(ev)
        time.sleep(cfg.sleep_seconds)

    summary = summarize(evaluations)

    payload = {
        "meta": {
            "timestamp": datetime.now().isoformat(),
            "evaluator_model": cfg.model,
            "temperature": cfg.temperature,
            "input_dataset": str(cfg.input_json_path),
            "mode": "B",
            "scoring_rule": "pass if match_score >= 70 and predicted_personality == expected_personality",
        },
        "summary": summary,
        "evaluations": evaluations,
    }

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    report_md = render_markdown_report(cfg, dataset, summary, out_json, evaluations)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(report_md)

    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80)
    print(f"Saved evaluations: {out_json}")
    print(f"Saved report: {out_md}")
    print(f"Overall avg Gemini match score: {summary['overall']['avg_score']:.2f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
