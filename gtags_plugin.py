import GTags.scripts.gtags_ui as gtags_ui
import GTags.scripts.gtags_shelf as gtags_shelf

def run():
    gtags_ui.run()  # Run the UI

def shelf():
    gtags_shelf.add_shelf_button_deferred()  # Create the shelf button
