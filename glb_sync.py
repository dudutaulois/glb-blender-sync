# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENCE BLOCK #####

bl_info = {
    "name": "GLB Importer and Sync",
    "author": "DuDutaulois",
    "version": (1, 0, 4),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > GLB Sync & Properties > Render > GLB Sync",
    "description": "Import and Sync GLB files with Blender",
    "warning": "",
    "doc_url": "https://github.com/dudutaulois/glb-blender-sync",
    "category": "Import-Export",
}

import bpy
import os
import json
from bpy.types import Panel, Operator, PropertyGroup, UIList
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, CollectionProperty, BoolProperty, PointerProperty, EnumProperty, IntProperty

def import_glb(filepath):
    # Store the current object count
    initial_object_count = len(bpy.data.objects)
    
    # Import the GLB file
    bpy.ops.import_scene.gltf(filepath=filepath)
    
    # Get the newly imported objects
    new_objects = [obj for obj in bpy.data.objects if obj not in bpy.context.scene.objects[:initial_object_count]]
    
    # Rename the root object (if any) based on the file name
    file_name = os.path.splitext(os.path.basename(filepath))[0]
    root_objects = [obj for obj in new_objects if obj.parent is None]
    
    renamed_objects = []
    if root_objects:
        for root_obj in root_objects:
            new_name = file_name
            counter = 1
            
            # Check if the name already exists
            while new_name in bpy.data.objects:
                new_name = f"{file_name}.{str(counter).zfill(3)}"
                counter += 1
            
            root_obj.name = new_name
            renamed_objects.append(root_obj)
            print(f"Renamed object to: {root_obj.name}")  # Debug print
    else:
        print(f"No root objects found for {file_name}")  # Debug print
    
    return renamed_objects

def scan_for_glb_files(folder_path):
    glb_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.glb'):
                glb_files.append(os.path.join(root, file))
    return glb_files

def load_import_data(context):
    import_data = json.loads(context.scene.glb_sync.import_data)
    for obj_name, glb_source in import_data.items():
        if obj_name in context.scene.objects:
            context.scene.objects[obj_name]["glb_source"] = glb_source

def check_for_updates(context):
    updates = []
    import_data = json.loads(context.scene.glb_sync.import_data)
    for obj_name, glb_source in import_data.items():
        if os.path.exists(glb_source):
            file_mod_time = os.path.getmtime(glb_source)
            if obj_name in context.scene.objects:
                obj = context.scene.objects[obj_name]
                if "last_updated" not in obj or obj["last_updated"] < file_mod_time:
                    updates.append((obj_name, glb_source))
    return updates

# Modify the update_synced_objects_list function
def update_synced_objects_list(context):
    glb_sync = context.scene.glb_sync
    glb_sync.synced_objects.clear()
    for obj in context.scene.objects:
        if "glb_source" in obj:
            item = glb_sync.synced_objects.add()
            item.name = obj.name
            item.glb_source = obj["glb_source"]
    print(f"Updated synced objects list. Total objects: {len(glb_sync.synced_objects)}")  # Debug print

# Modify the save_import_data function
def save_import_data(context):
    import_data = {}
    for obj in context.scene.objects:
        if "glb_source" in obj:
            import_data[obj.name] = obj["glb_source"]
    
    context.scene.glb_sync.import_data = json.dumps(import_data)


class GLB_SYNC_OT_import_project(Operator, ImportHelper):
    bl_idname = "glb_sync.import_project"
    bl_label = "Import GLB Project"
    bl_description = "Import GLB files from project"

    directory: StringProperty(subtype="DIR_PATH")
    files: CollectionProperty(type=bpy.types.OperatorFileListElement)
    
    import_all: BoolProperty(
        name="Import All Subfolders",
        description="Import GLB files from all subfolders",
        default=True
    )
    
    material_mode: EnumProperty(
        name="Material Handling",
        items=[
            ('KEEP', "Keep GLB Materials", "Use materials from the GLB file"),
            ('REPLACE', "Replace with Blender Materials", "Replace materials with Blender defaults"),
        ],
        default='KEEP'
    )

    def execute(self, context):
        directory = self.directory
        glb_files = scan_for_glb_files(directory) if self.import_all else [os.path.join(directory, f.name) for f in self.files]
        
        if not glb_files:
            self.report({'WARNING'}, "No GLB files found in the selected directory")
            return {'CANCELLED'}
        
        total_imported = 0
        total_files = len(glb_files)
        
        wm = context.window_manager
        wm.progress_begin(0, total_files)
        
        for i, glb_file in enumerate(glb_files):
            try:
                print(f"Importing file: {glb_file}")  # Debug print
                imported_objects = import_glb(glb_file)
                total_imported += len(imported_objects)
                
                # Store the source file information
                for obj in imported_objects:
                    obj["glb_source"] = glb_file
                    obj["last_updated"] = os.path.getmtime(glb_file)
                
                self.report({'INFO'}, f"Imported {len(imported_objects)} objects from {os.path.basename(glb_file)}")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to import {os.path.basename(glb_file)}: {str(e)}")
            
            wm.progress_update(i + 1)
        
        wm.progress_end()
        
        # Apply material handling
        if self.material_mode == 'REPLACE':
            for obj in context.selected_objects:
                if obj.type == 'MESH':
                    obj.data.materials.clear()
                    obj.data.materials.append(bpy.data.materials.new(name=f"{obj.name}_material"))
        
        save_import_data(context)
        update_synced_objects_list(context)
        
        self.report({'INFO'}, f"Imported {total_imported} objects from {total_files} GLB files")
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "import_all")
        layout.prop(self, "material_mode")

class GLB_SYNC_OT_sync_project(Operator):
    bl_idname = "glb_sync.sync_project"
    bl_label = "Sync GLB Project"
    bl_description = "Sync changes from GLB project"

    preserve_materials: BoolProperty(
        name="Preserve Blender Materials",
        description="Keep materials assigned in Blender during sync",
        default=True
    )

    def execute(self, context):
        updates = check_for_updates(context)
        if not updates:
            self.report({'INFO'}, "No updates found")
            return {'FINISHED'}
        
        for obj_name, glb_source in updates:
            try:
                old_obj = context.scene.objects[obj_name]
                old_materials = {slot.material.name: slot.material for slot in old_obj.material_slots} if self.preserve_materials else {}
                
                bpy.ops.object.select_all(action='DESELECT')
                old_obj.select_set(True)
                context.view_layer.objects.active = old_obj
                bpy.ops.object.delete()
                
                import_glb(glb_source)
                
                for new_obj in context.selected_objects:
                    new_obj["glb_source"] = glb_source
                    new_obj["last_updated"] = os.path.getmtime(glb_source)
                    
                    if self.preserve_materials and new_obj.type == 'MESH':
                        for i, slot in enumerate(new_obj.material_slots):
                            if i < len(old_materials):
                                slot.material = old_materials[list(old_materials.keys())[i]]
                
                self.report({'INFO'}, f"Updated {obj_name}")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to update {obj_name}: {str(e)}")
        
        save_import_data(context)
        update_synced_objects_list(context)  # Add this line
        
        self.report({'INFO'}, f"Synced {len(updates)} objects")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preserve_materials")

class GLB_SYNC_UL_synced_objects(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon='OBJECT_DATA')
            if hasattr(item, 'glb_source'):
                layout.label(text=item.glb_source)
            else:
                layout.label(text="Source not available")

class GLB_SYNC_OT_remove_sync(Operator):
    bl_idname = "glb_sync.remove_sync"
    bl_label = "Remove Sync"
    bl_description = "Remove the selected object from sync tracking"

    def execute(self, context):
        obj = context.scene.glb_sync.synced_objects[context.scene.glb_sync.synced_objects_index]
        if obj.name in context.scene.objects:
            del context.scene.objects[obj.name]["glb_source"]
            del context.scene.objects[obj.name]["last_updated"]
        context.scene.glb_sync.synced_objects.remove(context.scene.glb_sync.synced_objects_index)
        save_import_data(context)
        return {'FINISHED'}


class GLB_SYNC_synced_object(PropertyGroup):
    name: StringProperty()
    glb_source: StringProperty()

class GLB_SYNC_properties(PropertyGroup):
    import_data: StringProperty(
        name="Import Data",
        description="JSON string containing import data",
        default="{}"
    )
    synced_objects: CollectionProperty(type=GLB_SYNC_synced_object)
    synced_objects_index: IntProperty()


class GLB_SYNC_PT_sidebar_panel(Panel):
    bl_label = "GLB Sync"
    bl_idname = "GLB_SYNC_PT_sidebar_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "GLB Sync"

    def draw(self, context):
        layout = self.layout
        layout.operator("glb_sync.import_project", text="Import GLB Project")
        layout.operator("glb_sync.sync_project", text="Sync Project")
        
        layout.separator()
        layout.label(text="Synced Objects:")
        row = layout.row()
        row.template_list("GLB_SYNC_UL_synced_objects", "", context.scene.glb_sync, "synced_objects", context.scene.glb_sync, "synced_objects_index")
        col = row.column(align=True)
        col.operator("glb_sync.remove_sync", icon='X', text="")

class GLB_SYNC_PT_render_panel(Panel):
    bl_label = "GLB Sync"
    bl_idname = "GLB_SYNC_PT_render_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        layout.operator("glb_sync.import_project", text="Import GLB Project")
        layout.operator("glb_sync.sync_project", text="Sync Project")

classes = (
    GLB_SYNC_synced_object,
    GLB_SYNC_properties,
    GLB_SYNC_PT_sidebar_panel,
    GLB_SYNC_PT_render_panel,
    GLB_SYNC_OT_import_project,
    GLB_SYNC_OT_sync_project,
    GLB_SYNC_UL_synced_objects,
    GLB_SYNC_OT_remove_sync,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.glb_sync = PointerProperty(type=GLB_SYNC_properties)

def unregister():
    del bpy.types.Scene.glb_sync
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()