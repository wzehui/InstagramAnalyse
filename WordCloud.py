#导入wordcloud模块和matplotlib模块
from wordcloud import WordCloud,STOPWORDS,ImageColorGenerator
import matplotlib.pyplot as plt
from scipy import misc
import pandas as pd


df = pd.read_csv('/Users/ze/Documents/PycharmProjects/Data/Instagram/hashtags'
                 '.csv', index_col=False)
text = df[['name', 'media_count']].copy()
text['name'] = text['name'].astype('str')
#print(text.name)
#text_dict = text.to_dict()


## In[3]:
#
##使用背景图片制作词云图片
#'''
#mask : nd-array or None (default=None) //如果参数为空，则使用二维遮罩绘制词云。如果 mask 非空，设置的宽高值将被忽略，遮罩形状被 mask 取代。
#       除全白（#FFFFFF）的部分将不绘制，其余部分会都绘制词云。如：bg_pic = imread('读取一张图片.png')，背景图片画布一定要设置为白色（#FFFFFF）,
#       然后显示的形状为不是白色的其他颜色。可以用ps工具将自己要显示的形状复制到一个纯白色的画布上再保存，就ok了。
#background_color : color value (default=”black”) //背景颜色，如background_color='black',背景颜色为黑色。
#scale : float (default=1) //按照比例进行放大画布，如设置为1.5，则长和宽都是原来画布的1.5倍。
#generate(text)  //根据文本生成词云
#'''
##读入背景图片
#bg_pic = misc.imread('D:\\Python\\notebook\\love.jpg')
#
##生成词云
#wordcloud = WordCloud(mask=bg_pic,background_color='black',scale=1.5).generate_from_frequencies(text)
## 从背景图片生成颜色值
#image_colors = ImageColorGenerator(bg_pic)
#
##显示词云图片
#plt.imshow(wordcloud)
#plt.axis('off')
#plt.show()


# In[7]:

#不使用背景图片制作词云图
#生成词云
#text_dict = text.set_index('name').T.to_dict('list')
text_dict = {}
for index, item_iter in text.iterrows():
    text_dict[item_iter['name']] = item_iter.media_count
wc = WordCloud(width=800, height=400, max_words=200).fit_words(text_dict)
#wordcloud = WordCloud(background_color='black',scale=5).generate(text)

#显示词云图片
plt.imshow(wc)
plt.axis('off')
plt.show()
