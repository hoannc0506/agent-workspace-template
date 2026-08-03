#!/bin/bash
input=$(cat)

# Parse JSON using python3 (no jq dependency)
_get() {
  python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    keys = '$1'.split('.')
    for k in keys:
        if k: d = d.get(k, '')
    print(d if d is not None else '')
except: print('')
" <<< "$input"
}

cwd=$(_get cwd)
model=$(_get model.display_name)
used_pct=$(_get context_window.used_percentage)
total_input=$(_get context_window.total_input_tokens)
ctx_size=$(_get context_window.context_window_size)
repo_host=$(_get workspace.repo.host)
repo_owner=$(_get workspace.repo.owner)
repo_name=$(_get workspace.repo.name)
pr_number=$(_get pr.number)
pr_url=$(_get pr.url)
pr_state=$(_get pr.review_state)

# ANSI colors
RESET='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'
RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
CYAN='\033[36m'

# Line 1: Directory + Model + Context window usage
dir_display="${cwd/#$HOME/\~}"
line1=$(printf "${BOLD}${CYAN}%s${RESET}" "$dir_display")
[ -n "$model" ] && line1+=$(printf "  ${DIM}%s${RESET}" "$model")

if [ -n "$used_pct" ] && [ "$used_pct" != "0" ]; then
  used_int=$(printf '%.0f' "$used_pct" 2>/dev/null || echo 0)
  if [ "$used_int" -ge 80 ]; then ctx_color="$RED"
  elif [ "$used_int" -ge 50 ]; then ctx_color="$YELLOW"
  else ctx_color="$GREEN"; fi
  used_k=$(python3 -c "print(f'{$total_input/1000:.1f}k')" 2>/dev/null || echo "${total_input}")
  line1+=$(printf "  ${DIM}ctx:${RESET} ${ctx_color}%s%%%s${RESET} ${DIM}(%s / %s)${RESET}" \
    "$used_int" " used" "$used_k" "$ctx_size")
fi

# Line 2: Git status + GitHub repo/PR link
line2=""
if [ -n "$cwd" ] && git -C "$cwd" rev-parse --git-dir >/dev/null 2>&1; then
  branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null \
           || git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null)
  staged=$(git -C "$cwd" --no-optional-locks diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
  unstaged=$(git -C "$cwd" --no-optional-locks diff --name-only 2>/dev/null | wc -l | tr -d ' ')
  untracked=$(git -C "$cwd" --no-optional-locks ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')

  branch_display=$(printf "${BOLD}${BLUE}%s${RESET}" "$branch")
  status_parts=""
  [ "$staged" -gt 0 ]    && status_parts+=$(printf " ${GREEN}+%s staged${RESET}" "$staged")
  [ "$unstaged" -gt 0 ]  && status_parts+=$(printf " ${YELLOW}~%s unstaged${RESET}" "$unstaged")
  [ "$untracked" -gt 0 ] && status_parts+=$(printf " ${RED}?%s untracked${RESET}" "$untracked")
  [ -z "$status_parts" ] && status_parts=$(printf " ${GREEN}clean${RESET}")
  line2=$(printf "git: %s%s" "$branch_display" "$status_parts")
fi

if [ -n "$repo_host" ] && [ -n "$repo_owner" ] && [ -n "$repo_name" ]; then
  repo_url="https://${repo_host}/${repo_owner}/${repo_name}"
  repo_link=$(printf '\033]8;;%s\033\\%s/%s\033]8;;\033\\' "$repo_url" "$repo_owner" "$repo_name")
  [ -n "$line2" ] && line2+="  "
  line2+=$(printf "${CYAN}%s${RESET}" "$repo_link")
  if [ -n "$pr_number" ] && [ -n "$pr_url" ]; then
    case "$pr_state" in
      approved)           pr_color="$GREEN"  ;;
      changes_requested)  pr_color="$RED"    ;;
      draft)              pr_color="$DIM"    ;;
      *)                  pr_color="$YELLOW" ;;
    esac
    pr_link=$(printf '\033]8;;%s\033\\PR #%s (%s)\033]8;;\033\\' "$pr_url" "$pr_number" "${pr_state:-open}")
    line2+=$(printf "  ${pr_color}%s${RESET}" "$pr_link")
  fi
fi

# Assemble
out=""
add() { [ -n "$1" ] && { [ -n "$out" ] && out+="\n"; out+="$1"; }; }
add "$line1"
add "$line2"

printf "%b\n" "$out"
