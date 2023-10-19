import matplotlib
matplotlib.use("QtAgg")

import pandas as pd
import seaborn as sns

sns.set_style("darkgrid")

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib import pyplot as plt

from db_stuff import create_connection

runner_data = None

judge_data = pd.read_csv('./judge_demo.csv')

def get_data():
    # conn = create_connection("./population.db")
    # return pd.read_sql("SELECT Time as Year, TPopulation1Jan / 1000.0 as Population FROM population WHERE Location = 'World'", conn)
    global runner_data
    if runner_data is None:
        runner_data = pd.read_csv('./loc_demo.csv')
    return runner_data


# class FigureCanvas(FigureCanvasQTAgg):
#     def __init__(self, width, height, dpi):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes = fig.add_subplot(111)
#         super().__init__(fig)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CI491 Demo")

        df = get_data()
        
        self.runner_combo_box = QtWidgets.QComboBox(self)
        self.runner_combo_box.addItem('All', 'all')
        for item in df.keys()[2:]:
            self.runner_combo_box.addItem(item.replace("_", " ").title(), item)
        self.runner_label = QtWidgets.QLabel('Runner:')
        self.runner_label.setBuddy(self.runner_combo_box)
        self.runner_combo_box.currentIndexChanged.connect(self.redraw_plot)
        
        # canvas = FigureCanvas(5, 5, 100)
        self.figure = plt.figure()
        self.canvas = FigureCanvasQTAgg(self.figure)

        self.plot(df)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.runner_label)
        layout.addWidget(self.runner_combo_box)
        layout.addWidget(self.canvas)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.show()
    
    def redraw_plot(self, *args):
        # sns.lineplot(data=df, x="Year", y="Population", ax=canvas.figure.subplots()).set(title="World Population (mil) Per Year", ylabel="People (mil)")
        df = get_data()
        data = df

        selected_runner = self.runner_combo_box.currentData()
        if selected_runner != 'all':
            data = df[["time", "max_loc", selected_runner]]

        self.plot(data)

    def plot(self, df):
        self.figure.clear()

        sns.lineplot(data=pd.melt(df, ['time']), x='time', y='value', hue='variable', ax=self.figure.subplots())

        try:
            for _, row in judge_data.iterrows():
                for item in row[1:]:
                    if item == '~':
                        plt.scatter(row.iloc[0], df.loc[df['time'] == row.iloc[0]]['runner_1'], color='r', marker='*')
                    elif item == '>':
                        plt.scatter(row.iloc[0], df.loc[df['time'] == row.iloc[0]]['runner_1'], color='r', marker='>')
        except Exception:
            pass

        self.canvas.draw()


app = QApplication([])

window = MainWindow()
window.show()

app.exec()