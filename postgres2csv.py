import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://root:St_rsql1504!@127.0.0.1:3306/instagram')
with engine.connect() as connection:
    sql = 'SELECT id, owner_id, location_id, caption, edge_media_to_comment, edge_liked_by, taken_at_timestamp FROM media'
    df = pd.read_sql_query(sql, connection)
    print('Loading data finished!')
    df.dropna(how='any', subset=['owner_id', 'location_id'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df[['owner_id', 'location_id']] = df[['owner_id', 'location_id']].astype('int64')
    df[['id', 'owner_id', 'location_id']] = df[['id', 'owner_id', 'location_id']].astype(str)
    df[['edge_media_to_comment', 'edge_liked_by']] = df[['edge_media_to_comment', 'edge_liked_by']].astype(int)
    df['caption'] = df['caption'].astype(str)
    df['taken_at_timestamp'] = pd.to_datetime(df.taken_at_timestamp,
                                              infer_datetime_format=True,
                                              errors='coerce')
    df.to_csv('./media.csv', index = False)
