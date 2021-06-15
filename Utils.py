import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import openai
import re

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
                                          u"\U0001F600-\U0001F64F"  # emoticons
                                          u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                          u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                          u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                          u"\U00002702-\U000027B0"
                                          u"\U000024C2-\U0001F251"
                                          "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)


def detect_language(phase):
    OPENAI_API_KEY = 'sk-vNN45jeT8PUGFAKr1gbAniV4oy9W8XiNnvX3ZWBr'
    openai.api_key = OPENAI_API_KEY
    ans = openai.Answer.create(
        model="curie",
        documents=["ar", "de", "en", "ja", "ko", "nl", "ru"],
        question="What language is contained in this phase {}".format(phase),
        examples_context="This phase is written in German.",
        examples=[["What language is contained in this phase '🌹❤️😘   es ist "
                   "was es ist sagt die liebe❣' ","de"],
                  ["What language is contained in this phase 'sildipi thank "
                   "you so much🙏🙏'", "en"]
                  ],
        max_tokens=5,
        stop=["\n", "<|endoftext|>"]
    )
    return ans

if __name__ == '__main__':
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


