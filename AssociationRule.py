import os
import folium
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN, KMeans, AgglomerativeClustering
from mlxtend.frequent_patterns import fpgrowth, association_rules

def DataLoader(file_name, usecols, lineterminator=None):
    path = '/Users/ze/Documents/PycharmProjects/Data/Instagram/'    # MacBookPro
    #path = '/root/work/Data/'   # AI Server
    df = pd.read_csv(os.path.join(path, file_name), usecols=usecols,
                     lineterminator=lineterminator)
    if file_name == 'extended_locations.csv':
        # Data cleaning
        df = df[df['edge_media_count'] != 0]
        # Filter geographic data
        df = df[
            (df['lat'] > 47.35) & (df['lat'] < 47.9) &
            (df['lon'] > 8.65) & (df['lon'] < 9.9)]
    df.reset_index(drop=True, inplace=True)
    return df

class Clusterizer(object):
    def __init__(self):
        self.path_save = '/Users/ze/Documents/PycharmProjects/Data/Instagram'   #Macbook
        #DBSCAN
        self.kms_per_radian = 6371.0088
        self.epsilon = 1
        self.min_sample = 70
        self.min_item = 0.0005
        # NKMeans
        self.n_clusters = 53
        self.n_outlier = 0.353899

    def ClusterDBSCAN(self, df, epsilon=None, min_sample=None, min_item=None):
        if epsilon is None:
            epsilon = self.epsilon
        if min_sample is None:
            min_sample = self.min_sample
        if min_item is None:
            min_item = self.min_item
        # Clustering
        coords = df[['lat','lon']]
        # Conduct DBSCAN Clustering
        clt = DBSCAN(eps=epsilon/self.kms_per_radian, min_samples=min_sample,
                     algorithm='ball_tree',
                     metric='haversine').fit(np.radians(coords))
        cluster_labels = clt.labels_
        df['cluster'] = cluster_labels
        df.drop(df[df['cluster'] == -1].index, inplace=True)
        # print number of clustering
        num_clusters = len(set(cluster_labels))
        print('Number of clusters: {}'.format(num_clusters))
        # Filter: popular clusters, whose uploads are larger than threshold
        cluster_list = df.cluster.unique()
        media_sum = df.edge_media_count.sum()
        for cluster_list_iter in cluster_list:
            cluster_sum = df[df['cluster']==cluster_list_iter].edge_media_count.sum()
            if (cluster_sum / media_sum) < min_item:
                df = df.append(df[df['cluster']==cluster_list_iter])
                df.drop_duplicates(keep=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
        # Save clustering result
        df.to_csv(os.path.join(self.path_save, 'clustering.csv'), index=False)
        print('Cluster Result is saved.')
        return df

    def ClusterNKMeans(self, df, n_clusters=None, n_outlier=None):
        if n_clusters is None:
            n_clusters = self.n_clusters
        if n_outlier is None:
            n_outlier = self.n_outlier
        kmeans = KMeans(n_clusters=n_clusters)
        coords = df[['lat','lon']]
        kmeans.fit(np.radians(coords))
        cluster_labels = kmeans.labels_
        df['cluster'] = cluster_labels
        return df

    def ClusterAgglomerative(self, df, n_clusters=None):
        if n_clusters is None:
            n_clusters = self.n_clusters
        agg = AgglomerativeClustering(n_clusters=n_clusters)
        coords = df[['lat','lon']]
        agg.fit(np.radians(coords))
        cluster_labels = agg.labels_
        df['cluster'] = cluster_labels
        return df

def map(df, file_name='Bodensee_clustering.html', radius=200, zoom_start=10,
        location=[47.6,9.4]):
    colors = [
        '#0048BA',
        '#B0BF1A',
        '#B284BE',
        '#E52B50',
        '#FF7E00',
        '#FFBF00',
        '#C46210',
        '#72A0C1',
        '#915C83',
        '#FF91AF',
        '#3D2B1F',
        '#1B4D3E',
        '#E9D66B',
        '#F4C2C2',
        '#9C2542',
        '#8A2BE2',
        '#A2A2D0',
        '#0D98BA'
    ]
    m = folium.Map(
        location=location,
        zoom_start=zoom_start,
    )
    m.add_child(folium.LatLngPopup())
    for index, item_iter in df.iterrows():
        lon = item_iter.lon
        lat = item_iter.lat
        label = int(item_iter.cluster)
        folium.Circle(
            radius=radius,
            location=[lat, lon],
            popup=str(label),
            color=colors[int(label % 18)],
            fill='black'
        ).add_to(m)
    m.save(file_name)

def Add_cluster(df,df_cluster):
    cluster_list = df_cluster['cluster'].unique()
    df_p = pd.DataFrame()
    for cluster_list_iter in cluster_list:
        location_list = df_cluster[df_cluster.cluster == cluster_list_iter].id
        print("Cluster {} has {} locations".format(cluster_list_iter,
                                                  location_list.size))
        df_temp = df[df['location_id'].isin(location_list)]
        df_temp.insert(df_temp.shape[1], 'cluster', cluster_list_iter)
        df_p = df_p.append(df_temp, ignore_index=True)
    return df_p

def AssociationRule(df, file_name='association_rules', min_upload=50,
                    min_support=0.004):
    df = df[df.groupby('location_id').location_id.transform('count') > min_upload]
    pivot_df = df.pivot_table(index='owner_id', columns='cluster',
                              values='id', aggfunc='count',
                              fill_value=0)
    pivot_df[pivot_df > 0] = 1
    # Association Rules
    frequent_items = fpgrowth(pivot_df, min_support=min_support, use_colnames=True)
    association_ruleset = association_rules(frequent_items, metric='lift',
                                            min_threshold=1)
    # Results
    association_ruleset.sort_values(by='lift', ascending=False,
                                    inplace=True)
    path_save = '/Users/ze/Documents/PycharmProjects/Data/Instagram'    #Macbook
    df.to_csv(os.path.join(path_save, file_name), index=False)
    print('Association rules is saved.')
    return association_ruleset

if __name__ == '__main__':
    clusterizer = Clusterizer()
    df_location = DataLoader('extended_locations.csv', ['id','lat','lon',
                                               'edge_media_count'])
    df_media = DataLoader('media.csv', ['id','owner_id','location_id',
                                        'city_id'], '\n')

#    # City level
#    df_location = clusterizer.ClusterDBSCAN(df_location)
#    map(df_location)
#    df_media = Add_cluster(df_media, df_location)
#    association_rule = AssociationRule(df_media)

#    # Location Level
#    # Friedrichshafen
#    df_FH = df_location[
#    (df_location['lat'] > 47.64) & (df_location['lat'] < 47.66) &
#    (df_location['lon'] > 9.46) & (df_location['lon'] < 9.49)]
#    df_FH = clusterizer.ClusterDBSCAN(df_FH, epsilon=0.022, min_sample=5,
#                                      min_item=0.00001)
#    map(df_FH, 'Friedrichshafen_clustering.html', 5, 17, [47.6512,9.4772])
#    df_FH_media = Add_cluster(df_media, df_FH)
#    association_rule_FH = AssociationRule(df_FH_media,
#                                          'association_rules_FH',
#                                          min_upload=20, min_support=0.004)

#   # Lindau
#    df_LD = df_location[
#    (df_location['lat'] > 47.541) & (df_location['lat'] < 47.574) &
#    (df_location['lon'] > 9.67) & (df_location['lon'] < 9.72)]
#    df_LD = clusterizer.ClusterDBSCAN(df_LD, epsilon=0.02, min_sample=5,
#                                      min_item=0.00001)
#    map(df_LD, 'Lindau_clustering.html', 5, 16, [47.548,9.688])
#    df_LD_media = Add_cluster(df_media, df_LD)
#    association_rule_LD = AssociationRule(df_LD_media,
#                                          'association_rules_LD',
#                                          min_upload=20, min_support=0.004)

    # different clustering method
    # DBSCAN
    df_location = clusterizer.ClusterDBSCAN(df_location)
    map(df_location)
    # NKMeans
    df_location = clusterizer.ClusterNKMeans(df_location)
    map(df_location, file_name='NKMeans_clustering.html')
#    # Agglomerative
#    df_location = clusterizer.ClusterAgglomerative(df_location)
#    map(df_location, file_name='Agglomerative_clustering.html')
