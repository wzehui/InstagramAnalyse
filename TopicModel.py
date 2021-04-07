import pandas as pd
from langdetect import detect
import langid
from Utils import detect_language


path = '/Users/ze/Documents/PycharmProjects/Data/Instagram/'  # MacBookPro
df = pd.read_csv(path + 'comment.csv', nrows=10)

df_text = df['text'].str.replace('[’·°–!"#$%&\'()*+,'
                                 '-./:;<=>?@，。?★、…【】（）《》？“”‘’！[\\]^_`{|}~]+',
                                 " ", regex=True)
#df_text = df_text.apply(lambda x: ' '.join([w for w in x.split() if len(w)>3]))
df_text = df_text.apply(lambda x: x.lower())

df_language_1 = pd.DataFrame()
df_language_2 = pd.DataFrame()
df_language_openai = pd.DataFrame()

for index, item_iter in df_text.iteritems():
    #df_text.iloc[index] = deEmojify(item_iter)
    try:
        lg = detect(item_iter)
    except:
        lg = 'unknown'
    df_language_1.loc[index, 0] = lg

    try:
        lg = langid.classify(item_iter)
    except:
        lg = 'unknown'
    df_language_2.loc[index, 0] = lg[0]

    lg = detect_language(item_iter)
    df_language_openai.loc[index, 0] = lg['answers'][0]

df_text = pd.concat([df_text, df_language_1, df_language_2,
                     df_language_openai], axis='columns', sort=False)
df_text.columns = (['text', 'langdetect', 'langid', 'openai'])

#for index, item_iter in df_text.iterrows():
#    lg = detect_language(item_iter.text)
#    df_language_openai.loc[index, 0] = lg['answers'][0]
#df_text = pd.concat([df_text, df_language_openai], axis='columns', sort=False)
#df_text.columns = (['text', 'language', 'language_ai'])
