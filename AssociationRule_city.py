import folium
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from mlxtend.frequent_patterns import fpgrowth, association_rules

def cluster_dbscan(df):
    # Clustering
    coords = df[['lat','lon']]
    # Conduct DBSCAN Clustering
    kms_per_radian = 6371.0088
    epsilon = 1 / kms_per_radian
    clt = DBSCAN(eps=epsilon, min_samples=70, algorithm='ball_tree',
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


def map(df):
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
        location=[47.6, 9.4],
        zoom_start=30. #10,
    )
    m.add_child(folium.LatLngPopup())
    for index, item_iter in df.iterrows():
        lon = item_iter.lon
        lat = item_iter.lat
        label = item_iter.cluster
        folium.Circle(
            radius=5, #200,
            location=[lat, lon],
            popup=str(label),
            color=colors[int(label % 18)],
            fill='black'
        ).add_to(m)
    m.save('Bodensee.html')

def AssociationRule(df):
    pivot_df = df.pivot_table(index='owner_id', columns='cluster',
                                      values='id', aggfunc='count',
                                      fill_value=0)
    pivot_df[pivot_df > 0] = 1

    # Association Rules
    frequent_items = fpgrowth(pivot_df, min_support=0.004, use_colnames=True)
    association_ruleset = association_rules(frequent_items, metric='lift',
                                            min_threshold=1)

    # Results
    association_ruleset.sort_values(by='lift', ascending=False,
                                       inplace=True)
    return association_ruleset, pivot_df

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

if __name__ == '__main__':
    # %% Loading data from CSV-file
    path = '/Users/ze/Documents/PycharmProjects/Data/Instagram/'  # MacBookPro
    df = pd.read_csv(path + '/extended_locations.csv', usecols=[
        'id', 'name', 'lat', 'lon', 'edge_media_count'])

    # %% Data cleaning
    df = df[df['edge_media_count'] != 0]

    # %% Filter geographic data
    df = df[
        (df['lat'] > 47.35) & (df['lat'] < 47.9) & (df['lon'] > 8.65) & (
                df['lon'] < 9.9)]
    #%% Clustering
    df = cluster_dbscan(df)
    print('Number of filtered clushers: {}'.format(len(df.cluster.unique())))
    df.to_csv('./clustering.csv', index=False)

    #%% Visualisation
    map(df)

    #%% Loading data from CSV-file
    df = pd.read_csv(path + '/media_modified.csv', usecols=['id','owner_id',
                                                            'location_id',
                                                            'city_id'])
    
    df_cluster = pd.read_csv(path + '/clustering.csv')
    df_p = Add_cluster(df_cluster)
    # Filter：Ensure that each location and user has enough upload posts
    cleaned_df = df_p[
        df_p.groupby('location_id').location_id.transform('count') > 50]
    #cleaned_df = cleaned_df[cleaned_df.groupby('owner_id').owner_id.transform(
    #     'count') > 5].copy()
    association_rule, pivot_table = AssociationRule(cleaned_df)
