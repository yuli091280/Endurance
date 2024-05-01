from enum import IntEnum, IntFlag, auto

import matplotlib.dates
import numpy as np

from matplotlib import pyplot
from matplotlib.figure import Figure
from matplotlib.text import OffsetFrom

import matplotlib.dates as mpl_dates


class JudgeCallType(IntEnum):
    """
    Enum representing the type of judge calls on the graph.
    """

    BENT_KNEE = auto()
    LOC = auto()


class AthletePlotGroup:
    """
    A group of plots for a particular athlete.

    :param loc_plot: The LOC data of this athlete as a line plot
    :type loc_plot: matplotlib.lines.Line2D
    :param annotation: Annotation to display judge data on the line plot
    :type annotation: matplotlib.text.Annotation
    """

    def __init__(self, loc_plot, annotation=None):
        self.loc_plot = loc_plot
        self.annotation = annotation
        self.judge_call_plots = list()

    def select(self):
        """
        Select this plot group to be displayed. Also adds athlete selection to the
        judge call plot groups belonging to this group.
        """
        self.loc_plot.set_visible(True)
        for call_group in self.judge_call_plots:
            call_group.select(JudgeCallPlotGroup.Selection.ATHLETE)

    def deselect(self):
        """
        Deselect this plot group and hide it. Also removes athlete selection from the
        judge call plot groups belonging to this group.
        """
        self.loc_plot.set_visible(False)
        for call_group in self.judge_call_plots:
            call_group.deselect(JudgeCallPlotGroup.Selection.ATHLETE)

    def get_visible(self):
        """
        Check if the LOC line under this group is visible.

        :return: True if any plot in this group is visible, False otherwise
        :rtype: bool
        """
        return self.loc_plot.get_visible()

    def add_judge_call_plot_group(self, plot_group):
        """
        Add a judge call plot group to this group.

        :param plot_group: The plot group to add
        :type plot_group: JudgeCallPlotGroup
        """
        self.judge_call_plots.append(plot_group)

    def get_judge_call_plot_group(self):
        """
        Get all the judge call plot groups belonging to this group.

        :return: A list of judge call plot groups
        :rtype: list[JudgeCallPlotGroup]
        """
        return self.judge_call_plots


class JudgeCallPlotGroup:
    """
    A group of plots for judge calls of a particular judge and call type.

    :param yellow: The yellow judge calls plot
    :type yellow: matplotlib.collections.PathCollection
    :param red: The red judge calls plot
    :type red: matplotlib.collections.PathCollection
    """

    class Selection(IntFlag):
        """
        Enum representing how this plot group was selected by the user.
        """

        NONE = 0b000
        TYPE = 0b001
        JUDGE = 0b010
        ATHLETE = 0b100
        ALL = 0b111

    def __init__(self, yellow, red):
        self.yellow = yellow
        self.red = red
        self.selected = JudgeCallPlotGroup.Selection.NONE

    def select(self, selection):
        """
        Select this plot group in some way. The plot group will not become visible
        until this group has been selected by everything.

        :param selection: Which method to select
        :type selection: JudgeCallPlotGroup.Selection
        """
        self.selected = self.selected | selection
        visible = self.selected == JudgeCallPlotGroup.Selection.ALL
        self.yellow.set_visible(visible)
        self.red.set_visible(visible)

    def deselect(self, selection):
        """
        Unselect this plot group in some way, making this plot group invisible.

        :param selection: Which method to unselect
        :type selection: JudgeCallPlotGroup.Selection
        """
        self.selected = self.selected & (~selection)
        self.yellow.set_visible(False)
        self.red.set_visible(False)

    def get_visible(self):
        """
        Check if any plots under this group are visible.

        :return: True if this group is visible, False otherwise
        :rtype: bool
        """
        return self.yellow.get_visible() or self.red.get_visible()

    def get_plots(self):
        """
        Get all plots belonging to this group

        :return: The plots belonging to this group
        :rtype: tuple[matplotlib.collections.PathCollection]
        """
        return self.yellow, self.red


class LocGraph:
    """
    Create the figure where athlete LOC values are graphed.

    :param width: Graph width
    :type width: int
    :param height: Graph height
    :type height: int
    :param dpi: Graph dpi
    :type dpi: int
    :param max_loc: Value at which to draw the Max LOC line
    :type max_loc: int
    """

    def __init__(self, width=5, height=4, dpi=100, max_loc=60):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.subplots()

        # Initialize value to keep track of the max LOC
        self.max_loc = max_loc
        self.max_loc_line = None

        # Map plots in various ways so that they can be referenced easily later
        self.athlete_plots = dict()
        self.call_type_plots = dict()
        self.judge_plots = dict()

    def reset(self):
        """
        Reset this graph object to before any LOC values were graphed.
        """
        self.fig.clear()
        self.ax = self.fig.subplots()
        self.athlete_plots = dict()
        self.call_type_plots = dict()
        self.judge_plots = dict()

    def get_figure(self):
        """
        Get the Matplotlib figure this class is using to plot.

        :return fig: The LocGraph stored in the class.
        :return fig: matplotlib.figure.Figure
        """
        return self.fig

    def redraw_max_loc(self, loc):
        """
        Redraws a max loc line on the plot and corrects the plot title to match.

        :param loc: The loc value
        :type loc: int
        """
        self.max_loc = loc
        self.ax.set_title(f"Walker LOC over Time w/ Max LOC = {self.max_loc} ms")
        self.max_loc_line.loc_plot.set_ydata([loc, loc])

    def display_athletes(self, selected_bibs):
        """
        Displays all selected athletes on the graph.

        :param selected_bibs: A list of bib numbers corresponding to the athlete to be displayed
        :type selected_bibs: list[int]
        """
        # Set up a list of visible lines to draw the legend from
        visible_lines = [self.max_loc_line]

        for bib in self.athlete_plots:
            visible = bib in selected_bibs
            plot = self.athlete_plots[bib]
            if visible:
                visible_lines.append(plot)
                plot.select()
            else:
                plot.deselect()

        # Redraw the legend based on visible lines
        self.ax.legend(handles=[line.loc_plot for line in visible_lines])

    def display_judge_call_by_type(self, call_type, show):
        """
        Select a type of judge call to be displayed or hidden.

        :param call_type: The type of judge call to show or hide
        :type call_type: JudgeCallType
        :param show: Whether the user wants to see this type of judge call or not
        :type show: bool
        """
        if call_type not in self.call_type_plots:
            return
        if show:
            for plot_group in self.call_type_plots[call_type]:
                plot_group.select(JudgeCallPlotGroup.Selection.TYPE)
        else:
            for plot_group in self.call_type_plots[call_type]:
                plot_group.deselect(JudgeCallPlotGroup.Selection.TYPE)

    def display_judge_call_by_judges(self, selected_judges):
        """
        Select the judges that will have their judge calls displayed.

        :param selected_judges: List of judge ids to be displayed
        :type selected_judges: list[int]
        """
        for judge in self.judge_plots:
            if judge in selected_judges:
                for plot_group in self.judge_plots[judge]:
                    plot_group.select(JudgeCallPlotGroup.Selection.JUDGE)
            else:
                for plot_group in self.judge_plots[judge]:
                    plot_group.deselect(JudgeCallPlotGroup.Selection.JUDGE)

    def plot(self, loc_values, judge_data, athletes, judges):
        """
        Plot the given LOC values as well as judge calls, and make them invisible.

        :param loc_values: The LOC values to graph
        :type loc_values: dict[int, pandas.DataFrame]
        :param judge_data: The judge calls to graph
        :type judge_data: dict[int, dict[int, pandas.DataFrame]]
        :param athletes: Information for each athlete that is graphed
        :type athletes: list[tuple[str, str, int]]
        :param judges: A dictionary of judge ids and names for the judges involved in this race
        :type judges: dict[int, str]
        """
        # setup colormap to avoid duplicate colors
        colors = pyplot.cm.nipy_spectral(np.linspace(0, 1, len(athletes)))
        self.ax.set_prop_cycle("color", colors)

        # Set plot title and axis labels
        self.ax.set_title(f"Walker LOC over Time w/ Max LOC = {self.max_loc} ms")
        self.ax.set_ylabel("Walker LOC (ms)")
        self.ax.set_xlabel("Time")
        self.ax.xaxis.set_major_formatter(mpl_dates.DateFormatter("%H:%M:%S %p"))

        # Draw max LOC cutoff line
        self.max_loc_line = AthletePlotGroup(
            self.ax.axhline(y=self.max_loc, color="r", label="Max LOC")
        )

        for index, (last_name, first_name, bib_number) in enumerate(athletes):
            walker_data = loc_values[bib_number]
            loc_plot = self.ax.plot(
                walker_data["Time"],
                walker_data["LOCAverage"],
                label=f"{last_name}, {first_name} ({bib_number})",
                marker="o",
                visible=False,
            )[-1]

            annotation = self.ax.annotate(
                "",
                xy=(0, 0),
                ha="left",
                bbox=dict(boxstyle="round", fc="w"),
                arrowprops=dict(
                    arrowstyle="->",
                    connectionstyle="angle,angleA=0,angleB=90,rad=10",
                ),
                visible=False,
            )

            self.athlete_plots[bib_number] = AthletePlotGroup(loc_plot, annotation)

            per_athlete_judge_calls = judge_data[bib_number]

            for judge_id in per_athlete_judge_calls:
                per_judge_calls = per_athlete_judge_calls[judge_id]
                judge_name = judges[judge_id]
                for call_type in per_judge_calls:
                    yellow_data = per_judge_calls[call_type][0]
                    red_data = per_judge_calls[call_type][1]
                    yellow_data["LOCAverage"] = np.interp(
                        # Converts the datetimes to seconds since epoch, which is how
                        # matplotlib converts these internally
                        (yellow_data["Time"].astype("int64") // 10**9).tolist(),
                        (walker_data["Time"].astype("int64") // 10**9).tolist(),
                        walker_data["LOCAverage"].tolist(),
                    )
                    red_data["LOCAverage"] = np.interp(
                        # Converts the datetimes to seconds since epoch, which is how
                        # matplotlib converts these internally
                        (red_data["Time"].astype("int64") // 10**9).tolist(),
                        (walker_data["Time"].astype("int64") // 10**9).tolist(),
                        walker_data["LOCAverage"].tolist(),
                    )
                    if call_type == JudgeCallType.LOC:
                        yellow_plot = self.ax.scatter(
                            x=yellow_data["Time"],
                            y=yellow_data["LOCAverage"],
                            label=f"LOC Yellow Card\n - {judge_name}",
                            color="y",
                            marker=r"$\sim$",
                            visible=False,
                        )
                        red_plot = self.ax.scatter(
                            x=red_data["Time"],
                            y=red_data["LOCAverage"],
                            label=f"LOC Red Card\n - {judge_name}",
                            color="r",
                            marker=r"$\sim$",
                            visible=False,
                        )
                    elif call_type == JudgeCallType.BENT_KNEE:
                        yellow_plot = self.ax.scatter(
                            x=yellow_data["Time"],
                            y=yellow_data["LOCAverage"],
                            label=f"Bent Knee Yellow Card\n - {judge_name}",
                            color="y",
                            marker="$>$",
                            visible=False,
                        )
                        red_plot = self.ax.scatter(
                            x=red_data["Time"],
                            y=red_data["LOCAverage"],
                            label=f"Bent Knee Red Card\n - {judge_name}",
                            color="r",
                            marker="$>$",
                            visible=False,
                        )
                    else:
                        raise RuntimeError("Unknown judge call type while plotting.")

                    plot = JudgeCallPlotGroup(yellow_plot, red_plot)
                    self.call_type_plots.setdefault(call_type, list()).append(plot)
                    self.judge_plots.setdefault(judge_id, list()).append(plot)
                    self.athlete_plots[bib_number].add_judge_call_plot_group(plot)

        # Create a legend for the plot
        self.ax.legend(handles=[self.max_loc_line.loc_plot])

    def redraw_annotation(self, plot_group, pos, text, previous_annotation=None):
        """
        Handles the displaying of annotations over points, taking into account
        the boundaries of the plot as well as other annotations.

        :param plot_group: The plot group to which the annotation belongs
        :type plot_group: AthletePlotGroup
        :param pos: Position of the annotation on the graph
        :type pos: numpy.ma.core.MaskedArray
        :param text: The text of the annotation
        :type text: str
        :param previous_annotation: The previous annotation to position off of, None otherwise
        :type: matplotlib.text.Annotation or None
        """
        plot_group.annotation.xy = pos
        plot_group.annotation.set_text(text)
        # Set annotation color to match that of the line
        plot_group.annotation.get_bbox_patch().set_facecolor(
            plot_group.loc_plot.get_c()
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
        """
        Hover event for the plot, ties into self.redraw_annotation to supply position
        and text information for judge data.

        :param event: The mouse event on the graph
        :type event: matplotlib.backend_bases.MouseEvent
        """
        if event.inaxes == self.ax:
            # Keep the last annotation drawn to be used to position subsequent annotations off the first visible one
            previous_annotation = None
            # If we're inbounds, look at every token plot to see if we're on one of their points
            for plot_group in self.athlete_plots.values():
                # If the main line isn't visible, neither will the token plots
                if not plot_group.get_visible():
                    continue

                pos = None
                judge_calls = []
                for groups in plot_group.get_judge_call_plot_group():
                    for scatter in groups.get_plots():
                        # Check each token plot to see if we're on their point
                        cont, ind = scatter.contains(event)
                        if cont:
                            # Set the position of the annotation
                            pos = scatter.get_offsets()[ind["ind"][0]]
                            # Add the judgement call to the annotation text
                            dt = matplotlib.dates.num2date(pos[0]).strftime("%I:%M%p")
                            info_str = f"{plot_group.loc_plot.get_label()}: {scatter.get_label()} @ {dt}"
                            if info_str not in judge_calls:
                                judge_calls.append(info_str)

                # If one of the points matches, draw the annotation
                if judge_calls:
                    self.redraw_annotation(
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
