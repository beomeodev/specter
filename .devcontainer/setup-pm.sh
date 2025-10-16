#!/bin/bash
# Project Manager Setup Script
# Run this once on a new machine to enable 'pm' command
# Supports both bash and zsh

echo "🚀 Setting up Project Manager (pm) function..."

PM_FUNCTION='
# ======= Project Manager (pm) =======
# Usage: pm <project> <command>
# Example: pm sab cc  → cd to spade-ace-backtester && make sabcc
function pm() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "❌ Usage: pm <project> <command>"
        echo "Example: pm sab cc"
        return 1
    fi
    cd /mnt/d/underway_project/$1 && make -C .devcontainer -f Makefile ${1}${2}
}
'

# Detect and add to appropriate shell config
ADDED_TO=""

# Add to bash if it exists
if [ -f ~/.bashrc ]; then
    if ! grep -q "function pm()" ~/.bashrc 2>/dev/null; then
        echo "$PM_FUNCTION" >> ~/.bashrc
        ADDED_TO="~/.bashrc"
    else
        echo "⚠️  pm function already exists in ~/.bashrc (skipped)"
    fi
fi

# Add to zsh if it exists
if [ -f ~/.zshrc ]; then
    if ! grep -q "function pm()" ~/.zshrc 2>/dev/null; then
        echo "$PM_FUNCTION" >> ~/.zshrc
        if [ -z "$ADDED_TO" ]; then
            ADDED_TO="~/.zshrc"
        else
            ADDED_TO="$ADDED_TO and ~/.zshrc"
        fi
    else
        echo "⚠️  pm function already exists in ~/.zshrc (skipped)"
    fi
fi

# Report results
if [ -n "$ADDED_TO" ]; then
    echo "✅ pm function added to $ADDED_TO"
    echo ""
    echo "To activate immediately, run:"
    if [[ "$ADDED_TO" == *"bashrc"* ]]; then
        echo "  source ~/.bashrc"
    fi
    if [[ "$ADDED_TO" == *"zshrc"* ]]; then
        echo "  source ~/.zshrc"
    fi
else
    echo "ℹ️  pm function already configured"
fi

echo ""
echo "Usage examples:"
echo "  pm sab cc  # Start spade-ace-backtester with Claude Code"
echo "  pm sab cx  # Start spade-ace-backtester with Codex"
echo "  pm sab cr  # Resume last Codex session"
echo ""
echo "🎉 Setup complete!"
