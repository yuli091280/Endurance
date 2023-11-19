import matplotlib

from PyQt6.QtWidgets import QVBoxLayout, QWidget

import seaborn as sns

import matplotlib.backends.backend_qt5agg as mlp_backend
from matplotlib.figure import Figure

from rwv.util import judge_data

matplotlib.use("QtAgg")


class MpWidget(QWidget):
    def __init__(self, canvas=None):
        super().__init__()
        toolbar = mlp_backend.NavigationToolbar2QT(canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)

        # Create a placeholder widget to hold our toolbar and canvas.
        self.setLayout(layout)


class MplCanvas(mlp_backend.FigureCanvasQTAgg):
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.subplots()

        # Initialize dictionary to keep track of our plots, necessary for redrawing
        self.data_plots = {}

        # Initialize booleans to keep track of bent knee/loc display state
        self.display_bent_knee = True
        self.display_loc = True

        super(MplCanvas, self).__init__(self.fig)

    def redraw_plot(self, caller):
        # Get bib number of selected runner from caller, since the regular arg only returns the full label
        selected_runner = caller.currentData()

        for bib_key in self.data_plots.keys():
            visibility = (
                True if selected_runner == "all" else (selected_runner == bib_key)
            )

            # Set main line to visible if selected or all
            self.data_plots[bib_key][0].set_visible(visibility)

            # Set LOC points to visible if selected or all, and we have the box checked
            self.data_plots[bib_key][1].set_visible(self.display_loc and visibility)

            # Set bent knee points to visible if selected or all, and we have the box checked
            self.data_plots[bib_key][2].set_visible(
                self.display_bent_knee and visibility
            )

        self.draw()

    def redraw_points(self, caller, *args):
        # No data variable, so we have to match to the label
        if caller.text() == "Bent Knee":
            self.display_bent_knee = args[0] != 0
        else:
            self.display_loc = args[0] != 0

        for plots in self.data_plots.values():
            # If the line for this athlete is visible, update the LOC and bent knee display values accordingly
            if plots[0].get_visible():
                plots[1].set_visible(self.display_loc)
                plots[2].set_visible(self.display_bent_knee)

        self.draw()

    def plot(self, df, athletes):
        ax = self.fig.subplots()

        # Set plot title and axis labels
        ax.set_title("Racer Leg Height over Time w/ Max LOC = 3")
        ax.set_ylabel("Racer Leg Height")
        ax.set_xlabel("Time")

        # Draw max LOC cutoff line
        sns.lineplot(data=df, x="time", y="max_loc", ax=ax)

        labels = ["Max LOC"]

        for index, (last_name, first_name, bib_number) in enumerate(athletes):
            self.data_plots[bib_number] = [
                # Draw line plot of LOC
                sns.lineplot(data=df, x="time", y=f"runner_{index + 1}", ax=ax).lines[
                    -1
                ],
                # Draw red LOC infractions
                sns.scatterplot(
                    data=df[
                        df["time"].isin(
                            judge_data.query(
                                "judge_1 == '~' | judge_2 == '~' | judge_3 == '~'"
                            ).query(f"runner == {index + 1}")["time"]
                        )
                    ][["time", f"runner_{index + 1}"]],
                    x="time",
                    y=f"runner_{index + 1}",
                    ax=ax,
                    color="r",
                    marker="*",
                    s=70,
                ).collections[-1],
                # Draw red bent knee infractions
                sns.scatterplot(
                    data=df[
                        df["time"].isin(
                            judge_data.query(
                                "judge_1 == '>' | judge_2 == '>' | judge_3 == '>'"
                            ).query(f"runner == {index + 1}")["time"]
                        )
                    ][["time", f"runner_{index + 1}"]],
                    x="time",
                    y=f"runner_{index + 1}",
                    ax=ax,
                    color="r",
                    marker=">",
                    s=50,
                ).collections[-1],
            ]

            # Add labels for legend
            labels.append(f"{last_name}, {first_name} ({bib_number})")

        ax.legend(handles=ax.lines, labels=labels)

        self.draw()
