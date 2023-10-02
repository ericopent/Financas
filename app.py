import pandas as pd
import streamlit as st
import datetime
import gspread
from gspread_dataframe import set_with_dataframe
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

def read_data(sheet = "FutIate", tab = "Ranking"):
    
    gc = gspread.service_account(filename=service_account)

    sh = gc.open(sheet)    
    
    worksheet = sh.worksheet(tab)

    df = pd.DataFrame(worksheet.get_all_records())

    return(df)

def write_data (dados, data, nome, gols, assists, presença, sheet = "FutIate", tab = "Ranking"):
    
    df = [{
        
        'DATA': data,
        'NOME': nome,
        'GOLS': gols,
        'ASSISTÊNCIAS': assists,
        'PRESENÇA': presença
    }]
    
    gc = gspread.service_account(filename=service_account)

    sh = gc.open(sheet)    
    
    worksheet = sh.worksheet(tab)
    
    df = pd.DataFrame(df)    
    
    db = pd.concat([dados, df])
    db['DATA'] = pd.to_datetime(db['DATA'])
    
    db['DATA'] = db['DATA'].apply(lambda x: x.strftime("%d/%m/%Y"))
    
    set_with_dataframe(worksheet, db)
    # pd.concat([dados, df])
    return()

dados = read_data(sheet = "FutIate", tab = "Ranking").drop_duplicates(subset=['DATA', 'NOME'], keep = 'last')

dados['DATA'] = pd.to_datetime(dados['DATA'])

st.markdown(
    "# Fut Iate :crown: :trophy:"
)

def stable_matching(ranking):
    team_size = 5
    players = ranking['Nome'].tolist()
    scores = ranking['Score'].tolist()
    
    n = len(players)
    proposals = [-1] * n
    engaged = [-1] * n
    preferences = {players[i]: [(scores[i], i) for i in range(n)] for i in range(n)}
    
    while -1 in engaged:
        free_player = engaged.index(-1)
        for _, preferred_player_idx in preferences[players[free_player]]:
            if proposals[preferred_player_idx] == -1:
                engaged[free_player] = preferred_player_idx
                proposals[preferred_player_idx] = free_player
                break
            else:
                current_partner_idx = proposals[preferred_player_idx]
                if preferences[players[preferred_player_idx]].index((scores[free_player], free_player)) < preferences[players[preferred_player_idx]].index((scores[current_partner_idx], current_partner_idx)):
                    engaged[free_player] = preferred_player_idx
                    proposals[preferred_player_idx] = free_player
                    engaged[current_partner_idx] = -1
                    break
            
    teams = []
    substitutes = []
    
    for i in range(0, n, team_size):
        
        team_players = players[i:i+team_size]
        
        if len(team_players) < team_size:
            substitutes.extend(team_players)
        else:
            teams.append(team_players)
    
    st.markdown(f"**Time 1: {' | '.join(teams[0])}**")
    st.markdown(f"**Time 2: {' | '.join(teams[1])}**")
    st.markdown(f"**Substitutos: {' | '.join(substitutes)}**")
    return teams, substitutes
    
import random

def form_random_teams_with_substitutes(ranking):
    
    team_size = 5
    players = ranking['Nome'].tolist()
    
    random.shuffle(players)  # Shuffle the list of players randomly
    num_teams = len(players) // team_size
    teams = [players[i:i+team_size] for i in range(0, len(players), team_size)]
    substitutes = players[num_teams * team_size:]  # Any remaining players are substitutes

    st.markdown(f"**Time 1: {' | '.join(teams[0])}**")
    st.markdown(f"**Time 2: {' | '.join(teams[1])}**")
    st.markdown(f"**Substitutos: {' | '.join(substitutes)}**")

    return teams, substitutes

def head2head(dados, person1, person2, metrica):
    
    person1_db = dados[dados['NOME'] == person1]
    person2_db = dados[dados['NOME'] == person2]
    
    person2_ratio = person2_db[metrica].sum()/person2_db.PRESENÇA.sum()
    person1_ratio = person1_db[metrica].sum()/person2_db.PRESENÇA.sum()

    if (person2_ratio < person1_ratio):
        st.markdown(f"**{metrica.title()}:\n {person1.title()} | {person1_db[metrica].sum()} {metrica} em {person1_db['PRESENÇA'].sum()} dia(s) :crown:**")

    elif (person2_ratio > person1_ratio):
        st.markdown(f"**{metrica.title()}:\n {person2.title()} | {person2_db[metrica].sum()} {metrica} em {person2_db['PRESENÇA'].sum()} dia(s) :crown:**")

    elif (person2_ratio == person1_ratio):
        st.markdown(f"**{metrica.title()}:\n EMPATE**")

def RankingTotal (dados, pesoGols, pesoAssists, pesoPresença):
    
    
    if(pesoGols + pesoAssists + pesoPresença != 1):
        st.error('Pesos não somam 1')
    else:
        
        result = dados.groupby('NOME').apply(lambda x: x.GOLS.sum()*pesoGols + x.PRESENÇA.sum()*pesoPresença + x.ASSISTÊNCIAS.sum()*pesoAssists).sort_values(ascending=False)
        
        result = result.to_frame().reset_index()
        
        result.columns = ['NOME', 'Score']
        
        result = pd.merge(dados.groupby('NOME').sum(['GOLS', 'ASSISTÊNCIAS', 'PRESENÇA']), result, on='NOME')

        def format_score(score):
            return f"{score:.2f}"

        result.sort_values('Score', inplace=True, ascending=False)
        result.reset_index(inplace = True, drop=True)
        result['Posição'] = result['Score'].rank(method='min', ascending=False).astype(int)
        result = result[['NOME', 'GOLS', 'ASSISTÊNCIAS', 'PRESENÇA', 'Score', 'Posição']]
        
        result.columns = ['Nome', 'Gols', 'Assistências', 'Presença','Score', 'Posição']
        result['Score'] = result['Score'].apply(lambda x: round(x, 2))  
        view = result.style.hide(axis="index")
        
        view.set_table_styles([
        {'selector': "th", 'props': [("font-weight", "bold"), ("text-transform", "capitalize")]},])
        
        view.format(lambda x: f"<i title='tooltip'>{x}</i>", 'Posição')
            
        st.markdown(view.to_html(), unsafe_allow_html=True)
        return(result)

def RankingMes (dados, pesoGols, pesoAssists, pesoPresença):
    
    
    if(pesoGols + pesoAssists + pesoPresença != 1):
        st.error('Pesos não somam 1')
    else:
                
        dados['MONTH'] = dados['DATA'].dt.month

        unique_months = dados['MONTH'].unique()

        result = []  
        
        for month in unique_months:
            data_for_month = dados[dados['MONTH'] == month]
            
            result_for_month = data_for_month.groupby('NOME').apply(lambda x: x.GOLS.sum() * pesoGols + x.PRESENÇA.sum() * pesoPresença + x.ASSISTÊNCIAS.sum() * pesoAssists)
            
            sorted_result_for_month = result_for_month.sort_values(ascending=False).reset_index().reset_index()     
            sorted_result_for_month.columns = ['Posição', 'Nome', 'Score']
            
            meses = {1: 'Janeiro',
             2: 'Fevereiro',
             3: 'Março',
             4: 'Abril',
             5: 'Maio',
             6: 'Junho',
             7: 'Julho',
             8: 'Agosto',
             9: 'Setembro',
             10: 'Outubro',
             11: 'Novembro',
             12: 'Dezembro'}
            
            
            sorted_result_for_month['Mês'] = meses[month]
            sorted_result_for_month['Posição'] = sorted_result_for_month['Posição']+1
            sorted_result_for_month = sorted_result_for_month[['Mês', 'Nome', 'Posição']]
            result.append(sorted_result_for_month)
        
        resultados = pd.concat(result)   
        
        nNomes = len(resultados['Nome'].unique())
        resultados = resultados.pivot(index='Nome', columns='Mês', values='Posição')
        
        resultados['Max'] = resultados.apply(lambda x: max(x))
        
        for column in resultados.columns:
            resultados['Max'] = nNomes
            resultados[column] = resultados[column].fillna(nNomes + 1)        
            resultados[column] = resultados[column].apply(lambda x: int(x))  
            
        resultados = resultados.drop('Max', axis=1)
        resultados['Soma'] = resultados.sum(axis=1, numeric_only=True)
        resultados = resultados.sort_values('Soma')
        
        resultados['Posição'] = resultados['Soma'].rank(method='min', ascending=True).astype(int)
        
        resultados.reset_index(inplace = True) 
        
        view = resultados.style.hide(axis="index")
        
        view.set_table_styles([
        {'selector': "th", 'props': [("font-weight", "bold"), ("text-transform", "capitalize")]},])
        
        view.format(lambda x: f"<i title='tooltip'>{x}</i>", 'Posição')
            
        st.markdown(view.to_html(), unsafe_allow_html=True)
        return(result)


with st.sidebar:
    
    data = st.date_input('Data', value=datetime.datetime.today())
    nome_options = dados['NOME'].unique().tolist()
    nome_options.append('Novo Nome')
    nome = st.selectbox('Nome', options=nome_options)
    if(nome == 'Novo Nome'):
        
        nome = st.text_input('Nome a adicionar', '')
        
        if(nome in nome_options):
            st.error('Nome Já existe')
        elif(nome ==''):
             st.error('Adicione um Nome')
        else:
                        
            gols = st.number_input('Gols', min_value=0., max_value=100., value = 0., step = 1.)
            assists = st.number_input('Assistências', min_value=0., max_value=100., value = 0.,step = 1.)
            presença = st.number_input('Presença', min_value=0., max_value=100.,value = 0.,step = 1.)
            bt = st.button('ADD dados')
            if bt:
                write_data(dados.drop_duplicates(subset=['DATA', 'NOME'], keep = 'last'), data=data,nome = nome, gols=gols, assists=assists, presença=presença, sheet = "FutIate", tab = "Ranking")
                dados = read_data(sheet='FutIate', tab='Ranking').drop_duplicates(subset=['DATA', 'NOME'], keep = 'last')
    else:
        
        gols = st.number_input('Gols', min_value=0., max_value=100., value = 0., step = 1.)
        assists = st.number_input('Assistências', min_value=0., max_value=100., value = 0.,step = 1.)
        presença = st.number_input('Presença', min_value=0., max_value=100.,value = 0.,step = 1.)
        bt = st.button('ADD dados')
        if bt:
            write_data(dados.drop_duplicates(subset=['DATA', 'NOME'], keep = 'last'), data=data,nome = nome, gols=gols, assists=assists, presença=presença, sheet = "FutIate", tab = "Ranking")
            dados = read_data(sheet='FutIate', tab='Ranking').drop_duplicates(subset=['DATA', 'NOME'], keep = 'last')
        
              
tab1, tab2, tab3 = st.tabs(['# Ranking All-Time', "# Ranking Mensal", "# Ranking Agregado"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        pesoGols = st.number_input('Peso de Gols', min_value=0.,max_value=1., value = 0.2)
    with col2:
        pesoAssistências = st.number_input('Peso de Assistências', min_value=0.,max_value=1.,value = 0.2)
    with col3:
        pesoPresença = st.number_input('Peso de Presença', min_value=0.,max_value=1.,value = 0.6)
        
    ranking = RankingTotal(dados,pesoGols,pesoAssistências,pesoPresença)

with tab2:

    dateRef = st.date_input('Data de Referência', pd.to_datetime(dados['DATA']).unique()[-1])
    
    dt = dados[dados['DATA'].apply(lambda x: pd.to_datetime(x).month) == dateRef.month]
    
    st.write('Mês de Referência: ', dateRef.strftime('%m-%Y').title())
    
    col1, col2, col3 = st.columns(3)
    with col1:
        pesoGols1 = st.number_input('Peso de Gols - mensal', min_value=0.,max_value=1., value = 0.4)
    with col2:
        pesoAssistências2 = st.number_input('Peso de Assistências - mensal', min_value=0.,max_value=1.,value = 0.3)
    with col3:
        pesoPresença3 = st.number_input('Peso de Presença - mensal', min_value=0.,max_value=1.,value = 0.3)
    
    if (dt.empty):
        st.error('Ainda não tiveram partidas esse Mês')
    else:
        ranking = RankingTotal(dt,pesoGols1,pesoAssistências2,pesoPresença3)
with tab3:
        
    st.write('Mês de Referência: ', dateRef.strftime('%m-%Y').title())
    
    col1, col2, col3 = st.columns(3)
    with col1:
        pesoGols4 = st.number_input('Peso de Gols - agregado', min_value=0.,max_value=1., value = 0.4)
    with col2:
        pesoAssistências5 = st.number_input('Peso de Assistências - agregado', min_value=0.,max_value=1.,value = 0.3)
    with col3:
        pesoPresença6 = st.number_input('Peso de Presença - agregado', min_value=0.,max_value=1.,value = 0.3)

    ranking = RankingMes(dados,pesoGols4,pesoAssistências5,pesoPresença6)
        
with st.sidebar:

    with st.expander("# Head-To-Head"):
        st.markdown("## Head-to-head :rage:")
        with st.form(key="head2head"):
            person1 = st.selectbox("Player 1: ", dados['NOME'].unique())
            person2 = st.selectbox("Player 2: ", [el for el in dados['NOME'].unique() if el != person1])
            submit_head2head = st.form_submit_button(label="Submit")
            
            if(submit_head2head):
                head2head(dados, person1, person2, 'GOLS')
                head2head(dados, person1, person2, 'PRESENÇA')
                head2head(dados, person1, person2, 'ASSISTÊNCIAS')
                
    with st.expander('# Seletor de Times'):
        st.markdown("## Usando Stable Matching de Gale-Shapley :computer:")
        with st.form(key="Gale-Shapley"):
            submit_stable = st.form_submit_button(label="Bater Time")
            if(submit_stable):
                stable_matching(ranking)
            
        st.markdown("## Random Selector :1234:")
        with st.form(key="Random"):

            submit_random = st.form_submit_button(label="Time Random")
            if(submit_random):
                
                form_random_teams_with_substitutes(ranking)
