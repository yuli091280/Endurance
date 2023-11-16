import matplotlib

from PyQt6.QtWidgets import QVBoxLayout, QWidget

import pandas as pd
import seaborn as sns

import matplotlib.pyplot as plt
import matplotlib.backends.backend_qt5agg as mlp_backend
from matplotlib.figure import Figure

from rwv.util import get_data, judge_data

matplotlib.use("QtAgg")

class MpWidget(QWidget):
    def __init__(self, canvas = None):
        super().__init__()
        toolbar = mlp_backend.NavigationToolbar2QT(canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)

        # Create a placeholder widget to hold our toolbar and canvas.
        self.setLayout(layout)


class MplCanvas(mlp_backend.FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100, plot=None):
        if plot is None:
            self.fig = Figure(figsize=(width, height), dpi=dpi)
        else:
            self.fig = plot["fig"]
            self.axes = plot["axs"]
        super(MplCanvas, self).__init__(self.fig)

    def redraw_plot(self, *args):
        selected_runner = args[0]

        if selected_runner.lower() == 'all':
            self.runner_1.set_visible(True)
            self.runner_2.set_visible(True)
            self.runner_3.set_visible(True)
        else:
            self.runner_1.set_visible(False)
            self.runner_2.set_visible(False)
            self.runner_3.set_visible(False)
            getattr(self, selected_runner).set_visible(True)

        self.draw()

    def redraw_points(self, owner, *args):
        try:
            plot = self.loc

            if owner.text() == "Bent Knee":
                plot = self.bent_knee
            
            plot.set_visible(args[0] != 0)

            self.draw()
        except:
            pass

    def plot(self, df):
        self.fig.clear()

        ax = self.fig.subplots()

        ax.set_title("Racer Leg Height over Time w/ Max LOC = 3")
        ax.set_ylabel("Racer Leg Height")
        ax.set_xlabel("Time")

        self.max_loc = sns.lineplot(data=df, x='time', y='max_loc', ax=ax).lines[-1]
        self.runner_1 = sns.lineplot(data=df, x='time', y='runner_1', ax=ax).lines[-1]
        self.runner_2 = sns.lineplot(data=df, x='time', y='runner_2', ax=ax).lines[-1]
        self.runner_3 = sns.lineplot(data=df, x='time', y='runner_3', ax=ax).lines[-1]

        ax.legend(handles=ax.lines[1:], labels=["Runner 1", "Runner 2", "Runner 3"])

        self.loc = sns.scatterplot(data=df[df["time"].isin(judge_data.query("judge_1 == '~' | judge_2 == '~' | judge_3 == '~'")["time"])][["time", "runner_1"]], x="time", y="runner_1", ax=ax, color="r", marker="*", s=70).collections[-1]
        
        self.bent_knee = sns.scatterplot(data=df[df["time"].isin(judge_data.query("judge_1 == '>' | judge_2 == '>' | judge_3 == '>'")["time"])][["time", "runner_1"]], x="time", y="runner_1", ax=ax, color="r", marker=">", s=50).collections[-1]

        self.draw()