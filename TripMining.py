import pandas as pd
from AssociationRule import AssociationRule
from mlxtend.frequent_patterns import fpgrowth, association_rules

if __name__ == '__main__':
    # %% Loading data from CSV-file
    path = '/Users/ze/Documents/PycharmProjects/Data/Instagram/'  # MacBookPro
    df = pd.read_csv(path + 'media_modified.csv')
    df.drop(columns='Unnamed: 0', inplace=True)
    df['city_id'] = df['city_id'].astype('int64')
    df.drop(df[df['city_id'] == 0].index, inplace=True)
    df.reset_index(drop=True, inplace=True)

    df_city = pd.read_csv(path + '/cities.csv')
    df_city['id'] = df_city['id'].astype('int64')

    df_city_extended = pd.read_csv(path + '/extended_locations.csv')

    #%%
    cleaned_df = df[
        df.groupby('city_id').city_id.transform('count') > 60]
    cleaned_df = cleaned_df[cleaned_df.groupby('owner_id').owner_id.transform(
        'count') > 20].copy()

    pivot_df = cleaned_df.pivot_table(index='owner_id', columns='city_id',
                                      values='id', aggfunc='count',
                                      fill_value=0)
    pivot_df[pivot_df > 0] = 1

    #%% Association Rules
    frequent_items = fpgrowth(pivot_df, min_support=0.004, use_colnames=True)
    association_ruleset = association_rules(frequent_items, metric='lift',
                                            min_threshold=10)

    # Results
    association_ruleset.sort_values(by='lift', ascending=False,
                                    inplace=True)

    #%%
    for index, item_iter in association_ruleset.iterrows():
        ante = list(item_iter.antecedents)
        cons = list(item_iter.consequents)
        if len(ante) ==1 and len(cons) == 1:
            location_ante = df_city[df_city.id ==
                                        ante[0]].name.values[0]
            location_cons = str(df_city[df_city.id ==
                                            cons[0]].name.values[0])
            if location_ante == location_cons:
                pass
#           else:
#                amount_AB = pivot_df.shape[0] * item_iter.support
#                P_AB = item_iter['antecedent support'] * item_iter[
#                    'consequent support']
#                p = 1 - norm.cdf(amount_AB - 0.5, pivot_df.shape[0]*P_AB,
#                                 m.sqrt(pivot_df.shape[0]*P_AB*(1-P_AB)))
#                print('p-value: {}'.format(p))

            print('lift: {}, support: {}'.format(item_iter.lift,
                                                 item_iter.support))
            for ante_iter in ante:
                # print(str(df_location[df_location.id == ante_iter].name.values[0]))
                location_ante = str(df_city[df_city.id ==
                                                ante_iter].name.values[0])
                print(location_ante)
            print('---->')
            for cons_iter in cons:
                # print(str(df_location[df_location.id == cons_iter].name.values[0]))
                location_cons = str(df_city[df_city.id ==
                                                cons_iter].name.values[0])
                print(location_cons)
            print('\n')



