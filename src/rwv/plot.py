import matplotlib

from PyQt6.QtWidgets import QVBoxLayout, QWidget

import seaborn as sns

import matplotlib.backends.backend_qt5agg as mlp_backend
from matplotlib.figure import Figure

from rwv.util import judge_data

matplotlib.use("QtAgg")


def redraw_annotations(line_group, pos, text):
    line_group["annotations"].xy = pos
    line_group["annotations"].set_text(text)
    line_group["annotations"].get_bbox_patch().set_facecolor(
        line_group["main_plot"].get_c()
    )
    line_group["annotations"].get_bbox_patch().set_alpha(0.4)


class MplCanvas(mlp_backend.FigureCanvasQTAgg):
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.subplots()

        # Initialize dictionary to keep track of our plots, necessary for redrawing
        self.data_plots = {}

        # Initialize dictionary to keep track of the max LOC
        self.max_loc = {}

        # Initialize booleans to keep track of bent knee/loc display state
        self.display_bent_knee = True
        self.display_loc = True

        # Connect hover annotations
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover_annotations)

        super(MplCanvas, self).__init__(self.fig)

    def redraw_plot(self, caller):
        # Get bib number of selected runner from caller, since the regular arg only returns the full label
        selected_runner = caller.currentData()

        # Set up a list of visible lines to draw the legend from
        visible_lines = [self.max_loc]

        for bib_key in self.data_plots.keys():
            visibility = (
                True if selected_runner == "all" else (selected_runner == bib_key)
            )

            # If visible, add to list of visible lines
            if visibility:
                visible_lines.append(self.data_plots[bib_key])

            # Set main line to visible if selected or all
            self.data_plots[bib_key]["main_plot"].set_visible(visibility)

            # Set LOC points to visible if selected or all, and we have the box checked
            self.data_plots[bib_key]["token_plots"][0].set_visible(
                self.display_loc and visibility
            )

            # Set bent knee points to visible if selected or all, and we have the box checked
            self.data_plots[bib_key]["token_plots"][1].set_visible(
                self.display_bent_knee and visibility
            )

        # Redraw the legend based on visible lines
        self.ax.legend(
            handles=[line["main_plot"] for line in visible_lines],
            labels=[line["label"] for line in visible_lines],
        )

        self.draw()

    def hover_annotations(self, event):
        if event.inaxes == self.ax:
            # If we're inbounds, look at every token plot to see if we're on one of their points
            for line_group in self.data_plots.values():
                # If the main line isn't visible, neither will the token plots
                if not line_group["main_plot"].get_visible():
                    pass

                pos = None
                judge_calls = []
                for index, scatter in enumerate(line_group["token_plots"]):
                    # Check each token plot to see if we're on their point
                    cont, ind = scatter.contains(event)
                    if cont:
                        # Set the position of the annotation
                        # x, y = scatter.get_data()  # Strat for getting line data
                        # pos = (x[ind["ind"][0]], y[ind["ind"][0]])
                        pos = scatter.get_offsets()[ind["ind"][0]]
                        # Add the judgement call to the annotation text
                        # TODO: Tie in judge "data" value
                        judge_calls.append(f"Chart {index}: {pos}")

                # If one of the points matches, draw the annotation
                if judge_calls:
                    redraw_annotations(line_group, pos, "\n".join(judge_calls).strip())
                    line_group["annotations"].set_visible(True)
                    self.fig.canvas.draw_idle()
                # Otherwise, if we're still visible, remove the annotation
                else:
                    if line_group["annotations"].get_visible():
                        line_group["annotations"].set_visible(False)
                        self.fig.canvas.draw_idle()

    def redraw_points(self, caller, *args):
        # No data variable, so we have to match to the label
        if caller.text() == "Bent Knee":
            self.display_bent_knee = args[0] != 0
        else:
            self.display_loc = args[0] != 0

        for plots in self.data_plots.values():
            # If the line for this athlete is visible, update the LOC and bent knee display values accordingly
            if plots["main_plot"].get_visible():
                plots["token_plots"][0].set_visible(self.display_loc)
                plots["token_plots"][1].set_visible(self.display_bent_knee)

        self.draw()

    def plot(self, df, athletes):
        # Set plot title and axis labels
        self.ax.set_title("Racer Leg Height over Time w/ Max LOC = 3")
        self.ax.set_ylabel("Racer Leg Height")
        self.ax.set_xlabel("Time")

        # Draw max LOC cutoff line
        self.max_loc = {
            "label": "Max LOC",
            "main_plot": sns.lineplot(data=df, x="time", y="max_loc", ax=self.ax).lines[
                -1
            ],
        }

        labels = ["Max LOC"]

        # TODO: Find better method of preventing clashes on annotation position
        place = 20
        for index, (last_name, first_name, bib_number) in enumerate(athletes):
            label = f"{last_name}, {first_name} ({bib_number})"
            self.data_plots[bib_number] = {
                "label": label,
                # Draw line plot of LOC
                "main_plot": sns.lineplot(
                    data=df, x="time", y=f"runner_{index + 1}", ax=self.ax
                ).lines[-1],
                "annotations": self.ax.annotate(
                    "",
                    xy=(0, 0),
                    xytext=(20, place),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"),
                    visible=False,
                ),
                "token_plots": [
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
                        ax=self.ax,
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
                        ax=self.ax,
                        color="r",
                        marker=">",
                        s=50,
                    ).collections[-1],
                ],
            }
            place += 20

            # Add labels for legend
            labels.append(label)

        # Create a legend for the plot
        self.ax.legend(handles=self.ax.lines, labels=labels)

        self.draw()
