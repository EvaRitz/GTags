import maya.cmds as cmds
import maya.OpenMaya as om
from PySide2.QtWidgets import QMessageBox  # Import QMessageBox from PySide2

def create_g_tags(type_group, sdiv_group, add_edit, auto_group):
    """Creates the GuerillaTags for selected objects."""
    
    # Get the selected type, subdivision level, and additional tags
    type_tags = type_group.checkedButton().text()  # Get the selected type
    sdiv_tags = sdiv_group.checkedButton().text()  # Get the selected subdivision level
    add_tags = add_edit.text()  # Get any additional tags

    # Get the currently selected objects (using full path names)
    selected_objects = cmds.ls(selection=True, long=True)
    if not selected_objects:
        QMessageBox.warning(None, "Error", "No objects selected!")
        return

    # Initialize an empty list to store transforms to process
    transforms_to_select = []

    # Loop through the selected objects to find individual transforms (not groups)
    for obj in selected_objects:
        if cmds.objectType(obj, isType="transform"):
            # Find all descendants of this object
            descendants = cmds.listRelatives(obj, allDescendents=True, fullPath=True) or []
            
            # Filter descendants: include only transforms that are not groups
            non_group_transforms = [
                node for node in cmds.ls(descendants, type="transform")
                if not cmds.listRelatives(node, children=True, type="transform")
            ]

            # Include the current object if it's a valid transform (but not a group)
            if not cmds.listRelatives(obj, children=True, type="transform"):
                transforms_to_select.append(obj)
            
            # Add all valid non-group descendants
            transforms_to_select.extend(non_group_transforms)

    # Remove duplicates
    transforms_to_select = list(set(transforms_to_select))

    # Get the selected auto tag type (e.g., Full_hierarchy, Group_hierarchy, etc.)
    hierarchy_type = auto_group.checkedButton().text()

    # Flag to track overwrite confirmation
    overwrite_all = None

    # Process each transform and add GuerillaTags
    for transform in transforms_to_select:
        # Check if the 'GuerillaTags' attribute exists, and create it if not
        if not cmds.attributeQuery("GuerillaTags", node=transform, exists=True):
            cmds.addAttr(transform, longName="GuerillaTags", dataType="string")

        # Get the current tags for the transform
        current_tags = cmds.getAttr(f"{transform}.GuerillaTags") or ""

        # Handle overwrite confirmation only once
        if current_tags and overwrite_all is None:
            msgBox = QMessageBox()
            msgBox.setText("Guerilla tags found")
            msgBox.setInformativeText(
                "Some objects already have Guerilla tags. Do you want to overwrite them?"
            )
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.No)
            ret = msgBox.exec()

            overwrite_all = (ret == QMessageBox.Yes)

        # Skip updating if the user chose not to overwrite and tags already exist
        if current_tags and not overwrite_all:
            om.MGlobal.displayWarning(f"Skipping {transform}, existing tags not overwritten.")
            continue

        # Create the base tag string
        new_tags = f"{type_tags},{sdiv_tags}"

        # Handle the auto tag behavior based on hierarchy
        if hierarchy_type == "Full_hierarchy":
            # Include the object’s name and all of its parents up to the root
            hierarchy = []
            current_obj = transform
            while current_obj:
                hierarchy.append(current_obj.split('|')[-1])  # Add current object's name
                current_obj = cmds.listRelatives(current_obj, parent=True, fullPath=True)
                if current_obj:
                    current_obj = current_obj[0]  # listRelatives returns a list, get the first item
            new_tags += "," + ",".join(reversed(hierarchy))

        elif hierarchy_type == "Group_hierarchy":
            # Only include the object’s parents up to the root, exclude the object itself
            parents = []
            current_obj = cmds.listRelatives(transform, parent=True, fullPath=True)
            while current_obj:
                parents.append(current_obj[0].split('|')[-1])  # Add parent's name
                current_obj = cmds.listRelatives(current_obj[0], parent=True, fullPath=True)
            if parents:
                new_tags += "," + ",".join(reversed(parents))

        elif hierarchy_type == "Object_name":
            # Only include the object’s own name
            object_name = transform.split('|')[-1]
            new_tags += "," + object_name

        elif hierarchy_type == "None":
            # Do not append any hierarchy information
            pass

        # Add optional user input tags (if any)
        if add_tags:
            new_tags += f",{add_tags}"

        # Remove any trailing commas
        new_tags = new_tags.rstrip(',')

        # Set the GuerillaTags attribute on the transform
        cmds.setAttr(f"{transform}.GuerillaTags", new_tags, type="string")

    # Display success message
    om.MGlobal.displayInfo("Guerilla Tags successfully added to all transforms!")
