import sys
import bpy
import os
from math import sqrt, ceil
import argparse
from mathutils import Vector
from itertools import chain

def import_image_and_fbx(image_path: str, fbx_path: str) -> None:
  bpy.ops.import_scene.fbx(filepath = fbx_path)
  
  # Grab all imported objects
  imported_model_objects = list(bpy.context.selected_objects)
  
  # Initialise minimum x, y, z, and maximum x, y, coordinates.
  min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
  max_x, max_y = float('-inf'), float('-inf')

  # Functional code to get world_corners, which contains 8 Vector objects
  # Each Vector objects represent a corner of the object's bounding box in world space.
  # You can then iterate through these to find the min/max X, Y, Z.
  world_corners = [
    obj.matrix_world @ Vector(corner)
    for obj in imported_model_objects
    if obj.type == 'MESH'
    for corner in obj.bound_box
  ]

  # Finds the bounding box of the imported model, allowing us to find the minimum z.
  for world_corner in world_corners:
    if world_corner.z < min_z:
      min_z = world_corner.z
    if world_corner.x < min_x:
      min_x = world_corner.x
    if world_corner.x > max_x:
      max_x = world_corner.x
    if world_corner.y < min_y:
      min_y = world_corner.y
    if world_corner.y > max_y:
      max_y = world_corner.y
    
  # Create the floor material by creating the material data block,
  # and adding the texture node to it
  material = bpy.data.materials.new(name = "FloorMaterial")
  material.use_nodes = True
  image = bpy.data.images.load(filepath = image_path)
  texture_node = material.node_tree.nodes.new(type = 'ShaderNodeTexImage')
  texture_node.image = image
  principled = material.node_tree.nodes.get('Principled BSDF')

  if principled:
    material.node_tree.links.new(
      texture_node.outputs['Color'],
      principled.inputs['Base Color']
    )

  # Create an EMPTY floor object to parent the object and assign the material to it
  floor_empty = bpy.data.objects.new("FloorEmpty", None)
  bpy.context.collection.objects.link(floor_empty)

  # Position the floor at min_z and at the center of the model bounding box.
  floor_empty.location.x = (min_x + max_x) / 2
  floor_empty.location.y = (min_y + max_y) / 2
  floor_empty.location.z = min_z

  # Calculate the bottom area of the imported model to figure out how to scale the plane.
  model_area = (max_x - min_x) * (max_y - min_y)
  plane_size = float(ceil(sqrt(model_area * 10 / 3)))

  # Create the actual floor object and mesh (the plane primitive does both)
  # and set its parent to the EMPTY floor object. Localise the plane to (0, 0, 0)
  bpy.ops.mesh.primitive_plane_add(size=plane_size, enter_editmode=False, align='WORLD')
  plane_object = bpy.context.object
  plane_object.parent = floor_empty
  plane_object.location = (0, 0, 0)
  plane_object.rotation_euler = (0, 0, 0)

  # Finally, assign the material to the plane mesh data
  plane_object.data.materials.append(material)

  # Select all objects and export them. It's good practice to deselect all objects first!
  bpy.ops.object.select_all(action='DESELECT')

  for obj in imported_model_objects:
    obj.select_set(True) # Set the object's selection status to True

  if floor_empty: # Check if the object exists
    floor_empty.select_set(True)
  if plane_object: # Check if the object exists
    plane_object.select_set(True)
  
  # Build an absolute output path in the current working directory
  export_dir  = os.getcwd()
  export_name = "exported_scene.fbx"
  export_path = os.path.join(export_dir, export_name)
  bpy.ops.export_scene.fbx(
    filepath=export_path,
    use_selection=True
  )

  print("Models successfully exported")

def parse_args():
  """Parse command-line args after the `--` separator."""
  argv = sys.argv
  if "--" not in argv:
    print("Error: expected '--' followed by --image and --fbx")
    sys.exit(1)
      
  idx = argv.index("--") + 1
  parser = argparse.ArgumentParser(description="Import image & FBX into Blender")
  parser.add_argument("--image", required=True, help="Path to the image file")
  parser.add_argument("--fbx", required=True, help="Path to the FBX model")
  return parser.parse_args(argv[idx:])

if __name__ == "__main__":
  args = parse_args()
  import_image_and_fbx(args.image, args.fbx)