# -*- coding: utf-8 -*-
"""InstagramAnalysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_80Y1uIcYWD0UDV57nDJpLw5noHEvVQe
"""

!pip install mlxtend
!pip install mlxtend --upgrade --no-deps

import os
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from mlxtend.frequent_patterns import fpgrowth, association_rules
from google.colab import drive

drive.mount('/content/drive')
path = '/content/drive/My Drive/InstagramAnalysis'
os.chdir(path)
os.listdir(path)

df = pd.read_csv('./media.csv')
df_location = pd.read_csv('./locations.csv')
df_city = pd.read_csv('./cities.csv')

df.dropna(subset=['taken_at_timestamp'], inplace=True)
df.reset_index(inplace=True)
df['taken_at_timestamp'] = pd.to_datetime(df.taken_at_timestamp, infer_datetime_format=True, errors='coerce')

monthly_total = df.set_index('taken_at_timestamp').resample(rule='W').id.agg('count')
monthly_likes = df.set_index('taken_at_timestamp').resample(rule='W').edge_liked_by.agg('sum')
monthly_comment = df.set_index('taken_at_timestamp').resample(rule='W').edge_media_to_comment.agg('sum')
monthly_interactions = (monthly_likes + monthly_comment) / monthly_total
monthly = pd.concat([monthly_total, monthly_interactions], axis='columns', sort=False)
monthly.columns = ['total', 'interaction']
monthly.reset_index(inplace=True)
monthly.rename(columns={'taken_at_timestamp':'Jahre'}, inplace=True)

scale = int(monthly.total.mean() / monthly.interaction.mean())
monthly['interaction'] = monthly['interaction'] * scale

sns.set(style='whitegrid')
fig, ax1 = plt.subplots(figsize=(20,5))
sns.lineplot(data=monthly, x='Jahre', y='total', ax=ax1)
sns.lineplot(data=monthly, x='Jahre', y='interaction', ax=ax1)
ax2 = ax1.twinx()
ax2.set_ylabel('Interaction')
ax2.set_ylim(ax1.get_ylim())
ax2.set_yticklabels(np.around(ax1.get_yticks()/scale))
ax1.set_ylabel('Beiträge')
#fig.savefig('chart.png', dpi=1000, bbox_inches='tight')
plt.show()

df.dropna(how='any', subset=['location_id','owner_id'], inplace=True)
df.reset_index(inplace=True)
df[['location_id', 'owner_id', 'edge_media_to_comment', 'edge_liked_by']] = df[['location_id', 'owner_id', 'edge_media_to_comment', 'edge_liked_by']].astype(int)

df_location.fillna(value={'city_id':0}, inplace=True)
df_location['city_id'] = df_location['city_id'].astype(int)

cleaned_df = df[df.groupby('location_id').location_id.transform('count')>60]
cleaned_df = cleaned_df[cleaned_df.groupby('owner_id').owner_id.transform('count')>20].copy()

pivot_df = cleaned_df.pivot_table(index='owner_id', columns='location_id', values='id', aggfunc='count', fill_value=0)
pivot_df[pivot_df > 0 ] = 1

frequent_itemsets = fpgrowth(pivot_df, min_support=0.004, use_colnames=True)
association_rulesets = association_rules(frequent_itemsets, metric='confidence', min_threshold=0.3)

association_rulesets_80 = association_rulesets[association_rulesets.confidence>0.8].copy()
association_rulesets_80.sort_values(by='confidence', ascending=False, inplace=True)

for index, item_iter in association_rulesets_80.iterrows():
  ante = list(item_iter.antecedents)
  for ante_iter in ante:
    location_ante = str(df_location[df_location.id == ante_iter].name.values[0])
    print(location_ante)
  print('---->')
  cons = list(item_iter.consequents)
  for cons_iter in cons:
    location_con = str(df_location[df_location.id == ante_iter].name.values[0])
    print(location_ante)
  print('\n')

a = df_location.id.unique()
for index, item_iter in cleaned_df.iterrows():
  if item_iter.location_id in a:
    city_id = df_location[df_location.id==item_iter.location_id].city_id.values[0]
    cleaned_df.loc[index, 'city_id'] = city_id