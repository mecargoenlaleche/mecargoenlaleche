# Cargueiros Previstos

kminho = 'U:\\2. Operacional\\7. Resultados Operacionais\\BASES DE DADOS\\Base de Dados - Power BI\\Single Days\\'
uei = 'U:\\5. SLOTS\\9. Estadia - Realizado\\Dados\\'

from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
from datetime import timedelta
import base64
import numpy as np

sd = pd.read_csv('Live_GRU_S26-SD.txt', dtype='unicode', skiprows=1, usecols=[0,1,2,3,4,6,8,9,10,11])
sd = sd[sd['Serv.type'].isin(['M', 'F', 'H', 'A'])]
sd = sd[sd['Term'].isin(['CARGO-INT'])]
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

# Datas auxiliares para filtrar sem comparar textos em DD/MM/AAAA.
datas_voos = pd.to_datetime(
    sd['Data'], format='%d/%m/%Y', errors='coerce'
)

operadores = sorted(sd['Operador'].dropna().unique().tolist())

estilo_campo = {
    'flex': '1 1 260px',
    'minWidth': '260px'
}

estilo_rotulo = {
    'display': 'block',
    'marginBottom': '8px',
    'fontWeight': 'bold',
    'fontSize': '13px'
}

app.layout = html.Div(
    [
        html.Img(
            src=app.get_asset_url('gru_logo.png'),
            style={
                'float': 'right',
                'maxWidth': '180px',
                'marginLeft': '20px'
            }
        ),

        html.H1(
            'VOOS CARGUEIROS PREVISTOS',
            style={'fontSize': '26px'}
        ),

        html.Div(
            [
                html.P(
                    'Previsão das operações cargueiras com slot '
                    'alocado para os próximos 30 dias'
                ),
                html.P(
                    'Todas as informações são fornecidas previamente '
                    'pelas companhias aéreas'
                ),
                html.P(
                    'Dúvidas sobre alterações podem ser esclarecidas '
                    'diretamente nos canais de atendimento das '
                    'empresas responsáveis'
                ),
            ],
            style={
                'fontSize': '13px',
                'lineHeight': '1.6',
                'marginBottom': '30px'
            }
        ),

        # Área de filtros
        html.Div(
            [
                html.Div(
                    [
                        html.Label('Período', style=estilo_rotulo),

                        dcc.DatePickerRange(
                            id='filtro-periodo',
                            min_date_allowed=oggi.date(),
                            max_date_allowed=sem_irmã.date(),
                            initial_visible_month=oggi.date(),
                            start_date=oggi.date(),
                            end_date=sem_irmã.date(),
                            display_format='DD/MM/YYYY',
                            month_format='MM/YYYY',
                            start_date_placeholder_text='Data inicial',
                            end_date_placeholder_text='Data final',
                            minimum_nights=0,
                            first_day_of_week=1,
                            clearable=True
                        ),
                    ],
                    style=estilo_campo
                ),

                html.Div(
                    [
                        html.Label('Operador', style=estilo_rotulo),

                        dcc.Dropdown(
                            id='filtro-operador',
                            options=[
                                {'label': op, 'value': op}
                                for op in operadores
                            ],
                            multi=True,
                            searchable=True,
                            clearable=True,
                            placeholder='Todos os operadores'
                        ),
                    ],
                    style=estilo_campo
                ),

                html.Div(
                    [
                        html.Label('Movimento', style=estilo_rotulo),

                        dcc.Dropdown(
                            id='filtro-movimento',
                            options=[
                                {
                                    'label': 'Chegadas',
                                    'value': 'Chegadas'
                                },
                                {
                                    'label': 'Partidas',
                                    'value': 'Partidas'
                                },
                            ],
                            multi=True,
                            clearable=True,
                            placeholder='Chegadas e partidas'
                        ),
                    ],
                    style=estilo_campo
                ),
            ],
            style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'gap': '20px',
                'padding': '20px',
                'backgroundColor': '#EAF7F7',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'clear': 'both'
            }
        ),

        html.Div(
            id='resumo-filtros',
            style={
                'marginBottom': '12px',
                'fontSize': '13px',
                'fontWeight': 'bold',
                'color': '#006E73'
            }
        ),

        dash_table.DataTable(
            id='tafeia',
            columns=[
                {'name': coluna, 'id': coluna}
                for coluna in sd.columns
            ],
            data=sd.to_dict('records'),

            filter_action='native',
            filter_options={
                'placeholder_text': 'Filtrar valor'
            },

            sort_action='native',
            sort_mode='multi',

            page_action='native',
            page_current=0,
            page_size=25,

            style_table={
                'overflowX': 'auto'
            },

            style_cell={
                'textAlign': 'left',
                'color': 'white',
                'fontFamily': 'Verdana',
                'fontSize': '12px',
                'padding': '10px',
                'minWidth': '90px',
                'maxWidth': '240px',
                'whiteSpace': 'normal'
            },

            style_header={
                'backgroundColor': '#17383B',
                'color': 'white',
                'fontWeight': 'bold'
            },

            style_filter={
                'backgroundColor': '#F1F7F7',
                'color': '#222'
            },

            style_data={
                'backgroundColor': '#00ABBD'
            },

            style_data_conditional=[
                {
                    'if': {
                        'filter_query': '{C/P} eq "Partidas"'
                    },
                    'backgroundColor': '#00919A',
                    'color': 'white'
                }
            ],
        ),
    ],
    style={
        'fontFamily': 'Verdana',
        'padding': '24px',
        'color': '#243638'
    }
)


@app.callback(
    Output('tafeia', 'data'),
    Output('tafeia', 'page_current'),
    Input('filtro-periodo', 'start_date'),
    Input('filtro-periodo', 'end_date'),
    Input('filtro-operador', 'value'),
    Input('filtro-movimento', 'value'),
)
def atualizar_tabela(data_inicial, data_final, operadores, movimentos):
    mascara = pd.Series(True, index=sd.index)

    if data_inicial:
        mascara &= datas_voos >= pd.Timestamp(data_inicial).normalize()

    if data_final:
        mascara &= datas_voos <= pd.Timestamp(data_final).normalize()

    if operadores:
        mascara &= sd['Operador'].isin(operadores)

    if movimentos:
        mascara &= sd['C/P'].isin(movimentos)

    filtrado = sd.loc[mascara]

    # Volta à primeira página sempre que um filtro externo mudar.
    return filtrado.to_dict('records'), 0


@app.callback(
    Output('resumo-filtros', 'children'),
    Input('tafeia', 'derived_virtual_data'),
)
def atualizar_resumo(registros):
    # Considera também os filtros digitados nas colunas.
    if registros is None:
        registros = sd.to_dict('records')

    total = len(registros)
    chegadas = sum(
        registro.get('C/P') == 'Chegadas'
        for registro in registros
    )
    partidas = sum(
        registro.get('C/P') == 'Partidas'
        for registro in registros
    )

    if total == 0:
        return 'Nenhum voo encontrado para os filtros selecionados.'

    return (
        f'{total} voos encontrados | '
        f'{chegadas} chegadas | {partidas} partidas'
    )


if __name__ == '__main__':
    app.run()
    

