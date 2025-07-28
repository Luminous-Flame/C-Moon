#!/bin/bash

if [ -n "$ZSH_VERSION" ]; then
  current_shell="zsh"
elif [ -n "$BASH_VERSION" ]; then
  current_shell="bash"
else
  echo "지원되지 않는 쉘: $SHELL"
  exit 1
fi

rcfile="$HOME/.${current_shell}rc"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" && pwd)"

alias_marker="# >>> C-Moon alias >>>"
alias_block=$(cat <<EOF

$alias_marker
alias cmoon='source ~/.c-moon/bin/activate'
alias cview='python3 $SCRIPT_DIR/scripts/view.py'
alias cupdate='python3 $SCRIPT_DIR/scripts/update.py'
# <<< C-Moon alias <<<

EOF
)

if ! grep -qF "$alias_marker" "$rcfile"; then
  echo "$alias_block" >> "$rcfile"
  echo "alias add complete: $rcfile"
else
  echo "Already present alias : $rcfile"
fi

if [ -f "$rcfile" ]; then
  echo "Applying : $rcfile"
  source "$rcfile"
else
  echo "No rc file : $rcfile"
  exit 1
fi

