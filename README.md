# GLB to Blender Sync Add-on

This Blender add-on facilitates a seamless workflow between GLB and Blender for architectural visualization projects.

## Features

1. **GLB Importer**
   - Imports multiple GLB files
   - Maintains original object names and hierarchy
   - Supports a specific folder structure for models and textures

2. **Sync Functionality**
   - Updates existing objects in the Blender scene
   - Preserves Blender-specific modifications (materials, modifiers, etc.)

3. **Material Handling**
   - Option to keep GLB materials or replace with Blender defaults
   - Preserves Blender materials during sync (optional)

4. **Synced Objects Management**
   - Displays a list of synced objects in the Blender UI
   - Allows removal of objects from sync tracking

## Installation

1. Download the latest release from the [Releases](https://github.com/dudutaulois/glb-blender-sync/releases) page.
2. In Blender, go to Edit > Preferences > Add-ons.
3. Click "Install" and select the downloaded ZIP file.
4. Enable the add-on by checking the box next to "Import-Export: GLB to Blender Sync".

## Usage

1. Export your Sketchup models as GLB files.
2. In Blender, use the "Import GLB Project" option to import the GLB files.
3. Make necessary adjustments and apply high-quality materials in Blender.
4. Use the "Sync Project" button to update the Blender scene with any changes made in GLB.

## Folder Structure

```
project_folder/
├── glb/
│   ├── object1.glb
│   ├── object2.glb
│   └── ...
└── textures/
    ├── texture1.png
    ├── texture2.jpg
    └── ...
```

## Compatibility

- Designed for Blender 4.0 and above

## Development

To contribute to this project, please see our [Contribution Guidelines](CONTRIBUTING.md).

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Changelog

For a detailed list of changes and version history, please see the [CHANGELOG](CHANGELOG.md).

## Support

If you encounter any issues or have questions, please file an issue on the [GitHub issue tracker](https://github.com/yourusername/GLB-blender-sync/issues).

## Acknowledgements

- Thanks to the Blender Foundation for their excellent 3D creation suite.
- Thanks to the GLB team for their 3D modeling software.