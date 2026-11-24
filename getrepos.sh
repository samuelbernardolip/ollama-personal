#!/usr/bin/env bash

ORG="$1"
SINCE="2024-01-01T00:00:00Z" # Format: YYYY-MM-DDTHH:MM:SSZ
URL="https://api.github.com/orgs/$ORG/repos?per_page=100&sort=pushed&direction=desc"

echo "Fetching repositories for '$ORG' updated since $SINCE..."

# Check if 'gh' is installed and authenticated
if command -v gh &> /dev/null && gh auth status &> /dev/null; then
  echo "Using GitHub CLI (gh)..."
  REPOS=$(gh repo list "$ORG" --limit 100 --json pushedAt,sshUrl \
    --jq ".[] | select(.pushedAt >= \"$SINCE\") | .sshUrl")
else
  echo "GitHub CLI not available or not logged in. Falling back to curl..."
  if ! command -v jq &> /dev/null; then
    echo "Error: 'jq' is required when falling back to curl. Please install jq."
    exit 1
  fi
  REPOS=$(curl -sf -H "User-Agent: bash-script" $URL | \
    jq -r ".[] | select(.pushed_at >= \"$SINCE\") | .ssh_url")
fi

if [ -z "$REPOS" ]; then
  echo "No repositories found matching that date."
  exit 0
fi

echo -e "\nThe following repositories will be cloned via SSH:"
echo "$REPOS"
echo ""

# Pause and prompt for confirmation (case-insensitive)
read -r -p "Do you want to continue? [y/N]: " response
case "${response,,}" in
  y|yes)
    echo "Cloning repositories..."
    echo "$REPOS" | xargs -n 1 git clone
    ;;
  *)
    echo "Aborted."
    exit 1
    ;;
esac

