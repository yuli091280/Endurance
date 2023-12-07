import numpy as np
import seaborn as sns

from matplotlib.figure import Figure
from matplotlib.text import OffsetFrom

import matplotlib.dates as mpl_dates


class PlotGroup:
    def __init__(self, main_plot, annotation=None, token_plots=None):
        if token_plots is None:
            token_plots = []

        self.main_plot = main_plot
        self.annotation = annotation
        self.token_plots = token_plots


# LocGraph showing loc for each selected runner with judge calls placed on top if requested
class LocGraph:
    def __init__(self, width=5, height=4, dpi=100, max_loc=60):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.subplots()

        # Set plot title and axis labels
        self.ax.set_title(f"Racer Leg Height over Time w/ Max LOC = {max_loc}")
        self.ax.set_ylabel("Racer Leg Height")
        self.ax.set_xlabel("Time")
        self.ax.xaxis.set_major_formatter(mpl_dates.DateFormatter("%H:%M:%S %p"))

        # Initialize dictionary to keep track of our plots, necessary for redrawing
        self.data_plots = {}

        # Initialize value to keep track of the max LOC
        self.max_loc_value = max_loc
        self.max_loc = None

        # Initialize booleans to keep track of bent knee/loc display state
        self.display_bent_knee = True
        self.display_loc = True

    def get_figure(self):
        return self.fig

    def redraw_max_loc(self, loc):
        self.max_loc_value = loc
        self.ax.set_title(f"Racer LOC over Time w/ Max LOC = {self.max_loc_value} ms")
        self.max_loc.main_plot.set_ydata([loc, loc])

    def display_runners(self, selected_runners):
        # Set up a list of visible lines to draw the legend from
        visible_lines = [self.max_loc]

        for bib_key in self.data_plots.keys():
            visible = bib_key in selected_runners

            if visible:
                visible_lines.append(self.data_plots[bib_key])

            # Set main line to visible if selected or all
            self.data_plots[bib_key].main_plot.set_visible(visible)

            # Set LOC points to visible if selected or all, and we have the box checked
            self.data_plots[bib_key].token_plots[0].set_visible(
                self.display_loc and visible
            )

            # Set bent knee points to visible if selected or all, and we have the box checked
            self.data_plots[bib_key].token_plots[1].set_visible(
                self.display_bent_knee and visible
            )

        # Redraw the legend based on visible lines
        self.ax.legend(handles=[line.main_plot for line in visible_lines])

    def display_points(self, point_type, visible):
        # No data variable, so we have to match to the label
        if point_type == "Bent Knee":
            self.display_bent_knee = visible
        else:
            self.display_loc = visible

        for plot_group in self.data_plots.values():
            # If the line for this athlete is visible, update the LOC and bent knee display values accordingly
            if plot_group.main_plot.get_visible():
                plot_group.token_plots[0].set_visible(self.display_loc)
                plot_group.token_plots[1].set_visible(self.display_bent_knee)

    def plot(self, loc_values, judge_data, athletes):
        # Draw max LOC cutoff line
        self.max_loc = PlotGroup(
            self.ax.axhline(y=self.max_loc_value, color="r", label="Max LOC")
        )

        for index, (last_name, first_name, bib_number) in enumerate(athletes):
            if bib_number not in list(loc_values.columns):
                continue

            main_plot = sns.lineplot(
                data=loc_values,
                x="Time",
                y=bib_number,
                label=f"{last_name}, {first_name} ({bib_number})",
                ax=self.ax,
            ).lines[-1]

            judge_calls = judge_data.query(f"BibNumber == {bib_number}").copy()
            judge_calls["y"] = np.interp(
                x=judge_calls["Time"],
                xp=main_plot.get_xdata(orig=True),
                fp=main_plot.get_ydata(orig=True),
            )

            self.data_plots[bib_number] = PlotGroup(
                main_plot=main_plot,
                annotation=self.ax.annotate(
                    "",
                    xy=(0, 0),
                    xytext=(20, 20),
                    textcoords="offset points",
                    ha="left",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(
                        arrowstyle="->",
                        connectionstyle="angle,angleA=0,angleB=90,rad=10",
                    ),
                    visible=False,
                ),
                token_plots=[
                    # Draw red LOC infractions
                    sns.scatterplot(
                        data=judge_calls.query("Color == 'Red' & Infraction == '~'"),
                        x="Time",
                        y="y",
                        label="LOC Red Card",
                        ax=self.ax,
                        color="r",
                        marker="*",
                        s=100,
                    ).collections[-1],
                    # Draw red bent knee infractions
                    sns.scatterplot(
                        data=judge_calls.query("Color == 'Red' & Infraction == '<'"),
                        x="Time",
                        y="y",
                        label="Bent Knee Red Card",
                        ax=self.ax,
                        color="r",
                        marker=">",
                        s=100,
                    ).collections[-1],
                ],
            )

        # Create a legend for the plot
        self.ax.legend(handles=[self.max_loc.main_plot])

    @staticmethod
    def redraw_annotations(plot_group, pos, text, previous_annotation=None):
        plot_group.annotation.xy = pos
        plot_group.annotation.set_text(text)
        # Set annotation color to match that of the line
        plot_group.annotation.get_bbox_patch().set_facecolor(
            plot_group.main_plot.get_c()
        )

        if previous_annotation:
            plot_group.annotation.set_verticalalignment("top")
            plot_group.annotation.xyann = (3, -5)
            plot_group.annotation.set_anncoords(
                OffsetFrom(previous_annotation.get_bbox_patch(), (0, 0))
            )
        else:
            plot_group.annotation.set_verticalalignment("bottom")
            plot_group.annotation.xyann = (20, 20)
            plot_group.annotation.set_anncoords("offset points")

    def hover_annotations(self, event):
        if event.inaxes == self.ax:
            # List of active annotations, will be used to position subsequent annotations off the first visible one
            active_annotations = []
            # If we're inbounds, look at every token plot to see if we're on one of their points
            for index, plot_group in enumerate(self.data_plots.values()):
                # If the main line isn't visible, neither will the token plots
                if not plot_group.main_plot.get_visible():
                    continue

                pos = None
                judge_calls = []
                for scatter in plot_group.token_plots:
                    # Check each token plot to see if we're on their point
                    cont, ind = scatter.contains(event)
                    if cont:
                        # Set the position of the annotation
                        # x, y = scatter.get_data()  # Strategy for getting line data
                        # pos = (x[ind["ind"][0]], y[ind["ind"][0]])
                        pos = scatter.get_offsets()[ind["ind"][0]]
                        # Add the judgement call to the annotation text
                        # TODO: Tie in judge "data" value
                        judge_calls.append(f"{scatter.get_label()}: {pos}")

                # If one of the points matches, draw the annotation
                if judge_calls:
                    self.redraw_annotations(
                        plot_group,
                        pos,
                        "\n".join(judge_calls).strip(),
                        None if not active_annotations else active_annotations[-1],
                    )
                    plot_group.annotation.set_visible(True)
                    active_annotations.append(plot_group.annotation)
                    self.fig.canvas.draw_idle()
                # Otherwise, if we're still visible, remove the annotation
                else:
                    if plot_group.annotation.get_visible():
                        plot_group.annotation.set_visible(False)
                        self.fig.canvas.draw_idle()
