# Dependencies:

# Data manipulation
import pandas as pd

# Plotting
import plotly.express as px
import plotly.graph_objects as go

# Dashboarding:
import dash
import dash_table as dt
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output


df = pd.read_csv('./data/umap.csv',index_col=0)
df2 = pd.read_csv('./data/umap2.csv',index_col=0)
row = df.iloc[0]
patients = pd.read_csv('./data/indexed.csv',index_col=0)

labels = patients.index.unique().to_list()
df.index = labels
df2.index = labels

meta_data = patients.groupby(patients.index).first()
meta_data.drop(columns=['time'],inplace=True)

fig1 = go.Figure()
fig1.add_trace(go.Scatterpolar(
    r=[],
    theta=row.index,
        mode = 'lines',
))

fig2 = px.scatter(x=df2['Latent Factor 1'], y=df2['Latent Factor 2'],
                hover_name=df2.index)

description = '''The visualizations displayed here are the result of an embedding model. Each point corresponds to a patient in the embedding space. 

**Usage: Select points in the scatter plot to see their phenoptypic features visualized in the radar plot and their patient profile in the table below.**

All data was extracted from the following publication and belongs to the original authors
                
> [Lodin, Karin et al. “Longitudinal co-variations between inflammatory cytokines, lung function and patient reported outcomes in patients with asthma.” PloS one vol. 12,9 e0185019. 15 Sep. 2017, doi:10.1371/journal.pone.0185019][1]
[1]:https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5600400/'''

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[html.Div(className='Intro',
                                        children=[html.H1(children='Asthma Phenotyping Project - Interactive Dashboard',style={'text-align':'center'}),
                                                html.Div(children='## Prototype under Development ##',style={'text-align':'center','font-style': 'italic'}),
                                                html.Div(children=dcc.Markdown(description),style={'margin-left':'30px','margin-bottom':'30px','margin-top':'30px','width':'60%'}),
                                                ]),
                            
                            html.Div(className='graphs',
                                        children=[html.Div(className='scatter-graph',
                                                        children = [html.Div(children=[html.Div(children='Figure 1: 2-dimensional embedding')],style={'text-align':'center'}),
                                                                    html.Div(children=[html.Div(children='Instructions: Select region in figure with "Lasso Select" tool; double-click to reset')],style={'font-size':'11pt','margin-top':'5px','font-style': 'italic','text-align':'center'}),
                                                                    dcc.Graph(id='scatter',figure=fig2)
                                                                    ]),
                                                html.Div(className='Radar-chart',
                                                            children=[html.Div(children=[html.Div(children='Figure 2: Latent Factor Visualization')],style={'text-align':'center'}),
                                                                    dcc.Graph(id='radar',figure=fig1)
                                                                    ])
                                                ],style={'columnCount': 2}),
                            
                            html.Div(id='table-intro',children=[dcc.Markdown('Selected Patients appear here &#8595; &#8595;')]),
                            html.Div(id='table-cont')])



@app.callback(
[Output('radar', 'figure'),
Output('table-cont','children')],
[Input('scatter','selectedData')])
def display_selected_data(selectedData):

    tempFig = go.Figure()
    tempFig.add_trace(go.Scatterpolar(
            r=[],
            theta=row.index,
            mode = 'lines',
    ))

    tableFill = html.Div()
    if selectedData is not None:
        idx = [el['hovertext'] for el in selectedData['points']]
        rows = df.loc[idx,:]
        for i,this_row in rows.iterrows():
            tempFig.add_trace(go.Scatterpolar(
                r=this_row.values,
                theta=row.index,
                mode = 'lines',
                showlegend=False,
                connectgaps = True,
                hovertext =this_row.name,
                line={'color':'rgba(192,192,192,0.5)'}
                ))
        
        tempFig.add_trace(go.Scatterpolar(
                r=rows.mean(axis=0),
                theta=row.index,
                mode = 'lines',
                name='mean',
                showlegend=True,
                connectgaps = True,
                hovertext =this_row.name,
                #hoverlabel ={'hover_name':this_row.name},
                line={'color':'rgba(255,165,0,0.8)'}
                ))
        
        tableData = meta_data.loc[idx,:]
        tableData.reset_index()
        tableFill = dt.DataTable(id='patient_data',
                        data=tableData.to_dict('rows'),
                        columns=[{"name": i, "id": i,} for i in (tableData.columns)],
                        row_selectable='multi',
                    sort_action='native')
        
    return [{
        'data': tempFig.data,
        'layout':tempFig.layout
        },tableFill]

app.run_server()
    