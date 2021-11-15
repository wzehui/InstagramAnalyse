import pandas as pd
import matplotlib.pyplot as plt
from main import *

path = '/Users/ze/Documents/PycharmProjects/Data/Instagram/'  # MacBookPro
#df = pd.read_csv(os.path.join(path, 'media.csv'), usecols=['id','owner_id',
#                                                           'location_id',
#                                                           'taken_at_timestamp'],
#                 nrows=10000,
#                 lineterminator='\n')
##df = DataLoader('media.csv', ['id','owner_id','location_id',
##                             'taken_at_timestamp'], lineterminator='\n')
#df.taken_at_timestamp = pd.to_datetime(df.taken_at_timestamp).dt.date
#pivot_df = df.pivot_table(index='taken_at_timestamp',
#                          columns='owner_id',
#                         values='id', aggfunc='count',
#                         fill_value=0)
#pivot_df.index = pd.to_datetime(pivot_df.index)
#
#date_list = ['M','W']
#
#for date_list_iter in date_list:
#    pivot_df_t = pivot_df
#    pivot_df_t = pivot_df_t.resample(date_list_iter).sum()
#    pivot_df_t[pivot_df_t > 0] = 1
#    pivot_df_t.loc['sum'] = pivot_df_t.apply(lambda x:x.sum())
#    if date_list_iter == 'M':
#        threshold = 30
#    elif date_list_iter == 'W':
#        threshold = 100
#    pivot_df_t = pivot_df_t.T.loc[pivot_df_t.T['sum'] >= threshold]
#    exec('{} = pivot_df_t.index.values'.format('owner_' + date_list_iter))
#    pivot_df_t.sort_values('sum', ascending=False, inplace=True)
#    pivot_df_t.to_csv('./' + date_list_iter + '.csv')
#
#owner_c = np.intersect1d(owner_W, owner_M)
#pivot_df = pivot_df[pivot_df.columns[pivot_df.columns.isin(owner_c)]]
#pivot_df[pivot_df > 0] = 1
#pivot_df.loc['sum'] = pivot_df.apply(lambda x:x.sum())
#pivot_df.sort_values('sum', axis=1, ascending=False, inplace=True)
#pivot_df.to_csv('./D.csv')
#
#
#
#

# Week-frequency
#owner_list = pd.read_csv(os.path.join(path, 'W.csv'))
#owner_list_W = owner_list[['owner_id','sum']]
#owner_list_W = owner_list_W[owner_list_W['sum'] > 30]
#owner_list_W.set_index('owner_id', inplace=True)
#owner_list_W.hist(bins=50)

# Month-frequency
#owner_list = pd.read_csv(os.path.join(path, 'M.csv'))
#owner_list_M = owner_list[['owner_id','sum']]
#owner_list_M = owner_list_M[owner_list_M['sum'] > 5]
#owner_list_M.set_index('owner_id', inplace=True)
#owner_list_M.hist(bins=50)

# Day-frequency
owner_list = pd.read_csv(os.path.join(path, 'D.csv'))
#owner_list = owner_list.iloc[3540,:]
#owner_list = owner_list.drop(labels='taken_at_timestamp')
#owner_list.hist(bins=300)

# Weekday Filter
from datetime import datetime
weekday_filter = pd.DataFrame()
weekday_filter['time'] = owner_list['taken_at_timestamp']
weekday_filter.drop(len(weekday_filter)-1, inplace=True)

weekday_filter['time'] = pd.to_datetime(weekday_filter['time']).dt.date
for index, item in weekday_filter.iterrows():
    if (datetime.isoweekday(item['time']) == 6) or (datetime.isoweekday(item[
                                                                         'time']) == 7):
        weekday_filter.iloc[index].time = False
    else:
        weekday_filter.iloc[index].time = True

for index, item in owner_list.iloc[:,1:].iteritems():
    num_weekday = (item.iloc[:-1] & weekday_filter['time']).values.sum()
    owner_list.loc['%', index] = num_weekday/item.iloc[-1]

owner_list = owner_list.drop(columns='taken_at_timestamp')
owner_list.sort_values('%', axis=1, ascending=False, inplace=True)
owner_list = owner_list.T
owner_list = owner_list.loc[owner_list['%'] >= 0.5]
owner_list = owner_list.loc[owner_list[3540] >= 100]
owner_list = owner_list.index.to_list()
#owner_list.drop(axis=1)
#plt.title('User Daily Upload Frequency')
#plt.xlabel('Upload Frequency')
#plt.ylabel('User Count')
#plt.show()

clusterizer = Clusterizer()
df_location = DataLoader('extended_locations.csv', ['id', 'lat', 'lon',
                                                    'edge_media_count'])
df_media = DataLoader('media.csv', ['id', 'owner_id', 'location_id',
                                    'city_id'], '\n')
df_media = df_media[~df_media['owner_id'].apply(str).isin(owner_list)]

df_location = clusterizer.ClusterDBSCAN(df_location)
df_location = PopularClusterFilter(df_location)
df_media = Add_cluster(df_media, df_location)
df_media = PopularUploadFilter(df_media)
#Mapping(df_location, file_name='DBSCAN_clustering_________.html')
association_rule, rule_sum = AssociationRule(df_media)


