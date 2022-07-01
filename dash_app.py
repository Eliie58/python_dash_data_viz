import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

app = dash.Dash(__name__)

month_mapping = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}

df = pd.read_csv('hotel_bookings.csv')
df['year'] = df['arrival_date_year']
df['month'] = df['arrival_date_month'].map(month_mapping)
df['day'] = df['arrival_date_day_of_month']
df['arrival_date'] = pd.to_datetime(df[['year', 'month', 'day']])

grouped_by_hotel_and_date = df.groupby(['hotel', 'arrival_date'], as_index=False).count()[
    ['hotel', 'arrival_date', 'is_canceled']].rename(
    columns={'hotel': 'Hotel', 'arrival_date': 'Arrival Date', 'is_canceled': 'Count'})

fig = px.line(grouped_by_hotel_and_date, x="Arrival Date", y="Count", color='Hotel', title='Hotel reservations '
                                                                                           'per Date')

grouped_by_cancellation = df.groupby(['is_canceled', 'arrival_date_month', 'month'], as_index=False).count()[
    ['arrival_date_month', 'is_canceled', 'hotel', 'month']].rename(
    columns={'arrival_date_month': 'Month', 'is_canceled': 'Is Canceled', 'hotel': 'Count'}).sort_values(by='month')
grouped_by_cancellation.loc[grouped_by_cancellation['Is Canceled'] == 0, 'Is Canceled'] = 'Yes'
grouped_by_cancellation.loc[grouped_by_cancellation['Is Canceled'] == 1, 'Is Canceled'] = 'No'

fig_2 = px.bar(grouped_by_cancellation, x="Month", y="Count", color="Is Canceled", barmode='group',
               title='Hotel cancellation Per month')

weekday_map = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}

weekday_data = pd.DataFrame(df['arrival_date'].dt.dayofweek.value_counts()).sort_index()
weekday_data['Day of Week'] = weekday_data.index.map(weekday_map)
weekday_data = weekday_data.rename(columns={'arrival_date': 'Count'})

fig_3 = px.pie(weekday_data, names="Day of Week", values="Count",
               title='Hotel Reservation Distribution Per Week')

guest_data = df.dropna(subset=['adults', 'children'])
guest_data['guests'] = (guest_data['adults'] + guest_data['children']).astype(int)
grouped_by_number_of_guests = guest_data.groupby(['guests'], as_index=False).count()[
    ['guests', 'is_canceled']].rename(
    columns={'guests': 'Number of Guests', 'is_canceled': 'Count'})

fig_4 = px.treemap(grouped_by_number_of_guests, path=['Number of Guests'], values="Count", title='Number of guests per '
                                                                                                 'Reservation',
                   hover_name='Number of Guests', hover_data=['Count'])

reserved_room_type_data = df.rename(
    columns={'reserved_room_type': 'Reserved Room Type', 'hotel': 'Hotel', 'adr': 'Average Daily Rate'})
fig_5 = px.scatter(reserved_room_type_data, y='Reserved Room Type', x="Average Daily Rate",
                   title='Average Daily Rate per Room Type',
                   color='Hotel')

app.layout = html.Div(
    html.Div([
        html.H1('Dash Sample Project'),
        html.H4('Author : Elie Yaacoub'),
        dcc.Graph(
            id='example-graph',
            figure=fig
        ),
        dcc.Graph(
            id='example-graph-2',
            figure=fig_2
        ),
        dcc.Graph(
            id='example-graph-3',
            figure=fig_3
        ),
        dcc.Graph(
            id='example-graph-4',
            figure=fig_4
        ),
        dcc.Graph(
            id='example-graph-5',
            figure=fig_5
        )
    ])
)

if __name__ == '__main__':
    app.run_server(debug=True)
