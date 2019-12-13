import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import pandas as pd
import time
import math
import warnings
warnings.filterwarnings("ignore")


df_ori = pd.read_csv('ecom_products.csv')
df = df_ori.reindex(columns=['name','price','quantity','qpcascade','catname','subcatname','link'])
totalprod = len(df)

start_time = time.time()
print('Scraping Started at', time.ctime())
savestr = ''
for index, row in df.iterrows():
    if type(df['name'][index]) != str:
        res = requests.get(row['link'])
        if(res.status_code==200):
            soup = BeautifulSoup(res.text, 'html.parser')
            itemname = soup.findAll('h1',{'class': 'page-title'})[0].findChild().text
            try:
                itemprice = soup.findAll('span',{'class': 'price'})[0].text
            except IndexError:
                itemprice = 'null'
            try:
                itemqty = soup.findAll('input',{'class': 'input-text qty'})[0]['value'] if len(soup.findAll('input',{'class': 'input-text qty'}))>=1 else soup.findAll('span',{'class': 'tier-select-qty'})[0].text
            except IndexError:
                itemqty = 'null'
            try:
                t2 = ''
                for node in soup.findAll('tr',{'class': 'item'}):
                    t = ('_'.join(node.findAll(text=True)))
                    for i,c in enumerate(t):
                        if(c=='%'):
                            t = t[:i-1]+t[i:]
                    t = t.replace(' ','').replace('_',' ')[1:].replace(' - ','-').replace('  ','').replace(' +','+')
                    t2 += t+' | '
                itemcascade = t2
            except IndexError:
                itemcascade = 'null'            
            df['name'][index]=itemname
            df['price'][index]=itemprice
            df['quantity'][index]=itemqty
            df['qpcascade'][index]=itemcascade

        else:
            df['name'][index]='null E'+str(res.status_code)
            df['price'][index]='null'
            df['quantity'][index]='null'
            df['qpcascade'][index]='null'
            print('NullError',res.status_code,row['link'])
        
        if(index % 100==0): #CHECKPOINT
            df.to_csv('ecom_products.csv')
            savestr = '| saved till #{}'.format(index)

    print('[{}/{}] Product Pages Scraped {}'.format(index+1,totalprod,savestr), end='\r')


df.to_csv('ecom_products_final.csv',index=False)
print('Scraping Complete at', time.ctime())
print('Time Elapsed: ', time.strftime("%H hrs %M mins %S secs", time.gmtime(time.time() - start_time)))
