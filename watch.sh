#!/bin/bash

# Command to run when changes are detected
COMMAND="bash deploy.sh"

# Detect the operating system
OS=$(uname)
INSTALLED=false
if [ "$OS" == "Linux" ]; then
    if ! command -v inotifywait &> /dev/null; then
        INSTALLED=false
    else
        INSTALLED=true
    fi
elif [ "$OS" == "Darwin" ]; then
    if ! command -v fswatch &> /dev/null; then
        INSTALLED=false
    else
        INSTALLED=true
    fi
else
    echo "Unknown operating system: $OS"
    INSTALLED=false
fi

if [ "$INSTALLED" == "false" ]; then
    while true; do
        # Check if there are modified but uncommitted files
        CHANGED_FILES=$(git status --porcelain | grep '^[ M]')
        if [ -z "$CHANGED_FILES" ]; then
            # echo "No changes to commit."
            sleep 1
            continue
        else
            echo "Changes detected"
            $COMMAND
            sleep 1
        fi
    done
fi

if [ "$OS" == "Linux" ]; then
    echo "Monitoring the current directory for changes on Linux..."
    while true; do
        inotifywait -r -e modify,create,delete,move . && \
        echo "Change detected. Running command: $COMMAND" && \
        $COMMAND
    done

elif [ "$OS" == "Darwin" ]; then
    echo "Monitoring the current directory for changes on macOS..."
    fswatch -o . | while read; do
        echo "Change detected. Running command: $COMMAND"
        $COMMAND
    done

else
    echo "Unsupported operating system: $OS"
    exit 1
fi