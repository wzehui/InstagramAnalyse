import pandas as pd
from sqlalchemy import create_engine

#engine = create_engine('mysql+pymysql://root:4812@127.0.0.1/instagram')
#with engine.connect() as connection:
#    sql = 'SELECT id, edge_media_to_comment, edge_liked_by, taken_at_timestamp FROM media'
#    df = pd.read_sql_query(sql, connection)
#    df.to_csv('/home/zehui/PycharmProjects/InstagramAnalyse/media.csv', index=False)
#    print('Loading data finished!')

df = pd.read_csv('/home/zehui/PycharmProjects/InstagramAnalyse/media.csv', index_col=False)
df.dropna(subset=['taken_at_timestamp'], inplace=True)
df.taken_at_timestamp = pd.to_datetime(df.taken_at_timestamp, infer_datetime_format=True, errors='coerce')
daily_total = df.set_index('taken_at_timestamp').resample('D')['id'].agg('count')
