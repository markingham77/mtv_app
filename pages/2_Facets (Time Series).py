import datetime
import streamlit as st
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
from utils import load_sql_data, load_local_data, instantiate_initial_state, save_value, get_value
from streamlit_extras.app_logo import add_logo
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Timeseries Data Viewer",layout="wide")
add_logo("mtv_logo_bw.png",height=90)
width = streamlit_js_eval(js_expressions='screen.width', key = 'SCR')
if "grid_plot_width" not in st.session_state:
    if width<1600:
        st.session_state.grid_plot_width = 500
    else:    
        st.session_state.grid_plot_width = 0.5*width


# st.title('Multi-Dimensional Data Viewer (MD<sup>2</sup>V)')
st.markdown('''
    <h3>Facet plots of various metrics through time across specfied dimensions</h3>
                        
            ''',unsafe_allow_html=True)

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False
    




categorical_columns=[]
quantitative_columns=[]
date_columns=[]
other_columns=[]
# @st.cache_data(persist="disk")
# def load_sql_data(freq='month'):
#     """
#     loads data via 'teimseries.sql' tempalte and tben expands the comma-delimited
#     lists of splits and split_values (one coloumn for each split)
#     """

#     q = pydqt.Query(f'''
#     select * from core_wip.timeseries_{freq}
#     join core_wip.timeseries_lookup
#     using (series_id)
#     ;
#     ''')
#     try:
#         q.load()
#     except:
#         env_edit()    
#         q.load()
#     cols = q.df['SPLITS'].values[0].split(',')
#     df=q.df
#     df[cols] = q.df['SPLIT_VALUES'].str.split(',',expand=True)
#     columns = ['PERIOD_DS'] +  cols + ['METRIC','VALUE']
#     df = df[columns]
#     df = df.set_index(['PERIOD_DS'] +  cols)
#     df = df.pivot(columns='METRIC',values='VALUE').reset_index()
#     df.columns.name=''
#     # df.to_csv(loc,index=False)
#     columns = df.columns
#     new_columns=[]
#     for c in columns:
#         if c=='BUY2PI_RATE':
#             new_columns.append('CONVERSION_RATE')
#         elif c=='PI2SESSION_RATE':
#             new_columns.append('LEAD_GEN_RATE')
#         else:
#             new_columns.append(c)
#     df.columns = new_columns       
#     df['PI_COUNT'] = df['LEAD_GEN_RATE']*df['SESSION_COUNT']/100
#     df.columns.name=''
#     return df

# @st.cache_data
data=load_sql_data()


column_type_df = pd.DataFrame(columns=['Field', 'Date', 'Categorical', 'Quantitative', 'Other'])
for c in column_type_df.columns:
    column_type_df[c] = column_type_df[c].astype('bool')
column_type_df['Field'] = column_type_df['Field'].astype('str')    
i=0    
for column in data.columns:
    nunique = data[column].nunique()
    cardinality = nunique/data.shape[0]
    if column.upper() in ['DAY','MONTH','YEAR','DATE']:
        date_columns.append(column)
        column_type_df.loc[i] = [column, True, False, False, False]
    elif is_numeric_dtype(data[column]):
        quantitative_columns.append(column)
        column_type_df.loc[i] = [column, False, False, True, False]
    elif is_datetime64_any_dtype(data[column]):
        date_columns.append(column)
        column_type_df.loc[i] = [column, True, False, False, False]
    else:
        col_data = data[column][data[column]!='NaN']
        col_data = col_data[pd.notna(col_data)]
        if type(col_data.iloc[0])==str:
            if is_date(col_data.iloc[0]):
                # st.write(f'{column} here A')
                date_columns.append(column)
                column_type_df.loc[i] = [column, True, False, False, False]
            else:
                if is_categorical_dtype(data[column]) or nunique < 10 or cardinality<0.3:
                    categorical_columns.append(column)
                    column_type_df.loc[i] = [column, False, True, False, False]
                else:
                    other_columns.append(column)
                    column_type_df.loc[i] = [column, False, False, False, True]
        else:
            if type(col_data.iloc[0])==datetime.date:
                date_columns.append(column)
                column_type_df.loc[i] = [column, True, False, False, False]
            else:
                other_columns.append(column)   
                column_type_df.loc[i] = [column, False, False, False, True]
    i+=1
column_type_df = column_type_df.set_index('Field')    
splits = categorical_columns
    

def rot(x):
    """
    roatates a list by 1
    """
    return x[1:] + x[:1]


categorical = date_columns + [x.upper() for x in splits]
quantitative = quantitative_columns

# with st.sidebar.expander('Field categories'):
#     st.data_editor(column_type_df)

# x_item = st.sidebar.selectbox(
#     "X-Axis Item",
#     date_columns + quantitative
# )
x_item='PERIOD_DS'
remaining_categories = [x for x in categorical if x != x_item]
row = st.sidebar.selectbox(
    "Rows",
    remaining_categories,
    key='sidebar-rows'
)
filter_row_values=data[row].unique()
include_rows = st.sidebar.expander(label="Include Rows",expanded=False).multiselect(
    "",
    filter_row_values,
    default=filter_row_values,
    key='sidebar-include-rows'
)
if len(include_rows)>0:
    data = data[data[row].isin(include_rows)]

remaining_categories=rot(remaining_categories)
column = st.sidebar.selectbox(
    "Columns",
    remaining_categories,
    key='sidebar-columns'
)
filter_column_values = data[column].unique()
include_columns = st.sidebar.expander(label="Include Columns",expanded=False).multiselect(
    "",
    filter_column_values,
    default=filter_column_values,
    key='sidebar-include-columns'
)
if len(include_columns)>0:
    data = data[data[column].isin(include_columns)]
    
remaining_categories=rot(remaining_categories)
color = st.sidebar.selectbox(
    "Colour",
    remaining_categories,
    key='sidebar-colours'
)
filter_color_values = data[color].unique()
include_colors = st.sidebar.expander(label="Include Colours",expanded=False).multiselect(
    "",
    filter_color_values,
    default=filter_color_values
)
if len(include_colors)>0:
    data = data[data[color].isin(include_colors)]

# color_ex_nan = st.sidebar.checkbox(f'exclude NaNs',key='colour')
# if color_ex_nan:
#     data = data[~data[color].isna()]
#     data = data[data[column]!='NaN']
#     data = data[data[color]!='nan']

remaining_categories=rot(remaining_categories)

remaining_dims = [x for x in categorical if x not in [x_item, color, row,column]]
# st.write(data.columns)
remaining_dim_values=[]
for dim in remaining_dims:
    x = st.sidebar.selectbox(
        f'{dim}',
        [x for x in data[dim].unique()] + ['All']
    )
    if x!='All':
        data = data[data[dim]==x]
    remaining_dim_values.append(x)

chart_type = st.sidebar.selectbox('Chart Type',['line', 'stacked bar', 'scatter'])
tabs = st.tabs(quantitative)

if "button" not in st.session_state:
    st.session_state.button = True

# write a function for toggle functionality
def toggle():
    if st.session_state.button:
        st.session_state.button = False
    else:
        st.session_state.button = True

# with st.expander('expander', expanded=st.session_state.button):
#     st.write('Hello!')

# the actual plots
total_facets_width=st.session_state.grid_plot_width
total_facets_height=420
facet_width = total_facets_width/len(include_columns)
facet_height = total_facets_height/len(include_rows)

if "single_facet_plot_row_index" not in st.session_state:
    st.session_state.single_facet_plot_row_index = 0
    # single facet plot selectbox callbacks
def row_change_callback(item='',selection=[]):
    if item !='' and len(selection)>0:
        st.session_state.single_facet_plot_row_index = selection.index(st.session_state[f'{item}-row-zoom'])
    st.write('ere',item,st.session_state.single_facet_plot_row_index)


detailed_plot_expander = st.sidebar.expander(label="Detailed Plot",expanded=True)
detailed_plot_expander.button("Toggle Grid Plot", on_click=toggle)
col1,col2 = detailed_plot_expander.columns(2)
row_zoom = col1.selectbox(row,data[row].unique().tolist())
# key = f'{y_item}-col-zoom'
column_zoom = col2.selectbox(column,data[column].unique())

for i,tab in enumerate(tabs):
    y_item=quantitative[i]
    ymin = data[y_item].dropna().min()
    ymax = data[y_item].dropna().max()

    y_q10 = data[y_item].dropna().quantile(0.01)
    y_q90 = data[y_item].dropna().quantile(0.99)

    multi_facet_container = tab.expander(label='Grid Plot',expanded=st.session_state.button)
    selection = alt.selection_point(fields=[color], bind='legend')
    if chart_type != 'stacked bar':
        key = f'{y_item}-yaxis-slider'

        # yaxis_slider = tab.slider('Y-Axis Limits',min_value=ymin, max_value=ymax, value=(ymin,ymax), key=key)            
        yaxis_slider = multi_facet_container.slider('Y-Axis Limits',min_value=ymin, max_value=ymax, value=(y_q10,y_q90), key=key)                    

        data.loc[data[y_item]<=yaxis_slider[0],y_item]=np.nan
        data.loc[data[y_item]>=yaxis_slider[1],y_item]=np.nan
        dom = [yaxis_slider[0], yaxis_slider[1]]
    if chart_type == 'stacked bar':
        chart = alt.Chart(data).mark_bar()
        dom = [ymin, ymax]    
    elif chart_type == 'line':
        chart = alt.Chart(data).mark_line()                
    elif chart_type == 'scatter':
        chart = alt.Chart(data).mark_circle()                

    c = chart.encode(
        alt.X(x_item + ':O',axis=alt.Axis(tickSize=0, labelFontSize=0, grid=False)).title(''),
        alt.Y(f'{y_item}:Q', scale=alt.Scale(domain=dom)).title(''),
        # alt.Y(f'{y_item}:Q').title(''),
        color=color,
        tooltip = [x_item,y_item,color],
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    ).properties(
        width=facet_width,
        height=facet_height
    ).facet(
        column=f'{column}:N',
        row=f'{row}:N',
        # title=facet_expander
    ).add_params(
        selection
    )
    # tab.subheader(y_item)
    # tab.altair_chart(c, use_container_width=True)
    multi_facet_container.subheader(y_item)
    multi_facet_container.altair_chart(c, use_container_width=True)

    

    tab.markdown('<h5>Single Facet Plot</h5>',unsafe_allow_html=True)
    row_col, col_col = tab.columns(2)
    key = f'{y_item}-row-zoom'
    row_selections = data[row].unique().tolist()
    
    # set session state for row and col zoom for given y_item
    key0=f'{y_item}-row-zoom'
    if key0 not in st.session_state:
        st.session_state[key0] = row_selections[0]

    # st.write('single_facet_plot_row_index before',st.session_state.single_facet_plot_row_index)
    # row_zoom = row_col.selectbox(row,row_selections,key=key, index=st.session_state.single_facet_plot_row_index, on_change=row_change_callback(item=y_item, selection=row_selections))
    # st.write('single_facet_plot_row_index after',st.session_state.single_facet_plot_row_index)
    # st.write(st.session_state.single_facet_plot_row_index)
    
    selection = alt.selection_point(fields=[color], bind='legend')
    zoom_data = data
    if chart_type == 'stacked bar':
        zoom_chart = alt.Chart(data[(data[column]==column_zoom) & (data[row]==row_zoom)]).mark_bar().properties(title=f'{y_item} of {row_zoom} and {column_zoom}')           
    elif chart_type == 'line':
        zoom_chart = alt.Chart(data[(data[column]==column_zoom) & (data[row]==row_zoom)]).mark_line(point=True).properties(title=f'{y_item} of {row_zoom} and {column_zoom}')           
    elif chart_type == 'scatter':
        zoom_chart = alt.Chart(data[(data[column]==column_zoom) & (data[row]==row_zoom)]).mark_circle().properties(title=f'{y_item} of {row_zoom} and {column_zoom}')           

    # zoom_chart.configure_title(anchor="middle",align="center").configure_point(size=1000)
    zoom_c = zoom_chart.encode(
        alt.X(x_item + ':T',axis=alt.Axis(grid=True)).title(''),
        alt.Y(f'{y_item}:Q').title(y_item),
        color=color,
        tooltip = [x_item,y_item,color],
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    ).add_params(
        selection
    )
    tab.altair_chart(zoom_c, use_container_width=True)


        