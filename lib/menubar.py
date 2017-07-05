from PyQt5.QtWidgets import QAction

class menubar():
    def __init__(self, view):
        menu = view.menuBar()

        fileMenu = menu.addMenu('&File')

        openButton = QAction('&Open', view)
        openButton.triggered.connect(view.open)
        fileMenu.addAction(openButton)

        saveButton = QAction('&Save', view)
        saveButton.triggered.connect(view.save)
        fileMenu.addAction(saveButton)

        exportButton = QAction('&Export CSV', view)
        exportButton.triggered.connect(view.export)
        fileMenu.addAction(exportButton)

        viewMenu = menu.addMenu('&View')

        view.hideButton = QAction('&Hide Generated', view)
        view.hideButton.setEnabled(False)
        view.hideButton.setCheckable(True)
        view.hideButton.triggered.connect(view.hideToggle)
        viewMenu.addAction(view.hideButton)

        view.highlightButton = QAction('&Highlight Duplicates', view)
        view.highlightButton.setEnabled(False)
        view.highlightButton.setCheckable(True)
        view.highlightButton.triggered.connect(view.highlightToggle)
        viewMenu.addAction(view.highlightButton)

        view.checkButton = QAction('&Double Check These...', view)
        view.checkButton.setEnabled(False)
        view.checkButton.setCheckable(True)
        view.checkButton.triggered.connect(view.checkToggle)
        viewMenu.addAction(view.checkButton)

        view.fix100Button = QAction('&Fix first 100', view)
        view.fix100Button.setEnabled(False)
        view.fix100Button.setCheckable(True)
        view.fix100Button.triggered.connect(view.fix100Toggle)
        viewMenu.addAction(view.fix100Button)
