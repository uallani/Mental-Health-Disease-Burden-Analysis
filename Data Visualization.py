import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from flask import send_from_directory
import os
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the path to your Visualizations folder
visualizations_folder = os.path.join(os.getcwd(), 'Visualizations')


# Custom route to serve images from the Visualizations folder
@app.server.route('/visualizations/<path:path>')
def serve_visualizations(path):
    return send_from_directory(visualizations_folder, path)


# Load the CSV file into a DataFrame
df = pd.read_csv(r"C:\Users\uallani\PycharmProjects\MHALYS Project\Dataset_with_metric (1).csv")

# Create Treemap (fig1)
fig1 = px.treemap(
    df,
    path=["location", "cause"],  # Hierarchy
    values="val_MHALYs",  # Size of rectangles
    color="val_MHALYs",  # Color by MHALYs
    color_continuous_scale="Viridis",  # Optional color scale
    title="Treemap of Locations, Causes, and MHALYs"
)

# Calculate the mean of the measures for bar chart (fig2)
measures = ['val_DALYs (Disability-Adjusted Life Years)', 'val_Deaths',
            'val_YLDs (Years Lived with Disability)', 'val_YLLs (Years of Life Lost)',
            'MH-DWAF', 'val_MHALYs']
measure_means = df[measures].mean().reset_index()
measure_means.columns = ['Measure', 'Mean Value']

# Create a bar chart using Plotly (fig2)
fig2 = px.bar(measure_means,
              x='Measure',
              y='Mean Value',
              text='Mean Value',
              color='Mean Value',
              color_continuous_scale='Blues',
              title='Average Values of Different Measures')

# Customize the layout for fig2
fig2.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig2.update_layout(
    xaxis_title='Measure',
    yaxis_title='Mean Value',
    coloraxis_showscale=False,
    plot_bgcolor='white',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True)
)

# Prepare data for Word Cloud (fig3)
cause_counts_dict = df['cause'].value_counts().to_dict()

# Generate the word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='Blues').generate_from_frequencies(
    cause_counts_dict)

# Save the word cloud to a file
wordcloud_image_path = os.path.join(visualizations_folder, 'wordcloud_all_causes.png')
wordcloud.to_file(wordcloud_image_path)

# Create the Violin Plot (fig4)
fig4 = px.violin(
    df,
    x='year',
    y='val_Deaths',
    color='cause',  # Color by cause
    title='Distribution of Deaths Over Years by Cause (Violin Plot)',
    labels={'val_Deaths': 'Number of Deaths', 'year': 'Year'},
    box=True,  # Add box plot inside the violin plot
    points='all',  # Display all points
    color_discrete_sequence=px.colors.qualitative.Set1  # Choose a visually distinct color palette
)

# Customize the layout for fig4
fig4.update_layout(
    title_x=0.5,  # Center the title
    xaxis=dict(tickmode='linear', tickangle=45),  # Rotate x-axis labels
    yaxis=dict(title='Number of Deaths'),
)

# Aggregate data to get the total deaths per year per cause (fig5)
top_causes_year_deaths = df.groupby(['year', 'cause'])['val_Deaths'].sum().reset_index()

# Sort by deaths within each year and select the top 5 causes for each year
top_causes_year_deaths = top_causes_year_deaths.sort_values(['year', 'val_Deaths'], ascending=[True, False])

# Use groupby().head(5) to get top 5 causes per year based on total deaths
top_causes_year_deaths = top_causes_year_deaths.groupby('year').head(5)

# Create a facet grid for the top 5 causes by year based on deaths
fig5 = px.bar(
    top_causes_year_deaths,
    x='cause',
    y='val_Deaths',  # Use deaths as the y-axis
    color='cause',
    facet_col='year',  # Create separate plots for each year
    title="Top 5 Causes of Deaths by Year",
    labels={'val_Deaths': 'Number of Deaths', 'cause': 'Cause'},
)

# --- New Visualization (fig6) --- #

# Assuming `top_causes_age` is available in your dataset, it could be something like this:
top_causes_age = df.groupby(['age', 'cause']).size().reset_index(name='count')

# Create the stacked bar chart for top 5 causes by age group
fig6 = px.bar(
    top_causes_age,
    x='age',
    y='count',
    color='cause',
    title='Top 5 Causes by Age Group',
    labels={'count': 'Count', 'age': 'Age Group', 'cause': 'Cause'},
    color_discrete_sequence=px.colors.qualitative.Set1,
    text='count'  # Show count on top of each bar
)

import plotly.express as px

# Aggregate data (example: summing val_MHALYs by age group and cause)
aggregated_data = df.groupby(['age', 'cause'])['val_MHALYs'].sum().reset_index()

# Create the stacked bar chart
fig6 = px.bar(
    aggregated_data,
    x='age',
    y='val_MHALYs',
    color='cause',  # Different causes will be stacked
    title='Contributions of Causes to Mental Health Metrics by Age Group'
)

# Customize the layout
fig6.update_layout(
    barmode='stack',  # Stack bars to show contribution of each cause
    title_x=0.5,  # Center the title
    xaxis_title='Age Group',
    yaxis_title='Mental Health-Adjusted Life Years (MHALYs)',  # Update based on metric
    xaxis=dict(tickangle=45),  # Rotate x-axis labels
    hovermode='x unified'  # Group hover information by age group
)



# Fig 7 - Violin Plot
fig7 = px.violin(
    df,
    x='age',
    y='val_Deaths',
    color='cause',
    box=True,
    points='all',
    hover_data=['cause', 'val_Deaths'],
    category_orders={'age': sorted(df['age'].unique())},
    color_discrete_sequence=px.colors.qualitative.Set1,
    title='Distribution of Deaths by Age Group and Cause'
)
fig7.update_layout(
    title='Distribution of Deaths by Age Group and Cause',
    title_x=0.5,
    title_font_size=18,
    xaxis_title='Age Group',
    yaxis_title='Number of Deaths',
    xaxis=dict(tickangle=45),
    yaxis=dict(showgrid=True),
    legend_title='Cause',
    legend=dict(
        title_font_size=14,
        font_size=12,
        x=1.05,
        y=1,
        xanchor='left',
        yanchor='top'
    ),
)

# Fig 8 - Pie Chart
age_deaths = df.groupby('age')['val_Deaths'].sum().reset_index()
fig8 = px.pie(
    age_deaths,
    names='age',
    values='val_Deaths',
    title='Proportion of Deaths by Age Group',
    color='age',
    color_discrete_sequence=px.colors.qualitative.Set3
)

# Fig 9 - Bar Chart (Deaths by Location)
location_deaths = df.groupby('location')['val_Deaths'].sum().reset_index()
location_deaths_sorted = location_deaths.sort_values('val_Deaths', ascending=False)
fig9 = px.bar(
    location_deaths_sorted,
    x='location',
    y='val_Deaths',
    labels={'location': 'State', 'val_Deaths': 'Total Deaths'},
    color='val_Deaths',
    color_continuous_scale='Viridis',
    text='val_Deaths',
    width=1000,
    height=600
)
fig9.update_layout(
    title='Deaths by Location (All States)',
    title_x=0.5,
    title_font=dict(size=20),
    xaxis_tickangle=-45,
    xaxis_title='State',
    yaxis_title='Total Deaths',
    template='plotly_dark',
    showlegend=False
)

# Fig 10 - Stacked Area Chart (Deaths by Cause and Gender)
fig10 = px.area(
    df,
    x='cause',
    y='val_Deaths',
    color='sex',
    labels={'cause': 'Cause of Death', 'val_Deaths': 'Number of Deaths', 'sex': 'Gender'},
    title='Deaths by Cause and Gender (Stacked)',
    height=600,
    width=1000
)
fig10.update_layout(
    title_x=0.5,
    title_font=dict(size=24),
    xaxis_tickangle=-45,
    xaxis_title='Cause of Death',
    yaxis_title='Number of Deaths',
    template='plotly_dark',
    showlegend=True
)

# Fig 11 - Scatter Plot (Deaths by Age and Gender)
df_grouped = df.groupby(['age', 'sex'], as_index=False)['val_Deaths'].sum()
fig11 = px.scatter(
    df_grouped,
    x='age',
    y='val_Deaths',
    color='sex',
    title='Deaths by Age and Gender (Scatter Plot)',
    labels={'val_Deaths': 'Number of Deaths', 'age': 'Age Group'},
    color_discrete_sequence=px.colors.qualitative.Set2
)

# Fig 12 - Histogram (Deaths by Age Group)
fig12 = px.histogram(
    df,
    x='age',
    y='val_Deaths',
    histfunc='sum',
    title='Distribution of Deaths by Age Group',
    labels={'age': 'Age Group', 'val_Deaths': 'Total Deaths'},
    color='age',
    color_discrete_sequence=px.colors.qualitative.Set1
)
fig12.update_layout(
    title_x=0.5,
    title_font=dict(size=20),
    xaxis_title='Age Group',
    yaxis_title='Total Deaths',
    showlegend=False
)



# Define the layout
app.layout = html.Div(
   [
       # Impressive Centered Title with Animation
       html.Div(
           [
               html.H1(
                   "Refining Mental Health Measurement in Disease Burden Analysis",
                   style={
                       "textAlign": "center",
                       "color": "transparent",
                       "fontSize": "50px",
                       "fontWeight": "bold",
                       "background": "linear-gradient(90deg, rgba(255, 0, 0, 1), rgba(255, 0, 255, 1), rgba(0, 0, 255, 1))",
                       "WebkitBackgroundClip": "text",  # Gradient text effect
                       "animation": "titleAnimation 15s ease-in-out",
                       "textShadow": "4px 4px 10px rgba(0, 0, 0, 0.7)",
                   },
               ),
               html.H2(
                   "A Novel Approach Incorporating Advanced Metrics and Visualization",
                   style={
                       "textAlign": "center",
                       "color": "#333",
                       "fontSize": "30px",
                       "fontStyle": "italic",
                       "opacity": "0.8",
                       "animation": "fadeIn 6s ease-in-out",
                   },
               ),
           ],
           style={
               "display": "flex",
               "flexDirection": "column",
               "justifyContent": "center",
               "alignItems": "center",
               "height": "80vh",  # Take up most of the vertical space
           },
       ),


       # Buttons at Bottom Center
       html.Div(
           [
               dbc.Button(
                   "Team",
                   id="team-button",
                   color="primary",
                   style={
                       "marginRight": "20px",
                       "fontSize": "20px",
                       "padding": "15px 30px",
                       "borderRadius": "10px",
                       "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.3)",
                   },
                   n_clicks=0,
                   className="button-hover",
               ),
               dbc.Button(
                   "Visualizations",
                   id="visualizations-button",
                   color="secondary",
                   style={
                       "fontSize": "20px",
                       "padding": "15px 30px",
                       "borderRadius": "10px",
                       "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.3)",
                   },
                   n_clicks=0,
                   className="button-hover",
               ),
           ],
           style={
               "display": "flex",
               "justifyContent": "center",
               "position": "fixed",
               "bottom": "20px",
               "width": "100%",
           },
       ),


       # Modal for Team Details (Zoom-in effect)
       dbc.Modal(
           [
               dbc.ModalHeader("About Me"),
               dbc.ModalBody(
                   [
                       html.Div(
                           [
                               html.H5("Udaya Allani", style={"textAlign": "center", "fontWeight": "bold"}),
                               html.P("Email: uallani@ualr.edu", style={"textAlign": "center"}),

                               html.H5("Nihal Asjad Mohammad", style={"textAlign": "center", "fontWeight": "bold"}),
                               html.P("Email: nmohammad@ualr.edu", style={"textAlign": "center"}),
                           ],
                           style={"marginBottom": "20px"}
                       ),


                   ]
               ),
               dbc.ModalFooter(
                   dbc.Button("Close", id="close-team-modal", color="secondary")
               ),
           ],
           id="team-modal",
           is_open=False,
           style={"animation": "zoomOut 1s forwards"},
       ),


       # Content Placeholder for visualizations
       html.Div(id="page-content", style={"marginTop": "20px"}),
   ]
)





# Callbacks for modal and navigation
@app.callback(
   Output("team-modal", "is_open"),
   [Input("team-button", "n_clicks"), Input("close-team-modal", "n_clicks")],
   [State("team-modal", "is_open")],
)
def toggle_team_modal(team_clicks, close_clicks, is_open):
   if team_clicks or close_clicks:
       return not is_open
   return is_open




@app.callback(
   Output("page-content", "children"),
   Input("visualizations-button", "n_clicks"),
)
def show_visualizations(vis_clicks):
   if vis_clicks:
       return html.Div(
           [
               html.H3("Visualizations", style={"textAlign": "center", "marginTop": "20px"}),
               html.Div(
                   "If the image does not appear, check the file path or ensure the image exists in the Visualizations folder.",
                   style={"color": "red", "textAlign": "center", "fontSize": "14px"},
               ),
               dcc.Tabs([
                   dcc.Tab(label='Treemap', children=[dcc.Graph(figure=fig1)]),
                   dcc.Tab(label='Bar Chart - Measures', children=[dcc.Graph(figure=fig2)]),
                   dcc.Tab(label='Word Cloud', children=[html.Img(src='/visualizations/wordcloud_all_causes.png',
                                                                  style={'width': '100%', 'height': 'auto'})]),
                   dcc.Tab(label='Violin Plot - Deaths', children=[dcc.Graph(figure=fig4)]),
                   dcc.Tab(label='Bar Chart - Deaths by Cause', children=[dcc.Graph(figure=fig5)]),
                   dcc.Tab(label='Stacked Bar Chart - Causes by Age', children=[dcc.Graph(figure=fig6)]),
                   dcc.Tab(label='Violin Plot - Deaths by Age', children=[dcc.Graph(figure=fig7)]),
                   dcc.Tab(label='Pie Chart - Deaths by Age Group', children=[dcc.Graph(figure=fig8)]),
                   dcc.Tab(label='Bar Chart - Deaths by Location', children=[dcc.Graph(figure=fig9)]),
                   dcc.Tab(label='Stacked Area Chart - Deaths by Cause and Gender', children=[dcc.Graph(figure=fig10)]),
                   dcc.Tab(label='Scatter Plot - Deaths by Age and Gender', children=[dcc.Graph(figure=fig11)]),
               ])
           ]
       )
   return html.Div()




# Run the app
if __name__ == "__main__":
   app.run_server(debug=True)

