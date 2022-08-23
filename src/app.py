from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import datetime
from .production import check_if_working_day, calculate_production_time

# Setup app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

PROCESS_NAMES = ["사출", "경화", "냉각", "탈형/조립", "건조", "외주가공", "마무리 작업"]

load_figure_template('LUX')

SIDEBAR_STYLE = {
    "background-color": "#f8f9fa",
}

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

# Sidebar tabs
tab_1 = dcc.Tab(
    label='일반 정보',
    children=[
        html.Br(),
        html.Br(),
        html.H6('제품명'),
        dcc.Input(id='product_name', type='text', value="154kV"),
        html.Br(),
        html.Br(),
        html.H6('필요 개수 [개]'),
        dcc.Input(id='num_joints', type='number', value=1),
        html.Br(),
        html.Br(),
        html.H6('작업 시작 일 (예시: 2022-08-01)'),
        dcc.Input(id='start_time', type='text', value='2022-08-01'),
        html.Br(),
        html.Br(),
        html.H6('작업 시작 가능 시간(Early) [시]'),
        dcc.Input(id='working_time_min', type='number', value=9),
        html.Br(),
        html.Br(),
        html.H6('작업 시작 가능 시간(Late) [시]'),
        dcc.Input(id='working_time_max', type='number', value=16),
    ], style=tab_style, selected_style=tab_selected_style,
)

tab_2 =dcc.Tab(
    label='소요시간',
    children=[
        html.Br(),
        html.Br(),
        html.H6('사출 [시간]'),
        dcc.Input(id='injection_time', type='number', value=1),
        html.Br(),
        html.Br(),
        html.H6('경화 [시간]'),
        dcc.Input(id='curing_time', type='number', value=1),
        html.Br(),
        html.Br(),
        html.H6('냉각 [시간]'),
        dcc.Input(id='cooling_time', type='number', value=1),
        html.Br(),
        html.Br(),
        html.H6('탈형 및 금형 조립 [시간]'),
        dcc.Input(id='mold_reset_time', type='number', value=1),
        html.Br(),
        html.Br(),
        html.H6('금형 예열 [시간]'),
        dcc.Input(id='mold_preheating_time', type='number', value=1),
        html.Br(),
        html.Br(),
        html.H6('제품 건조 [일]'),
        dcc.Input(id='drying_time', type='number', value=1),
        html.Br(),
        html.Br(),
        html.H6('외주 가공 [일]'),
        dcc.Input(id='outsourcing_time', type='number', value=1),
        html.Br(),
        html.Br(),
        html.H6('마무리(그라인딩, 차폐 몰딩, 세척/포장 등)[일]'),
        dcc.Input(id='final_touch_time', type='number', value=1),
    ], style=tab_style, selected_style=tab_selected_style,
)

tab_3 = dcc.Tab(
    label='근태 계획',
    children=[
        html.Br(),
        html.Br(),
        html.H6('토요일 근무'),
        dcc.RadioItems(
            options=[
                {'label': "한다", 'value': True},
                {'label': "안한다", 'value': False}
            ],
            value=False,
            id='work_on_saturday',
            labelStyle={'display': 'block'}
        ),
        html.Br(),
        html.Br(),
        html.H6('일요일 근무'),
        dcc.RadioItems(
            options=[
                {'label': "한다", 'value': True},
                {'label': "안한다", 'value': False}
            ],
            value=False,
            style={"margin-right": "15px"},
            id='work_on_sunday',
            labelStyle={'display': 'block'}
        ),
        html.Br(),
        html.Br(),
        html.H6('공휴일 근무'),
        dcc.RadioItems(
            options=[
                {'label': "한다", 'value': True},
                {'label': "안한다", 'value': False}
            ],
            value=False,
            id='work_on_holiday',
            labelStyle={'display': 'block'}
        ),
        html.Br(),
        html.Br(),
        html.H6('3교대 (잠 안자고 휴일 안쉬고;;)'),
        dcc.RadioItems(
            options=[
                {'label': "한다", 'value': True},
                {'label': "안한다", 'value': False}
            ],
            value=False,
            id='three_day_shift',
            labelStyle={'display': 'block'}
        ),
    ], style=tab_style, selected_style=tab_selected_style,
)

# plotly plot
plotly_plot = html.Iframe(
    id='production_schedule_plot',
    style={'border-width': '0', 'width': 1100, 'height': 1100}
    )

## App Layout

app.layout = dbc.Container(
    [
        
        html.H1('Production Schedule', style={'textAlign': 'center'}),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Tabs(
                        [
                            tab_1,
                            tab_2,
                            tab_3,
                        ]
                        ),
                    ],
                    md=4,
                    style=SIDEBAR_STYLE,
                ),
                dbc.Col(
                    [
                        plotly_plot,
                        html.H6('Note: 커서를 그래프에 대면 상세 일정 조회가 가능합니다.', style={'textAlign': 'center'}),
                    ],
                    md=8
                )
            ]
        )
    ]
)

# Setup callbacks/backend
@app.callback(
    Output('production_schedule_plot', 'srcDoc'),
    Input('product_name', 'value'),
    Input('num_joints', 'value'),
    Input('start_time', 'value'),
    Input('working_time_min', 'value'),
    Input('working_time_max', 'value'),
    Input('injection_time', 'value'),
    Input('curing_time', 'value'),
    Input('cooling_time', 'value'),
    Input('mold_reset_time', 'value'),
    Input('mold_preheating_time', 'value'),
    Input('drying_time', 'value'),
    Input('outsourcing_time', 'value'),
    Input('final_touch_time', 'value'),
    Input('work_on_saturday', 'value'),
    Input('work_on_sunday', 'value'),
    Input('work_on_holiday', 'value'),
    Input('three_day_shift', 'value'),

)
def show_schedule(
    product_name, num_joints, start_time, working_time_min, working_time_max,
    injection_time, curing_time, cooling_time, mold_reset_time, mold_preheating_time, 
    drying_time, outsourcing_time, final_touch_time, work_on_saturday, work_on_sunday,
    work_on_holiday, three_day_shift
):
    df = calculate_production_time(
        num_joints, start_time, injection_time, curing_time, cooling_time, mold_reset_time,
        mold_preheating_time, drying_time, outsourcing_time, final_touch_time,
        working_time_min, working_time_max,
        work_on_saturday=work_on_saturday, work_on_sunday=work_on_sunday, 
        work_on_holiday=work_on_holiday, three_day_shift=three_day_shift,
    )
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Process", color="Number")
    fig.update_yaxes(autorange="reversed", title="공정 순서", title_font_size=20)
    fig.update_xaxes(title="시간", title_font_size=20, dtick="d1")
    fig.update_layout(autosize=False, height=1000, width=1000, 
                    title=f"{product_name} 제조 계획", title_font_size=30, title_x=0.5,
                    showlegend=False)
    output = fig.to_html()

    return output

if __name__ == '__main__':
    app.run_server(debug=True)