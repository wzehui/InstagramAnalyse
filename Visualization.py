import seaborn as sns
import matplotlib.pyplot as plt

sns.set(style='whitegrid')
tips = sns.load_dataset('tips')
fig = sns.relplot(x='day', y='tip', data=tips)

#fig.savefig('chart.png', dpi=1000, bbox_inches='tight')
plt.show()
