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
        # sns.lineplot(data=df, x="Year", y="Population", ax=canvas.figure.subplots()).set(title="World Population (mil) Per Year", ylabel="People (mil)")
        df = get_data()
        data = df

        selected_runner = args[0]

        if selected_runner != 'all':
            data = df[["time", "max_loc", selected_runner]]

        self.plot(data)

    def plot(self, df):
        self.fig.clear()

        sns.lineplot(data=pd.melt(df, ['time']), x='time', y='value', hue='variable', ax=self.fig.subplots())

        try:
            for _, row in judge_data.iterrows():
                for item in row[1:]:
                    if item == '~':
                        self.fig.axes[0].scatter(x=row.iloc[0], y=df.loc[df['time'] == row.iloc[0]]['runner_1'], color='r', marker='*')
                    elif item == '>':
                        self.fig.axes[0].scatter(x=row.iloc[0], y=df.loc[df['time'] == row.iloc[0]]['runner_1'], color='r', marker='>')
        except Exception:
            pass

        self.draw()