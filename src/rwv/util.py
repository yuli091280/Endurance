import pandas as pd

runner_data = None

judge_data = pd.read_csv('./judge_demo.csv')

def get_data():
    # conn = create_connection("./population.db")
    # return pd.read_sql("SELECT Time as Year, TPopulation1Jan / 1000.0 as Population FROM population WHERE Location = 'World'", conn)
    global runner_data
    if runner_data is None:
        runner_data = pd.read_csv('./loc_demo.csv')
    return runner_data