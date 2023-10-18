import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

runnerDF = pd.read_csv('rwvtest.csv')
judgeDF = pd.read_csv('judge_data.csv')

runnerTime = runnerDF['Time']
runnerData = runnerDF['JumpHeight']
judgeTime = judgeDF['Time']
colors = judgeDF['Color']

setColors={
    'red': 'red',
    'red*': 'darkred',
    'yellow': 'yellow',
    'yellow*': 'gold'
}
#sets colors based on color dictionary to blue if cant find any by default
colors = [setColors.get(color, 'blue') for color in colors]

plt.figure(figsize=(10, 5))
for i in range(len(judgeTime)):
    locTime = np.interp(judgeTime.iloc[i], runnerTime, runnerData)
    plt.scatter(judgeTime.iloc[i], locTime, color=colors[i], label='Judge Calls' if i == 0 else '')

# Plot the loc line
plt.plot(runnerTime, runnerData, label='Jump Height', color='b')

plt.xlabel('Time (s)')
plt.ylabel('Step Height')
plt.title('Step Height vs Time with Judge Calls')

plt.grid(False)
plt.legend()
plt.show()
