#!/bin/bash
set -euo pipefail

# =================================================================================
# Git Workflow Starter 🚀 v2.0
# =================================================================================

# Colors (satisfy ShellCheck SC2034)
readonly GREEN=$'\033[0;32m'
readonly YELLOW=$'\033[1;33m'
readonly BLUE=$'\033[0;34m'
readonly PURPLE=$'\033[0;35m'
readonly NC=$'\033[0m'

spinner() {
    local pid="$1"
    local spinstr='⠏⠇⠧⠦⠴⠼⠸⠹'
    local i=0
    while kill -0 "$pid" 2>/dev/null; do
        i=$(((i + 1) % 8))
        printf '\r%s %sWaiting...%s' "${spinstr:i:1}" "${PURPLE}" "${NC}"
        sleep 0.1
    done
    printf '\r\033[K\n'
}

log_info()    { printf '%s%s%s\n' "${BLUE}" "$1" "${NC}"; }
log_success() { printf '%s%s%s\n' "${GREEN}" "$1" "${NC}"; }
log_warn()    { printf '%s%s%s\n' "${YELLOW}" "$1" "${NC}"; }

printf '\n%s=== START-WORK ===%s\n' "${GREEN}" "${NC}"

# 1. Stash check
if git status --porcelain | grep -q .; then
    printf '%sUncommitted changes detected%s\n' "${YELLOW}" "${NC}"
    printf '%sStash and continue? (y/n): %s' "${YELLOW}" "${NC}"
    read -r choice
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        git stash push -m "Auto-stash by start-work.sh" &
        spinner "$!"
        log_success "Changes stashed ✓"
    else
        log_warn "Please commit/stash manually"
        exit 1
    fi
fi

# 2. Branch type (simple numbered menu)
printf '\n%sSelect branch type:%s\n' "${BLUE}" "${NC}"
echo "1) feature/  2) bugfix/  3) hotfix/  4) none"
printf '%sPick (1-4): %s' "${BLUE}" "${NC}"
read -r pick
case "$pick" in
    1|feature|feat) PREFIX="feature/";;
    2|bugfix|fix|bug) PREFIX="bugfix/";;
    3|hotfix) PREFIX="hotfix/";;
    *) PREFIX="";;
esac

# 3. Branch name
printf '\n%sBranch name: %s' "${BLUE}" "${NC}"
read -r name
CLEAN_NAME=$(echo "$name" | tr '[:upper:]' '[:lower:]' | tr -s ' ' '-' | sed 's/[^a-z0-9-]//g' | sed 's/^-*//;s/-*$//')

if [[ -z "$CLEAN_NAME" ]]; then
    log_warn "Invalid name, using 'work'"
    CLEAN_NAME="work"
fi

BRANCH="${PREFIX}${CLEAN_NAME}"
log_info "Creating/switching to: $BRANCH"

# 4. Git sync & branch
git fetch origin
MAIN_BRANCH=$(git remote show origin 2>/dev/null | grep 'HEAD branch' | cut -d' ' -f5 || echo "main")

log_info "Syncing $MAIN_BRANCH..."
git checkout "$MAIN_BRANCH"
git pull origin "$MAIN_BRANCH"

if git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
    log_info "Branch exists, switching..."
    git checkout "$BRANCH"
else
    log_success "Creating new branch: $BRANCH"
    git checkout -b "$BRANCH" "$MAIN_BRANCH"
fi

log_success "✅ Ready on branch: $BRANCH"
