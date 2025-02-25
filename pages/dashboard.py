import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
from datetime import datetime
import io
import base64
import chardet
from dash_iconify import DashIconify

dash.register_page(__name__, path='/')


def create_database():
    conn = sqlite3.connect('insurance_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS insurance_transactions (
        [Transaction Date] TEXT, [Policy No] TEXT, [Trans Type] TEXT, 
        Branch TEXT, Class TEXT, [Dr/Cr No] TEXT, [Risk ID] TEXT,
        Insured TEXT, [Intermediary Type] TEXT, Intermediary TEXT,
        Marketer TEXT, WEF TEXT, WET TEXT, CURRENCY TEXT,
        [Sum Insured] REAL, Premium REAL, PAID REAL,
        Year INTEGER, [Month Name] TEXT, Month INTEGER,
        Quarter INTEGER, Weeks INTEGER)''')
    conn.commit()
    conn.close()

def insert_data(df):
    expected_columns = [
        'Transaction Date', 'Policy No', 'Trans Type', 'Branch', 'Class',
        'Dr/Cr No', 'Risk ID', 'Insured', 'Intermediary Type', 'Intermediary',
        'Marketer', 'WEF', 'WET', 'CURRENCY', 'Sum Insured', 'Premium', 'PAID',
        'Year', 'Month Name', 'Month', 'Quarter', 'Weeks'
    ]
    
    # Check if columns match
    if not all(col in df.columns for col in expected_columns):
        missing_columns = [col for col in expected_columns if col not in df.columns]
        print(f"Missing columns in DataFrame: {missing_columns}")
        return
     # Convert specific columns to uppercase
    columns_to_upper = ['Branch', 'Class', 'Insured', 'Intermediary Type', 'Intermediary', 'Marketer']
    df[columns_to_upper] = df[columns_to_upper].apply(lambda x: x.str.upper() if x.dtype == "object" else x)
    
    try:
        conn = sqlite3.connect('insurance_data.db')
        df.to_sql('insurance_transactions', conn, if_exists='append', index=False)
        conn.commit()
        conn.close()
        print("Data inserted successfully.")
        
    except Exception as e:
        print(f"Error inserting data: {str(e)}")

def get_filter_options():
    conn = sqlite3.connect('insurance_data.db')
    query = '''SELECT DISTINCT 
               [Trans Type], Branch, Class, Year, 
               [Intermediary Type], Intermediary, 
               Marketer, CURRENCY, [Month Name]
               FROM insurance_transactions'''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Initialize the Dash app with dark theme and Bootstrap

# Layout

layout = dbc.Container([
dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total Premium", className="card-title text-center"),
                    html.H2(id="total-premium", className="text-center premium-value"),
                    html.P(id="total-premium-year", className="text-center text-muted")
                ])
            ], className='summary-card')
        ], width=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("New Business", className="card-title text-center"),
                    html.H2(id="new-business", className="text-center premium-value"),
                    html.P(id="new-business-year", className="text-center text-muted")
                ])
            ], className='summary-card')
        ], width=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Renewal Business", className="card-title text-center"),
                    html.H2(id="renewal-business", className="text-center premium-value"),
                    html.P(id="renewal-business-year", className="text-center text-muted")
                ])
            ], className='summary-card')
        ], width=4),
    ], className="mb-3"),

    
    dbc.Row([
        # Filters Column
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Filters", className="mb-0")),
                dbc.CardBody([
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        className='upload-box mb-3 text-success'
                    ),
                    html.Div(id='output-data-upload'),
                    dcc.Dropdown(id='trans-type-filter', placeholder="Transaction Type", className='mb-2'),
                    dcc.Dropdown(
                        id='branch-filter',
                        placeholder="Branch",
                        className='mb-2',
                        multi=True  # Enable multiple selection
                    ),
                    dcc.Dropdown(id='class-filter', placeholder="Class", className='mb-2'),
                    dcc.Dropdown(
                        id='year-filter',
                        placeholder="Year",
                        className='mb-2',
                        multi=True  # Enable multiple selection
                    ),
                    dcc.Dropdown(id='intermediary-type-filter', placeholder="Intermediary Type", className='mb-2'),
                    dcc.Dropdown(id='intermediary-filter', placeholder="Intermediary", className='mb-2'),
                    dcc.Dropdown(id='marketer-filter', placeholder="Marketer", className='mb-2'),
                    dcc.Dropdown(id='currency-filter', placeholder="Currency", className='mb-2'),
                    dcc.Dropdown(id='month-name-filter', placeholder="Month Name", className='mb-2'),
                ])
            ], className='filter-card')
        ], width=4),

        # Charts Column
        dbc.Col([
            dbc.Row([        
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Weekly-Monthly Premium Analysis", className="mb-4 text-success")),
                        dbc.CardBody([
                            dash_table.DataTable(
                                id='weekly-monthly-table',
                                style_table={'overflowX': 'auto'},
                                style_header={
                                    'backgroundColor': 'rgb(30, 30, 30)',
                                    'color': 'white',
                                    'fontWeight': 'bold'
                                },
                                style_cell={
                                    'backgroundColor': 'rgb(50, 50, 50)',
                                    'color': 'white',
                                    'border': '1px solid rgb(70, 70, 70)'
                                }
                            )
                        ])
                    ], className='dashboard-card mb-4')
                ], width=12),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Premium Trend", className="mb-3 text-success")),
                        dbc.CardBody([
                            dcc.Graph(id='premium-trend')
                        ])
                    ], className='dashboard-card mt-3')
                ], width=12),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Branch Premium", className="mb-0 text-success")),
                        dbc.CardBody([
                            dcc.Graph(id='branch-premium')
                        ])
                    ], className='dashboard-card mt-3 mb-3')
                ], width=12),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5(f"Class Comparison", className="mb-4 text-success")),
                        dbc.CardBody([
                            dash_table.DataTable(
                                id='class-comparison-table',
                                style_table={'overflowX': 'auto'},
                                style_header={
                                    'backgroundColor': 'rgb(30, 30, 30)',
                                    'color': 'white',
                                    'fontWeight': 'bold'
                                },
                                style_cell={
                                    'backgroundColor': 'rgb(50, 50, 50)',
                                    'color': 'white',
                                    'border': '1px solid rgb(70, 70, 70)'
                                }
                            )
                        ])
                    ], className='dashboard-card')
            ], width=12, className='mt-2'),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Monthly Premium: Yearly Comparison", className="mb-4 text-success")),
                    dbc.CardBody([
                        dash_table.DataTable(
                            id='monthly-comparison-table',
                            style_table={'overflowX': 'auto'},
                            style_header={
                                'backgroundColor': 'rgb(30, 30, 30)',
                                'color': 'white',
                                'fontWeight': 'bold'
                            },
                            style_cell={
                                'backgroundColor': 'rgb(50, 50, 50)',
                                'color': 'white',
                                'border': '1px solid rgb(70, 70, 70)'
                            }
                        )
                    ])
                ], className='dashboard-card')
            ], width=12, className='mt-2'),
            ])
        ], width=8)
    ], className='mt-2'),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Class Premium Analysis", className="mb-4 text-success")),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='class-premium-table',
                        style_table={'overflowX': 'auto'},
                        
                        style_header={
                            'backgroundColor': 'rgb(30, 30, 30)',
                            'color': 'white',
                            'fontWeight': 'bold'
                        },
                        style_cell={
                            'backgroundColor': 'rgb(50, 50, 50)',
                            'color': 'white',
                            'border': '1px solid rgb(70, 70, 70)'
                        },
                    )
                ])
            ], className='dashboard-card mb-4')
        ], width=4, className='mt-5'),
                        
            dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Quarterly Progress", className="mb-0")),
                            dbc.CardBody([
                                dcc.Graph(id='quarterly-progress')
                            ])
                        ], className='dashboard-card mt-7')
                    ], width=8, className='mt-5'),
    ], )
        
], fluid=True, className='app-container', id='main-container')




@dash.callback(
    [Output('total-premium', 'children'),
     Output('total-premium-year', 'children'),
     Output('new-business', 'children'),
     Output('new-business-year', 'children'),
     Output('renewal-business', 'children'),
     Output('renewal-business-year', 'children')],
    [Input('year-filter', 'value'),
     Input('branch-filter', 'value'),
     Input('class-filter', 'value'),
     Input('intermediary-type-filter', 'value'),
     Input('intermediary-filter', 'value'),
     Input('marketer-filter', 'value'),
     Input('currency-filter', 'value'),
     Input('month-name-filter', 'value')]
)
def update_summary_cards(years, branches, class_, int_type, intermediary, 
                        marketer, currency, month_name):
    conn = sqlite3.connect('insurance_data.db')
    
    # Build the WHERE clause based on filters
    filters = []
    
    # Handle multiple branch selections
    if branches:
        branch_conditions = [f"Branch = '{branch}'" for branch in branches]
        filters.append(f"({' OR '.join(branch_conditions)})")
    
    if class_: filters.append(f"Class = '{class_}'")
    if int_type: filters.append(f"[Intermediary Type] = '{int_type}'")
    if intermediary: filters.append(f"Intermediary = '{intermediary}'")
    if marketer: filters.append(f"Marketer = '{marketer}'")
    if currency: filters.append(f"CURRENCY = '{currency}'")
    if month_name: filters.append(f"[Month Name] = '{month_name}'")
    
    # Handle multiple year selections
    current_year = datetime.now().year
    if years:
        year_conditions = [f"Year = {year}" for year in years]
        filters.append(f"({' OR '.join(year_conditions)})")
    else:
        filters.append(f"Year = {current_year}")
    
    where_clause = " AND ".join(filters) if filters else "1=1"
    
    # Rest of the queries remain the same, just using the updated where_clause
    total_query = f"""
    SELECT SUM(Premium) as Total_Premium
    FROM insurance_transactions
    WHERE {where_clause}
    """
    
    new_query = f"""
    SELECT SUM(Premium) as New_Business
    FROM insurance_transactions
    WHERE {where_clause} AND [Trans Type] = 'New Business'
    """
    
    renewal_query = f"""
    SELECT SUM(Premium) as Renewal_Business
    FROM insurance_transactions
    WHERE {where_clause} AND [Trans Type] = 'Renewal'
    """
    
    # Execute queries
    total_premium = pd.read_sql_query(total_query, conn)['Total_Premium'].iloc[0]
    new_business = pd.read_sql_query(new_query, conn)['New_Business'].iloc[0]
    renewal_business = pd.read_sql_query(renewal_query, conn)['Renewal_Business'].iloc[0]
    
    conn.close()
    
    # Format values
    total_formatted = f"{total_premium:,.2f}" if total_premium else "0.00"
    new_formatted = f"{new_business:,.2f}" if new_business else "0.00"
    renewal_formatted = f"{renewal_business:,.2f}" if renewal_business else "0.00"
    
    # Year text - modified to show multiple years if selected
    if years:
        year_text = f"For Years {', '.join(map(str, years))}"
    else:
        year_text = f"For Year {current_year}"
    
    return (
        total_formatted,
        year_text,
        new_formatted,
        year_text,
        renewal_formatted,
        year_text
    )


# Callback for upload status
@dash.callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents')
)
def update_output(contents):
    if contents is not None:
        return html.Div(['File uploaded successfully!'], className='success-message')
    return html.Div()

# Callback to update filters
@dash.callback(
    [Output('trans-type-filter', 'options'),
     Output('branch-filter', 'options'),
     Output('class-filter', 'options'),
     Output('year-filter', 'options'),
     Output('intermediary-type-filter', 'options'),
     Output('intermediary-filter', 'options'),
     Output('marketer-filter', 'options'),
     Output('currency-filter', 'options'),
     Output('month-name-filter', 'options')],
    [Input('upload-data', 'contents')]
)


def update_filters(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        try:
            if 'xlsx' in content_type:
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                result = chardet.detect(decoded)
                encoding = result['encoding']
                df = pd.read_csv(io.BytesIO(decoded), encoding=encoding)
            
            create_database()
            insert_data(df)
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return [[]] * 9
    
    filter_data = get_filter_options()
    return [
        [{'label': str(x), 'value': str(x)} for x in filter_data[col].unique() if pd.notnull(x)]
        for col in filter_data.columns
    ]

# Callback to update charts
@dash.callback(
    [Output('class-premium-table', 'data'),
     Output('class-premium-table', 'columns'),
     Output('weekly-monthly-table', 'data'),
     Output('weekly-monthly-table', 'columns'),
     Output('premium-trend', 'figure'),
     Output('quarterly-progress', 'figure'),
     Output('branch-premium', 'figure'),
     Output('class-comparison-table', 'data'),
     Output('class-comparison-table', 'columns'),
     Output('monthly-comparison-table', 'data'),
     Output('monthly-comparison-table', 'columns')],
    [Input('trans-type-filter', 'value'),
     Input('branch-filter', 'value'),
     Input('class-filter', 'value'),
     Input('year-filter', 'value'),
     Input('intermediary-type-filter', 'value'),
     Input('intermediary-filter', 'value'),
     Input('marketer-filter', 'value'),
     Input('currency-filter', 'value'),
     Input('month-name-filter', 'value'),
     Input('theme-switch', 'value')]
)
def update_charts(trans_type, branches, class_, years, int_type, intermediary, 
                 marketer, currency, month_name, dark_mode):
    conn = sqlite3.connect('insurance_data.db')
    
    # Handle year selection and current/previous year logic
    current_date = datetime.now()
    default_current_year = current_date.year
    
    # If years is None or empty, use default current year
    if not years:
        current_year = default_current_year
        years = [current_year]
    else:
        # If multiple years are selected, use the most recent one as current_year
        current_year = max(years)
    
    previous_year = int(current_year) - 1

    # Build the WHERE clause based on filters
    filters = []
    if trans_type: filters.append(f"[Trans Type] = '{trans_type}'")
    
    # Handle multiple branch selections
    if branches:
        branch_conditions = [f"Branch = '{branch}'" for branch in branches]
        filters.append(f"({' OR '.join(branch_conditions)})")
    
    if class_: filters.append(f"Class = '{class_}'")
    if int_type: filters.append(f"[Intermediary Type] = '{int_type}'")
    if intermediary: filters.append(f"Intermediary = '{intermediary}'")
    if marketer: filters.append(f"Marketer = '{marketer}'")
    if currency: filters.append(f"CURRENCY = '{currency}'")
    if month_name: filters.append(f"[Month Name] = '{month_name}'")
    
    base_where_clause = " AND ".join(filters) if filters else "1=1"
    
    # Weekly-Monthly Premium Analysis
    year_conditions = [f"Year = {year}" for year in years]
    year_where_clause = f"({' OR '.join(year_conditions)})" if year_conditions else f"Year = {current_year}"
    where_clause = f"{base_where_clause} AND {year_where_clause}"
    
    weekly_monthly_query = f"""
    SELECT Weeks,
           SUM(CASE WHEN [Month Name] = 'January' THEN Premium ELSE 0 END) as Jan,
           SUM(CASE WHEN [Month Name] = 'February' THEN Premium ELSE 0 END) as Feb,
           SUM(CASE WHEN [Month Name] = 'March' THEN Premium ELSE 0 END) as Mar,
           SUM(CASE WHEN [Month Name] = 'April' THEN Premium ELSE 0 END) as Apr,
           SUM(CASE WHEN [Month Name] = 'May' THEN Premium ELSE 0 END) as May,
           SUM(CASE WHEN [Month Name] = 'June' THEN Premium ELSE 0 END) as Jun,
           SUM(CASE WHEN [Month Name] = 'July' THEN Premium ELSE 0 END) as Jul,
           SUM(CASE WHEN [Month Name] = 'August' THEN Premium ELSE 0 END) as Aug,
           SUM(CASE WHEN [Month Name] = 'September' THEN Premium ELSE 0 END) as Sep,
           SUM(CASE WHEN [Month Name] = 'October' THEN Premium ELSE 0 END) as Oct,
           SUM(CASE WHEN [Month Name] = 'November' THEN Premium ELSE 0 END) as Nov,
           SUM(CASE WHEN [Month Name] = 'December' THEN Premium ELSE 0 END) as Dec
    FROM insurance_transactions
    WHERE {where_clause}
    GROUP BY Weeks
    ORDER BY Weeks
    """
    weekly_monthly_df = pd.read_sql_query(weekly_monthly_query, conn)
    
    # Format Premium values
    for col in weekly_monthly_df.columns:
        if col != 'Weeks':
            weekly_monthly_df[col] = weekly_monthly_df[col].apply(lambda x: f"{x:,.2f}")
    
    weekly_monthly_data = weekly_monthly_df.to_dict('records')
    weekly_monthly_columns = [{"name": i, "id": i} for i in weekly_monthly_df.columns]
    
    # Class Premium Table
    class_query = f"""
    SELECT Class, SUM(Premium) as Total_Premium
    FROM insurance_transactions
    WHERE {where_clause}
    GROUP BY Class
    """
    class_df = pd.read_sql_query(class_query, conn)
    
    # Format Premium values
    class_df['Total_Premium'] = class_df['Total_Premium'].apply(lambda x: f"{x:,.2f}")
    
    table_data = class_df.to_dict('records')
    table_columns = [{"name": i, "id": i} for i in class_df.columns]
    
    # Premium Trend
    trend_query = f"""
    SELECT [Month Name], SUM(Premium) as Total_Premium
    FROM insurance_transactions
    WHERE {where_clause}
    GROUP BY Month, [Month Name]
    ORDER BY Month
    """
    trend_df = pd.read_sql_query(trend_query, conn)
    trend_line = px.line(trend_df, x='Month Name', y='Total_Premium',
                        title="Premium Trend by Month")
    
    # Quarterly Progress
    quarter_query = f"""
    SELECT Quarter, SUM(Premium) as Total_Premium
    FROM insurance_transactions
    WHERE {where_clause}
    GROUP BY Quarter
    ORDER BY Quarter
    """
    quarter_df = pd.read_sql_query(quarter_query, conn)
    quarter_progress = px.bar(quarter_df, x='Quarter', y='Total_Premium',
                            title="Quarterly Premium Progress")
    
    # Branch Premium
    branch_query = f"""
    SELECT Branch, SUM(Premium) as Total_Premium
    FROM insurance_transactions
    WHERE {where_clause}
    GROUP BY Branch
    """
    branch_df = pd.read_sql_query(branch_query, conn)
    branch_chart = px.bar(branch_df, x='Branch', y='Total_Premium',
                         title="Premium by Branch")
    
    # Update chart layouts
    chart_bg_color = 'rgba(50, 50, 50, 0.8)' if dark_mode else 'rgba(255, 255, 255, 1)'
    font_color = 'white' if dark_mode else 'black'
    
    for chart in [trend_line, quarter_progress, branch_chart]:
        chart.update_layout(
            plot_bgcolor=chart_bg_color,
            paper_bgcolor=chart_bg_color,
            font_color=font_color
        )
    
    # Class Comparison Table
    class_comparison_query = f"""
    SELECT 
        Class, 
        SUM(CASE WHEN Year = {current_year} THEN Premium ELSE 0 END) as Current_Year_Premium,
        SUM(CASE WHEN Year = {previous_year} THEN Premium ELSE 0 END) as Previous_Year_Premium,
        ROUND(
            (SUM(CASE WHEN Year = {current_year} THEN Premium ELSE 0 END) - 
             SUM(CASE WHEN Year = {previous_year} THEN Premium ELSE 0 END)) * 100.0 / 
            NULLIF(SUM(CASE WHEN Year = {previous_year} THEN Premium ELSE 0 END), 0), 
        2) as Percentage_Change
    FROM insurance_transactions
    WHERE {base_where_clause}
    GROUP BY Class
    """
    
    class_comparison_df = pd.read_sql_query(class_comparison_query, conn)
    
    # Format values
    class_comparison_df['Current_Year_Premium'] = class_comparison_df['Current_Year_Premium'].apply(lambda x: f"{x:,.2f}")
    class_comparison_df['Previous_Year_Premium'] = class_comparison_df['Previous_Year_Premium'].apply(lambda x: f"{x:,.2f}")
    class_comparison_df['Percentage_Change'] = class_comparison_df['Percentage_Change'].apply(
    lambda x: f"{x:,.2f}%" if x is not None else "N/A"
)
    
    # Rename columns with specific years
    class_comparison_df.columns = ['Class', f'{current_year} Premium', f'{previous_year} Premium', '% Change']
    
    class_comparison_data = class_comparison_df.to_dict('records')
    class_comparison_columns = [{"name": i, "id": i} for i in class_comparison_df.columns]
    
    # Monthly Comparison Table
    monthly_comparison_query = f"""
    SELECT 
        [Month Name],
        SUM(CASE WHEN Year = {current_year} THEN Premium ELSE 0 END) as Current_Year_Premium,
        SUM(CASE WHEN Year = {previous_year} THEN Premium ELSE 0 END) as Previous_Year_Premium,
        ROUND(
            (SUM(CASE WHEN Year = {current_year} THEN Premium ELSE 0 END) - 
             SUM(CASE WHEN Year = {previous_year} THEN Premium ELSE 0 END)) * 100.0 / 
            NULLIF(SUM(CASE WHEN Year = {previous_year} THEN Premium ELSE 0 END), 0), 
        2) as Percentage_Change
    FROM insurance_transactions
    WHERE {base_where_clause}
    GROUP BY [Month Name]
    ORDER BY 
        CASE [Month Name]
            WHEN 'January' THEN 1
            WHEN 'February' THEN 2
            WHEN 'March' THEN 3
            WHEN 'April' THEN 4
            WHEN 'May' THEN 5
            WHEN 'June' THEN 6
            WHEN 'July' THEN 7
            WHEN 'August' THEN 8
            WHEN 'September' THEN 9
            WHEN 'October' THEN 10
            WHEN 'November' THEN 11
            WHEN 'December' THEN 12
        END
    """
    
    monthly_comparison_df = pd.read_sql_query(monthly_comparison_query, conn)
    
    # Format values
    monthly_comparison_df['Current_Year_Premium'] = monthly_comparison_df['Current_Year_Premium'].apply(lambda x: f"{x:,.2f}")
    monthly_comparison_df['Previous_Year_Premium'] = monthly_comparison_df['Previous_Year_Premium'].apply(lambda x: f"{x:,.2f}")
    monthly_comparison_df['Percentage_Change'] = monthly_comparison_df['Percentage_Change'].apply(
    lambda x: f"{x:,.2f}%" if x is not None else "N/A"
)
    
    # Rename columns with specific years
    monthly_comparison_df.columns = ['Month', f'{current_year} Premium', f'{previous_year} Premium', '% Change']
    
    monthly_comparison_data = monthly_comparison_df.to_dict('records')
    monthly_comparison_columns = [{"name": i, "id": i} for i in monthly_comparison_df.columns]
    
    conn.close()
    
    return (table_data, table_columns, 
            weekly_monthly_data, weekly_monthly_columns,
            trend_line, quarter_progress, branch_chart, 
            class_comparison_data, class_comparison_columns,
            monthly_comparison_data, monthly_comparison_columns)