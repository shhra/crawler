import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from analysis import Analyze
from collections import Counter
from itertools import combinations


df = pd.read_csv("top_rgb_palette.csv", sep=',', names=['c1', 'c2', 'c3', 'c4', 'c5'])
colors = np.array(df)
global_list = []
unsorted = []
for each in colors:
    a = list(combinations(each, 1))
    for cur in a:
        # global_list.append([cur[0], cur[1]])
        # global_list.append((sorted(cur)[0], sorted(cur)[1]))
        unsorted.append(cur)

counts = Counter(unsorted)
with open("Combination_single.csv", "w") as f:
    for key in (counts.keys()):
        # f.write(str(key[0] + "," + key[1]) + "," + str(counts[key]) + '\n')
        f.write(str(key[0] + "," + str(counts[key]) + '\n'))
# print(Counter(unsorted))

analyzer = Analyze()

# The following code will produce bar chart on top 1000 data
colors = analyzer.select_all()
print(colors.head())
fig, ax = plt.subplots(figsize=(200, 10))
plt.tick_params(axis='x', labelbottom=False)
df = pd.read_csv("Combination_single.csv", names=['color', 'count'])
print(df.head())
df = df.set_index('color')
df = df.reindex(index=colors['hex'])
df = df.reset_index()
df.fillna(0)
x = np.arange(0, 1000)
ax.set_xticks(x)

y = df['count']
plt.bar(x, y)
plt.savefig('bar.png')
# plt.show()






