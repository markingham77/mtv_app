# mark.ingham@ly.st
# BI_AND_ANALYTICS

import sqlparse
import snowflake.connector
import streamlit as st
import os
import pandas as pd
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import re

# dqt-lite
@st.cache_resource()
def py_connect_db(login=None, role=None, warehouse = None) -> snowflake.connector.connection.SnowflakeConnection:
    """connect to snowflake, credentials will be set in sidebar of app and the saved to state"""

    if login==None:
        if "login" in st.session_state:
            login=st.session_state['login']
    else:
        login=login.upper()
        st.session_state.login = login
    assert login!=None, "login has not been specified and is not in session_state"
    

    if role==None:
        if "role" in st.session_state:
            role=st.session_state['role']
    else:
        role=role.upper()
        st.session_state.role = role
    assert role!=None, "role has not been specified and is not in session_state"

    if warehouse==None:
        if "warehouse" not in st.session_state:
            warehouse = f"{role}_QUERY_LARGE_WH"
        else:
            warehouse = st.session_state.warehouse
    else:
        st.session_state['warehouse'] = warehouse                   


    return snowflake.connector.connect(
        account="fs67922.eu-west-1",
        user=login.upper(),
        authenticator="externalbrowser",
        database="LYST",
        schema="LYST_ANALYTCS",
        role=role.upper(),
        warehouse=warehouse,
        client_session_keep_alive=True,
    );

def compile(template='timeseries.sql',*args,**kwargs):
    """
    creates sql queries by injecting into template
    or takes a string query and substitues params
    """
    template_dir = os.path.join(str(Path(__file__).parents[0]),'templates/')
    environment = Environment(loader=FileSystemLoader([
        template_dir,
    ]))
    if 'select' in template.lower():
        s=template
        if len(args)>0:
            for i,arg in enumerate(args):
                s=s.replace(f'${1+i}',arg)
        
        pattern = r'macros\.[\w]+\('
        r=re.search(pattern,s)

        if ('{%' in s) or (r!=None):
            filename = str(uuid.uuid4()) + '.sql'
            full_filename = os.path.join(template_dir,filename) 
            if (r!=None):
                s = "{% import 'macros.jinja' as macros %}\n" + s

            with open(full_filename, 'w+') as f:
                f.write(s)
            template = environment.get_template(filename)
            os.remove(full_filename)

            rendered_str = template.render(kwargs)
            pattern = '\'[A-Za-z0-9_.-\/]+\.csv\''
            m=re.findall(pattern, rendered_str)
            if len(m)>0:
                rendered_str=rendered_str.replace(m[0],f'read_csv_auto({m[0]}, header=true)')
            return rendered_str
        else:
            for key,val in kwargs.items():
                s=s.replace('{{' + key + '}}',val)
            rendered_str=s                
            pattern = '\'[A-Za-z0-9_.-\/]+\.csv\''
            m=re.findall(pattern, rendered_str)
            if len(m)>0:
                rendered_str=rendered_str.replace(m[0],f'read_csv_auto({m[0]}, header=true)')    
            return rendered_str
    else:
        template = environment.get_template(template)
        rendered_str = template.render(kwargs)
        pattern = '\'[A-Za-z0-9_.-\/]+\.csv\''
        m=re.findall(pattern, rendered_str)
        if len(m)>0:
            rendered_str=rendered_str.replace(m[0],f'read_csv_auto({m[0]}, header=true)')    
        return rendered_str

@st.cache_data(persist="disk")
def load_sql_data(freq='month'):
    key = f'data_{freq}'
    compiled_sql=compile("timeseries.sql", freq=freq)
    conn = py_connect_db()
    df = pd.read_sql(compiled_sql, conn)
    # explode split_values
    cols = df['SPLITS'].values[0].split(',')
    df[cols] = df['SPLIT_VALUES'].str.split(',',expand=True)
    columns = ['PERIOD_DS'] +  cols + ['METRIC','VALUE']
    df = df[columns]
    df = df.set_index(['PERIOD_DS'] +  cols)
    df = df.pivot(columns='METRIC',values='VALUE').reset_index()
    df.columns.name=''
    columns = df.columns
    new_columns=[]
    for c in columns:
        if c=='BUY2PI_RATE':
            new_columns.append('CONVERSION_RATE')
        elif c=='PI2SESSION_RATE':
            new_columns.append('LEAD_GEN_RATE')
        else:
            new_columns.append(c)
    df.columns = new_columns       
    df['PI_COUNT'] = df['LEAD_GEN_RATE']*df['SESSION_COUNT']/100
    df.columns.name=''
    return df
