#!/bin/bash

# Script to launch Jekyll site locally (and on the local network).
# Usage: ./serve.sh

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Try to get this machine\'s LAN IP (for access from other devices)
get_lan_ip() {
    if command -v hostname &> /dev/null; then
        hostname -I 2>/dev/null | awk '{print $1; exit}'
    elif command -v ip &> /dev/null; then
        ip -4 route get 1 2>/dev/null | grep -oE 'src [0-9.]+' | awk '{print $2}' | head -1
    elif [[ "$(uname -s)" == "Darwin" ]]; then
        ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null
    fi
}

echo -e "${GREEN}Starting Jekyll local server...${NC}"

# Check if bundle is installed
if ! command -v bundle &> /dev/null; then
    echo -e "${RED}Error: bundle is not installed.${NC}"
    echo "Please install Ruby and Bundler first:"
    echo "  gem install bundler"
    exit 1
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Jekyll is installed (via bundle)
if ! bundle exec jekyll --version &> /dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    bundle install
fi

# Check if port is already in use and stop existing process
PORT=4002
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo -e "${YELLOW}Port $PORT is in use. Stopping existing process...${NC}"
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Show where to open the site
echo -e "${GREEN}Starting Jekyll server (host 0.0.0.0, baseurl \"\")...${NC}"
echo -e "${BLUE}On this machine:  http://localhost:$PORT/${NC}"
LAN_IP=$(get_lan_ip)
if [[ -n "$LAN_IP" ]]; then
    echo -e "${CYAN}On local network: http://${LAN_IP}:$PORT/${NC}"
fi
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Serve on all interfaces so other devices on the LAN can connect; empty baseurl for local dev
bundle exec jekyll serve --host 0.0.0.0 --port "$PORT" --baseurl ""
