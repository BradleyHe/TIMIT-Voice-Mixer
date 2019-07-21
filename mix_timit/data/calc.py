import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# generated 33 data files
data_list = []
df = pd.DataFrame()

for x in range(1, 34):
	df = df.append(pd.read_csv('per_data_{}.csv'.format(x), index_col=0))

data_mean = df.groupby(level=0).mean()
data_std = df.groupby(level=0).std()
	
data_mean.plot(kind='line', ylim=[0.25, 0.8])
plt.xlabel('TIR')
plt.ylabel('PER')
for col in data_mean.columns:
	std = data_std[col]
	mean = data_mean[col]

	plt.fill_between(data_mean.index, mean - std * 2, mean + std * 2, alpha=0.35)
plt.show()