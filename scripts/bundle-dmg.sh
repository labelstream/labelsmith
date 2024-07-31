#!/bin/bash

# Define variables
APP_NAME="Shyft.app"
DMG_NAME="Shyft-0.0.1a6.dmg" # Modify to suit current version
SOURCE_DIR="./Shyft.app"
DEST_DIR="./output"
BACKGROUND_IMG="./src/labelsmith/shyft/resources/dmg-background.png"

# Ensure SOURCE_DIR exists
if [ ! -d "$SOURCE_DIR" ]; then
  echo "Source directory does not exist: $SOURCE_DIR"
  exit 1
fi

# Ensure DEST_DIR exists, or create it
if [ ! -d "$DEST_DIR" ]; then
  mkdir -p "$DEST_DIR"
  if [ $? -ne 0 ]; then
    echo "Failed to create destination directory: $DEST_DIR"
    exit 1
  fi
fi

# Ensure BACKGROUND_IMG exists
if [ ! -f "$BACKGROUND_IMG" ]; then
  echo "Background image does not exist: $BACKGROUND_IMG"
  exit 1
fi

# Create the DMG
create-dmg \
  --volname "Shyft Installer" \
  --background "$BACKGROUND_IMG" \
  --window-size 600 400 \
  --icon-size 100 \
  --app-drop-link 400 150 \
  --icon "$APP_NAME" 200 150 \
  "$DEST_DIR/$DMG_NAME" \
  "$SOURCE_DIR"

# Check if the DMG creation was successful
if [ $? -eq 0 ]; then
  echo "DMG created successfully: $DEST_DIR/$DMG_NAME"
else
  echo "Failed to create DMG"
fi
