import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash import Input, Output

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
                   hover_name='Number of Guests', hover_data={'Count':True,'Number of Guests':False}, )

reserved_room_type_data = df.rename(
    columns={'reserved_room_type': 'Reserved Room Type', 'hotel': 'Hotel', 'adr': 'Average Daily Rate'})

app.layout = html.Div(
    html.Div([
        html.H1('Dash Sample Project'),
        html.H4('Author : Elie Yaacoub'),
        html.P('Change the selected dates in the below Date Picker Range to zoom in on a specific Date Range'),
        dcc.DatePickerRange(
            id='date-picker-range',
            display_format='MMM Do, YY',
            start_date_placeholder_text='MMM Do, YY',
            min_date_allowed=grouped_by_hotel_and_date["Arrival Date"].min(),
            max_date_allowed=grouped_by_hotel_and_date["Arrival Date"].max(),
            start_date=grouped_by_hotel_and_date["Arrival Date"].min(),
            end_date=grouped_by_hotel_and_date["Arrival Date"].max()
        ),
        html.P('Change the selected Hotels in the below Dropdown List to filter by a specific Hotel'),
        dcc.Dropdown(options=grouped_by_hotel_and_date["Hotel"].unique(), multi=True, id="hotel-dropdown",
                     value=grouped_by_hotel_and_date["Hotel"].unique()),
        dcc.Graph(
            id='example-graph'
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
        html.P('Change the selected values in the below Range Slider to zoom in on a specific Range'),
        dcc.RangeSlider(min=reserved_room_type_data["Average Daily Rate"].min(),
                        max=reserved_room_type_data["Average Daily Rate"].max(),
                        value=[reserved_room_type_data["Average Daily Rate"].min(),
                               reserved_room_type_data["Average Daily Rate"].max()],
                        id='reserved-room-type-data-slider',
                        tooltip={"placement": "bottom"}
                        ),
        dcc.Graph(
            id='example-graph-5'
        )
    ])
)


@app.callback(
    Output('example-graph-5', 'figure'),
    [Input('reserved-room-type-data-slider', 'value')])
def update_reserved_room_type(adr_range):
    filtered_reserved_room_type_data = reserved_room_type_data[
        (reserved_room_type_data['Average Daily Rate'] >= adr_range[0]) & (
                reserved_room_type_data['Average Daily Rate'] <= adr_range[1])]

    fig_5 = px.scatter(filtered_reserved_room_type_data, y='Reserved Room Type', x="Average Daily Rate",
                       title='Average Daily Rate per Room Type',
                       color='Hotel')

    fig_5.update_layout(transition_duration=100)

    return fig_5


@app.callback(
    Output('example-graph', 'figure'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('hotel-dropdown', 'value'))
def update_output(start_date, end_date, hotels):
    filtered_grouped_by_hotel_and_date = grouped_by_hotel_and_date[
        (grouped_by_hotel_and_date["Arrival Date"] >= start_date) &
        (grouped_by_hotel_and_date["Arrival Date"] <= end_date) &
        (grouped_by_hotel_and_date["Hotel"].isin(hotels))]

    fig = px.line(filtered_grouped_by_hotel_and_date, x="Arrival Date", y="Count", color='Hotel',
                  title='Hotel reservations per Date')

    fig.update_layout(transition_duration=100)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
