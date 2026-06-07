#!/bin/bash

# Download and install Quarto (Cloudflare Pages doesn't have it pre-installed)
echo "Downloading Quarto..."
curl -LO https://github.com/quarto-dev/quarto-cli/releases/download/v1.4.554/quarto-1.4.554-linux-amd64.tar.gz

echo "Extracting Quarto..."
mkdir -p _quarto_install
tar -zxvf quarto-1.4.554-linux-amd64.tar.gz -C _quarto_install --strip-components=1

# Add Quarto to the path
export PATH="$(pwd)/_quarto_install/bin:$PATH"

# Render the Quarto website
echo "Rendering Quarto website..."
quarto render
