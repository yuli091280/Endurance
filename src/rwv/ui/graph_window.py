from PyQt6 import QtWidgets
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QFileDialog
from rwv.loc_graph import LocGraph, JudgeCallType

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

        edit_menu = QtWidgets.QMenu("&Edit", self)
        menu_bar.addMenu(edit_menu)

        # Add actions to the file menu
        save_graph = file_menu.addAction("Save Graph")
        save_graph.triggered.connect(self.save_current_graph)
        save_graph.setShortcut('Ctrl+S')


        exit_action = file_menu.addAction("Close Graph")
        exit_action.triggered.connect(self.close_application)
        exit_action.setShortcut('Ctrl+Q')


        self.bent_knee = edit_menu.addAction("Bent Knee")
        self.bent_knee.setCheckable(True)
        self.bent_knee.setChecked(True)
        self.bent_knee.triggered.connect(
            lambda checked: self.redraw_points(JudgeCallType.BENT_KNEE, checked)
        )

        self.loc = edit_menu.addAction("LOC")
        self.loc.setCheckable(True)
        self.loc.setChecked(True)
        self.loc.triggered.connect(
            lambda checked: self.redraw_points(JudgeCallType.LOC, checked)
        )

        layout.setMenuBar(menu_bar)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        self.setLayout(layout)


    def redraw_points(self, point_type, visible):
        """
        Redraws specific point types based on visibility toggle.

        :param point_type: The type of points to draw (e.g., LOC, BENT_KNEE)
        :type point_type: loc_graph.JudgeCallType
        :param visible: Determines if the points should be visible
        :type visible: bool
        """
        if hasattr(self.canvas, 'graph'):
            self.canvas.graph.display_judge_call_by_type(point_type, visible)
            self.canvas.draw_idle()
    

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


    def closeEvent(self, event):
        """
        Overrides the closeEvent function to close the window and show the show graph button.
        """
        self.show_graph_button.show()
        self.close()
        event.accept()

    def show_window(self):
        """
        Shows the window.
        """
        self.show()

    def close_window(self):
        """
        Hides the window.
        """
        self.close()