#!/bin/bash

# 1. Gather Basic Info (same as before)
PROJECT_INFO=$(cat package.json 2>/dev/null | jq -r '.name + " v" + .version' || echo "Unknown project")
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
NODE_VER=$(node -v 2>/dev/null || echo 'not installed')

# 2. Read the Markdown File
# Change 'PROJECT_CONTEXT.md' to your actual filename
MD_FILE="code.md"

if [ -f "$MD_FILE" ]; then
    # Read the file content
    MD_CONTENT=$(cat "$MD_FILE")
else
    MD_CONTENT="(No $MD_FILE found)"
fi

# 3. Construct the Header
HEADER="Project: $PROJECT_INFO | Branch: $BRANCH | Node: $NODE_VER"

# 4. Generate JSON using jq
# We use --arg to pass shell variables safely into jq. 
# jq handles all the escaping for newlines and quotes automatically.
jq -n \
  --arg header "$HEADER" \
  --arg md "$MD_CONTENT" \
  '{
    hookSpecificOutput: {
      hookEventName: "SessionStart",
      additionalContext: ($header + "\n\n--- Context File ---\n" + $md)
    }
  }'