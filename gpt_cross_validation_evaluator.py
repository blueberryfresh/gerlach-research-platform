import json
import os
import re
import time
import getpass
import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI


@dataclass
class EvalConfig:
    model: str = "gpt-4o"
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


def _safe_json_extract(text: str) -> Dict[str, Any]:
    text = text.strip()

    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        raise ValueError("No JSON object found in GPT output")

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

    definitions_block = "\n\n".join(
        [f"- {k}: {v}" for k, v in PERSONALITY_DEFINITIONS.items()]
    )

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
        "Only output JSON."
    )

    return system, user


def _call_openai_text(
    client: OpenAI,
    cfg: EvalConfig,
    system: str,
    user: str,
) -> Tuple[str, Optional[str], str]:
    """Call OpenAI model and return (text, request_id, api_used).

    Prefer the Responses API (works with modern models like gpt-5).
    Fall back to Chat Completions if needed.
    """

    # Preferred: Responses API
    try:
        resp = client.responses.create(
            model=cfg.model,
            instructions=system,
            input=user,
            temperature=cfg.temperature,
            max_output_tokens=cfg.max_output_tokens,
        )

        text = getattr(resp, "output_text", None)
        if text is None:
            # Defensive fallback if SDK shape changes
            text = json.dumps(resp.model_dump(), indent=2)

        return text, getattr(resp, "id", None), "responses"
    except Exception as e:
        # For GPT-5 family, avoid falling back to Chat Completions.
        # GPT-5 is best supported via Responses and may reject Chat Completions parameters.
        if cfg.model.startswith("gpt-5"):
            raise e

        pass

    # Fallback: Chat Completions API
    completion = client.chat.completions.create(
        model=cfg.model,
        temperature=cfg.temperature,
        max_completion_tokens=cfg.max_output_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )

    content = completion.choices[0].message.content or ""
    return content, getattr(completion, "id", None), "chat_completions"


def evaluate_one(
    client: OpenAI,
    cfg: EvalConfig,
    item: Dict[str, Any],
) -> Dict[str, Any]:
    expected = item["personality_type"]
    question = item["prompt"]
    response = item["response"]

    system, user = _build_eval_prompt(expected, question, response)

    last_err: Optional[Exception] = None

    for attempt in range(1, cfg.max_retries + 1):
        try:
            content, request_id, api_used = _call_openai_text(client, cfg, system, user)
            parsed = _safe_json_extract(content)

            return {
                "expected_personality": expected,
                "category": item.get("category"),
                "prompt": question,
                "claude_response": response,
                "gpt_raw": content,
                "gpt_parsed": parsed,
                "openai_request_id": request_id,
                "openai_api": api_used,
                "timestamp": datetime.now().isoformat(),
                "attempt": attempt,
            }
        except Exception as e:
            last_err = e
            time.sleep(min(2.0, cfg.sleep_seconds * (2**attempt)))

    raise RuntimeError(f"GPT evaluation failed after {cfg.max_retries} retries: {last_err}")


def summarize(evals: List[Dict[str, Any]]) -> Dict[str, Any]:
    per_personality: Dict[str, Dict[str, Any]] = {}
    confusion: Dict[str, Dict[str, int]] = {
        p: {q: 0 for q in PERSONALITY_DEFINITIONS.keys()} for p in PERSONALITY_DEFINITIONS.keys()
    }

    for e in evals:
        expected = e["expected_personality"]
        parsed = e["gpt_parsed"]
        predicted = parsed.get("predicted_personality")
        score = parsed.get("match_score")
        passed = parsed.get("pass")

        if expected not in per_personality:
            per_personality[expected] = {
                "count": 0,
                "pass_count": 0,
                "avg_score": 0.0,
                "scores": [],
            }

        per_personality[expected]["count"] += 1
        if isinstance(score, (int, float)):
            per_personality[expected]["scores"].append(float(score))

        if passed is True:
            per_personality[expected]["pass_count"] += 1

        if expected in confusion and predicted in confusion[expected]:
            confusion[expected][predicted] += 1

    for p, stats in per_personality.items():
        scores = stats["scores"]
        stats["avg_score"] = sum(scores) / len(scores) if scores else 0.0
        stats["pass_rate"] = stats["pass_count"] / stats["count"] if stats["count"] else 0.0

    overall_scores = [s for p in per_personality.values() for s in p.get("scores", [])]

    return {
        "overall": {
            "count": len(evals),
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
    lines.append("# GPT Blind Validation Report (Mode B)")
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
        f"This report evaluates **Claude-generated** responses from the existing validation session dated "
        f"`{session.get('date', 'unknown')}`. `{cfg.model}` acted as an **independent judge** (Mode B), meaning it did not "
        f"use our internal marker lists and instead judged the responses against high-level Gerlach personality definitions."  # noqa: E501
    )
    lines.append("")

    lines.append("## Inputs (What GPT is validating)")
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

    lines.append("## Personality definitions used by GPT (Mode B rubric)")
    lines.append("")
    lines.append("GPT is instructed to classify each response as exactly one of:")
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
    lines.append("- Set your API key: `OPENAI_API_KEY` environment variable")
    lines.append("")

    lines.append("### Step 2: Run the evaluator")
    lines.append("")
    lines.append("Example command used for this report:")
    lines.append("")
    lines.append("```bash")
    lines.append(
        f"python gpt_cross_validation_evaluator.py --model {cfg.model} --input {cfg.input_json_path.name} --output-dir {str(cfg.output_dir).replace('\\\\', '/')}"
    )
    lines.append("```")
    lines.append("")
    lines.append("Outputs:")
    lines.append(f"- **Raw evaluations JSON:** `{output_json_path.name}`")
    lines.append("- **Summary report (this file):** `gpt_validation_report_<timestamp>.md`")
    lines.append("")

    lines.append("### Step 3: What is sent to GPT for each evaluation")
    lines.append("")
    lines.append(
        "For each item, the evaluator sends GPT: (a) the target personality key, (b) the target definition, "
        "(c) all four possible personality definitions, (d) the prompt, and (e) the Claude response text."
    )
    lines.append("")

    lines.append("### Step 4: What GPT must return (strict JSON)")
    lines.append("")
    lines.append("GPT is required to return a single JSON object with:")
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
        "(expected vs GPT predicted)."
    )
    lines.append("")

    lines.append("## Overall Summary")
    lines.append("")
    lines.append(f"- **Total items evaluated:** {summary['overall']['count']}")
    lines.append(f"- **Average match score (0-100):** {summary['overall']['avg_score']:.2f}")
    lines.append("")

    lines.append("## Per-Personality Results")
    lines.append("")
    lines.append("| Personality | Items | Avg GPT Match Score | Pass Rate |")
    lines.append("|---|---:|---:|---:|")
    for p in ["average", "role_model", "self_centred", "reserved"]:
        stats = summary["per_personality"].get(p, {"count": 0, "avg_score": 0.0, "pass_rate": 0.0})
        lines.append(
            f"| {p.replace('_', ' ').title()} | {stats['count']} | {stats['avg_score']:.2f} | {stats['pass_rate']*100:.1f}% |"
        )
    lines.append("")

    lines.append("## Confusion Matrix (Expected vs GPT Predicted)")
    lines.append("")
    header = "| Expected \\ Predicted | " + " | ".join([p.replace('_', ' ').title() for p in PERSONALITY_DEFINITIONS.keys()]) + " |"
    sep = "|---|" + "---:|" * len(PERSONALITY_DEFINITIONS)
    lines.append(header)
    lines.append(sep)
    cm = summary["confusion_matrix"]
    for expected in PERSONALITY_DEFINITIONS.keys():
        row = [str(cm.get(expected, {}).get(pred, 0)) for pred in PERSONALITY_DEFINITIONS.keys()]
        lines.append(
            "| " + expected.replace("_", " ").title() + " | " + " | ".join(row) + " |"
        )
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

        parsed = ev.get("gpt_parsed", {})
        lines.append(f"### Example: {title}")
        lines.append("")
        lines.append(f"- **Prompt:** {ev.get('prompt','')}")
        lines.append(f"- **GPT predicted:** `{parsed.get('predicted_personality')}`")
        score = parsed.get("match_score")
        verdict = "PASS" if parsed.get("pass") else "FAIL"
        lines.append(f"- **Match score:** {score} ({verdict})")
        lines.append("- **Evidence quotes (Claude):**")
        for q in (parsed.get("evidence_quotes") or [])[:4]:
            lines.append(f"  - \"{q}\"")
        lines.append(f"- **Reasoning (GPT):** {parsed.get('reasoning','')}")
        lines.append("")

    lines.append("## How this supports the mission")
    lines.append("")
    lines.append(
        "The mission of this validation study is to demonstrate that the four Gerlach personality types are "
        "(1) authentically expressed and (2) distinguishable. A blind GPT evaluation provides external evidence "
        "that the personalities 'stand up' even when judged by an independent model family. The confusion matrix "
        "directly tests distinguishability (whether the evaluator can correctly identify the intended type), and "
        "the match scores/pass rates quantify authenticity."  # noqa: E501
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-4o"))
    parser.add_argument(
        "--input",
        default=os.environ.get("GPT_VALIDATION_INPUT", "personality_validation_20251228_090433.json"),
        help="Path to personality_validation_*.json (Claude dataset)",
    )
    parser.add_argument(
        "--output-dir",
        default=os.environ.get("GPT_VALIDATION_OUTPUT_DIR", "."),
        help="Directory to write gpt_validation_*.json and gpt_validation_report_*.md",
    )
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or api_key.strip().lower().startswith("your_") or len(api_key.strip()) < 30:
        api_key = getpass.getpass("Enter OPENAI_API_KEY (input hidden): ")
    api_key = (api_key or "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required.")

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

    client = OpenAI(api_key=api_key)

    ts = _now_ts()
    out_json = cfg.output_dir / f"gpt_validation_{ts}.json"
    out_md = cfg.output_dir / f"gpt_validation_report_{ts}.md"

    evaluations: List[Dict[str, Any]] = []

    print("=" * 80)
    print("GPT BLIND PERSONALITY VALIDATION (Mode B)")
    print("=" * 80)
    print(f"Model: {cfg.model}")
    print(f"Input dataset: {cfg.input_json_path}")
    print(f"Total items: {len(items)}")

    for idx, item in enumerate(items, 1):
        expected = item.get("personality_type")
        prompt = item.get("prompt", "")

        print(f"\n[{idx}/{len(items)}] Evaluating {expected}: {prompt[:70]}...")
        ev = evaluate_one(client, cfg, item)
        parsed = ev["gpt_parsed"]
        print(
            f"  GPT predicted={parsed.get('predicted_personality')} score={parsed.get('match_score')} pass={parsed.get('pass')}"
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
    print(f"Overall avg GPT match score: {summary['overall']['avg_score']:.2f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
