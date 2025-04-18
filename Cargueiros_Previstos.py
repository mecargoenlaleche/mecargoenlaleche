# Cargueiros Previstos

kminho = 'U:\\2. Operacional\\7. Resultados Operacionais\\BASES DE DADOS\\Base de Dados - Power BI\\Single Days\\'
uei = 'U:\\5. SLOTS\\9. Estadia - Realizado\\Dados\\'

from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
from datetime import timedelta
import base64
import numpy as np

sd = pd.read_csv('Live_GRU_S25-SD.txt', dtype='unicode', skiprows=1, usecols=[0,1,2,3,4,6,8,9,10,11])
sd = sd[sd['Serv.type'].isin(['M', 'F', 'H', 'A'])]
sd['Serv.type'] = sd['Serv.type'].replace({'M':'Correios','F':'Regular Cargo', 'H':'Extra Cargo', 'A':'Mix Cargo/Pax'})
sd['Term'] = sd['Term'].replace({'CARGO-INT':'Internacional', 'CARGO-DOM':'Doméstico'})
sd['ArrDep'] = sd['ArrDep'].replace({'A':'Chegadas', 'D':'Partidas'})
sd['Date'] = pd.to_datetime(sd['Date'], dayfirst=True)
sd['Hora']= sd.Time = sd.Time.str[:2] + ':' + sd.Time.str[-2:]
sd = sd.rename(columns={'Serv.type': 'Serviço', 'Term': 'Natureza','ArrDep':'C/P','Actyp':'Aeronave'})
oggi = pd.to_datetime('today').normalize()
sem_irmã = oggi + timedelta(days=29)
sd = sd[(sd['Date']>=oggi) & (sd['Date']<=sem_irmã)]
sd = sd.sort_values(['Date','Hora'],ascending=[True,True])
sd['Data'] = sd['Date'].dt.strftime('%d/%m/%Y')

orig = pd.read_excel('referências.xlsx', sheet_name = 'destinos', usecols=[0,2])
orig = orig.rename(columns={'IATA': 'OrigDest', 'DESTINO': 'Origem/Destino'})
last = pd.read_excel('referências.xlsx', sheet_name = 'destinos', usecols=[0,2])
last = last.rename(columns={'IATA': 'LastNext', 'DESTINO': 'Escala'})
opes = pd.read_excel('referências.xlsx', sheet_name = 'operador',usecols = [0,1])
opes = opes.rename(columns={'Iata Code': 'Airl.Desig', 'OPERADOR': 'Operador'})

sd = pd.merge(sd, orig, how = 'inner', on = 'OrigDest')
sd = pd.merge(sd, last, how = 'inner', on = 'LastNext')
sd = pd.merge(sd, opes, how = 'inner', on = 'Airl.Desig')
sd['Voo'] = sd['Airl.Desig']+sd['Fltno']
sd = sd.drop(['Time','Airl.Desig', 'Fltno','OrigDest', 'LastNext'], axis=1)
sd = sd.sort_values(['Date','Hora'],ascending=[True,True])
sd = sd[['Data','Hora','C/P','Operador','Voo', 'Aeronave','Origem/Destino','Escala', 'Serviço','Natureza']]
oje = sd['Data'].iloc[0]

sd['Origem/Destino'] = np.where(sd['Origem/Destino'] == "Guarulhos", sd['Escala'], sd['Origem/Destino'])
sd['Escala'] = np.where(sd['Escala'] == "Guarulhos", sd['Origem/Destino'], sd['Escala'])

sd.loc[sd['Origem/Destino'] == sd['Escala'], 'Escala'] = ''

image_path = r'\assets\gru_logo.png'
#encoded_image = base64.b64encode(open(image_path, 'rb').read())

app = Dash(__name__)
app.title = 'Cargueiros Previstos'
server = app.server
#PAGE_SIZE = 15
#dias = sd.Operador.unique().tolist()

app.layout = html.Div(
    [
        #html.Img(src='data:image/png;base64,{}'.format(image_path),style={'float':'right'}),
	html.Img(src=image_path,style={'float':'right'}),    
        html.H1('VOOS CARGUEIROS PREVISTOS', style={'font-family':'verdana'}),
        html.Div(children='''
            Previsão das operações cargueiras com slot alocado para os próximos 30 dias
        ''', style={'font-family':'verdana'}),
        html.Div(children='''
            Todas as informações são fornecidas previamente pelas companhias aéreas
        ''', style={'font-family':'verdana'}),
        html.Div(children='''
            Dúvidas sobre alterações podem ser esclarecidas diretamente nos canais de atendimento das empresas responsáveis
        ''', style={'font-family':'verdana'}),
        html.Div(children='''
            
        '''),
#        html.Div(children='''
#            -Selecione Um Operador-
#        ''', style={'font-family':'verdana'}),
#        html.Div(children='''
#            ------------------
#        '''),
        
        html.Div(
        children=[
#            dcc.Dropdown(
#				id='selectioneer',
#				options=[{'label':dt, 'value': dt}for dt in dias],
#				placeholder='Sel. Operador',
#				multi=False,
#                                style={"width": "35%"},
#				#value=oje,
#            ),        
			dash_table.DataTable(
				id='tafeia',
				columns=[{"name": i, "id": i} for i in sd.columns],
                                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{C/P} eq "Partidas"'
                        },
                        'backgroundColor': '#00919A',
                        'color': 'white'
                    },
                                        ],
				filter_action="native",
				filter_options={"placeholder_text": "Filtrar Valor"},
				data=sd.to_dict("records"),
                page_current=0,
                #page_size=PAGE_SIZE,
				style_cell=dict(textAlign="left",color='white',font_family='verdana'),
				style_header=dict(backgroundColor='black'),
				style_data=dict(backgroundColor='#00ABBD'),
            ),],
			),])

@app.callback(
    Output("tafeia", "data"), 
    Input("selectioneer", "value")
)
def update_table(data):
    if data:
        sdd = sd[sd['Operador']==data]
        return sdd.to_dict('records')
    return sd.to_dict('records')


if __name__ == "__main__":
    app.run_server()
    
