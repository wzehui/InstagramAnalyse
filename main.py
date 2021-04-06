'''
+---------------------------------------------------------------+
| Main function/script                                          |
+---------------------------------------------------------------+
------------------------------------------------------------------
Copyright: 2021 Wang,Zehui (wzehui@hotmail.com)
@author: Wang,Zehui
'''

import pandas as pd
from scipy.stats import norm
import math as m
from AssociationRule import AssociationRule

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    #%% Loading data from CSV-file
    path = '/Users/ze/Documents/PycharmProjects/Data/Instagram/'    # MacBookPro
    df = pd.read_csv(path + 'media_modified.csv')
    df_location = pd.read_csv(path + '/locations.csv')
    df_city = pd.read_csv(path + '/cities.csv')
    location_r = pd.read_csv(path + '/location_redundancy.csv')
    location_extended = pd.read_csv(path + '/extended_locations.csv')

    #%% Preprocessing
    #df.reset_index(drop=True, inplace=True)
    df.drop(columns='Unnamed: 0', inplace=True)
    df.taken_at_timestamp = pd.to_datetime(df.taken_at_timestamp,
                                           infer_datetime_format=True,
                                           errors='coerce')
    df['city_id'] = df['city_id'].astype('int64')
    #location_extended['city_id'] = location_extended['city_id'].astype('int64')
#    df.drop(columns=['Unnamed: 0','level_0','index'], inplace=True)
    # Remove redundenz from table with city_id
    for index, item_iter in location_r.iterrows():
        print(location_extended[location_extended['id'] == item_iter['id']].lat)
        print(location_extended[location_extended['id'] == item_iter['id']].lon)
        print(location_extended[location_extended['id'] == item_iter[
            'id_replaced']].lat)
        print(location_extended[location_extended['id'] == item_iter[
            'id_replaced']].lon)

#        df.loc[df['location_id'] == item_iter['id_replaced'], 'location_id']
##        = \#                    item_iter['id']
#        index += 1#
    #%% Association Rule
    association_ruleset, pivot_df = AssociationRule(df)
#    df_r = pd.DataFrame(columns=['id', 'id_replaced'], dtype='int64')
    # Showing results
    for index, item_iter in association_ruleset.iterrows():
        ante = list(item_iter.antecedents)
        cons = list(item_iter.consequents)
        if len(ante) ==1 and len(cons) == 1:
            location_ante = df_location[df_location.id ==
                                            ante[0]].name.values[0]
            location_cons = str(df_location[df_location.id ==
                                           cons[0]].name.values[0])
#            if location_ante == location_cons:
#                item_r = {'id':ante[0], 'id_replaced':cons[0]}
#                df_r = df_r.append(item_r, ignore_index=True)
#                print(ante[0],cons[0])
#            else:
#                amount_AB = pivot_df.shape[0] * item_iter.support
#                P_AB = item_iter['antecedent support'] * item_iter[
#                    'consequent support']
#                p = 1 - norm.cdf(amount_AB - 0.5, pivot_df.shape[0]*P_AB,
#                                 m.sqrt(pivot_df.shape[0]*P_AB*(1-P_AB)))
#                print('p-value: {}'.format(p))
            print('lift: {}, support: {}'.format(item_iter.lift,
                                                 item_iter.support))

#            df_r.to_csv(path + 'location_redundancy.csv', index=False)
#
            for ante_iter in ante:
                # print(str(df_location[df_location.id == ante_iter].name.values[0]))
                location_ante = str(df_location[df_location.id ==
                                                ante_iter].name.values[0])
                print(location_ante)
            print('---->')
            for cons_iter in cons:
                # print(str(df_location[df_location.id == cons_iter].name.values[0]))
                location_cons = str(df_location[df_location.id ==
                                               cons_iter].name.values[0])
                print(location_cons)
            print('\n')



