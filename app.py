import pandas as pd
import streamlit as st
import datetime
import gspread
from gspread_dataframe import set_with_dataframe
from datetime import datetime

st.set_page_config(
    layout="wide",
    page_title = 'Fut Iate',
    page_icon='https://www.icrj.com.br/iate/images/logo/logo60.png')
    
st.markdown("""
    <style>
    p {
        font-size:20px;
        place-items: center;

    }
    
    .st-af {
        font-size: 19px;
    }
    
    .css-10trblm.eqr7zpz0 {
        
        font-size:25px;
    }
    
    code {
        color: rgb(9, 171, 59);
        overflow-wrap: break-word;
        font-size: 20px;
    }   
    
    .stMarkdown {
    display: grid;
    place-items: center;
    }
    
    button{
        display: grid;
        place-items: center;
        
    }
    
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] {
        font-size:24px;
        text-align: center;
        place-items: center;

    }
    
    .css-q8sbsg.eqr7zpz4 {
        
        font-size:24px;
        text-align: center;
        place-items: center;
        
    }
    
    .css-10trblm.eqr7zpz0 {
        
        font-size:40px;
        text-align: center;
        place-items: center;
        
    }
    
    .css-3mmywe.e15ugz7a0 {
        
        place-items: center;
        align-content: center;
        
    }
    
    h2 {text-align: center;}
    </style>
    """, unsafe_allow_html=True)

service_account = "service-account-key.json"

def read_data(sheet = "Orçamento mensal", tab = "Transações"):
    
    gc = gspread.service_account(filename=service_account)

    sh = gc.open(sheet)    
    
    worksheet = sh.worksheet(tab)

    df = pd.DataFrame(worksheet.get_all_records())

    return(df)

dados = read_data(sheet = "Orçamento mensal", tab = "Transações")

dados['Mes'] = dados['Data'].apply(lambda x: datetime.strptime(x, "%d/%m/%Y").month)

mensal = dados.groupby('Mes').sum('Valor')
mensal.reset_index(inplace = True)

mensal.tail(1)['Mes'].values
st.metric(label = mensal.tail(1)['Mes'].values[0], value = mensal.tail(1)['Valor'].values[0], delta = mensal.tail(1)['Valor'].values[0] - mensal.tail(2).head(1)['Valor'].values[0])

