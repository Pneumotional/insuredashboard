# pages/agents.py
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dash import dash_table
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.graph_objects as go

dash.register_page(__name__, path='/direct')

# Get current year and previous year
current_year = datetime.now().year
previous_year = current_year - 1

def get_agent_data(year=None, month=None, quarter=None, intermediary=None):
    conn = sqlite3.connect('insurance_data.db')
    
    # Build where clause
    filters = [f"[Intermediary Type] = 'DIRECT'"]
    if year: filters.append(f"Year = {year}")
    if month: filters.append(f"Month = {month}")
    if quarter: filters.append(f"Quarter = {quarter}")
    if intermediary: filters.append(f"Intermediary = '{intermediary}'")
    # if Direct: filters.append(f"Direct = '{Direct}'")
    
    
    
    where_clause = " AND ".join(filters)
    
    return conn, where_clause

layout = dbc.Container([
    #Summary Cards
    dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Total Direct Production", className="card-title"),
                            html.H3(id="total-Direct-production", className="premium-value"),
                            html.P(id="Direct-production-year", className="text-muted")
                        ])
                    ], className='summary-card mb-3')
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("New Business", className="card-title"),
                            html.H3(id="Direct-new-business", className="premium-value"),
                            html.P(id="Direct-new-year", className="text-muted")
                        ])
                    ], className='summary-card mb-3')
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Renewals", className="card-title"),
                            html.H3(id="Direct-renewals", className="premium-value"),
                            html.P(id="Direct-renewal-year", className="text-muted")
                        ])
                    ], className='summary-card mb-3')
                ], width=4)
            ]),
    
    dbc.Row([
        # Filters Column
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Filters")),
                dbc.CardBody([
                    html.Label("Year", className="text-light mb-2"),
                    dcc.Dropdown(
                        id='Direct-year-filter',
                        options=[
                            {'label': str(year), 'value': year}
                            for year in range(previous_year, current_year + 1)
                        ],
                        value=current_year,
                        className='mb-3'
                    ),
                    html.Label("Month", className="text-light mb-2"),
                    dcc.Dropdown(
                        id='Direct-month-filter',
                        options=[
                            {'label': month, 'value': i}
                            for i, month in enumerate(['January', 'February', 'March', 
                                                     'April', 'May', 'June', 'July', 
                                                     'August', 'September', 'October', 
                                                     'November', 'December'], 1)
                        ],
                        className='mb-3'
                    ),
                    html.Label("Quarter", className="text-light mb-2"),
                    dcc.Dropdown(
                        id='Direct-quarter-filter',
                        options=[
                            {'label': f'Q{i}', 'value': i}
                            for i in range(1, 5)
                        ],
                        className='mb-3'
                    ),
                    html.Label("Direct", className="text-light mb-2"),
                    dcc.Dropdown(
                        id='Direct-filter',
                        className='mb-3'
                    )
                ])
            ], className='h-100')
        ], width=4),
        
        # Analysis Column
        dbc.Col([
            # Monthly Comparison Table
            dbc.Card([
                dbc.CardHeader(html.H5("Monthly Performance Comparison")),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='Direct-monthly-table',
                        style_header={
                            'backgroundColor': 'rgb(30, 30, 30)',
                            'fontWeight': 'bold',
                            'color':'white'
                        },
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'Difference',
                                      'filter_query': '{Difference} < 0'},
                                'color': '#ff4444'
                            },
                            {
                                'if': {'column_id': 'Difference',
                                      'filter_query': '{Difference} >= 0'},
                                'color': '#00C851'
                            }
                        ]
                    )
                ], className='mb-3')
            ]),
            
            # Quarterly Comparison Table
            dbc.Card([
                dbc.CardHeader(html.H5("Quarterly Performance Comparison")),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='Direct-quarterly-table',
                        style_header={
                            'backgroundColor': 'rgb(30, 30, 30)',
                            'fontWeight': 'bold',
                            'color':'white'
                        },
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'Difference',
                                      'filter_query': '{Difference} < 0'},
                                'color': '#ff4444'
                            },
                            {
                                'if': {'column_id': 'Difference',
                                      'filter_query': '{Difference} >= 0'},
                                'color': '#00C851'
                            }
                        ]
                    )
                ])
            ])
        ], width=8),
    ]),
    
            # Rankings Column
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Direct Rankings")),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='Direct-rankings-table',
                                            style_header={
                            'backgroundColor': 'rgb(30, 30, 30)',
                            'fontWeight': 'bold',
                            'color':'white'
                        },
                        style_table={'height': '100%',
                                     'backgroundColor': 'rgb(30, 30, 30)',
                                     },
                        # style_data_conditional=[
                        #     {
                        #         'if': {'row_index': 'odd'},
                        #         'backgroundColor': 'rgba(0, 0, 0, 0.05)'
                        #     }
                        # ],
                        page_size=10
                    )
                ])
            ], className='h-80')
        ], width=12)
], fluid=True)

# Callbacks
@dash.callback(
    [Output('Direct-filter', 'options')],
    [Input('Direct-year-filter', 'value')]
)
def update_agent_options(year):
    conn, where_clause = get_agent_data(year=year)
    query = f"""
    SELECT DISTINCT Intermediary
    FROM insurance_transactions
    WHERE {where_clause}
    ORDER BY Intermediary
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    options = [{'label': Direct, 'value': Direct} for Direct in df['Intermediary']]
    
    # Ensure that the value is updated to the first item by default (or set based on a logic)
    # You can set the first Direct as the default or use `None` if you want it blank by default
    # default_value = df['Intermediary'].iloc[0] if not df.empty else None
    
    # return [[{'label': Direct, 'value': Direct} for Direct in df['Intermediary']]]
    return [options]

@dash.callback(
    [Output('total-Direct-production', 'children'),
     Output('Direct-new-business', 'children'),
     Output('Direct-renewals', 'children'),
     Output('Direct-production-year', 'children'),
     Output('Direct-new-year', 'children'),
     Output('Direct-renewal-year', 'children')],
    [Input('Direct-year-filter', 'value'),
     Input('Direct-month-filter', 'value'),
     Input('Direct-quarter-filter', 'value'),
     Input('Direct-filter', 'value')]
)
def update_summary_cards(year, month, quarter, Direct):
    conn, where_clause = get_agent_data(year, month, quarter, Direct)
    
    # Total Production Query
    total_query = f"""
    SELECT SUM(Premium) as Total
    FROM insurance_transactions
    WHERE {where_clause}
    """
    
    # New Business Query
    new_query = f"""
    SELECT SUM(Premium) as Total
    FROM insurance_transactions
    WHERE {where_clause} AND [Trans Type] = 'New Business'
    """
    
    # Renewals Query
    renewal_query = f"""
    SELECT SUM(Premium) as Total
    FROM insurance_transactions
    WHERE {where_clause} AND [Trans Type] = 'Renewal'
    """
    
    total_premium = pd.read_sql_query(total_query, conn)['Total'].iloc[0]
    new_business = pd.read_sql_query(new_query, conn)['Total'].iloc[0]
    renewals = pd.read_sql_query(renewal_query, conn)['Total'].iloc[0]
    
    conn.close()
    
    # Format numbers with fallback to 0 if None
    total_premium = f"{total_premium:,.2f}" if total_premium is not None else "0.00"
    new_business = f"{new_business:,.2f}" if new_business is not None else "0.00"
    renewals = f"{renewals:,.2f}" if renewals is not None else "0.00"
    
    year_text = f"Year {year if year else current_year}"
    
    return (
        total_premium,
        new_business,
        renewals,
        year_text,
        year_text,
        year_text
    )


@dash.callback(
    [Output('Direct-monthly-table', 'data'),
     Output('Direct-monthly-table', 'columns')],
    [Input('Direct-year-filter', 'value'),
     Input('Direct-filter', 'value')]
)
def update_monthly_table(year, Direct):
    conn, where_clause = get_agent_data(intermediary=Direct)
    
    query = f"""
    SELECT 
        [Month Name] as Month,
        SUM(CASE WHEN Year = {previous_year} THEN Premium ELSE 0 END) as "{previous_year}",
        SUM(CASE WHEN Year = {current_year} THEN Premium ELSE 0 END) as "{current_year}",
        (SUM(CASE WHEN Year = {current_year} THEN Premium ELSE 0 END) - 
         SUM(CASE WHEN Year = {previous_year} THEN Premium ELSE 0 END)) / 
         NULLIF(SUM(CASE WHEN Year = {previous_year} THEN Premium ELSE 0 END), 0) * 100 as Difference
    FROM insurance_transactions
    WHERE {where_clause}
    GROUP BY [Month Name], Month
    ORDER BY 
    CASE 
        WHEN [Month Name] = 'January' THEN 1
        WHEN [Month Name] = 'February' THEN 2
        WHEN [Month Name] = 'March' THEN 3
        WHEN [Month Name] = 'April' THEN 4
        WHEN [Month Name] = 'May' THEN 5
        WHEN [Month Name] = 'June' THEN 6
        WHEN [Month Name] = 'July' THEN 7
        WHEN [Month Name] = 'August' THEN 8
        WHEN [Month Name] = 'September' THEN 9
        WHEN [Month Name] = 'October' THEN 10
        WHEN [Month Name] = 'November' THEN 11
        WHEN [Month Name] = 'December' THEN 12
    END;
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Format numbers
    df[str(previous_year)] = df[str(previous_year)].apply(lambda x: f"{x:,.2f}")
    df[str(current_year)] = df[str(current_year)].apply(lambda x: f"{x:,.2f}")
    df['Difference'] = df['Difference'].apply(lambda x: f"{x:,.2f}%" if pd.notnull(x) else "N/A")
    
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]

@dash.callback(
    [Output('Direct-quarterly-table', 'data'),
     Output('Direct-quarterly-table', 'columns')],
    [Input('Direct-year-filter', 'value'),
     Input('Direct-filter', 'value')]
)
def update_quarterly_table(year, Direct):
    conn, where_clause = get_agent_data(intermediary=Direct)
    
    query = f"""
    SELECT 
        'Q' || Quarter as Quarter,
        SUM(CASE WHEN Year = {previous_year} THEN Premium ELSE 0 END) as "{previous_year}",
        SUM(CASE WHEN Year = {current_year} THEN Premium ELSE 0 END) as "{current_year}",
        (SUM(CASE WHEN Year = {current_year} THEN Premium ELSE 0 END) - 
         SUM(CASE WHEN Year = {previous_year} THEN Premium ELSE 0 END)) / 
         NULLIF(SUM(CASE WHEN Year = {previous_year} THEN Premium ELSE 0 END), 0) * 100 as Difference
    FROM insurance_transactions
    WHERE {where_clause}
    GROUP BY Quarter
    ORDER BY Quarter
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Format numbers
    df[str(previous_year)] = df[str(previous_year)].apply(lambda x: f"{x:,.2f}")
    df[str(current_year)] = df[str(current_year)].apply(lambda x: f"{x:,.2f}")
    df['Difference'] = df['Difference'].apply(lambda x: f"{x:,.2f}%" if pd.notnull(x) else "N/A")
    
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]

@dash.callback(
    [Output('Direct-rankings-table', 'data'),
     Output('Direct-rankings-table', 'columns')],
    [Input('Direct-year-filter', 'value'),
     Input('Direct-month-filter', 'value'),
     Input('Direct-quarter-filter', 'value')]
)
def update_rankings_table(year, month, quarter):
    conn, where_clause = get_agent_data(year, month, quarter)
    
    query = f"""
    SELECT 
        Intermediary as Direct,
        COUNT(DISTINCT [Policy No]) as Policies,
        SUM(Premium) as Premium,
        RANK() OVER (ORDER BY SUM(Premium) DESC) as Rank
    FROM insurance_transactions
    WHERE {where_clause}
    GROUP BY Intermediary
    ORDER BY Premium DESC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Format numbers
    df['Premium'] = df['Premium'].apply(lambda x: f"{x:,.2f}")
    
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]