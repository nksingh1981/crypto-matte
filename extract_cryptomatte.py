import sys

# PySide2/PySide6 Compatibility
try:
    from PySide6.QtWidgets import (
        QApplication, QWidget, QPushButton, QTextBrowser, QLabel,
        QVBoxLayout, QHBoxLayout, QComboBox
    )
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QListView
    from PySide6.QtCore import QStringListModel, QItemSelectionModel

except ImportError:
    from PySide2.QtWidgets import (
        QApplication, QWidget, QPushButton, QTextBrowser, QLabel,
        QVBoxLayout, QHBoxLayout, QComboBox
    )
    from PySide2.QtCore import Qt
    from PySide2.QtWidgets import QListView
    from PySide2.QtCore import QStringListModel, QItemSelectionModel

import nuke


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Extract Cryptomattes")
        self.previous_node = None
        self.current_node = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        content_layout = QHBoxLayout()

        # Left side with buttons
        left_layout = QVBoxLayout()
        self.gather_button1 = QPushButton("Extract Crypto")
        self.gather_button1.setFixedWidth(130)
        self.gather_button1.clicked.connect(self.check_crypto_layer)
        self.gather_button1.setToolTip("Select the Read node with Cryptomatte and click the button")

        self.create_button2 = QPushButton("Create_Cryptomatte")
        self.create_button2.setFixedWidth(130)
        self.create_button2.setToolTip("To create the cryptomatte node select the matte/s from the listView.")
        self.create_button2.clicked.connect(self.create_cryptomatte)

        left_layout.addWidget(self.gather_button1)
        left_layout.addSpacing(20)
        left_layout.addWidget(self.create_button2)
        left_layout.addStretch()

        # Right side with combo box and list View
        right_layout = QVBoxLayout()
        self.layer_label = QLabel("Cryptomattes Layer:")
        self.crypto_layer_combo = QComboBox()
        self.crypto_layer_combo.setToolTip("Select a layer to view its available mattes.")
        self.crypto_layer_combo.currentTextChanged.connect(self.crypto_layers)  ####

        self.cryptomatte_list_view = QListView()
        self.cryptomatte_list_view.setToolTip("Select one or more mattes to create Cryptomatte nodes.")
        self.crypto_list_model = QStringListModel()
        self.cryptomatte_list_view.setModel(self.crypto_list_model)
        self.cryptomatte_list_view.setSelectionMode(QListView.ExtendedSelection)

        right_layout.addWidget(self.layer_label)
        right_layout.addWidget(self.crypto_layer_combo)
        right_layout.addWidget(self.cryptomatte_list_view)

        content_layout.addLayout(left_layout)
        content_layout.addLayout(right_layout)

        # Bottom close button
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        bottom_layout.addWidget(self.close_button)

        # Add all to main layout
        main_layout.addLayout(content_layout)
        main_layout.addLayout(bottom_layout)

    def check_crypto_layer(self):
        nodes = nuke.selectedNodes()
        if len(nodes) != 1:
            self.crypto_layer_combo.clear()
            self.crypto_list_model.setStringList(["Select exactly one Read Node."])
            return

        node = nodes[0]
        if node.Class() != "Read":
            self.crypto_layer_combo.clear()
            self.crypto_list_model.setStringList(["Selected node is not a Read Node."])
            return

        # new read node is selected
        if node != self.previous_node:
            self.crypto_layer_combo.clear()
            self.crypto_list_model.setStringList([])

            self.previous_node = node
            self.current_node = node

        self.metadata = node.metadata()
        keys = self.metadata.keys()

        if not self.metadata:
            nuke.message("No metadata present for selected node")
            return
        if not keys:
            nuke.message("No keys available to extract")
            return

        self.manifest_list = []
        self.layer_names_list = []

        for key in keys:
            if "cryptomatte" in key and "manifest" in key:
                self.manifest_list.append(key)
            if "cryptomatte" in key and "name" in key:
                self.layer_names_list.append(self.metadata[key])
        self.crypto_layer_combo.addItems(self.layer_names_list)
        if self.layer_names_list:
            self.crypto_layer_combo.setCurrentIndex(0)
            ## to do populate listView
            self.crypto_layers(self.layer_names_list[0])

    # Add the cryptomattes in the list view
    def crypto_layers(self, layer_name):

        if not self.current_node:
            return
        manifest_dict = eval(self.metadata[self.manifest_list[self.crypto_layer_combo.currentIndex()]])

        if not self.layer_names_list:
            nuke.message("No Crypto layer available")
            return

        if not manifest_dict:
            nuke.message("No Crypto metadata available")
            return

        ids_list = []
        for item in manifest_dict:
            ids_list.append(item)
        self.crypto_list_model.setStringList(ids_list)


    def create_cryptomatte(self):
        if not self.current_node:
            return

        selected_indexes = self.cryptomatte_list_view.selectedIndexes()
        if not selected_indexes:
            nuke.message("No Matte/s selected")
            return

        selected_matte = [index.data() for index in selected_indexes]

        if not selected_matte:
            nuke.message("No mattes available")
            return

        for _matte in selected_matte:
            if _matte != "default":
                crypto_node = nuke.nodes.Cryptomatte()
                crypto_node.setInput(0, self.current_node)
                crypto_node.setXpos(self.current_node.xpos() + ((selected_matte.index(_matte) + 1) * 150))
                crypto_node.setYpos(self.current_node.ypos() + 100)
                crypto_node["matteList"].setValue(_matte)
                crypto_node["cryptoLayerChoice"].setValue(self.crypto_layer_combo.currentIndex())
                crypto_node["label"].setValue(_matte)


def crypto_tool():
        
    try:
        app = QApplication.instance() or QApplication(sys.argv)
    except RuntimeError:
        return
        
    global crypto_tool_window
    crypto_tool_window = MyWindow()
    crypto_tool_window.resize(600, 400)
    crypto_tool_window.show()
