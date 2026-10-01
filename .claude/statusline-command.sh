#!/usr/bin/env bash
set -euo pipefail

input="$(cat)"

read_value() {
  INPUT="$input" KEY_PATH="$1" python3 - <<'PY'
import json
import os

try:
    value = json.loads(os.environ["INPUT"])
    for key in os.environ["KEY_PATH"].split("."):
        value = value.get(key, "")
    print(value if value is not None else "")
except Exception:
    print("")
PY
}

cwd="$(read_value cwd)"
model="$(read_value model.display_name)"
used_pct="$(read_value context_window.used_percentage)"

line="$cwd"
[[ -n "$model" ]] && line+="  $model"
[[ -n "$used_pct" ]] && line+="  context: ${used_pct}% used"

if [[ -n "$cwd" ]] && git -C "$cwd" rev-parse --git-dir >/dev/null 2>&1; then
  branch="$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null || git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null || true)"
  [[ -n "$branch" ]] && line+="  git: $branch"
fi

printf '%s\n' "$line"
