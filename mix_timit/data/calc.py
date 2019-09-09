import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

categories = ['MM', 'MF', 'FF', 'FM']

# generated 33 data files
data_list = []
df = pd.DataFrame()

for x in range(1, 34):
	df = df.append(pd.read_csv('per_data_{}.csv'.format(x), index_col=0))

data_mean = df.groupby(level=0).mean()
data_std = df.groupby(level=0).std()
data_mean.to_csv('data_mean.csv')
data_std.to_csv('data_std.csv')

print(data_mean)
print(data_std)

for category in categories:
	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)

	plt.plot(list(data_mean.index), data_mean[category], color='k', linewidth=1, marker='o', mfc='g', clip_on=False, zorder=100)
	plt.errorbar(data_mean.index, data_mean[category], fmt='none', ecolor='k', capsize=4, yerr=data_std[category])

	ax.set_xlim(0, 12)
	ax.set_ylim(0.27, 0.78)
	ax.set_zorder(-5)

	plt.setp(ax.spines.values(), linewidth=2)
	plt.grid(True)
	plt.axhline(y=0.26, color='k', linestyle='--')

	plt.xticks(range(0, 33, 3))
	plt.yticks(np.arange(0.25, 0.8, 0.05))
	plt.xlabel('TIR (dB)')
	plt.ylabel('PER')
	plt.legend((category[0] + '-' + category[1], 'Unmodified'), loc='upper right')
	ax.set_title('Performance with ' + category[0] + '-' + category[1]  + ' mixing', fontdict={'fontsize': 10, 'fontweight': 'medium'})
	plt.savefig(category + '.pdf', bbox_inches = 'tight', pad_inches = 0)