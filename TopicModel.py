import pandas as pd
import re
from langdetect import detect
from LanguageDetect import detect_language

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
                                          u"\U0001F600-\U0001F64F"  # emoticons
                                          u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                          u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                          u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                          "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

path = '/Users/ze/Documents/PycharmProjects/Data/Instagram/'  # MacBookPro
df = pd.read_csv(path + 'comment.csv', nrows=999)

df_text = df['text'].str.replace('[’·°–!"#$%&\'()*+,'
                                 '-./:;<=>?@，。?★、…【】（）《》？“”‘’！[\\]^_`{|}~]+',
                                 " ", regex=True)
#df_text = df_text.apply(lambda x: ' '.join([w for w in x.split() if len(w)>3]))
df_text = df_text.apply(lambda x: x.lower())

df_language = pd.DataFrame()
for index, item_iter in df_text.iteritems():
    #df_text.iloc[index] = deEmojify(item_iter)
    try:
        lg = detect(item_iter)
    except:
        lg = 'unknown'
    df_language.loc[index, 0] = lg
df_text = pd.concat([df_text, df_language], axis='columns', sort=False)
df_text.columns = (['text', 'language'])

df_language_openai = pd.DataFrame()
for index, item_iter in df_text.iterrows():
    lg = detect_language(item_iter.text)
    df_language_openai.loc[index, 0] = lg['answers'][0]
df_text = pd.concat([df_text, df_language_openai], axis='columns', sort=False)
df_text.columns = (['text', 'language', 'language_ai'])
