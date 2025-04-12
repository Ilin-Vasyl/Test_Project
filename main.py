import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import dash
from dash import dcc, html
import pandas as pd
import os
import warnings

# Отключаем предупреждения
warnings.filterwarnings('ignore')

# Создаем приложение Dash
app = dash.Dash(__name__)

# Загружаем данные
deals = pd.read_pickle('deals.pkl')

# Подготовка данных для первого графика
owner_df = deals.groupby('Deal_Owner_Name').size().reset_index(name='total')
payment_done_df = deals[(deals['Stage'] == 'Payment Done') & (deals['Offer_Total_Amount'] > 0)].groupby('Deal_Owner_Name').agg(
    payment_done=('Stage', 'count'),
    deal_amount_sum=('Offer_Total_Amount', 'sum')
).reset_index()

owner_data = pd.merge(owner_df, payment_done_df, on='Deal_Owner_Name', how='left')
owner_data['conversion_rate'] = (owner_data['payment_done'] / owner_data['total'] * 100).round(2)
owner_data = owner_data.sort_values('conversion_rate', ascending=False)

# График 1
fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=owner_data['Deal_Owner_Name'],
    y=owner_data['total'],
    name='Количество клиентов',
    marker_color='lightskyblue',
    text=owner_data['conversion_rate'].astype(str) + '%',
    textposition='outside',
    textfont=dict(size=12, color='orange'),
    yaxis='y1'
))

fig1.add_trace(go.Scatter(
    x=owner_data['Deal_Owner_Name'],
    y=owner_data['deal_amount_sum'],
    name='Общая стоимость договоров',
    mode='lines+markers',
    line=dict(color='darkgreen', width=3, dash='dash'),
    yaxis='y2'
))

fig1.update_layout(
    title='Эффективность работы менеджеров',
    xaxis=dict(title='Менеджер'),
    yaxis=dict(
        title='Количество клиентов',
        tickangle=45,
        side='left',
        rangemode='tozero'
    ),
    yaxis2=dict(
        title='Сумма по договорам',
        overlaying='y',
        side='right',
        showgrid=False,
        rangemode='tozero'
    ),
    legend=dict(
        x=0.6,
        y=0.99,
        title=dict(text='Обозначения')
    ),
    bargap=0.2,
    template='plotly_white',
    height=750,
    margin=dict(t=100)
)

# Подготовка данных для второго графика
ad_df = deals.groupby('Ad').size().reset_index(name='total')
payment_done_df = deals[(deals['Stage'] == 'Payment Done') & (deals['Offer_Total_Amount'] > 0)].groupby('Ad').agg(
    payment_done=('Stage', 'count'),
    deal_amount_sum=('Offer_Total_Amount', 'sum')
).reset_index()

owner_data = pd.merge(ad_df, payment_done_df, on='Ad', how='left')
owner_data['conversion_rate'] = (owner_data['payment_done'] / owner_data['total'] * 100).round(2)
owner_data = owner_data.sort_values('conversion_rate', ascending=False)

# График 2
fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=owner_data['Ad'],
    y=owner_data['total'],
    name='Количество клиентов',
    marker_color='lightskyblue',
    text=owner_data['conversion_rate'].astype(str) + '%',
    textposition='outside',
    textfont=dict(size=12, color='orange'),
    yaxis='y1'
))

fig2.add_trace(go.Scatter(
    x=owner_data['Ad'],
    y=owner_data['deal_amount_sum'],
    name='Общая стоимость договоров',
    mode='lines+markers',
    line=dict(color='darkgreen', width=3, dash='dash'),
    yaxis='y2'
))

fig2.update_layout(
    title='Эффективность рекламных компаний',
    xaxis=dict(title='Рекламная компания'),
    yaxis=dict(
        title='Количество клиентов',
        tickangle=45,
        side='left',
        rangemode='tozero'
    ),
    yaxis2=dict(
        title='Сумма по договорам',
        overlaying='y',
        side='right',
        showgrid=False,
        rangemode='tozero'
    ),
    legend=dict(
        x=0.68,
        y=0.99,
        title=dict(text='Обозначения')
    ),
    bargap=0.2,
    template='plotly_white',
    height=750,
    margin=dict(t=100)
)

# Подготовка данных для третьего графика
paid_deals = deals[(deals['Stage'] == 'Payment Done') & (deals['Offer_Total_Amount'] > 0)]
pivot_table_sum = paid_deals.pivot_table(index='Product', columns='Education_Type', values='Offer_Total_Amount', aggfunc='sum').drop(index='NoData')
pivot_table_reset_sum = pivot_table_sum.reset_index()

fig3a = px.bar(pivot_table_reset_sum,
               x='Product',
               y=pivot_table_reset_sum.columns[1:],
               title='Структура студентов по направлению и форме обучения в сумме контрактов',
               labels={'Product': 'Продукт', 'value': 'Сумма'},
               height=400)

pivot_table_count = paid_deals.pivot_table(index='Product', columns='Education_Type', values='Offer_Total_Amount', aggfunc='count').drop(index='NoData')
pivot_table_reset_count = pivot_table_count.reset_index()

fig3b = px.bar(pivot_table_reset_count,
               x='Product',
               y=pivot_table_reset_count.columns[1:],
               title='Структура студентов по направлению и форме обучения в количестве контрактов',
               labels={'Product': 'Продукт', 'value': 'Количество оплаченных договоров'},
               height=400)

# Размещение графиков в одном дашборде
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Эффективность работы менеджеров', 'Эффективность рекламных компаний', 'Структура студентов'),
    shared_yaxes=False
)

# Добавляем первый график
fig.add_traces(fig1.data, rows=1, cols=1)

# Добавляем второй график
fig.add_traces(fig2.data, rows=1, cols=2)

# Добавляем третий график (состоящий из двух частей)
fig.add_traces(fig3a.data, rows=2, cols=1)
fig.add_traces(fig3b.data, rows=2, cols=2)

# Обновляем макет
fig.update_layout(
    barmode='stack',
    title_text='Дашборд с графиками',
    title_x=0.5,
    height=1000,
    showlegend=True
)

# Устанавливаем порт через переменную окружения, если доступна
port = int(os.environ.get('PORT', 8050))

# Запуск Dash-приложения
app.layout = html.Div([
    dcc.Graph(figure=fig)
])

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True)