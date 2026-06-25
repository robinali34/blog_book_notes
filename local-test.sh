#!/bin/bash

# Local Test Script for Jekyll Blog
# This script builds and serves the blog locally on port 4000

# Don't use set -e, we'll handle errors manually

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Jekyll Blog Local Test Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if bundle is installed
if ! command -v bundle &> /dev/null; then
    echo -e "${YELLOW}Error: bundle is not installed.${NC}"
    echo "Please install Ruby and Bundler first:"
    echo "  gem install bundler"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "Gemfile" ]; then
    echo -e "${YELLOW}Error: Gemfile not found.${NC}"
    echo "Please run this script from the blog root directory."
    exit 1
fi

# Check and fix Gemfile.lock permissions if needed
if [ -f "Gemfile.lock" ]; then
    if [ ! -w "Gemfile.lock" ]; then
        FILE_OWNER=$(stat -c '%U' Gemfile.lock 2>/dev/null || stat -f '%Su' Gemfile.lock 2>/dev/null)
        CURRENT_USER=$(whoami)
        
        if [ "$FILE_OWNER" != "$CURRENT_USER" ]; then
            echo -e "${YELLOW}Warning: Gemfile.lock is owned by $FILE_OWNER, not $CURRENT_USER${NC}"
            echo -e "${YELLOW}Attempting to fix permissions...${NC}"
            
            # Try to fix without sudo first
            chmod 644 Gemfile.lock 2>/dev/null || {
                echo -e "${YELLOW}Could not fix permissions automatically.${NC}"
                echo -e "${YELLOW}Please run the following command manually:${NC}"
                echo "  sudo chown $CURRENT_USER:$CURRENT_USER Gemfile.lock"
                echo "  chmod 644 Gemfile.lock"
                echo ""
                echo -e "${YELLOW}Or continue without updating Gemfile.lock (may cause issues)${NC}"
                # Only prompt if running interactively
                if [ -t 0 ]; then
                    read -p "Continue anyway? (y/N) " -n 1 -r
                    echo
                    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                        exit 1
                    fi
                else
                    echo -e "${YELLOW}Non-interactive mode: continuing anyway...${NC}"
                fi
            }
        fi
    fi
fi

# Install dependencies if needed
if [ ! -d "vendor/bundle" ] || [ "Gemfile" -nt "Gemfile.lock" ]; then
    echo -e "${BLUE}Installing dependencies...${NC}"
    # Use --path to install to vendor/bundle (user-writable location)
    # This avoids permission issues with system gem directory
    bundle install --path vendor/bundle || {
        echo -e "${YELLOW}Warning: bundle install failed. Trying without --path...${NC}"
        bundle install
    }
    echo ""
fi

# Clean previous build
echo -e "${BLUE}Cleaning previous build...${NC}"
bundle exec jekyll clean
echo ""

# Build the site
echo -e "${BLUE}Building the site...${NC}"
bundle exec jekyll build
echo ""

# Check if build was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo ""
else
    echo -e "${YELLOW}✗ Build failed. Please check the errors above.${NC}"
    exit 1
fi

# Get the local URL
LOCAL_URL="http://localhost:4000/blog_book_notes/"
HOST="0.0.0.0"
PORT="4000"

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Starting Jekyll server...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Server will be available at:"
echo -e "  ${GREEN}Local:  ${LOCAL_URL}${NC}"
echo -e "  ${GREEN}Network: http://${HOST}:${PORT}/blog_book_notes/${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Function to open browser (works on Linux, macOS, and Windows with WSL)
open_browser() {
    sleep 3  # Wait for server to start
    
    if command -v xdg-open &> /dev/null; then
        # Linux
        xdg-open "$LOCAL_URL" 2>/dev/null &
    elif command -v open &> /dev/null; then
        # macOS
        open "$LOCAL_URL" 2>/dev/null &
    elif command -v start &> /dev/null; then
        # Windows (Git Bash)
        start "$LOCAL_URL" 2>/dev/null &
    fi
}

# Open browser in background
open_browser &

# Start Jekyll server with all development features
bundle exec jekyll serve \
    --host "$HOST" \
    --port "$PORT" \
    --livereload \
    --incremental \
    --trace
