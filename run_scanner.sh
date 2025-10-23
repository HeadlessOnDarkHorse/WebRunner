#!/bin/bash

# ============================================================================
#  Web Automation Framework Runner Script
# ============================================================================
# This script is the entrypoint for the Podman container. It will:
#   1. Prompt the user for their credentials and test parameters.
#   2. Set the necessary environment variables.
#   3. Run the web crawler and scanner.
# ============================================================================

echo "========================================="
echo " Web Automation Framework"
echo "========================================="
echo

# --- 1. Prompt for User Input ---
read -p "Enter the URL to scan: " url
read -p "Enter the crawl depth (default: 1): " depth
read -p "Run AODA scan? (y/n, default: n): " aoda_scan_choice
read -p "Enter your Azure username: " azure_username
read -s -p "Enter your Azure password: " azure_password
echo
echo

# --- 2. Set Defaults and Environment Variables ---
if [ -z "$depth" ]; then
    depth=1
fi

export AZURE_USERNAME=$azure_username
export AZURE_PASSWORD=$azure_password

# --- 3. Construct and Run the Command ---
aoda_flag=""
if [[ "$aoda_scan_choice" == "y" || "$aoda_scan_choice" == "Y" ]]; then
    aoda_flag="--aoda-scan"
fi

echo "[INFO] Starting the scan with the following parameters:"
echo "  - URL: $url"
echo "  - Crawl Depth: $depth"
echo "  - AODA Scan: $aoda_scan_choice"
echo

python web_automation_framework/src/main.py "$url" --depth "$depth" $aoda_flag
