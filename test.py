import numpy as np
import pandas as pd
import os
import math
from AssociationRule import *
from sklearn.neighbors import NearestNeighbors

df_location = DataLoader('extended_locations.csv', ['id','lat','lon',
                                                    'edge_media_count'])
coords = df_location[['lat','lon']].copy()
coords.loc[:, ['heavy', 'outlier']] = [False, True]
n_outlier = 9975
z = n_outlier/161
#n = 8.449

neigh = NearestNeighbors(algorithm='ball_tree', metric='haversine')
neigh.fit(coords[['lat','lon']])

for n in np.linspace(0.0000001, 0.1, 19):
    print('n={}'.format(n))
    coords_copy = coords.copy()
    opt = math.pow(2, n)
    r = 2 * math.sqrt(opt/z)
    for index, item_iter in coords_copy.iterrows():
        rng = neigh.radius_neighbors([[item_iter.lat, item_iter.lon]], radius=r)
        if len(rng[1][0]) >= 2 * z:
            coords_copy.loc[index, 'heavy'] = True
    print(coords_copy[coords_copy['heavy']==True].heavy.sum())
    for index, item_iter in coords_copy.iterrows():
        rng = neigh.radius_neighbors([[item_iter.lat, item_iter.lon]], radius=r)
        for index_iter in rng[1][0]:
            if coords_copy.loc[index_iter, 'heavy'] == True:
                coords_copy.loc[index, 'outlier'] = False
                break
    print(coords_copy[coords_copy['outlier'] == True].outlier.sum())
    print('\n')
    #coords[coords['outlier']==True]

    #print(coords[coords['outlier']==True].outlier.sum())
#
#    if len(rng[1][0]) >= 2 * n_outlier:
#        coords.loc[index, 'status'] = 'heavy'
#    else:
#        coords.loc[index, 'status'] = 'light'
#
