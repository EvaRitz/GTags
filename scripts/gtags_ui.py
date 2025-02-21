import maya.cmds as cmds
from PySide2.QtWidgets import (
    QWidget, QDialog, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QFrame, 
    QRadioButton, QButtonGroup, QSizePolicy
)
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt
import shiboken2  # To wrap Maya's Qt widgets into PySide2
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import os
import GTags.scripts.gtags_logic as logic  # Import the logic module

def maya_main_window():
    """Get Maya's main window as a QWidget."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(main_window_ptr), QDialog)

def get_abspath(relative_path):
    """Returns the absolute path of a file inside GTagsV2."""
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Get GTagsV2 directory
    return os.path.join(base_dir, relative_path).replace("\\", "/")

class GTagsTool(QDialog):
    def __init__(self, parent=maya_main_window()):
        super(GTagsTool, self).__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setModal(False)
        self.init_ui()

        self.load_stylesheet()

        self.setWindowIcon(QIcon(get_abspath("icons/gtags_icon.png")))  # Set the window icon

        self.show()

    def load_stylesheet(self):
        """Loads the external stylesheet."""
        stylesheet_path = get_abspath("icons/stylesheet.css")
        if os.path.exists(stylesheet_path):  # Ensure the file exists
            with open(stylesheet_path, "r") as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        else:
            print(f"Warning: Stylesheet not found at {stylesheet_path}")

    def init_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout()

        self.init_type_tags()
        self.main_layout.addWidget(self.separator())  # Separator line

        self.init_subdivision_tags()
        self.main_layout.addWidget(self.separator())  # Separator line

        self.init_automatic_tags()
        self.main_layout.addWidget(self.separator())  # Separator line

        self.init_add_tags()
        self.main_layout.addWidget(self.separator())  # Separator line

        # Add apply button
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.create_g_tags)
        self.main_layout.addWidget(self.apply_btn)

        # Set main layout
        self.setLayout(self.main_layout)
        self.setWindowTitle("GTags")
        self.resize(400, 700)

    def init_type_tags(self):
        """Initializes the type section."""
        self.type_layout = QVBoxLayout()
        self.type_btn_layout = QHBoxLayout()

        # Create button group for prefixes
        self.type_group = QButtonGroup()
        
        # Widgets
        self.type_buttons = {
            "sets": QRadioButton("sets"),
            "characters": QRadioButton("characters"),
            "props": QRadioButton("props"),
            "setdress": QRadioButton("setdress")
        }
        self.type_title = QLabel("Select type:")
        self.type_title.setProperty("class", "titleLabel")

        # Set the size policy of the title to expanding
        self.type_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Automatically select sets first
        self.type_buttons["sets"].setChecked(True)

        # Add buttons to button group
        for button in self.type_buttons.values():
            self.type_group.addButton(button)

        # Add to layouts
        for button in self.type_buttons.values():
            self.type_btn_layout.addWidget(button)

        self.type_layout.addWidget(self.type_title)
        self.type_layout.addLayout(self.type_btn_layout)

        # Add to main layout
        self.main_layout.addLayout(self.type_layout)

    def init_subdivision_tags(self):
        """Initializes the subdivision section."""
        self.sdiv_layout = QVBoxLayout()
        self.sdiv_btn_layout = QHBoxLayout()

        # Create button group for prefixes
        self.sdiv_group = QButtonGroup()
        
        # Widgets
        self.sdiv_buttons = {
            "s0": QRadioButton("s0"),
            "s1": QRadioButton("s1"),
            "s2": QRadioButton("s2"),
            "s3": QRadioButton("s3"),
            "s4": QRadioButton("s4")
        }
        self.sdiv_title = QLabel("Select subdivision levels:")
        self.sdiv_title.setProperty("class", "titleLabel")

        # Set the size policy of the title to expanding
        self.sdiv_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Automatically select sets first
        self.sdiv_buttons["s2"].setChecked(True)

        # Add buttons to button group
        for button in self.sdiv_buttons.values():
            self.sdiv_group.addButton(button)

        # Add to layouts
        for button in self.sdiv_buttons.values():
            self.sdiv_btn_layout.addWidget(button)

        self.sdiv_layout.addWidget(self.sdiv_title)
        self.sdiv_layout.addLayout(self.sdiv_btn_layout)

        # Add to main layout
        self.main_layout.addLayout(self.sdiv_layout)

    def init_automatic_tags(self):
        """Initializes the automatic tags section."""
        self.auto_layout = QVBoxLayout()
        self.auto_btn_layout_1 = QHBoxLayout()
        self.auto_btn_layout_2 = QHBoxLayout()

        # Create button group for prefixes
        self.auto_group = QButtonGroup()
        
        # Widgets
        self.auto_buttons = {
            "Full_hierarchy": QRadioButton("Full_hierarchy"),
            "Group_hierarchy": QRadioButton("Group_hierarchy"),
            "Object_name": QRadioButton("Object_name"),
            "None": QRadioButton("None"),
        }
        self.auto_title = QLabel("Select automated tags type:")
        self.auto_title.setProperty("class", "titleLabel")

        # Set the size policy of the title to expanding
        self.auto_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Automatically select sets first
        self.auto_buttons["Full_hierarchy"].setChecked(True)

        # Add buttons to button group
        for button in self.auto_buttons.values():
            self.auto_group.addButton(button)

               # Horizontal layouts
        for index, (key, button) in enumerate(self.auto_buttons.items()):
            if index < 2:
                self.auto_btn_layout_1.addWidget(button)
            else:
                self.auto_btn_layout_2.addWidget(button)

        self.auto_layout.addWidget(self.auto_title)
        self.auto_layout.addLayout(self.auto_btn_layout_1)
        self.auto_layout.addLayout(self.auto_btn_layout_2)

        # Add to main layout
        self.main_layout.addLayout(self.auto_layout)

    def init_add_tags(self):
        """Initializes the add tags section."""
        self.add_layout = QVBoxLayout()
        self.add_h_layout = QHBoxLayout()

        self.add_title = QLabel("Add additional tags")
        self.add_title.setProperty("class", "titleLabel")
        self.add_label = QLabel("More tags: ")
        self.add_edit = QLineEdit()
        self.add_edit.setPlaceholderText("example1,example2,example3,ect...")

        # Set the size policy of the title to expanding
        self.add_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.add_h_layout.addWidget(self.add_label)
        self.add_h_layout.addWidget(self.add_edit)

        self.add_layout.addWidget(self.add_title)
        self.add_layout.addLayout(self.add_h_layout)

        # Add to main layout
        self.main_layout.addLayout(self.add_layout)

    # In your GTagsTool class
    def create_g_tags(self):
        """Calls the function from gtags_logic and passes the UI elements to it."""
        logic.create_g_tags(self.type_group, self.sdiv_group, self.add_edit, self.auto_group)

    
    def separator(self):
        """Creates a horizontal line separator."""        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

def run():
    """Launch the UI."""
    global gtags_window
    try:
        gtags_window.close()
        gtags_window.deleteLater()
    except:
        pass
    gtags_window = GTagsTool()
