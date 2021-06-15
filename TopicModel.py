import pandas as pd
from langdetect import detect
import langid
from Utils import detect_language
from nltk.corpus import stopwords
import emoji
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import matplotlib.pyplot as plt


def language_processing():
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

if __name__ == '__main__':
    # language_processing()
    #%%
    path = '/Users/ze/Documents/PycharmProjects/Data/Instagram/'  # MacBookPro
    df = pd.read_csv(path + 'comment_modified.csv')
    df_language = pd.DataFrame()
    for index, item_iter in df.iterrows():
        df.loc[index, 'text'] = emoji.get_emoji_regexp().sub(u'', df.loc[
            index, 'text'])
        if item_iter.langdetect == 'unknown':
            df_language.loc[index, 0] = 'unknown'
        else:
            df_language.loc[index, 0] = item_iter.openai
    df = pd.concat([df, df_language], axis='columns', sort=False)
    df.columns = (['text', '1', '2', '3', 'language'])
    df_en = df[df['language']=='en']

    #%%
    stop_words = stopwords.words('english')
    # tokenization
    tokenized_doc = df_en['text'].apply(lambda x: x.split())
    # remove stop-words
    tokenized_doc = tokenized_doc.apply(
        lambda x: [item for item in x if item not in stop_words])
    # de-tokenization
    detokenized_doc = pd.DataFrame()
    for index, item_iter in tokenized_doc.iteritems():
        t = ' '.join(tokenized_doc.loc[index])
        detokenized_doc.loc[index, 0] =  t
    df_en = pd.concat([df_en, detokenized_doc], axis='columns', sort=False)
    df_en.rename(columns={0:'detokenized'}, inplace=True)

    #%%
    vectorizer = TfidfVectorizer(max_features=12000,  # keep top 1000 terms
                                 max_df=0.3,
                                 smooth_idf=True)
    X = vectorizer.fit_transform(df_en['detokenized'])

    # SVD represent documents and terms in vectors
    svd_model = TruncatedSVD(n_components=3, algorithm='randomized',
                             n_iter=100, random_state=5)
    svd_model.fit(X)

    terms = vectorizer.get_feature_names()
    for i, comp in enumerate(svd_model.components_):
        terms_comp = zip(terms, comp)
        sorted_terms = sorted(terms_comp, key= lambda x:x[1], reverse=True)[:7]
        print("Topic "+str(i)+": ")
        for t in sorted_terms:
            print(t[0])
            print(" ")

#    import umap.umap_ as umap
#
#    X_topics = svd_model.fit_transform(X)
#    embedding = umap.UMAP(n_neighbors=150, min_dist=0.5,
#                          random_state=12).fit_transform(X_topics)
#    plt.figure(figsize=(14, 10))
#    plt.scatter(embedding[:, 0], embedding[:, 1],
#                c=[0,1,2,3,4,5],
#                s=10,  # size
#                edgecolor='none'
#                )
#    plt.show()