#!/bin/bash

# Function to check if a command exists and print its version
check_command_version() {
    if command -v $1 &> /dev/null; then
        echo -n "$1: "
        $1 $2 2>&1 | head -n 1
    fi
}

# Function to find all commands containing a specific string
find_commands() {
    compgen -c | grep -E "$1"
}

echo "=== Python-related commands and their versions ==="

# Check common Python commands
check_command_version "python" "--version"
check_command_version "python3" "--version"
check_command_version "pip" "--version"
check_command_version "pip3" "--version"

echo -e "\n=== All commands containing 'python', 'py', or 'pip' ==="

# Find and check all commands containing 'python', 'py', or 'pip'
commands=$(find_commands "python|py|pip")
for cmd in $commands; do
    check_command_version "$cmd" "--version"
done

echo -e "\n=== Python path ==="
which python
which python3

echo -e "\n=== Python installation directories ==="
ls -l /usr/bin/python* 2>/dev/null
ls -l /usr/local/bin/python* 2>/dev/null

echo -e "\n=== System Python information ==="
python -c "import sys; print(sys.version); print(sys.executable)"

echo -e "\n=== Pip list ==="
pip list 2>/dev/null || pip3 list 2>/dev/null

echo -e "\n=== Environment variables ==="
env | grep -i "python"