import time
import pandas as pd
import numpy as np
import glob

path = 'D:/ACA/fyp/bsc-fyp/monitoring/data_collection/data/cadvisor_original/'
files = glob.glob(path+'*.csv')
print(len(files))
for file in files:
    df = pd.read_csv(file)

    # df['unix_time'] = pd.to_datetime(df['timestamp'],utc=0)
    df['unix_time'] = df['timestamp']
    for i in range(df.shape[0]):
        df['unix_time'][i] = int(time.mktime(time.strptime(df['unix_time'][i], '%Y-%m-%d %H:%M:%S.%f%z')))
    df['unix_time'] = (np.round((df['unix_time'] / 5).astype(np.float)) * 5).astype(np.int)
    break