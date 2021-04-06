import pandas as pd
from scipy.stats import norm
import math as m
from mlxtend.frequent_patterns import fpgrowth, association_rules

dict = {'owner':['wang', 'zhang', 'li', 'zhao', 'qian', 'liu', 'ma'],
        'apple':[1, 0, 0, 1, 0, 0, 1],
        'banana':[1, 1, 0, 1, 0, 0, 1],
        'milk':[1, 0, 0, 0, 1, 0, 1],
        'cigarette':[0, 1, 1, 0, 0, 1, 0]
        }

df = pd.DataFrame(dict)
df.set_index('owner', inplace=True)
frequent_items = fpgrowth(df, min_support=0.004, use_colnames=True)
association_ruleset = association_rules(frequent_items, metric='lift',
                                        min_threshold=1)
for index, item_iter in association_ruleset.iterrows():
    ante = list(item_iter.antecedents)
    cons = list(item_iter.consequents)
    amount_AB = df.shape[0] * item_iter.support
    P_AB = item_iter['antecedent support'] * item_iter[
            'consequent support']
    p = 1 - norm.cdf(amount_AB - 0.5, df.shape[0] * P_AB,
                     m.sqrt(df.shape[0] * P_AB * (1 - P_AB)))
    print('p-value: {}'.format(p))
    print('lift: {}, support: {}'.format(item_iter.lift,
                                         item_iter.support))
    for ante_iter in ante:
            print(ante_iter)
    print('---->')
    for cons_iter in cons:
            print(cons_iter)
    print('\n')

