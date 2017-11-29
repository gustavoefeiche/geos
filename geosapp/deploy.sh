#!/bin/bash
if command -v python3 &>/dev/null; then
    python3 cloud-setup.py
else
    echo "Python 3 is required"
fi
