#!/bin/bash

# Get the list of changed files
CHANGED_FILES=$(git status --porcelain)

# Check if there are any changed files
if [ -z "$CHANGED_FILES" ]; then
    echo "No changes to commit"
    exit 0
fi

echo "Committing changes"
git add .
git commit -m "Deploy on $(date)"

CP_PATH=""

OS=$(uname)
if [ "$OS" == "Linux" ]; then
    echo "Running on Linux"
    
    # Identify the Linux distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            ubuntu|debian)
                CP_PATH="/media/$USER"
                ;;
            fedora|centos|rhel)
                CP_PATH="/run/media/$USER"
                ;;
            arch)
                CP_PATH="/run/media/$USER"
                ;;
            *)
                echo "Unknown Linux distribution: $ID"
                CP_PATH="/media"
                ;;
        esac
    else
        echo "Cannot determine Linux distribution"
        CP_PATH="/media"
    fi

elif [ "$OS" == "Darwin" ]; then
    echo "Running on macOS"
    CP_PATH="/Volumes"
else
    echo "Unknown operating system: $OS"
    exit 1
fi

echo "Copying code to CircuitPython drive"
CP_PATH="$CP_PATH/CIRCUITPY"
# Check if the CircuitPython drive is mounted
if [ ! -d "$CP_PATH" ]; then
    echo "CircuitPython drive not found at $CP_PATH"
    exit 1
fi

# Process each changed file line by line
echo "$CHANGED_FILES" | while IFS= read -r line; do
    file_path=$(echo "$line" | awk '{print $2}')
    action=$(echo "$line" | awk '{print $1}')
    if [ "$action" == "D" ]; then
        echo "Deleting file: $file_path"
        rm "$CP_PATH/$file_path"
    elif [ "$action" == "M" ] || [ "$action" == "??" ]; then
        echo "Copying file: $file_path"
        cp "$file_path" "$CP_PATH/$file_path"
    else
        echo "Unknown action $action for file: $file_path"
        continue
    fi
done

echo "Copied $(echo "$CHANGED_FILES" | wc -l) files to $CP_PATH"