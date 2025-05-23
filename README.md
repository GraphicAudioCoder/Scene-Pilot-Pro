# ScenePilotPro

## Overview
ScenePilotPro is a PyQt6-based application designed for creating, editing, and managing 3D spaces. The app provides an intuitive interface for designing environments, saving configurations, and visualizing them in a three-dimensional space. In the future, ScenePilotPro will also be used to create and control audiovisual tests.

## Features
- **Space Creation**: Design 3D spaces with customizable dimensions and colors.
- **Gallery Management**: Save and load spaces from a gallery.
- **Tool Palette**: Access tools for modifying space properties.
- **3D Visualization**: View spaces in a 3D environment with OpenGL.
- **Localization**: Support for multiple languages.

## Project Structure
```
ScenePilotPro/
├── main.py                # Entry point of the application
├── src/
│   ├── assets/            # Fonts and other assets
│   ├── components/        # Core components like MainWindow and SplashScreen
│   ├── config/            # Configuration files
│   ├── localization/      # Language files
│   ├── spaces/            # Saved spaces and their data
│   ├── styles/            # QSS stylesheets
│   └── widgets/           # UI widgets and frames
```

## How to Run
1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main.py
   ```

## Key Classes
- **MainWindow**: The main application window.
- **SpaceGalleryWidget**: Manages the gallery and space creation.
- **ToolPaletteFrame**: Provides tools for modifying space properties.
- **SpaceGalleryFrame**: Displays saved spaces in a scrollable gallery.

## Localization
Language files are located in the `src/localization/` directory. Add new languages by creating a JSON file with translations.

## Contributing
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request.

## License
This project is licensed under the MIT License.
