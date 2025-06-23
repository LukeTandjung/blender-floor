This is a Blender script created to add a floor to any Blender model. It takes in the file paths to the floor image and the 3D model as an imput, and exports the Blender scene as an output.

This script uses the uv package manager to run. To get all the dependencies needed to run this script, use
- pip install uv
- uv sync

The command to run (assuming you have blender!) is
blender --background --python /path/to/main.py -- --image /path/to/your/image.png --fbx /path/to/your/model.fbx


