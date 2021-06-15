import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
# from AssociationRule_city import *

## Find the clustering with most media items
#cluster_list = df_p.cluster.unique()
#num_max = 0
#for cluster_list_iter in cluster_list:
#    num = df_p[df_p.cluster == cluster_list_iter].count().id
#    print('Cluster {} has {} media items'.format(cluster_list_iter, num))
#    if num > num_max:
#        num_max = num
#        print('updated')
import AssociationRule_city


def cluster_dbscan(df):
    # Clustering
    coords = df[['lat','lon']]
    # Conduct DBSCAN Clustering
    kms_per_radian = 6371.0088
    epsilon = 0.01 / kms_per_radian
    clt = DBSCAN(eps=epsilon, min_samples=5, algorithm='ball_tree',
                 metric='haversine').fit(np.radians(coords))
    cluster_labels = clt.labels_
    num_clusters = len(set(cluster_labels))
    clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])
    print('Number of clusters: {}'.format(num_clusters))

    df['cluster'] = cluster_labels
    df.drop(df[df['cluster'] == -1].index, inplace=True)

    # Condition 4: popular clusters, whose owner is larger than 2%
    cluster_list = df.cluster.unique()
    media_sum = df.edge_media_count.sum()
    for cluster_list_iter in cluster_list:
        cluster_sum = df[df['cluster']==cluster_list_iter].edge_media_count.sum()
        if (cluster_sum / media_sum) < 0.0005:
            df = df.append(df[df['cluster']==cluster_list_iter])
            df.drop_duplicates(keep=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df

if __name__ == '__main__':
    path = '/Users/ze/Documents/PycharmProjects/Data/Instagram/'  # MacBookPro
    df = pd.read_csv(path + '/media_modified.csv', usecols=['id', 'owner_id',
                                                            'location_id',
                                                            'city_id'])
    df_location = pd.read_csv(path + '/extended_locations.csv', usecols=[
        'id', 'name', 'lat', 'lon', 'edge_media_count'])

    # %% Filter geographic data
    df_p = df_location[
        (df_location['lat'] > 47.6) & (df_location['lat'] < 47.71) & (df_location['lon'] > 9.314) & (
                df_location['lon'] < 9.629)]

    df_p = cluster_dbscan(df_p)
    AssociationRule_city.map(df_p)
    df_p = AssociationRule_city.Add_cluster(df, df_p)
    association_rule, pivot_table = AssociationRule_city.AssociationRule(df_p)
