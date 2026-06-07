import maya.cmds as cmds
import maya.utils
import os

def add_shelf_button():
    shelf = "Custom"
    
    # Get the path of the current script folder (GTagsV2 directory)
    script_dir = os.path.dirname(__file__)
    
    # Define the relative path to the icon
    icon_path = os.path.join(script_dir, "..", "icons", "gtags_icon.png")
    
    # Ensure the shelf "Custom" exists, create it if it doesn't
    if not cmds.shelfLayout(shelf, exists=True):
        shelf = cmds.shelfLayout(shelf, parent="ShelfLayout")
    
    # Add the shelf button to the "Custom" shelf
    cmds.shelfButton(
        label="GTags",
        command="import GTags.gtags_plugin; GTags.gtags_plugin.run()",
        image=icon_path,
        annotation="Launch GTags Tool",
        parent=shelf  # Explicitly set the parent to the "Custom" shelf
    )

# Use executeDeferred to ensure the button is added after Maya initializes
def add_shelf_button_deferred():
    maya.utils.executeDeferred(add_shelf_button)
