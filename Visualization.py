import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# import data from csv file
df = pd.read_csv('/Users/ze/Documents/PycharmProjects/Data/Instagram/media'
                 '.csv', index_col=False)


# Preprocessing
df.dropna(subset=['taken_at_timestamp'], inplace=True)
df.taken_at_timestamp = pd.to_datetime(df.taken_at_timestamp,
                                       infer_datetime_format=True, errors='coerce')
#daily_total = df.set_index('taken_at_timestamp').resample('D')['id'].agg(
# 'count')
monthly_total = df.set_index('taken_at_timestamp').resample(rule='W').id.agg(
    'count')
monthly_likes = df.set_index('taken_at_timestamp').resample(
    rule='W').edge_liked_by.agg('sum')
monthly_comment = df.set_index('taken_at_timestamp').resample(
    rule='W').edge_media_to_comment.agg('sum')
monthly_interactions = (monthly_likes + monthly_comment) / monthly_total
monthly = pd.concat([monthly_total, monthly_interactions], axis='columns',
                    sort=False)
monthly.columns = ['total', 'interaction']

# Plot
sns.set(style='whitegrid')
fig = sns.relplot(data=monthly, kind='line')
#fig.savefig('chart.png', dpi=1000, bbox_inches='tight')
plt.show()


