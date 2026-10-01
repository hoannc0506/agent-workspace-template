#!/usr/bin/env python3
"""
Workspace hook: redact secrets/credentials before they reach the model.
Works for BOTH Claude Code and Codex (Codex is detected by `turn_id` in the input).
Its patterns are also reused by .agents/tools/memory-lint.

Handles two hook events (dispatched on hook_event_name):

  * PostToolUse      -> Claude: silently rewrites tool output (Read/Bash/Grep/etc.)
                        via `updatedToolOutput`, masking secrets to first5***last5.
                        Codex: tool output can't be rewritten yet, so a SECURITY
                        WARNING is injected via additionalContext.
  * UserPromptSubmit -> cannot rewrite prompt text on either agent, so it BLOCKS the
                        prompt when a high-confidence secret is present.

Detection has two tiers:
  HIGH  - known token shapes / private keys. Used for BOTH redaction and prompt blocking.
  GENERIC - key=value style assignments (password=, api_key: ...). Used for redaction
            only (too noisy to block prompts on).

Fail-open by design: any error -> exit 0 with no output, so a hook bug never wedges
your session. Set REDACT_DEBUG=1 to log to ~/.claude/hooks/redact.log.
"""
import json
import os
import re
import sys

LOG = os.path.expanduser("~/.claude/hooks/redact.log")


def debug(msg):
    if os.environ.get("REDACT_DEBUG"):
        try:
            with open(LOG, "a") as f:
                f.write(msg + "\n")
        except Exception:
            pass


# (kind, compiled regex). Group 0 is replaced unless the pattern captures a group
# named "secret", in which case only that group is redacted (keeps the key visible).
def _p(kind, pattern, flags=0):
    return (kind, re.compile(pattern, flags))


HIGH = [
    _p("aws-access-key", r"\b(?:AKIA|ASIA|AGPA|AIDA|AROA|ANPA)[A-Z0-9]{16}\b"),
    _p("gcp-api-key", r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    _p("github-token", r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b"),
    _p("github-pat", r"\bgithub_pat_[A-Za-z0-9_]{60,}\b"),
    _p("anthropic-key", r"\bsk-ant-[A-Za-z0-9_\-]{20,}\b"),
    _p("openai-key", r"\bsk-(?:proj-)?[A-Za-z0-9_\-]{20,}\b"),
    _p("slack-token", r"\bxox[baprs]-[A-Za-z0-9\-]{10,}\b"),
    _p("stripe-key", r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}\b"),
    _p("google-oauth", r"\bya29\.[0-9A-Za-z_\-]{20,}\b"),
    _p("private-key", r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----.*?-----END (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----", re.DOTALL),
    _p("jwt", r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b"),
    _p("bearer-token", r"(?i)\bBearer\s+(?P<secret>[A-Za-z0-9_\-\.=]{20,})"),
    _p("slack-webhook", r"https://hooks\.slack\.com/services/[A-Za-z0-9/]+"),
]

# key = value / key: value assignments for common secret-ish names.
GENERIC = [
    _p(
        "credential-assignment",
        r"(?i)\b(?P<key>password|passwd|secret|api[_\-]?key|apikey|access[_\-]?token|"
        r"auth[_\-]?token|client[_\-]?secret|private[_\-]?key|db[_\-]?pass|"
        r"connection[_\-]?string)\b\s*[:=]\s*(?P<secret>[\"']?[^\s\"']{6,}[\"']?)",
    ),
]


def _mask(value):
    """first5***last5. If too short to keep both ends hidden, mask entirely."""
    if value is None:
        return "***"
    v = str(value)
    if len(v) <= 12:  # keeping 10 chars of a <=12 char secret reveals ~all of it
        return "***"
    return f"{v[:5]}***{v[-5:]}"


def _redact_str(s, patterns):
    """Return (redacted_string, [kinds_found])."""
    found = []
    for kind, rx in patterns:
        def repl(m, kind=kind):
            found.append(kind)
            if "secret" in (m.groupdict() or {}) and m.group("secret") is not None:
                prefix = m.string[m.start():m.start("secret")]
                return prefix + _mask(m.group("secret"))
            return _mask(m.group(0))
        s = rx.sub(repl, s)
    return s, found


def redact_tree(obj, patterns):
    """Recursively redact string leaves in a JSON-ish structure. Returns (obj, kinds)."""
    kinds = []
    if isinstance(obj, str):
        new, found = _redact_str(obj, patterns)
        return new, found
    if isinstance(obj, list):
        out = []
        for item in obj:
            v, f = redact_tree(item, patterns)
            out.append(v)
            kinds += f
        return out, kinds
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            nv, f = redact_tree(v, patterns)
            out[k] = nv
            kinds += f
        return out, kinds
    return obj, kinds


def _is_codex(data):
    """Both agents send `tool_response` and `prompt`; only Codex sends `turn_id`
    on turn-scoped events (PostToolUse, UserPromptSubmit)."""
    return "turn_id" in data


def handle_post_tool_use(data):
    codex = _is_codex(data)
    result = data.get("tool_response")
    if result is None:
        sys.exit(0)
    patterns = HIGH + GENERIC
    new_result, kinds = redact_tree(result, patterns)
    if not kinds:
        sys.exit(0)
    kinds_str = ", ".join(sorted(set(kinds)))
    debug(f"PostToolUse[{'codex' if codex else 'claude'}] "
          f"{data.get('tool_name')}: redacted {sorted(set(kinds))}")

    if codex:
        # Codex cannot rewrite tool output yet (updatedMCPToolOutput is parsed but
        # marks the hook run as failed), so only a warning is injected.
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"SECURITY WARNING: the preceding tool output contains "
                    f"{len(kinds)} secret/credential value(s) ({kinds_str}). "
                    "Treat them as sensitive: do not echo, store, or transmit them."
                ),
            }
        }))
    else:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "updatedToolOutput": new_result,
                "additionalContext": (
                    f"Note: the tool output above had {len(kinds)} secret value(s) "
                    f"auto-redacted ({kinds_str}). Do not attempt to reconstruct them."
                ),
            }
        }))
    sys.exit(0)


def handle_user_prompt_submit(data):
    # Claude: user_prompt   Codex: prompt (block-only on both, identical wire shape)
    prompt = data.get("user_prompt") or data.get("prompt") or ""
    _, kinds = _redact_str(prompt, HIGH)  # block only on high-confidence hits
    if not kinds:
        sys.exit(0)
    debug(f"UserPromptSubmit: blocked, found {sorted(set(kinds))}")
    print(json.dumps({
        "decision": "block",
        "reason": (
            "Your prompt appears to contain a secret/credential "
            f"({', '.join(sorted(set(kinds)))}). It was NOT sent to the model. "
            "Remove or replace the secret (e.g. use a placeholder or an env var "
            "reference) and resubmit."
        ),
    }))
    sys.exit(0)


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception as e:
        debug(f"parse error: {e}")
        sys.exit(0)  # fail open

    event = data.get("hook_event_name")
    try:
        if event == "PostToolUse":
            handle_post_tool_use(data)
        elif event == "UserPromptSubmit":
            handle_user_prompt_submit(data)
        else:
            sys.exit(0)
    except Exception as e:
        debug(f"handler error: {e}")
        sys.exit(0)  # fail open


if __name__ == "__main__":
    main()
