'''
+---------------------------------------------------------------+
| Main function/script                                          |
+---------------------------------------------------------------+
------------------------------------------------------------------
Copyright: 2021 Wang,Zehui (wzehui@hotmail.com)
@author: Wang,Zehui
'''

import os
import math
import folium
import pandas as pd
import numpy as np
from math import isnan
from random import sample
from folium import plugins
from sklearn import metrics
from scipy.stats import norm
from numpy.random import uniform
from sklearn.cluster import DBSCAN, KMeans
from sklearn.neighbors import NearestNeighbors
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

def PopularClusterFilter(df, min_items=0.001):
    # Filter: popular clusters, whose uploads are larger than threshold
    cluster_list = df.cluster.unique()
    num_clusters_o = len(cluster_list)
    media_sum = df.edge_media_count.sum()
    for cluster_list_iter in cluster_list:
        cluster_sum = df[
            df['cluster'] == cluster_list_iter].edge_media_count.sum()
        if (cluster_sum / media_sum) < min_items:
            df = df.append(df[df['cluster'] == cluster_list_iter])
            df.drop_duplicates(keep=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    # print reduced number of clustering
    num_clusters = len(df.cluster.unique())
    print('Number of reduced clusters: {}'.format(num_clusters_o -
                                                  num_clusters))
    return df

def PopularUploadFilter(df, min_upload=50):
    df = df[
        df.groupby('location_id').location_id.transform('count') > min_upload]
    return df

def HopkinsTest(X):
    d = X.shape[1]
    #d = len(vars) # columns
    n = len(X) # rows
    m = int(0.1 * n) # heuristic from article [1]
    nbrs = NearestNeighbors(n_neighbors=1).fit(X.values)

    rand_X = sample(range(0, n, 1), m)

    ujd = []
    wjd = []
    for j in range(0, m):
        u_dist, _ = nbrs.kneighbors(uniform(np.amin(X, axis=0),
                                            np.amax(X, axis=0), d).reshape(1,-1),
                                    2, return_distance=True)
        ujd.append(u_dist[0][1])
        w_dist, _ = nbrs.kneighbors(X.iloc[rand_X[j]].values.reshape(1, -1),
                                    2, return_distance=True)
        wjd.append(w_dist[0][1])

    H = sum(ujd) / (sum(ujd) + sum(wjd))
    if isnan(H):
        print(ujd, wjd)
        H = 0
    return H

def PTest(rules, sample_size):
    for index, rule_iter in rules.iterrows():
        P = rule_iter.support
        P_ante = rule_iter['antecedent support']
        P_cons = rule_iter['consequent support']
        # Check pre-condition for normal-approximation
        # if (%{SampleSize}*%{P1_2}*(1-%{P1_2}) > 9):

        # Calculate p-value by normal-approximation of binomial distribution
        p = 1 - norm.cdf(x = P * sample_size - 0.5,
                         loc = P_ante * P_cons * sample_size,
                         scale = math.sqrt(sample_size *
                                           P_ante * P_cons * (1 - P_ante *
                                                              P_cons)))
        # else:
        # p = 0
        # for i in range(1, %{Amount1_2}):
        # calculate binomial coefficient
        # binom = factorial(%{SampleSize}, exact=True) / (factorial(%{SampleSize}-i, exact=True) * factorial(i, exact=True))
        # calculate invers p-value
        # p = p + (binom * pow(%{P1_2}, i) * pow(1-%{P1_2}, %{SampleSize}-i))

        # p = 1-p

        # Convert result list into pandas dataframe
        rules.loc[index, 'p_value'] = p
    return rules

def ClusterEvaluator(df):
    sc_value = metrics.silhouette_score(df[['lat', 'lon']], df['cluster'],
                                        metric='euclidean')
    ch_value = metrics.calinski_harabasz_score(df[['lat', 'lon']],
                                               df['cluster'])
    db_value = metrics.davies_bouldin_score(df[['lat', 'lon']], df['cluster'])

    print('silhouette: {}, calinski harabasz: {}, davies bouldin: {}'.format(sc_value, ch_value, db_value))

class Clusterizer(object):
    def __init__(self):
        self.path_save = '/Users/ze/Documents/PycharmProjects/Data/Instagram'   #Macbook
        #DBSCAN
        self.kms_per_radian = 6371.0088
        self.epsilon = 1
        self.min_sample = 70
        # NKMeans
        self.n_clusters = 53
        self.n_outlier = 9975
        self.z = self.n_outlier / 161

    def ClusterDBSCAN(self, df, epsilon=None, min_sample=None):
        if epsilon is None:
            epsilon = self.epsilon
        if min_sample is None:
            min_sample = self.min_sample
        # Clustering
        coords = df[['lat','lon']]
        print('before noise removal H: {}'.format(HopkinsTest(coords[['lat',
                                                                      'lon']])))
        # Conduct DBSCAN Clustering
        clt = DBSCAN(eps=epsilon/self.kms_per_radian, min_samples=min_sample,
                     algorithm='ball_tree',
                     metric='haversine').fit(np.radians(coords))
        cluster_labels = clt.labels_
        df['cluster'] = cluster_labels
        df.drop(df[df['cluster'] == -1].index, inplace=True)
        print('after noise removal H: {}'.format(HopkinsTest(df[['lat',
                                                                  'lon']])))
        # Save clustering result
        df.to_csv(os.path.join(self.path_save, 'clustering.csv'), index=False)
        print('Cluster Result is saved.')
        return df

    def ClusterNKMeans(self, df, n_clusters=None, z=None):
        if n_clusters is None:
            n_clusters = self.n_clusters
        if z is None:
            z = self.z

        coords = df[['lat','lon']]
        print('before noise removal H: {}'.format(HopkinsTest(coords[['lat',
                                                                    'lon']])))
        coords.loc[:, ['heavy','outlier']] = [False, True]
        neigh = NearestNeighbors(algorithm='ball_tree', metric='haversine')
        neigh.fit(coords[['lat','lon']])

        n = -8.063   # guess by trying all powers of 2
        # for n in np.linspace(-10, -3, 8):
#        print('n={}'.format(n))
#        coords_copy = coords.copy()
        opt = math.pow(2, n)
        r = 2 * math.sqrt(opt / z)
        for index, item_iter in coords.iterrows():
            rng = neigh.radius_neighbors([[item_iter.lat, item_iter.lon]],
                                         radius=r)
            if len(rng[1][0]) >= 2 * z:
                coords.loc[index, 'heavy'] = True
        print(coords[coords['heavy'] == True].heavy.sum())
        for index, item_iter in coords.iterrows():
            rng = neigh.radius_neighbors([[item_iter.lat, item_iter.lon]],
                                         radius=r)
            for index_iter in rng[1][0]:
                if coords.loc[index_iter, 'heavy'] == True:
                    coords.loc[index, 'outlier'] = False
                    break
        print('outlier amount: {}'.format(coords[coords['outlier'] ==
                                        True].outlier.sum()))
        df[['heavy','outlier']] = coords[['heavy','outlier']]
        df.drop(df[df['outlier'] == True].index,inplace=True)
        df.drop(['heavy','outlier'], axis=1, inplace=True)
        print('after noise removal H: {}'.format(HopkinsTest(df[['lat','lon']])))
        kmeans = KMeans(n_clusters=n_clusters)
        kmeans.fit(np.radians(df[['lat','lon']]))
        cluster_labels = kmeans.labels_
        df['cluster'] = cluster_labels

        return df

def Mapping(df, file_name='Bodensee_clustering.html', radius=200, zoom_start=10,
        location=[47.6,9.4]):
    colors = [
        '#0048BA',
        '#545454',
        '#0D98BA',
        '#B0BF1A',
        '#B284BE',
        '#E52B50',
        '#FF7E00',
        '#C46210',
        '#FFBF00',
        '#C385A9',
        '#72A0C1',
        '#915C83',
        '#FF91AF',
        '#3D2B1F',
        '#8F6036',
        '#1B4D3E',
        '#E9D66B',
        '#F4C2C2',
        '#9C2542',
        '#8A2BE2',
        '#A2A2D0',
        '#AE841A'
    ]
    m = folium.Map(
        location=location,
        zoom_start=zoom_start
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
            color=colors[int(label % 21)],
            fill='black'
        ).add_to(m)
    m.save(file_name)

def HeatMapping(df):
     m = folium.Map(
        location=[47.548,9.688],
        zoom_start=11
     )
     heat_data = [[row['lat'], row['lon'], row['edge_media_count']] for
                  index,row in df.iterrows()]
     m.add_child(plugins.HeatMap(heat_data, radius=15))
     m.save('heatmap.html')

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

def AssociationRule(df, file_name='association_rules', min_support=0.004):
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
    association_ruleset.to_csv(os.path.join(path_save, file_name), index=False)
    print('Association rules is saved.')
    return association_ruleset, pivot_df.shape[0]

if __name__ == '__main__':
    clusterizer = Clusterizer()
    df_location = DataLoader('extended_locations.csv', ['id','lat','lon',
                                               'edge_media_count'])
    df_media = DataLoader('media.csv', ['id','owner_id','location_id',
                                        'city_id'], '\n')

   # Region level
#    df_location['cluster'] = 0
#    Mapping(df_location, 'DBSCAN_o.html')
#    HeatMapping(df_location)
#    df_location = clusterizer.ClusterDBSCAN(df_location)
#    Mapping(df_location)
#    df_media = Add_cluster(df_media, df_location)
#    association_rule = AssociationRule(df_media)

    # City Level
    # Friedrichshafen
#    df_FH = df_location[
#    (df_location['lat'] > 47.635) & (df_location['lat'] < 47.695) &
#    (df_location['lon'] > 9.4235) & (df_location['lon'] < 9.5224)]
#    df_FH['cluster'] = 0
#    Mapping(df_FH, 'Frid_o.html', 5, 17, [47.6512,9.4772])
#    df_FH = clusterizer.ClusterDBSCAN(df_FH, epsilon=0.025, min_sample=10)
#    Mapping(df_FH, 'Friedrichshafen_clustering.html', 5, 17, [47.6512,9.4772])
#    df_FH_media = Add_cluster(df_media, df_FH)
#    association_rule_FH = AssociationRule(df_FH_media,
#                                          'association_rules_FH',
#                                          min_support=0.004)

#   # Lindau
#    df_LD = df_location[
#    (df_location['lat'] > 47.541) & (df_location['lat'] < 47.574) &
#    (df_location['lon'] > 9.67) & (df_location['lon'] < 9.72)]
##    df_LD['cluster'] = 0
##    Mapping(df_LD, 'Lindau_o.html', 5, 16, [47.548, 9.688])
#    df_LD = clusterizer.ClusterDBSCAN(df_LD, epsilon=0.01, min_sample=5)
#    #0.025
#    Mapping(df_LD, 'Lindau_clustering_test.html', 5, 16, [47.548,9.688])
#    df_LD_media = Add_cluster(df_media, df_LD)
#    association_rule_LD = AssociationRule(df_LD_media,
#                                          'association_rules_LD',
#                                          min_support=0.004)

#    # different clustering method
    # DBSCAN
    df_location = clusterizer.ClusterDBSCAN(df_location)
    # NKMeans
    #df_location = clusterizer.ClusterNKMeans(df_location)
    #ClusterEvaluator(df_location)
    # popular cluster
    df_location = PopularClusterFilter(df_location)
    df_media = Add_cluster(df_media, df_location)
    df_media = PopularUploadFilter(df_media)

#    Mapping(df_location, file_name='DBSCAN_clustering.html')
    
    association_rule, rule_sum = AssociationRule(df_media)
    association_rule = PTest(association_rule, rule_sum)

    # Association Rule Mapping
    list = [1,3,8,15,
                    4,9,11,35,
                    2,5,18,24,29,49,6,
                    10,25]

    df_temp = df_location[df_location['cluster'].isin(list)]
    colors = [
        '#545454',
        '#0048BA',
        '#0D98BA',
        '#B0BF1A',
        '#B284BE',
        '#E52B50',
        '#FF7E00',
        '#C46210',
        '#FFBF00',
        '#C385A9',
        '#72A0C1',
        '#915C83',
        '#FF91AF',
        '#3D2B1F',
        '#8F6036',
        '#1B4D3E',
        '#E9D66B',
        '#F4C2C2',
        '#9C2542',
        '#8A2BE2',
        '#A2A2D0',
        '#AE841A'
    ]
    m = folium.Map(
        location=[47.6,9.4],
        zoom_start=10
    )
    m.add_child(folium.LatLngPopup())
    cluster_list = df_temp['cluster'].unique()
    for cluster_list_iter in cluster_list:
        df_cluster_temp = df_temp[df_temp['cluster']==cluster_list_iter]
        lon = df_cluster_temp['lon'].mean()
        lat = df_cluster_temp['lat'].mean()
        label = int(cluster_list_iter)
        folium.Circle(
            radius=400,
            location=[lat, lon],
            popup=str(label),
            color=colors[int(label % 21)],
            fill='black'
        ).add_to(m)
    m.save('Association_rule.html')
