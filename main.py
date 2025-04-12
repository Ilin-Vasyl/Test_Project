import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html
import warnings

warnings.filterwarnings('ignore')

# Инициализация приложения
app = Dash(__name__)
server = app.server

# Загрузка данных
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'deals.pkl')
deals = pd.read_pickle(DATA_PATH)


# Функция подготовки данных
def prepare_data():
    # Данные для менеджеров
    owner_stats = deals.groupby('Deal_Owner_Name').agg(
        total=('Stage', 'count'),
        payment_done=('Stage', lambda x: (x == 'Payment Done').sum()),
        deal_amount_sum=('Offer_Total_Amount', lambda x: x[x > 0].sum())
    ).reset_index()
    owner_stats['conversion_rate'] = (owner_stats['payment_done'] / owner_stats['total'] * 100).round(2)

    # Данные для рекламы
    ad_stats = deals.groupby('Ad').agg(
        total=('Stage', 'count'),
        payment_done=('Stage', lambda x: (x == 'Payment Done').sum()),
        deal_amount_sum=('Offer_Total_Amount', lambda x: x[x > 0].sum())
    ).reset_index()
    ad_stats['conversion_rate'] = (ad_stats['payment_done'] / ad_stats['total'] * 100).round(2)

    # Данные для продуктов
    paid_deals = deals[(deals['Stage'] == 'Payment Done') & (deals['Offer_Total_Amount'] > 0)]
    product_sum = paid_deals.pivot_table(index='Product', columns='Education_Type',
                                         values='Offer_Total_Amount', aggfunc='sum').drop(index='NoData')
    product_count = paid_deals.pivot_table(index='Product', columns='Education_Type',
                                           values='Offer_Total_Amount', aggfunc='count').drop(index='NoData')

    return owner_stats, ad_stats, product_sum, product_count


# Создание графиков
def create_figures(owner_stats, ad_stats, product_sum, product_count):
    fig = make_subplots(
        rows=2, cols=2,
        specs=[
            [{'type': 'xy', 'secondary_y': True}, {'type': 'xy', 'secondary_y': True}],
            [{'type': 'xy'}, {'type': 'xy'}]
        ],
        subplot_titles=(
            'Эффективность работы менеджеров',
            'Эффективность рекламных компаний',
            'Распределение по сумме контрактов',
            'Распределение по количеству контрактов'
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    # График 1: Менеджеры
    fig.add_trace(
        go.Bar(
            x=owner_stats['Deal_Owner_Name'],
            y=owner_stats['total'],
            name='Клиенты',
            marker_color='#1f77b4',
            text=owner_stats['conversion_rate'].astype(str) + '%',
            textposition='outside'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=owner_stats['Deal_Owner_Name'],
            y=owner_stats['deal_amount_sum'],
            name='Сумма договоров',
            line=dict(color='#ff7f0e', width=2),
            mode='lines+markers'
        ),
        row=1, col=1,
        secondary_y=True
    )

    # График 2: Реклама
    fig.add_trace(
        go.Bar(
            x=ad_stats['Ad'],
            y=ad_stats['total'],
            name='Клиенты',
            marker_color='#1f77b4',
            text=ad_stats['conversion_rate'].astype(str) + '%',
            textposition='outside',
            showlegend=False
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Scatter(
            x=ad_stats['Ad'],
            y=ad_stats['deal_amount_sum'],
            name='Сумма договоров',
            line=dict(color='#ff7f0e', width=2),
            mode='lines+markers',
            showlegend=False
        ),
        row=1, col=2,
        secondary_y=True
    )

    # График 3: Сумма контрактов
    for col in product_sum.columns:
        fig.add_trace(
            go.Bar(
                x=product_sum.index,
                y=product_sum[col],
                name=col,
                showlegend=(col == product_sum.columns[0])
            ),
            row=2, col=1
        )

    # График 4: Количество контрактов
    for col in product_count.columns:
        fig.add_trace(
            go.Bar(
                x=product_count.index,
                y=product_count[col],
                name=col,
                showlegend=False
            ),
            row=2, col=2
        )

    # Общие настройки
    fig.update_layout(
        height=1000,
        title_text='Аналитический дашборд',
        title_x=0.5,
        barmode='stack',
        legend_title="Параметры",
        template='plotly_white',
        margin=dict(t=100, b=150))

    # Настройка осей
    fig.update_yaxes(title_text="Количество клиентов", row=1, col=1)
    fig.update_yaxes(title_text="Сумма договоров", row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text="Количество клиентов", row=1, col=2)
    fig.update_yaxes(title_text="Сумма договоров", row=1, col=2, secondary_y=True)
    fig.update_yaxes(title_text="Сумма", row=2, col=1)
    fig.update_yaxes(title_text="Количество", row=2, col=2)

    return fig


# Подготовка данных и создание фигуры
owner_stats, ad_stats, product_sum, product_count = prepare_data()
fig = create_figures(owner_stats, ad_stats, product_sum, product_count)

# Макет приложения
app.layout = html.Div([
    dcc.Graph(
        figure=fig,
        config={'responsive': True},
        style={'height': '100vh'}
    )
])

# Запуск приложения
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)