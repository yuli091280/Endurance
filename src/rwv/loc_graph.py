import numpy as np

from matplotlib import pyplot
from matplotlib.figure import Figure
from matplotlib.text import OffsetFrom

import matplotlib.dates as mpl_dates


class PlotGroup:
    """
    PlotGroup is the grouping of the plot.

    :param main_plot: The main plot data.
    :type main_plot: list[str]
    :param annotation: The main plot data.
    :type annotation: list[str]
    :param token_plots: Token plots
    :type token_plots: list[str]
    """
    def __init__(self, main_plot, annotation=None, token_plots=None):
        if token_plots is None:
            token_plots = []

        self.main_plot = main_plot
        self.annotation = annotation
        self.token_plots = token_plots


# LocGraph showing loc for each selected runner with judge calls placed on top if requested
class LocGraph:
    """
    LocGraph is the class holding Loc Graph.

    :param width: Graph width
    :type width: int
    :param height: Graph height.
    :type height: int
    :param dpi: dpi value
    :type dpi: int
    :param max_loc: Max Loc line value.
    :type max_loc: int
    """
    def __init__(self, width=5, height=4, dpi=100, max_loc=60):
        """Create the graph object where LOC values are graphed.

        :param self: This LocGraph instance.
        :param width: Width of the canvas in inches.
        :param height: Height of the canvase in inches.
        :param dpi: Dots per inch of the canvas.
        :param max_loc: The LOC value in which a line is drawn.
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.subplots()

        # Initialize dictionary to keep track of our plots, necessary for redrawing
        self.data_plots = dict()

        # Initialize value to keep track of the max LOC
        self.max_loc_value = max_loc
        self.max_loc = None

        # Initialize booleans to keep track of bent knee/loc display state
        self.display_bent_knee = True
        self.display_loc = True

    def reset(self):
        """Reset this graph object to before any LOC values were graphed.

        :param self: This LocGraph instance.
        """
        self.fig.clear()
        self.ax = self.fig.subplots()
        self.data_plots = dict()

    def get_figure(self):
        """
        Get the Matplotlib figure this class is using to plot.

        :return fig: The LocGraph stored in the class.
        :return fig: Figure
        """
        return self.fig

    def redraw_max_loc(self, loc):
        """
        Redraws a max loc line on the plot along with a title.

        :param loc: The loc value.
        :type loc: int
        """
        self.max_loc_value = loc
        self.ax.set_title(f"Racer LOC over Time w/ Max LOC = {self.max_loc_value} ms")
        self.max_loc.main_plot.set_ydata([loc, loc])

    def display_runners(self, selected_runners):
        """
        Displays runners on the graph.

        :param selected_runners: A dictionary of runners to display, with their bib numbers as the key.
        :type selected_runners: dict[any]
        """
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
            self.data_plots[bib_key].token_plots[1].set_visible(
                self.display_loc and visible
            )

            # Set bent knee points to visible if selected or all, and we have the box checked
            self.data_plots[bib_key].token_plots[2].set_visible(
                self.display_bent_knee and visible
            )
            self.data_plots[bib_key].token_plots[3].set_visible(
                self.display_bent_knee and visible
            )

        # Redraw the legend based on visible lines
        self.ax.legend(handles=[line.main_plot for line in visible_lines])

    def display_points(self, point_type, visible):
        """
        Change visibility of selected point type on the graph.

        :param point_type: String representing the point type.
        :type point_type: str
        :param visible: Visibility of the point.
        :type visible: bool
        """
        # No data variable, so we have to match to the label
        if point_type == "Bent Knee":
            self.display_bent_knee = visible
        else:
            self.display_loc = visible

        for plot_group in self.data_plots.values():
            # If the line for this athlete is visible, update the LOC and bent knee display values accordingly
            if plot_group.main_plot.get_visible():
                plot_group.token_plots[0].set_visible(self.display_loc)
                plot_group.token_plots[1].set_visible(self.display_loc)
                plot_group.token_plots[2].set_visible(self.display_bent_knee)
                plot_group.token_plots[3].set_visible(self.display_bent_knee)

    def plot(self, loc_values, judge_data, athletes):
        """
        Plot the given LOC values as well as judge calls, and make them invisible.

        :param loc_values: The LOC values to graph.
        :type loc_values: list[int]
        :param judge_data: The judge calls to graph.
        :type judge_data: list[int]
        :param athletes: Information for each athlete that is graphed.
        :type athletes: list[str]
        """
        self.reset()

        # setup colormap to avoid duplicate colors
        colors = pyplot.cm.nipy_spectral(np.linspace(0, 1, len(athletes)))
        self.ax.set_prop_cycle("color", colors)

        # Set plot title and axis labels
        self.ax.set_title(f"Racer LOC over Time w/ Max LOC = {self.max_loc_value} ms")
        self.ax.set_ylabel("Racer LOC (ms)")
        self.ax.set_xlabel("Time")
        self.ax.xaxis.set_major_formatter(mpl_dates.DateFormatter("%H:%M:%S %p"))

        # Draw max LOC cutoff line
        self.max_loc = PlotGroup(
            self.ax.axhline(y=self.max_loc_value, color="r", label="Max LOC")
        )

        for index, (last_name, first_name, bib_number) in enumerate(athletes):
            runner_data = loc_values[bib_number]
            main_plot = self.ax.plot(
                runner_data["Time"],
                runner_data["LOCAverage"],
                label=f"{last_name}, {first_name} ({bib_number})",
                marker="o",
                visible=False,
            )[-1]

            judge_calls = judge_data[bib_number]

            judge_calls["LOCAverage"] = np.interp(
                # Converts the datetimes to seconds since epoch, which is how matplotlib converts these internally
                (judge_calls["Time"].astype("int64") // 10**9).tolist(),
                (runner_data["Time"].astype("int64") // 10**9).tolist(),
                runner_data["LOCAverage"].tolist(),
            )
            yellow_loc = judge_calls.query("Color == 'Yellow' & Infraction == '~'")
            red_loc = judge_calls.query("Color == 'Red' & Infraction == '~'")
            yellow_bent = judge_calls.query("Color == 'Yellow' & Infraction == '<'")
            red_bent = judge_calls.query("Color == 'Red' & Infraction == '<'")

            self.data_plots[bib_number] = PlotGroup(
                main_plot=main_plot,
                annotation=self.ax.annotate(
                    "",
                    xy=(0, 0),
                    ha="left",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(
                        arrowstyle="->",
                        connectionstyle="angle,angleA=0,angleB=90,rad=10",
                    ),
                    visible=False,
                ),
                token_plots=[
                    # Draw yellow LOC infractions
                    self.ax.scatter(
                        x=yellow_loc["Time"],
                        y=yellow_loc["LOCAverage"],
                        label="LOC Yellow Card",
                        color="y",
                        marker="*",
                        visible=False,
                    ),
                    # Draw red LOC infractions
                    self.ax.scatter(
                        x=red_loc["Time"],
                        y=red_loc["LOCAverage"],
                        label="LOC Red Card",
                        color="r",
                        marker="*",
                        visible=False,
                    ),
                    # Draw yellow bent knee infractions
                    self.ax.scatter(
                        x=yellow_bent["Time"],
                        y=yellow_bent["LOCAverage"],
                        label="Bent Knee Yellow Card",
                        color="y",
                        marker=">",
                        visible=False,
                    ),
                    # Draw red bent knee infractions
                    self.ax.scatter(
                        x=red_bent["Time"],
                        y=red_bent["LOCAverage"],
                        label="Bent Knee Red Card",
                        color="r",
                        marker=">",
                        visible=False,
                    ),
                ],
            )

        # Create a legend for the plot
        self.ax.legend(handles=[self.max_loc.main_plot])
        self.fig.canvas.draw_idle()

    def redraw_annotations(self, plot_group, pos, text, previous_annotation=None):
        """
        todo
        """
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
            plot_group.annotation.set_horizontalalignment("left")
            return

        x_bounds = self.ax.get_xlim()
        y_bounds = self.ax.get_ylim()
        plot_group.annotation.set_verticalalignment("bottom")
        plot_group.annotation.set_anncoords("offset points")
        x_offset = 20
        y_offset = 20
        if pos[0] > x_bounds[0] + (x_bounds[1] - x_bounds[0]) / 2:
            plot_group.annotation.set_horizontalalignment("right")
            x_offset = -x_offset
        else:
            plot_group.annotation.set_horizontalalignment("left")
        if pos[1] > y_bounds[1] - (y_bounds[1] - y_bounds[0]) * 0.1:
            y_offset = -y_offset
        plot_group.annotation.xyann = (x_offset, y_offset)

    def on_hover(self, event):
        if event.inaxes == self.ax:
            # Keep the last annotation drawn to be used to position subsequent annotations off the first visible one
            previous_annotation = None
            # If we're inbounds, look at every token plot to see if we're on one of their points
            for plot_group in self.data_plots.values():
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
                        pos = scatter.get_offsets()[ind["ind"][0]]
                        # Add the judgement call to the annotation text
                        # TODO: Tie in judge "data" value
                        if (
                            not f"{plot_group.main_plot.get_label()}: {scatter.get_label()}"
                            in judge_calls
                        ):
                            judge_calls.append(
                                f"{plot_group.main_plot.get_label()}: {scatter.get_label()}"
                            )

                # If one of the points matches, draw the annotation
                if judge_calls:
                    self.redraw_annotations(
                        plot_group,
                        pos,
                        "\n".join(judge_calls).strip(),
                        previous_annotation,
                    )
                    plot_group.annotation.set_visible(True)
                    previous_annotation = plot_group.annotation
                    self.fig.canvas.draw_idle()
                # Otherwise, if we're still visible, remove the annotation
                elif plot_group.annotation.get_visible():
                    plot_group.annotation.set_visible(False)
                    self.fig.canvas.draw_idle()
