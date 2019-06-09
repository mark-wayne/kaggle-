import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
#%matplotlib inline
import json
import warnings
warnings.filterwarnings('ignore')
 
import seaborn as sns
sns.set(color_codes=True)
 
#设置表格用什么字体
font = {
    'family' : 'SimHei'
}
matplotlib.rc('font', **font)#设置图表字体



 
##导入数据##
movies = pd.read_csv('tmdb_5000_movies.csv')
creditss = pd.read_csv('tmdb_5000_credits.csv')
 
#查看movies中数据
print(movies.head())
 
#查看movies中所有列名，以字典形式存储
print(movies.columns)
 
##查看creditss中数据
print(creditss.head())
 
#查看creditss中所有列名，以字典形式存储,一共4个列名
print(creditss.columns)
 
#两个数据框中的title列重复了，删除credits中的title列，还剩3个列名
del creditss['title'] 
 
#movies中的id列与credits中的movie_id列实际上等同，可当做主键合并数据框
full = pd.merge(movies, creditss, left_on='id', right_on='movie_id', how='left')
 
#某些列不在本次研究范围，将其删除
full.drop(['homepage','original_title','overview','spoken_languages',
           'status','tagline','movie_id'],axis=1,inplace=True)
 
#查看数据信息，每个字段数据量。
print(full.info())






###清洗数据###

print(full.isnull().any())#找到缺失数据的对象

print(full.loc[full['release_date'].isnull()==True])#找到‘release_date’的缺失数据所在地
full['release_date'] = full['release_date'].fillna('2014-06-01')

print(full.loc[full['runtime'].isnull()==True])
full['runtime'] = full['runtime'].fillna(94, limit=1)#limit=1，限制每次只填补一个值
full['runtime'] = full['runtime'].fillna(240, limit=1)#分两次准确填写缺失值

full['release_date'] = pd.to_datetime(full['release_date'], 
    format='%Y-%m-%d', errors='coerce').dt.year#规范日期数据的格式

json_column = ['genres','keywords','production_companies',
               'production_countries','cast','crew']#建立要转化格式的对象列表
for column in json_column:
    full[column]=full[column].map(json.loads)
    #json格式转化为字典表格 json.loads
    #将其他格式转化为json格式，则json.dumps
       
def getname(x):
    list = []
    for i in x:
        list.append(i['name'])
    return '|'.join(list)#将字典内的‘name’对应的值取出来


for column in json_column[0:4]:
    full[column] = full[column].map(getname)
    #对面列表json_column前4个的元素调用getname函数

def getcharacter(x):
    list = []
    for i in x:
        list.append(i['character'])
    return '|'.join(list[0:2])#定义获取主演的函数，在演员名单中的前两位

full['cast']=full['cast'].map(getcharacter)#在演员栏中使用getcharacter函数

def getdirector(x):
    list=[]
    for i in x:
        if i['job']=='Director':
            list.append(i['name'])
    return "|".join(list)#定义获取导演名单的函数

full['crew']=full['crew'].map(getdirector)#在工作人员栏中调用getcharacter函数
rename_dict = {'release_date':'year','cast':'actor','crew':'director'}#定义字典，准备将标签重命名
full.rename(columns=rename_dict, inplace=True)#rename函数进行重命名，并且永久修改
print(full.head(2))#查看表头前2行核对

original_df = full.copy()#备份数据，copy()
print(full)



##数据可视化##

genre_set = set()   #设置空集合
for x in full['genres']:
    genre_set.update(x.split('|'))  #genres数据以'|'来分隔
genre_set.discard('')  #删除''字符
print(genre_set)

genre_df = pd.DataFrame()  # 创建空的数据框架
for genre in genre_set:
    genre_df[genre] = full['genres'].str.contains(genre).map(lambda x:1 if x else 0)
    #如果一个电影类型在整个数据中出现一次，
    #则统计为1，否则为0。一部电影所属类型

genre_df['year']=full['year']#将原数据‘year’添加到数据框中
genre_by_year = genre_df.groupby('year').sum()#某一年某一个电影类型的数量
genresum_by_year = genre_by_year.sum().sort_values(ascending=False)#所有电影中的类型总数量


fig = plt.figure(figsize=(15,11))   #设置画图框的大小
ax = plt.subplot(1,1,1)     #设置框的位置
ax = genresum_by_year.plot.bar()#绘制电影数量随年份的变化图
plt.xticks(rotation=60)#x轴标签旋转60（标签名称多的时候需要）
plt.title('各类电影数量总和', fontsize=18)    #设置标题的字体大小，标题名
plt.xlabel('类型', fontsize=18)    #X轴名及轴名大小
plt.ylabel('数量', fontsize=18)    #y轴名及轴名大小
plt.show()  #可以用查看数据画的图。
#保存图片
fig.savefig('各类电影总数量1.png',dpi=600)


##筛选电影风格前Top8##

genre_by_year = genre_by_year[['Drama','Comedy','Thriller','Romance',
                               'Adventure','Crime', 'Science Fiction',
                               'Horror']].loc[1960:,:]
year_min = full['year'].min()   #最小年份
year_max = full['year'].max()   #最大年份

fig = plt.figure(figsize=(10,8))
ax1 = plt.subplot(1,1,1)
plt.plot(genre_by_year)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Film count', fontsize=12)
plt.title('Film count by year', fontsize=15)
plt.xticks(range(1960, 2017, 10))  #横坐标每隔10年一个刻度
plt.legend(['Drama(戏剧类)','Comedy(喜剧类)','Thriller(惊悚类)','Romance(浪漫类)',
                               'Adventure(Adventure)','Crime(犯罪类)', 'Science Fiction(科幻类)',
                               'Horror(惊恐类)'], loc='best',ncol=2) #设置说明标签
plt.show()
fig.savefig('film count by year2.png',dpi=600)


###不同风格电影的收益能力##
full['profit'] = full['revenue']-full['budget']#票房减去预算等于收益
profit_df = pd.DataFrame()#创建空的数据框
profit_df = pd.concat([genre_df.iloc[: ,:-1], full['profit']], axis=1)  #合并
print(profit_df.head())#查看新数据框信息


profit_by_genre = pd.Series(index=genre_set)
for genre in genre_set:
    profit_by_genre.loc[genre]=profit_df.loc[:,[genre,'profit']].groupby(genre, as_index=False).sum().loc[1,'profit']
print(profit_by_genre)#每一种电影类型都计算一下收益

budget_df = pd.concat([genre_df.iloc[:,:-1],full['budget']],axis=1)
print(budget_df.head(2))
budget_by_genre = pd.Series(index=genre_set)
for genre in genre_set:
    budget_by_genre.loc[genre]=budget_df.loc[:,[genre,'budget']].groupby(genre,as_index=False).sum().loc[1,'budget']
print(budget_by_genre)#计算总预算

profit_rate = pd.concat([profit_by_genre, budget_by_genre],axis=1)#计算收益率
profit_rate.columns=['profit','budget']   #更改列名


profit_rate['profit_rate'] = (profit_rate['profit']/profit_rate['budget'])*100
profit_rate.sort_values(by=['profit','profit_rate'], ascending=False, inplace=True)
print(profit_rate)

x = list(range(len(profit_rate.index)))


fig = plt.figure(figsize=(18,13))
ax1 = fig.add_subplot(111)
plt.bar(x, profit_rate['profit'],label='profit',alpha=0.7)
plt.xticks(rotation=60, fontsize=12)
plt.yticks(fontsize=12)
ax1.set_title('Profit by genres', fontsize=20)
ax1.set_ylabel('Film Profit',fontsize=18)
ax1.set_xlabel('Genre',fontsize=18)
ax1.set_ylim(0,1.2e11)#设置刻度
ax1.legend(loc=2,fontsize=15)


import matplotlib.ticker as mtick#纵坐标设置显示百分比
ax2 = ax1.twinx()
ax2.plot(x, profit_rate['profit_rate'],'ro-',lw=2,label='profit_rate')
fmt='%.2f%%'
yticks = mtick.FormatStrFormatter(fmt)
ax2.yaxis.set_major_formatter(yticks)
plt.xticks(fontsize=12,rotation=60)
plt.yticks(fontsize=15)
ax2.set_ylabel('Profit_rate',fontsize=18)
ax2.legend(loc=1,fontsize=15)
plt.grid(False)#关闭背景网格线
plt.show()
#保存图片
fig.savefig('profit by genres3.png', dpi=600)



##公司收益对比##

company_list = ['Universal Pictures', 'Paramount Pictures']
company_df = pd.DataFrame()
for company in company_list:
    company_df[company]=full['production_companies'].str.contains(company).map(lambda x:1 if x else 0)
company_df = pd.concat([company_df,genre_df.iloc[:,:-1],full['revenue']],axis=1)
#统计两公司的电影数量和票房收益


Uni_vs_Para = pd.DataFrame(index=['Universal Pictures', 'Paramount Pictures'],
                           columns=company_df.columns[2:])#

Uni_vs_Para.loc['Universal Pictures']=company_df.groupby('Universal Pictures',
               as_index=False).sum().iloc[1,2:]

Uni_vs_Para.loc['Paramount Pictures']=company_df.groupby('Paramount Pictures',
               as_index=False).sum().iloc[1,2:]
#构建两个公司的数据框架，包含影片数量和票房收益
fig = plt.figure(figsize=(4,3))
ax = fig.add_subplot(111)
Uni_vs_Para['revenue'].plot(ax=ax,kind='bar')
plt.xticks(rotation=0)
plt.title('Universal VS. Paramount')
plt.ylabel('Revenue')
plt.show()
fig.savefig('Universal vs Paramount by revenue4.png', dpi=600)
#两家公司的收益比较：Universal 比 Paramoun 高

Uni_vs_Para = Uni_vs_Para.T

universal = Uni_vs_Para['Universal Pictures'].iloc[:-1]
paramount = Uni_vs_Para['Paramount Pictures'].iloc[:-1]

universal['others']=universal.sort_values(ascending=False).iloc[8:].sum()
universal = universal.sort_values(ascending=True).iloc[-9:]

paramount['others']=paramount.sort_values(ascending=False).iloc[8:].sum()
paramount = paramount.sort_values(ascending=True).iloc[-9:]

fig = plt.figure(figsize=(13,6))
ax1 = plt.subplot(1,2,1)
ax1 = plt.pie(universal, labels=universal.index, autopct='%.2f%%',startangle=90,pctdistance=0.75)
plt.title('Universal Pictures',fontsize=15)
 
ax2 = plt.subplot(1,2,2)
ax2 = plt.pie(paramount, labels=paramount.index, autopct='%.2f%%',startangle=90,pctdistance=0.75)
plt.title('Paramount Pictures',fontsize=15)
plt.show()
fig.savefig('Universal vs Paramount5.png', dpi=600)
#两个公司各类影片数量占比


##票房相关性##
print(full[['runtime','popularity','vote_average',
      'vote_count','budget','revenue']].corr())
#受欢迎度和票房相关性：0.64
#评价次数和票房相关性：0.78
#电影预算和票房相关性：0.73

revenue = full[['popularity','vote_count','budget','revenue']]


fig = plt.figure(figsize=(17,5))
ax1 = plt.subplot(1,3,1)
ax1 = sns.regplot(x='popularity', y='revenue', data=revenue, x_jitter=.1)
ax1.text(400,2e9,'r=0.64',fontsize=15)
plt.title('revenue by popularity',fontsize=15)
plt.xlabel('popularity',fontsize=13)
plt.ylabel('revenue',fontsize=13)
 
ax2 = plt.subplot(1,3,2)
ax2 = sns.regplot(x='vote_count', y='revenue', data=revenue, x_jitter=.1,color='g',marker='+')
ax2.text(6800,1.1e9,'r=0.78',fontsize=15)
plt.title('revenue by vote_count',fontsize=15)
plt.xlabel('vote_count',fontsize=13)
plt.ylabel('revenue',fontsize=13)
 
ax3 = plt.subplot(1,3,3)
ax3 = sns.regplot(x='budget', y='revenue', data=revenue, x_jitter=.1,color='r',marker='^')
ax3.text(1.6e8,2.2e9,'r=0.73',fontsize=15)
plt.title('revenue by budget',fontsize=15)
plt.xlabel('budget',fontsize=13)
plt.ylabel('revenue',fontsize=13)
fig.savefig('revenue6.png', dpi=600)
plt.show()
