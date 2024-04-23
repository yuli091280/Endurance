from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFileDialog

class GraphWindow(QtWidgets.QWidget):
    """A window that displays a generated chart.

    :param toolbar: The toolbar for interacting with the plot
    :type toolbar: NavigationToolbar2QT
    :param canvas: The canvas where the graph is drawn
    :type canvas: MplCanvas
    """

    def __init__(self, toolbar, canvas, show_graph_button):
        super().__init__()
        self.setWindowTitle("Endurance")
        self.show_graph_button = show_graph_button
        self.toolbar = toolbar
        self.canvas = canvas

        layout = QtWidgets.QVBoxLayout(self)

        # Setup the menu bar
        menu_bar = QtWidgets.QMenuBar()
        file_menu = QtWidgets.QMenu("&File", self)
        menu_bar.addMenu(file_menu)

        # Add actions to the file menu
        save_graph = file_menu.addAction("Save Graph")
        save_graph.triggered.connect(self.save_current_graph)
        save_graph.setShortcut('Ctrl+S')


        exit_action = file_menu.addAction("Close Graph")
        exit_action.triggered.connect(self.close_application)
        exit_action.setShortcut('Ctrl+Q')

        layout.setMenuBar(menu_bar)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        self.setLayout(layout)

    def save_current_graph(self, checked=False):
        """
        Opens window for the user to save the current graph as PDF or JPEG.
        """
        file_path, save_choice = QFileDialog.getSaveFileName(
            self, "Save Graph", "", "PDF Files (*.pdf);;JPEG Files (*.jpeg;*.jpg)"
        )
        if file_path:
            if "PDF" in save_choice and not file_path.endswith(".pdf"):
                file_path += ".pdf"
            elif ("JPEG" in save_choice or "jpg" in save_choice) and not file_path.endswith((".jpeg", ".jpg")):
                file_path += ".jpeg"

            if "PDF" in save_choice:
                self.save_figure_as_pdf(file_path)
            elif "JPEG" in save_choice:
                self.save_figure_as_jpeg(file_path)


    def save_figure_as_pdf(self, file_path):
        """
        Saves the graph as a pdf at a file path.

        :param file_path: The file path to save the pdf to
        :type file_path: str
        """
        self.canvas.figure.savefig(file_path)

    def save_figure_as_jpeg(self, file_path):
        """
        Saves the graph as a jpeg at a file path.

        :param file_path: The file path to save the jpeg to
        :type file_path: str
        """
        self.canvas.figure.savefig(file_path, format='jpeg')

    def close_application(self, checked=False):
        """
        Closes the entire graph window.
        """
        self.close()


    def close_window(self):
        ""
        self.show_graph_button.show()
        self.close()

    def show_window(self):
        ""
        self.show()
