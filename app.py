import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from dash_iconify import DashIconify
import requests
from dash.exceptions import PreventUpdate


dashapp = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/style.css'],  use_pages=True, suppress_callback_exceptions=True)



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

# Initialize the Dash app with dark theme and Bootstrap
chat_interface = dbc.Collapse(
    dbc.Card([
        dbc.CardBody([
            html.Div([
                # Chat messages container
                html.Div([
                    # Initial welcome message
                    html.Div([
                        html.Img(src="/assets/pic.png", className="chat-avatar"),
                        html.Div([
                            html.P("Hi! I'm your dashboard assistant. How can I help you today?", 
                                  className="small p-2 ms-3 mb-1 rounded-3 bg-secondary text-white")
                        ])
                    ], className="d-flex flex-row justify-content-start mb-4")
                ], id="chat-messages", className="chat-container"),
                
                # Message input area
                html.Div([
                    dbc.Input(
                        type="text",
                        id="chat-input",
                        placeholder="Type your message...",
                        className="chat-input"
                    ),
                    dbc.Button([
                        DashIconify(icon="fa:paper-plane", width=20)
                    ], 
                    id="send-button",
                    color="secondary",
                    className="ms-2"
                    )
                ], className="d-flex align-items-center p-3")
            ])
        ], className="chat-body")
    ], className="chat-card", id="chat4"),
    id="chat-collapse",
    is_open=False,
    
)

chat_toggle = dbc.Button(
    [
        DashIconify(icon="fa:comments", width=15),
        html.Span("Chat Assistant", className="ms-2")
    ],
    id="chat-toggle",
    color="secondary",
    className="chat-toggle-btn",
)

# Database functions

navbar = dbc.Navbar(
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="/")),
        dbc.NavItem(dbc.NavLink("Brokers", href="/brokers")),
         dbc.NavItem(dbc.NavLink("Reinsurance", href="/reinsurance")),
          dbc.NavItem(dbc.NavLink("Agents", href="/agents")),
          dbc.NavItem(dbc.NavLink("Direct", href="/direct")),
        dbc.NavItem(dbc.NavLink("Data/Delete", href="/data")),
        # dbc.NavItem(dbc.NavLink("Assistant", href="/ai")),
    ],
    # brand="Insurance Analytics",
    # brand_href="/",
    color="dark",
    dark=True,
    # className="dark mb-4 bg-dark"
)
# color_mode_switch =  html.Span(
#     [
#         dbc.Label(className="fa fa-moon", html_for="switch"),
#         dbc.Switch( id="switch", value=True, className="d-inline-block ms-1", persistence=True),
#         dbc.Label(className="fa fa-sun", html_for="switch"),
#     ]
# )


dashapp.layout = dbc.Container([
    # color_mode_switch,
    navbar,
dbc.Row([
    dbc.Col([
        html.Div([
            dbc.Card([
                dbc.CardBody([
                    dbc.Switch(
                        id='theme-switch',
                        label=DashIconify(icon="ph:moon-fill", width=20),
                        value=True,
                        className='theme-switch'
                    )
                ])
            ], className='theme-switch-card')
        ], className='theme-switch-container')
    ], width=12)
], className="mb-4"),
        
    dbc.Row([
        dbc.Col(html.H1("Bedrock Insurance Dashboard", className="text-center text-light mb-4"), width=12)
    ]),
    
    dash.page_container,
    
    html.Div([
        chat_interface,
        chat_toggle
    ], className="chat-container-fixed"),
    
    dcc.Store(id='response-store', data=''),
    dcc.Store(id='user-input-store', data=''),
    dcc.Interval(id='stream-update', interval=100, disabled=True),
    
], fluid=True, className='app-container', id='main-container')


@dashapp.callback(
    [Output('main-container', 'className'),
     Output('class-premium-table', 'style_header'),
     Output('class-premium-table', 'style_cell'),
     Output('weekly-monthly-table', 'style_header'),
     Output('weekly-monthly-table', 'style_cell')
     ],
    [Input('theme-switch', 'value')]
)
def update_theme(dark_mode):
    if dark_mode:
        container_class = 'app-container dark-theme'
        table_header = {
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white',
            
        }
        table_cell = {
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white',
            'border': '1px solid rgb(70, 70, 70)'
        }
    else:
        container_class = 'app-container light-theme'
        table_header = {
            'backgroundColor': 'rgb(240, 240, 240)',
            'color': 'black',
            'fontWeight': 'bold'
        }
        table_cell = {
            'backgroundColor': 'white',
            'color': 'black',
            'border': '1px solid rgb(200, 200, 200)'
        }
    
    return container_class, table_header, table_cell, table_header, table_cell

# app.clientside_callback(
#     """
#     (switchOn) => {
#         document.documentElement.setAttribute("data-bs-theme", switchOn ? "light" : "dark");
#         return window.dash_clientside.no_update
#     }
#     """,
   
#     Output("switch", "id"),
#     Input("switch", "value"),
# )
@dash.callback(
    Output("chat-collapse", "is_open"),
    Input("chat-toggle", "n_clicks"),
    State("chat-collapse", "is_open"),
)
def toggle_chat(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@dash.callback(
    [Output("chat-messages", "children", allow_duplicate=True),
     Output("chat-input", "value"),
     Output("user-input-store", "data")],
    [Input("send-button", "n_clicks"),
     Input("chat-input", "n_submit")],
    [State("chat-input", "value"),
     State("chat-messages", "children")],
    prevent_initial_call=True
)
def send_message(n_clicks, n_submit, user_input, existing_messages):
    """Add user message and typing indicator"""
    if (not n_clicks and not n_submit) or not user_input:
        raise PreventUpdate
    
    if existing_messages is None:
        existing_messages = []
    elif not isinstance(existing_messages, list):
        existing_messages = [existing_messages]
    
    # User message
    user_message = html.Div([
        html.Div([
            html.P(user_input, className="small p-2 me-3 mb-1 text-white rounded-3 bg-success"),
        ], className="chat-message-right"),
    ], className="d-flex flex-row justify-content-end mb-4")
    
    # Typing indicator
    typing_indicator = html.Div([
        html.Img(src="/assets/pic.png", className="chat-avatar"),
        html.Div([
            html.Div(className="typing-dot", style={"animationDelay": "0s"}),
            html.Div(className="typing-dot", style={"animationDelay": "0.2s"}),
            html.Div(className="typing-dot", style={"animationDelay": "0.4s"}),
        ], className="typing-indicator")
    ], className="d-flex flex-row justify-content-start mb-4")
    
    new_messages = existing_messages + [user_message, typing_indicator]
    return new_messages, "", user_input

# Update the response handler callback
@dash.callback(
    Output("chat-messages", "children", allow_duplicate=True),
    Input("user-input-store", "data"),
    [State("chat-messages", "children")],
    prevent_initial_call=True
)
def get_assistant_response(user_input, existing_messages):
    """Handle AI response and replace typing indicator"""
    if not user_input or not existing_messages:
        raise PreventUpdate
    
    try:
        # Remove typing indicator (last element)
        existing_messages = existing_messages[:-1]
        
        # Make API call
        response = requests.post(
            "http://localhost:8000/chat",
            json={"message": user_input}
        )
        response.raise_for_status()
        assistant_response = response.json().get("response", "No response found.")
        # assistant_response = markdownify.markdownify(assistant_response)
        
        # Assistant message
        assistant_message = html.Div([
            html.Img(src="/assets/pic.png", className="chat-avatar"),
            html.Div([
                html.P(assistant_response,
                      className="small p-2 ms-3 mb-1 rounded-3 bg-secondary text-white")
            ])
        ], className="d-flex flex-row justify-content-start mb-4")
        
        return existing_messages + [assistant_message]
    
    except Exception as e:
        # Error message
        error_message = html.Div([
            html.Img(src="/assets/pic.png", className="chat-avatar"),
            html.Div([
                html.P(f"I'm sorry, I encountered an error: {str(e)}",
                      className="small p-2 ms-3 mb-1 rounded-3 bg-danger text-white")
            ])
        ], className="d-flex flex-row justify-content-start mb-4")
        
        return existing_messages + [error_message]




if __name__ == '__main__':
    create_database()
    dashapp.run_server(host='0.0.0.0', port=8050, debug=False)