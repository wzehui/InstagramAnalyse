import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import fpgrowth, association_rules


# import data from csv file
df = pd.read_csv('/Users/ze/Documents/PycharmProjects/Data/Instagram/media.csv')
df_location = pd.read_csv('/Users/ze/Documents/PycharmProjects/Data/Instagram'
                       '/locations.csv')
df_city = pd.read_csv('/Users/ze/Documents/PycharmProjects/Data/Instagram'
                      '/cities.csv')

# preprocessing
df_location.fillna(value={'city_id':0}, inplace=True)
df_location['city_id'] = df_location['city_id'].astype(int)

## write city_id from location into media
##df_filter = df[df.apply(lambda x: x.location_id.isin(df_location.id), axis=1)]
#a = df_location.id.unique()
#for index, item_iter in df.iterrows():
#    if item_iter.location_id in a:
#        df.loc[index, 'city_id'] = df_location[df_location.id
#                                               ==
#                                               item_iter.location_id].city_id.values[0]
#    else:
#        df.loc[index, 'city_id'] = 0
#        print(index)
#
df.dropna(how='any', subset=['location_id','owner_id'], inplace=True)
df.reset_index(inplace=True)
df = df[['id', 'location_id', 'owner_id', 'edge_media_to_comment',
    'edge_liked_by']].astype(int)

cleaned_df = df[df.groupby('location_id').location_id.transform('count')>60]
cleaned_df = cleaned_df[cleaned_df.groupby('owner_id').owner_id.transform(
    'count')>20].copy()

pivot_df = cleaned_df.pivot_table(index='owner_id', columns='location_id',
                                  values='id', aggfunc='count', fill_value=0)
pivot_df[pivot_df > 0] = 1

# Association Rules
frequent_itemsets = fpgrowth(pivot_df, min_support=0.004, use_colnames=True)
association_ruleset = association_rules(frequent_itemsets,
                                        metric='confidence', min_threshold=0.3)

# Results
association_ruleset_80 = association_ruleset[association_ruleset.confidence >
                                             0.8].copy()
association_ruleset_80.sort_values(by='confidence', ascending=False,
                                  inplace=True)

for index, item_iter in association_ruleset_80.iterrows():
    ante = list(item_iter.antecedents)
    for ante_iter in ante:
#        print(str(df_location[df_location.id == ante_iter].name.values[0]))
        location_ante = str(df_location[df_location.id ==
                                    ante_iter].name.values[0])
        print(location_ante)
    print('---->')
    cons = list(item_iter.consequents)
    for cons_iter in cons:
    #    print(str(df_location[df_location.id == cons_iter].name.values[0]))
        location_con = str(df_location[df_location.id ==
                                ante_iter].name.values[0])
        print(location_ante)
    print('\n')




