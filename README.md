# Android-Style Desktop Folder for Windows

A lightweight, borderless desktop widget built with **Python** and **PyQt6** that replicates the intuitive application grouping mechanism of mobile OS (Android/iOS) directly on the Windows desktop.

## ✨ Features

- **Android-Like Layout**: Combines multiple app shortcuts and documents into a clean, compact widget with a sleek grid layout.
- **Smart 4-Column Grid**: Icons automatically arrange themselves in a flexible grid configuration capped at 4 columns max.
- **Fluid Drag-and-Drop**: Easily drop any desktop icon, document, or executable onto the widget button to instantly include it in the folder.
- **Seamless Drag-Out Deletion**: Remove shortcuts from the folder by simply dragging them out back to the desktop without triggering redundant Windows file conflicts.
- **State Persistence**: Saves the current state of shortcuts into a local `folder_data.json` file so that your configuration is never lost upon reboot.
- **Frameless & Floating View**: Move the entire folder freely across your desktop screen in both closed and expanded states.

## 🛠️ Software Architecture (MVC-Inspired)

The application incorporates a decoupled **Model-View architecture** to strictly separate the user interface from storage operations:
- `FolderDataManager` (Data Layer): Handles serialization, updates, and JSON reading/writing entirely decoupled from GUI errors.
- `DraggableAppIcon` (Component View): Custom UI component replacing stock buttons to safely intercept multi-threaded OS drag actions.
- `AndroidFolder` (Main Application Wrapper): Coordinates coordinates, dynamically scales the container bounding boxes based on the current icon count, and prevents window clipping.

## 🚀 Getting Started

1. Install the required dependencies:
   ```bash
   pip install PyQt6
   ```

2. Run the main script:
   ```bash
   python sds.py
   ```
