from mlxtend.frequent_patterns import fpgrowth, association_rules

def AssociationRule(df):
    # Filter
    cleaned_df = df[
        df.groupby('location_id').location_id.transform('count') > 60]
    cleaned_df = cleaned_df[cleaned_df.groupby('owner_id').owner_id.transform(
        'count') > 20].copy()

    pivot_df = cleaned_df.pivot_table(index='owner_id', columns='location_id',
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

