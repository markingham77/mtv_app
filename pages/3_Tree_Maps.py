import datetime
import streamlit as st
import plotly.express as px
import os
import pandas as pd
import numpy as np
import altair as alt
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from dateutil.parser import parse
from pathlib import Path
import pydqt
from pydqt import env_edit
from utils import load_sql_data,load_local_data, instantiate_initial_state, save_value, get_value
from streamlit_extras.app_logo import add_logo

st.set_page_config(page_title="Timeseries Data Viewer",layout="wide")
add_logo("mtv_logo_bw.png",height=90)

frequency_chosen = st.sidebar.selectbox("Frequency",['Annual','Monthly'])
if frequency_chosen == 'Annual':
    freq='year'
else:
    freq='month'    
orig_data=load_sql_data(freq)
# orig_data=load_local_data(freq)
data=orig_data.copy()

try:
    data['PURCHASE INTENTS']=data['SESSION_COUNT']*data['PI2SESSION_RATE']/100
except:
    data['PURCHASE INTENTS']=data['PI_COUNT']    
if 'CONVERSION_RATE' not in data.columns:
    data['CONVERSION_RATE'] = data['BUY2PI_RATE']
if 'PI2SESSION_RATE' not in data.columns:
    data['PI2SESSION_RATE'] = 100*data['PI_COUNT']/data['SESSION_COUNT']

new_columns=[]
for col in data.columns:
    if col == 'PI2SESSION_RATE':
        new_columns.append('Lead Generation Rate')
    elif col == 'CONVERSION_RATE':     
        new_columns.append('Track Conversion Rate')
    elif col == 'SESSION_COUNT':
        new_columns.append('SESSIONS')       
    elif col == 'ORDER_COUNT':
        new_columns.append('ORDERS')       
    else:
        new_columns.append(col)
data.columns=new_columns



st.markdown('''
    <h3>Tree Maps of Hierarchical Dimensions for Sessions, Purchase Intents and Orders</h3>
                        
            ''',unsafe_allow_html=True)


period_chosen = st.sidebar.selectbox("Period",data['PERIOD_DS'].unique())

# tab_cols = []
# for c in data.columns:
#     if 'COUNT' in c.upper():
#         tab_cols.append(c)        
tab_cols = ['SESSIONS','PURCHASE INTENTS', 'ORDERS']
tab_colours = ['Lead Generation Rate', 'Track Conversion Rate', 'AOV']

tabs = st.tabs(tab_cols)

for i,tab in enumerate(tabs):
    # tab.plotly_chart(fig, theme="streamlit", use_container_width=True)
    
    plot_df = data[(data[tab_cols[i]]>0) & (data['PERIOD_DS']==period_chosen)]
    
    # fixing color_chosen since if a cell is all zeros then renorming does not work (too many zeros in conversion_rate) 
    # color_chosen = 'LEAD_GEN_RATE'     
    plot_df[['REGION', 'TRAFFIC_SOURCE','LANDING_PAGE','USERSHIP']] = plot_df[['REGION', 'TRAFFIC_SOURCE','LANDING_PAGE','USERSHIP']].fillna('nan')
    q_low = plot_df[tab_colours[i]].quantile(0.05)
    q_high = plot_df[tab_colours[i]].quantile(0.95)
    plot_df[tab_colours[i]][plot_df[tab_colours[i]]<q_low]=q_low
    plot_df[tab_colours[i]][plot_df[tab_colours[i]]>q_high]=q_high
    
    fig = px.treemap(plot_df, path=[px.Constant("WORLD"), 'REGION', 'TRAFFIC_SOURCE','LANDING_PAGE','USERSHIP'],
                    values=tab_cols[i]
                    ,color=tab_colours[i]
                    ,color_continuous_scale='RdBu'
                    ,height=700
                #   ,color_continuous_midpoint=np.average(df[color_chosen], weights=df[col_chosen])
                )
    tab.plotly_chart(fig, use_container_width=True)