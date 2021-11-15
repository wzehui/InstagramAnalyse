import numpy as np
import pandas as pd
import os
import math
from main import *
from sklearn.neighbors import NearestNeighbors
from random import sample
from numpy.random import uniform
from math import isnan
from scipy.stats import norm
from folium import plugins

df_location = DataLoader('extended_locations.csv', ['id','name','lat','lon',
                                                    'edge_media_count'])
df_media = DataLoader('media.csv', ['id', 'owner_id', 'location_id',
                                    'city_id'], '\n')
#coords = df_location[['lat','lon']].copy()
# Data cleaning
df_location = df_location[df_location['edge_media_count'] != 0]
# Filter geographic data
df_location = df_location[
#   Lindau
#    (df_location['lat'] > 47.541) & (df_location['lat'] < 47.574) &
#    (df_location['lon'] > 9.67) & (df_location['lon'] < 9.72)]

#   Friedrichshafen
    (df_location['lat'] > 47.647) & (df_location['lat'] < 47.682) &
    (df_location['lon'] > 9.432) & (df_location['lon'] < 9.513)]

df_location.reset_index(drop=True, inplace=True)

location_list = df_location['id']
df_temp = df_media[df_media['location_id'].isin(location_list)]

removed_location_list = [8910588, 1020672814677428, 1911327119158595,
                        826320607563842, 1026852966, 291854334575332,
                        319993314, 340029014, 554464482, 656730639,
                         745753206, 498668146, 1016366432, 106548726049781,
                         882168810, 795625046, 1029899866, 495869686,
                         728626810638673, 215810778, 1920680334832721,
                         249850711, 283233702, 742921502, 258058728,
                         1838822329701516, 283592214, 302154749, 890817203,
                         1304289372918251, 537075581, 264016784031,
                         103119069727734, 112193418796736, 147304635313360,
                         236306456, 236612924, 245491436, 254229250,
                         257213855, 260715934, 266545024, 282600071,
                         311506629, 338125840, 374219538, 548599148,
                         595568243, 655130395, 713373045, 718879000,
                         743836349, 751679402, 930875617, 162282951276059,
                         199672943378650]
removed_location = pd.DataFrame(columns=['id','name'])
removed_location['name'] = df_location[df_location['id'].isin(
    removed_location_list)].name
#removed_location['id'] = removed_location_list


df_location = df_location[df_location['edge_media_count'] >= 10]
df_location = df_location[~df_location['id'].isin(removed_location_list)]

clusterizer = Clusterizer()
df_location = clusterizer.ClusterDBSCAN(df_location, epsilon=0.04,
                                        min_sample=3)
#df_location = clusterizer.ClusterNKMeans(df_location, n_clusters=27)
ClusterEvaluator(df_location)

Mapping(df_location, 'Friedrichshafen_clustering.html', 5, 17, [47.6512,9.4772])
df_temp = Add_cluster(df_media, df_location)
association_rule_FH, rule_sum = AssociationRule(df_temp, 'association_FH',
                                      min_support=0.001)
association_rule_FH = PTest(association_rule_FH, rule_sum)

association_rule_FH.sort_values(by='lift', ascending=False,
                                inplace=True)
association_rule_FH.to_csv(os.path.join(
    '/Users/ze/Documents/PycharmProjects/Data/Instagram/',
    'association_rule_FR'), index=False)
#pivot_df = df_temp.pivot_table(index='owner_id', columns='location_id',
#                          values='id', aggfunc='count',
#                          fill_value=0)
#pivot_df[pivot_df > 0] = 1

#m = folium.Map(
#    location=[47.548,9.688],
#    zoom_start=6
#)
#heat_data = [[row['lat'], row['lon'], row['edge_media_count']] for index,
#                                                                   row in
#             df_location.iterrows()]
#m.add_child(plugins.HeatMap(heat_data, radius=15))
#m.save('test.html')

# Association Rules
#frequent_items = fpgrowth(pivot_df, min_support=0.004, use_colnames=True)
#association_ruleset = association_rules(frequent_items, metric='lift',
#                                        min_threshold=1)
## Results
#association_ruleset.sort_values(by='lift', ascending=False,
#                                inplace=True)

# Association Rule Mapping
list = [0,5,10,11,
        4,15,
        3,
        2,
        1,
        19,
        13,6,
        7,4,]

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
color_icon = ['red', 'blue', 'green', 'purple', 'orange', 'darkred',
             'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
             'darkpurple', 'pink', 'lightblue', 'lightgreen',
             'gray', 'black', 'lightgray']


m = folium.Map(
    location=[47.6, 9.4],
    zoom_start=14
)
m.add_child(folium.LatLngPopup())
cluster_list = df_temp['cluster'].unique()
for cluster_list_iter in cluster_list:
    df_cluster_temp = df_temp[df_temp['cluster'] == cluster_list_iter]
    lon = df_cluster_temp['lon'].mean()
    lat = df_cluster_temp['lat'].mean()
    label = int(cluster_list_iter)

    #   draw a circle marker
    folium.Circle(
            radius=30,
            location=[lat, lon],
            popup=str(label),
            color=colors[int(label % 21)],
            fill=True,
            fill_color = colors[int(label % 21)]
        ).add_to(m)

    # draw a coin marker
    #folium.Marker(
    #        location=[lat, lon],
    #        popup=str(label),
    #        icon=folium.Icon(color=colors[int(label % 18)], icon="users"),
    #    ).add_to(m)

    m.save('Association_rule_FH_test.html')
