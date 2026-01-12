#!/bin/bash
set -e

# Debug: show volume mount info
echo "Debug: TEMP_FILE_DIR=$TEMP_FILE_DIR"
ls -la /data 2>/dev/null || echo "Debug: /data does not exist or not accessible"
id

# Create temp directories if TEMP_FILE_DIR is set and writable
if [ -n "$TEMP_FILE_DIR" ]; then
    mkdir -p "$TEMP_FILE_DIR/uploads" "$TEMP_FILE_DIR/processed" 2>/dev/null || {
        echo "Warning: Could not create directories in $TEMP_FILE_DIR, falling back to /tmp/slimpdf"
        export TEMP_FILE_DIR="/tmp/slimpdf"
        mkdir -p "$TEMP_FILE_DIR/uploads" "$TEMP_FILE_DIR/processed"
    }
fi

# Execute the main command
exec "$@"
