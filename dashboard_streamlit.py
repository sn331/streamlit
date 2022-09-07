# -*- coding: utf-8 -*-
"""Dashboard_Streamlit.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1d21RBQSDVZgEjpd_j0vnuWFE8lF_a4Sg
"""

import streamlit as st
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import statsmodels.api as sm
import matplotlib.pyplot as plt
from datetime import datetime as dt
import altair as alt
import pickle

st.set_page_config(layout="wide")
st.title('EG Group Sales Dashboard')
options = st.multiselect('Pick a category',
       ['Unleaded', 'Tobacco', 'Diesel', 'Instant Lottery', 'Drinks',
       'Chiller', 'Confectionary', 'Grocery Vat', 'Snacks VAT',
       'National Lottery', 'Grocery Zero', 'Paypoint', 'Car Care',
       'Super Unleaded', 'Hot Drinks Unit', 'E-Cig/Vaping',
       'News & Mags (Unit)', 'Sandwiches Unit', 'Feminine Hygiene',
       'Fruit & Veg', 'Merchant VAT', 'Motor Oil', 'Pumptop Promotions',
       'Greeting Cards', 'Domestic Fuel', 'Ice Cream', 'Non-Scan',
       'Phonecards Vat', 'Stamps', 'Stationery', 'AdBlue Pack', 'Flowers',
       'Maps', 'Toys', 'Unmapped Items', 'Paypoint PPOD',
       'Spare Shop Sales 22', 'Phonecard Commission', 'Pick & Mix',
       'Bakery Cold', 'Total'], default = 'Total')
start_date = '2022-06-30'
st.text('Start Date = ' + start_date)
end_date = st.date_input('Pick a end date')
days = (dt.strptime(str(end_date), "%Y-%m-%d") - dt.strptime(str(start_date), "%Y-%m-%d")).days

'''
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
  siteA_cat = pd.read_csv(uploaded_file)


siteA_cat = siteA_cat.drop(['TransactionLineID','ItemCode','ID', 'Heading'],axis=1,inplace= False)
siteA_cat['TransactionTime']= pd.to_datetime(siteA_cat['TransactionTime']).dt.date
siteA_cat['Sales'] = siteA_cat['Quantity'] * siteA_cat['UnitPrice']
siteA_cat= siteA_cat.drop(['Quantity', 'UnitPrice'],axis=1,inplace= False)

site_A_cat= pd.DataFrame()
for date in siteA_cat.TransactionTime.unique():
    df= siteA_cat[(siteA_cat.TransactionTime == date)]
    df= df.groupby(['Category','TransactionTime']).sum()
    site_A_cat= site_A_cat.append(df,ignore_index= False)

site_A_cat = site_A_cat.round(2)
site_A_cat= site_A_cat.reset_index()
site_A_cat= pd.pivot_table(site_A_cat,index= 'TransactionTime',columns= 'Category',fill_value= 0)
site_A_cat['GrandTotal']= site_A_cat[list(site_A_cat.columns)].sum(axis= 1)

df = pd.DataFrame()
for column in site_A_cat.columns:
    train = site_A_cat.loc[:, (slice(None), column)]
    model = sm.tsa.statespace.SARIMAX(train, order = (1,0,1), seasonal_order = (1,1,1,7),
                                enforce_stationarity = False, enforce_invertibility = False, freq = 'D').fit()

'''
file= 'C:\\Users\\nirol\\OneDrive\\Documents\\MSc\\Dissertation\\Models\\SiteA' + option + '.pkl'
    loaded_model= pickle.load(open(file,'rb'))

df = pd.DataFrame()
forecast = model.forecast(steps = days)
forecast.name = column[1]
df = df.append(forecast)
df = df.T
df.columns = [*df.columns[:-1], 'Total']

df['Month'] = df.index.month
df['Year'] = df.index.year

total_sales = df[options].sum()
st.write('Total Sales =', total_sales.values)

st.line_chart(df[options])

df = df.groupby(df.Month)[options].sum()
site_A_cat = site_A_cat.groupby(pd.to_datetime(site_A_cat.index).month).sum()
'''bar = alt.Chart(site_A_cat).mark_bar().encode(
    x = site_A_cat.index,
    y = site_A_cat.loc[:, (slice(None), column)]
)'''

st.bar_chart(df)
#st.altair_chart(bar)
