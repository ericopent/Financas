import pandas as pd
import streamlit as st
import datetime
import gspread
from gspread_dataframe import set_with_dataframe
from datetime import datetime

st.set_page_config(
    layout="wide",
    page_title = 'Finanças',
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
dados['Data'] = pd.to_datetime(dados['Data'], format="%d/%m/%Y")

# Create a new column 'Group' to represent the date ranges
def assign_date_range(date):
    if date.day >= 30:
        start_date = date.replace(day=30)
        end_date = (start_date + pd.DateOffset(months=1)).replace(day=29)
    else:
        end_date = date.replace(day=29)
        start_date = (end_date - pd.DateOffset(months=1)).replace(day=30)
    return f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"

dados['Group'] = dados['Data'].apply(assign_date_range)

mensal = dados.groupby('Group')['Valor'].sum().reset_index()

mensal['Mes'] = mensal['Group'].apply(lambda x: pd.to_datetime(x.split('-')[1]).month)
dados['Mes'] = dados['Group'].apply(lambda x: pd.to_datetime(x.split('-')[1]).month)

meses = {
    1:'Janeiro',
    2:'Fevereiro',
    3:'Março',
    4:'Abril',
    5: 'Maio',
    6: 'Junho',
    7: 'Julho',
    8: 'Agosto',
    9:'Setembro',
    10: 'Outubro',
    11: 'Novembro',
    12: 'Dezembro'    
}

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label = meses[mensal.tail(3).head(1)['Mes'].values[0]], value = round(mensal.tail(3).head(1)['Valor'].values[0],0), delta = round(mensal.tail(3).head(1)['Valor'].values[0] - mensal.tail(4).head(1)['Valor'].values[0],0))
with col2:
    st.metric(label = meses[mensal.tail(2).head(1)['Mes'].values[0]], value = round(mensal.tail(2).head(1)['Valor'].values[0],0), delta = round(mensal.tail(2).head(1)['Valor'].values[0] - mensal.tail(3).head(1)['Valor'].values[0],0))
with col3:
    st.metric(label = meses[mensal.tail(1)['Mes'].values[0]], value = round(mensal.tail(1)['Valor'].values[0],0), delta = round(mensal.tail(1)['Valor'].values[0] - mensal.tail(2).head(1)['Valor'].values[0],0))

dici = read_data(sheet = "Orçamento mensal", tab = "DePara")
dici.columns = ['Descrição', 'Categoria']

db = pd.merge(dados, dici, on = 'Descrição')

db = db.groupby(['Mes','Categoria']).sum('Valor')

import plotly.express as px

# Assuming you have the data grouped as 'db' with the structure you mentioned.

fig = px.bar(db.reset_index(), x='Mes', y='Valor', color='Categoria',
             labels={'Mes': 'Mês', 'Valor': 'Valor', 'Categoria': 'Categoria'},
             title='Monthly Expenses by Category',
             category_orders={'Mes': sorted(db.index.get_level_values(0).unique())})

fig.update_layout(xaxis_type='category')  # Ensure x-axis is treated as categorical

st.plotly_chart(fig)
