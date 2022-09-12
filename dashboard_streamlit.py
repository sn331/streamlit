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
st.title('EG Group Sales Dashboard (SITE A)')

start_date = '2022-06-30'
st.sidebar.text_input('Start Date (Fixed)', value = start_date)
end_date = st.sidebar.date_input('Pick an end date')
days = (dt.strptime(str(end_date), "%Y-%m-%d") - dt.strptime(str(start_date), "%Y-%m-%d")).days

options = st.sidebar.multiselect('Pick a category',
       ['Unleaded', 'Tobacco', 'Diesel', 'Drinks',
       'Chiller', 'Confectionary', 'Snacks VAT',
       'Grocery Zero', 'Hot Drinks Unit', 'E-Cig/Vaping',
       'News & Mags (Unit)', 'Total'], default = 'Total')



uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
  siteA_cat = pd.read_csv(uploaded_file)

@st.cache(allow_output_mutation=True, ttl=24*3600)
def fetch_and_clean_data(siteA_cat):
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
        site_A_cat['Total']= site_A_cat[list(site_A_cat.columns)].sum(axis= 1)
        
        df = pd.DataFrame()
        for column in site_A_cat.columns:
            train = site_A_cat.loc[:, (slice(None), column)]
            model = sm.tsa.statespace.SARIMAX(train, order = (1,0,1), seasonal_order = (1,1,1,7),
                                        enforce_stationarity = False, enforce_invertibility = False, freq = 'D').fit()
            forecast = model.forecast(steps = days)
            forecast.name = column[1]
            df = df.append(forecast)
        df = df.T
        df.columns = [*df.columns[:-1], 'Total']

        df['Month'] = df.index.month
        df['Year'] = df.index.year
        df['quarter'] = pd.PeriodIndex(df.index, freq='Q')
        df['Period'] = df.index.to_period('M')
        return site_A_cat, df

site_A_cat, df = fetch_and_clean_data(siteA_cat)

total_sales = df[options].sum()
#st.write('Total Sales =', total_sales.values)
st.metric(label="Total Sales", value=int(total_sales.sum()))

st.subheader('Daily Sales Forecast')
st.line_chart(df[options])

df_cat = df.groupby(['quarter'])[options].sum()

st.subheader('Quarterly Sales Forecast')
st.bar_chart(df_cat)

site_A_cat['Month'] = pd.DatetimeIndex(site_A_cat.index).month
site_A_cat['Year'] = pd.DatetimeIndex(site_A_cat.index).year
site_A_cat['quarter'] = pd.PeriodIndex(site_A_cat.index, freq='Q')
site_A_cat.index = pd.to_datetime(site_A_cat.index)
site_A_cat['Period'] = site_A_cat.index.to_period('M')

site_A_cat_2020 = site_A_cat[site_A_cat.loc[:, 'Year'] == 2020]
site_A_cat_2020= site_A_cat_2020.groupby(['Month']).sum()
site_A_cat_2020 = site_A_cat_2020.reset_index()

site_A_cat_2021 = site_A_cat[site_A_cat.loc[:, 'Year'] == 2021]
site_A_cat_2021= site_A_cat_2021.groupby(['Month']).sum()
site_A_cat_2021 = site_A_cat_2021.reset_index()

df_2022 = df[df['Year'] == 2022]
df_2022= df_2022.groupby(['Month']).sum()
df_2022 = df_2022.reset_index()

df_2023 = df[df['Year'] == 2023]
df_2023= df_2023.groupby(['Month']).sum()
df_2023 = df_2023.reset_index()

st.subheader('Year-on-Year Sales Comparison')
for i in options:
    plt.clf()
    if i == 'Total':
        plt.bar(site_A_cat_2020['Month'], site_A_cat_2020[i].squeeze(), 0.2, alpha = 0.8, label = i + ' (2020)')
        plt.bar(site_A_cat_2021['Month'] + 0.2, site_A_cat_2021[i].squeeze(), 0.2, alpha = 0.8, label = i +' (2021)')
        plt.bar(df_2022['Month'] + 0.4, df_2022[i].squeeze(), 0.2, alpha = 0.8, label='Forecast (2022)')
        plt.bar(df_2023['Month'] + 0.6, df_2023[i].squeeze(), 0.2, alpha = 0.8, label='Forecast (2023)')
    else:
        plt.bar(site_A_cat_2020['Month'], site_A_cat_2020.loc[:, (slice(None), i)].squeeze(), 0.2, alpha = 0.8, label = i + ' (2020)')
        plt.bar(site_A_cat_2021['Month'] + 0.2, site_A_cat_2021.loc[:, (slice(None), i)].squeeze(), 0.2, alpha = 0.8, label = i +' (2021)')
        plt.bar(df_2022['Month'] + 0.4, df_2022[i].squeeze(), 0.2, alpha = 0.8, label='Forecast (2022)')
        plt.bar(df_2023['Month'] + 0.6, df_2023[i].squeeze(), 0.2, alpha = 0.8, label='Forecast (2023)')
    ax = plt.subplot(111)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title('Monthly Sales Comparison')
    plt.xlabel('Month')
    plt.ylabel('Sales')
    plt.show()
    st.pyplot(ax.figure)
