import pandas as pd

runner_data = None

judge_data = pd.read_csv("./judge_demo.csv")


def get_data():
    global runner_data
    if runner_data is None:
        runner_data = pd.read_csv("./loc_demo.csv")
    return runner_data
