import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dash import dash_table
import pandas as pd
import sqlite3
from datetime import datetime
from dash.exceptions import PreventUpdate
import io

dash.register_page(__name__, path='/data')

def get_filter_options():
    """Get all filter options from the database"""
    conn = sqlite3.connect('insurance_data.db')
    
    # Get unique values for each filter
    filters = {
        'years': pd.read_sql_query('SELECT DISTINCT Year FROM insurance_transactions ORDER BY Year', conn)['Year'].tolist(),
        'months': pd.read_sql_query('SELECT DISTINCT Month, "Month Name" FROM insurance_transactions ORDER BY Month', conn).to_dict('records'),
        'weeks': pd.read_sql_query('SELECT DISTINCT Weeks FROM insurance_transactions ORDER BY Weeks', conn)['Weeks'].tolist(),
        'intermediary_types': pd.read_sql_query('SELECT DISTINCT "Intermediary Type" FROM insurance_transactions ORDER BY "Intermediary Type"', conn)['Intermediary Type'].tolist(),
        'intermediaries': pd.read_sql_query('SELECT DISTINCT Intermediary FROM insurance_transactions ORDER BY Intermediary', conn)['Intermediary'].tolist(),
        'classes': pd.read_sql_query('SELECT DISTINCT Class FROM insurance_transactions ORDER BY Class', conn)['Class'].tolist()
    }
    
    conn.close()
    return filters

def build_filter_section():
    """Create the filter section with all dropdowns"""
    filters = get_filter_options()
    
    return dbc.Card([
        dbc.CardHeader(html.H5("Data Filters")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Year", className='text-light mb-2'),
                    dcc.Dropdown(
                        id='year-filter',
                        options=[{'label': str(year), 'value': year} for year in filters['years']],
                        multi=True,
                        className='mb-3'
                    )
                ], width=4),
                dbc.Col([
                    html.Label("Month", className='text-light mb-2'),
                    dcc.Dropdown(
                        id='month-filter',
                        options=[{'label': month['Month Name'], 'value': month['Month']} for month in filters['months']],
                        multi=True,
                        className='mb-3'
                    )
                ], width=4),
                dbc.Col([
                    html.Label("Week", className='text-light mb-2'),
                    dcc.Dropdown(
                        id='week-filter',
                        options=[{'label': f'Week {week}', 'value': week} for week in filters['weeks']],
                        multi=True,
                        className='mb-3'
                    )
                ], width=4)
            ]),
            dbc.Row([
                dbc.Col([
                    html.Label("Intermediary Type", className='text-light mb-2'),
                    dcc.Dropdown(
                        id='intermediary-type-filter',
                        options=[{'label': itype, 'value': itype} for itype in filters['intermediary_types']],
                        multi=True,
                        className='mb-3'
                    )
                ], width=4),
                dbc.Col([
                    html.Label("Intermediary", className='text-light mb-2'),
                    dcc.Dropdown(
                        id='intermediary-filter',
                        options=[{'label': intermediary, 'value': intermediary} for intermediary in filters['intermediaries']],
                        multi=True,
                        className='mb-3'
                    )
                ], width=4),
                dbc.Col([
                    html.Label("Class", className='text-light mb-2'),
                    dcc.Dropdown(
                        id='class-filter',
                        options=[{'label': class_name, 'value': class_name} for class_name in filters['classes']],
                        multi=True,
                        className='mb-3'
                    )
                ], width=4)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Apply Filters", id="apply-filters", color="primary", className="me-2"),
                    dbc.Button("Delete Filtered Data", id="delete-data", color="danger", className="me-2"),
                    dbc.Button("Download Excel", id="download-excel", color="success", className="me-2"),
                    dcc.Download(id="download-dataframe-xlsx"),
                    dbc.Modal([
                        dbc.ModalHeader("Confirm Deletion"),
                        dbc.ModalBody("Are you sure you want to delete the filtered data? This action cannot be undone."),
                        dbc.ModalFooter([
                            dbc.Button("Cancel", id="cancel-delete", className="me-2"),
                            dbc.Button("Delete", id="confirm-delete", color="danger")
                        ])
                    ], id="delete-modal",
                    class_name='text-dark',
                    is_open=False)
                ])
            ])
        ])
    ], className="mb-4")

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Data Management", className="text-center text-light mb-4")
        ])
    ]),
    
    build_filter_section(),
    
    dbc.Row([
        dbc.Col([
            html.Div(id="filter-summary", className="mb-3"),
            dash_table.DataTable(
                id='filtered-data-table',
                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)',
                    'fontWeight': 'bold',
                    'color': 'white'
                },
                style_data={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white'
                },
                page_size=10,
                style_table={'overflowX': 'auto'}
            )
        ])
    ])
], fluid=True)

def get_filtered_data(years, months, weeks, i_types, intermediaries, classes):
    """Helper function to get filtered data"""
    conn = sqlite3.connect('insurance_data.db')
    
    conditions = []
    if years and any(years):
        years_str = ','.join(str(y) for y in years)
        conditions.append(f"Year IN ({years_str})")
    if months and any(months):
        months_str = ','.join(str(m) for m in months)
        conditions.append(f"Month IN ({months_str})")
    if weeks and any(weeks):
        weeks_str = ','.join(str(w) for w in weeks)
        conditions.append(f"Weeks IN ({weeks_str})")
    if i_types and any(i_types):
        i_types_str = ','.join("'" + str(t).replace("'", "''") + "'" for t in i_types)
        conditions.append(f'"Intermediary Type" IN ({i_types_str})')
    if intermediaries and any(intermediaries):
        intermediaries_str = ','.join("'" + str(i).replace("'", "''") + "'" for i in intermediaries)
        conditions.append(f"Intermediary IN ({intermediaries_str})")
    if classes and any(classes):
        classes_str = ','.join("'" + str(c).replace("'", "''") + "'" for c in classes)
        conditions.append(f"Class IN ({classes_str})")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    query = f"SELECT * FROM insurance_transactions WHERE {where_clause}"
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@callback(
    Output("download-dataframe-xlsx", "data"),
    Input("download-excel", "n_clicks"),
    [State('year-filter', 'value'),
     State('month-filter', 'value'),
     State('week-filter', 'value'),
     State('intermediary-type-filter', 'value'),
     State('intermediary-filter', 'value'),
     State('class-filter', 'value')],
    prevent_initial_call=True
)
def download_xlsx(n_clicks, years, months, weeks, i_types, intermediaries, classes):
    if not n_clicks:
        raise PreventUpdate
    
    df = get_filtered_data(years, months, weeks, i_types, intermediaries, classes)
    
    # Create a formatted Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Insurance Data', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Insurance Data']
        
        # Add formats
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'bg_color': '#D3D3D3',
            'border': 1
        })
        
        # Format the header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)  # Set column width
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return dcc.send_bytes(output.getvalue(), f"insurance_data_{timestamp}.xlsx")

@callback(
    [Output('filtered-data-table', 'data'),
     Output('filtered-data-table', 'columns'),
     Output('filter-summary', 'children')],
    [Input('apply-filters', 'n_clicks')],
    [State('year-filter', 'value'),
     State('month-filter', 'value'),
     State('week-filter', 'value'),
     State('intermediary-type-filter', 'value'),
     State('intermediary-filter', 'value'),
     State('class-filter', 'value')]
)
def update_filtered_data(n_clicks, years, months, weeks, i_types, intermediaries, classes):
    if not n_clicks:
        # Return initial empty state or all data
        conn = sqlite3.connect('insurance_data.db')
        df = pd.read_sql_query('SELECT * FROM insurance_transactions', conn)
        conn.close()
        return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], f"Showing all {len(df)} records"
    
    conn = sqlite3.connect('insurance_data.db')
    
    # Build where clause
    conditions = []
    if years and any(years):
        years_str = ','.join(str(y) for y in years)
        conditions.append(f"Year IN ({years_str})")
    if months and any(months):
        months_str = ','.join(str(m) for m in months)
        conditions.append(f"Month IN ({months_str})")
    if weeks and any(weeks):
        weeks_str = ','.join(str(w) for w in weeks)
        conditions.append(f"Weeks IN ({weeks_str})")
    if i_types and any(i_types):
        i_types_str = ','.join("'" + str(t).replace("'", "''") + "'" for t in i_types)
        conditions.append(f'"Intermediary Type" IN ({i_types_str})')
    if intermediaries and any(intermediaries):
        intermediaries_str = ','.join("'" + str(i).replace("'", "''") + "'" for i in intermediaries)
        conditions.append(f"Intermediary IN ({intermediaries_str})")
    if classes and any(classes):
        classes_str = ','.join("'" + str(c).replace("'", "''") + "'" for c in classes)
        conditions.append(f"Class IN ({classes_str})")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
    SELECT * FROM insurance_transactions
    WHERE {where_clause}
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        
        # Create filter summary
        filter_summary = []
        if years and any(years): filter_summary.append(f"Years: {', '.join(map(str, years))}")
        if months and any(months): filter_summary.append(f"Months: {', '.join(map(str, months))}")
        if weeks and any(weeks): filter_summary.append(f"Weeks: {', '.join(map(str, weeks))}")
        if i_types and any(i_types): filter_summary.append(f"Intermediary Types: {', '.join(i_types)}")
        if intermediaries and any(intermediaries): filter_summary.append(f"Intermediaries: {', '.join(intermediaries)}")
        if classes and any(classes): filter_summary.append(f"Classes: {', '.join(classes)}")
        
        summary_text = f"Showing {len(df)} records with filters: " + "; ".join(filter_summary) if filter_summary else f"Showing all {len(df)} records"
        
        return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], summary_text
    
    except Exception as e:
        print(f"Error executing query: {e}")
        return [], [], "Error filtering data"
    
    finally:
        conn.close()
        
        


@callback(
    [Output("delete-modal", "is_open"),
     Output('apply-filters', 'n_clicks')],  # Add this to trigger filter refresh
    [Input("delete-data", "n_clicks"),
     Input("cancel-delete", "n_clicks"),
     Input("confirm-delete", "n_clicks")],
    [State("delete-modal", "is_open"),
     State('year-filter', 'value'),
     State('month-filter', 'value'),
     State('week-filter', 'value'),
     State('intermediary-type-filter', 'value'),
     State('intermediary-filter', 'value'),
     State('class-filter', 'value')]
)
def toggle_delete_modal(delete_n, cancel_n, confirm_n, is_open, years, months, weeks, i_types, intermediaries, classes):
    triggered_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == "confirm-delete" and confirm_n:
        conn = sqlite3.connect('insurance_data.db')
        cursor = conn.cursor()
        
        # Build where clause
        conditions = []
        if years and any(years):
            years_str = ','.join(str(y) for y in years)
            conditions.append(f"Year IN ({years_str})")
        if months and any(months):
            months_str = ','.join(str(m) for m in months)
            conditions.append(f"Month IN ({months_str})")
        if weeks and any(weeks):
            weeks_str = ','.join(str(w) for w in weeks)
            conditions.append(f"Weeks IN ({weeks_str})")
        if i_types and any(i_types):
            i_types_str = ','.join("'" + str(t).replace("'", "''") + "'" for t in i_types)
            conditions.append(f'"Intermediary Type" IN ({i_types_str})')
        if intermediaries and any(intermediaries):
            intermediaries_str = ','.join("'" + str(i).replace("'", "''") + "'" for i in intermediaries)
            conditions.append(f"Intermediary IN ({intermediaries_str})")
        if classes and any(classes):
            classes_str = ','.join("'" + str(c).replace("'", "''") + "'" for c in classes)
            conditions.append(f"Class IN ({classes_str})")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        delete_query = f"""
        DELETE FROM insurance_transactions
        WHERE {where_clause}
        """
        
        cursor.execute(delete_query)
        conn.commit()
        conn.close()
        
        # Return False for modal and increment n_clicks to trigger filter refresh
        return False, (confirm_n or 0) + 1
    
    elif triggered_id in ["delete-data", "cancel-delete"]:
        return not is_open, dash.no_update
    
    return is_open, dash.no_update












# @callback(
#     [Output('filtered-data-table', 'data'),
#      Output('filtered-data-table', 'columns'),
#      Output('filter-summary', 'children')],
#     [Input('apply-filters', 'n_clicks')],
#     [State('year-filter', 'value'),
#      State('month-filter', 'value'),
#      State('week-filter', 'value'),
#      State('intermediary-type-filter', 'value'),
#      State('intermediary-filter', 'value'),
#      State('class-filter', 'value')]
# )
# def update_filtered_data(n_clicks, years, months, weeks, i_types, intermediaries, classes):
#     if not n_clicks:
#         # Return initial empty state or all data
#         conn = sqlite3.connect('insurance_data.db')
#         df = pd.read_sql_query('SELECT * FROM insurance_transactions', conn)
#         conn.close()
#         return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], f"Showing all {len(df)} records"
    
#     conn = sqlite3.connect('insurance_data.db')
    
#     # Build where clause
#     conditions = []
#     if years and any(years):
#         years_str = ','.join(str(y) for y in years)
#         conditions.append(f"Year IN ({years_str})")
#     if months and any(months):
#         months_str = ','.join(str(m) for m in months)
#         conditions.append(f"Month IN ({months_str})")
#     if weeks and any(weeks):
#         weeks_str = ','.join(str(w) for w in weeks)
#         conditions.append(f"Weeks IN ({weeks_str})")
#     if i_types and any(i_types):
#         i_types_str = ','.join("'" + str(t).replace("'", "''") + "'" for t in i_types)
#         conditions.append(f'"Intermediary Type" IN ({i_types_str})')
#     if intermediaries and any(intermediaries):
#         intermediaries_str = ','.join("'" + str(i).replace("'", "''") + "'" for i in intermediaries)
#         conditions.append(f"Intermediary IN ({intermediaries_str})")
#     if classes and any(classes):
#         classes_str = ','.join("'" + str(c).replace("'", "''") + "'" for c in classes)
#         conditions.append(f"Class IN ({classes_str})")
    
#     where_clause = " AND ".join(conditions) if conditions else "1=1"
    
#     query = f"""
#     SELECT * FROM insurance_transactions
#     WHERE {where_clause}
#     """
    
#     print("Executing query:", query)  # For debugging
    
#     try:
#         df = pd.read_sql_query(query, conn)
        
#         # Create filter summary
#         filter_summary = []
#         if years and any(years): filter_summary.append(f"Years: {', '.join(map(str, years))}")
#         if months and any(months): filter_summary.append(f"Months: {', '.join(map(str, months))}")
#         if weeks and any(weeks): filter_summary.append(f"Weeks: {', '.join(map(str, weeks))}")
#         if i_types and any(i_types): filter_summary.append(f"Intermediary Types: {', '.join(i_types)}")
#         if intermediaries and any(intermediaries): filter_summary.append(f"Intermediaries: {', '.join(intermediaries)}")
#         if classes and any(classes): filter_summary.append(f"Classes: {', '.join(classes)}")
        
#         summary_text = f"Showing {len(df)} records with filters: " + "; ".join(filter_summary) if filter_summary else f"Showing all {len(df)} records"
        
#         return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], summary_text
    
#     except Exception as e:
#         print(f"Error executing query: {e}")  # For debugging
#         return [], [], "Error filtering data"
    
#     finally:
#         conn.close()
# # @callback(
# #     [Output('filtered-data-table', 'data'),
# #      Output('filtered-data-table', 'columns'),
# #      Output('filter-summary', 'children')],
# #     [Input('apply-filters', 'n_clicks')],
# #     [State('year-filter', 'value'),
# #      State('month-filter', 'value'),
# #      State('week-filter', 'value'),
# #      State('intermediary-type-filter', 'value'),
# #      State('intermediary-filter', 'value'),
# #      State('class-filter', 'value')]
# # )


# # @callback(
# #     Output('delete-data', 'disabled'),
# #     [Input('confirm-delete', 'n_clicks')],
# #     [State('year-filter', 'value'),
# #      State('month-filter', 'value'),
# #      State('week-filter', 'value'),
# #      State('intermediary-type-filter', 'value'),
# #      State('intermediary-filter', 'value'),
# #      State('class-filter', 'value')]
# # )
# # def delete_filtered_data(n_clicks, years, months, weeks, i_types, intermediaries, classes):
# #     if not n_clicks:
# #         raise PreventUpdate
    
# #     conn = sqlite3.connect('insurance_data.db')
# #     cursor = conn.cursor()
    
# #     # Build where clause
# #     conditions = []
# #     if years:
# #         years_str = ','.join(str(y) for y in years)
# #         conditions.append(f"Year IN ({years_str})")
# #     if months:
# #         months_str = ','.join(str(m) for m in months)
# #         conditions.append(f"Month IN ({months_str})")
# #     if weeks:
# #         weeks_str = ','.join(str(w) for w in weeks)
# #         conditions.append(f"Weeks IN ({weeks_str})")
# #     if i_types:
# #         i_types_str = ','.join("'" + str(t).replace("'", "''") + "'" for t in i_types)
# #         conditions.append(f'"Intermediary Type" IN ({i_types_str})')
# #     if intermediaries:
# #         intermediaries_str = ','.join("'" + str(i).replace("'", "''") + "'" for i in intermediaries)
# #         conditions.append(f"Intermediary IN ({intermediaries_str})")
# #     if classes:
# #         classes_str = ','.join("'" + str(c).replace("'", "''") + "'" for c in classes)
# #         conditions.append(f"Class IN ({classes_str})")
    
# #     where_clause = " AND ".join(conditions) if conditions else "1=1"
    
# #     delete_query = f"""
# #     DELETE FROM insurance_transactions
# #     WHERE {where_clause}
# #     """
    
# #     cursor.execute(delete_query)
# #     conn.commit()
# #     conn.close()
# @callback(
#     [Output("delete-modal", "is_open"),
#      Output("data-table", "data"),
#      Output("data-table", "columns"),
#      Output("status-message", "children")
#      ],  # Add this output
#     [Input("delete-data", "n_clicks"),
#      Input("cancel-delete", "n_clicks"),
#      Input("confirm-delete", "n_clicks")],
#     [State("delete-modal", "is_open"),
#      State('year-filter', 'value'),
#      State('month-filter', 'value'),
#      State('week-filter', 'value'),
#      State('intermediary-type-filter', 'value'),
#      State('intermediary-filter', 'value'),
#      State('class-filter', 'value')]
# )

# def toggle_delete_modal(delete_n, cancel_n, confirm_n, is_open, years, months, weeks, i_types, intermediaries, classes):
#     triggered_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    
#     if triggered_id == "confirm-delete" and confirm_n:
#         # Perform deletion
#         conn = sqlite3.connect('insurance_data.db')
#         cursor = conn.cursor()
        
#         # Build where clause
#         conditions = []
#         if years:
#             years_str = ','.join(str(y) for y in years)
#             conditions.append(f"Year IN ({years_str})")
#         if months:
#             months_str = ','.join(str(m) for m in months)
#             conditions.append(f"Month IN ({months_str})")
#         if weeks:
#             weeks_str = ','.join(str(w) for w in weeks)
#             conditions.append(f"Weeks IN ({weeks_str})")
#         if i_types:
#             i_types_str = ','.join("'" + str(t).replace("'", "''") + "'" for t in i_types)
#             conditions.append(f'"Intermediary Type" IN ({i_types_str})')
#         if intermediaries:
#             intermediaries_str = ','.join("'" + str(i).replace("'", "''") + "'" for i in intermediaries)
#             conditions.append(f"Intermediary IN ({intermediaries_str})")
#         if classes:
#             classes_str = ','.join("'" + str(c).replace("'", "''") + "'" for c in classes)
#             conditions.append(f"Class IN ({classes_str})")
        
#         where_clause = " AND ".join(conditions) if conditions else "1=1"
        
#         delete_query = f"""
#         DELETE FROM insurance_transactions
#         WHERE {where_clause}
#         """
        
#         cursor.execute(delete_query)
#         conn.commit()
        
#         # Get updated data for table
#         query = "SELECT * FROM insurance_transactions"
#         df = pd.read_sql_query(query, conn)
#         conn.close()
        
#         return False, df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], f"Showing all {len(df)} records"
    
#     elif triggered_id in ["delete-data", "cancel-delete"]:
#         return not is_open, dash.no_update, dash.no_update, dash.no_update
    
#     return is_open, dash.no_update, dash.no_update, dash.no_update

# # Remove the separate delete callback since we've merged it into the modal callback