from preswald import text, connect, get_df, selectbox, slider, checkbox, plotly, button, sidebar
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import time  



text("# 🎬 Movie Explorer")
text("Discover great movies and explore cinema trends!")


connect()
df = get_df('imdb')


df = df[
    (df['startYear'].notna()) &
    (df['averageRating'].notna()) &
    (df['numVotes'].notna()) &
    (df['runtimeMinutes'].notna())
]

df['startYear'] = pd.to_numeric(df['startYear'])
df['averageRating'] = pd.to_numeric(df['averageRating'])
df['numVotes'] = pd.to_numeric(df['numVotes'])
df['runtimeMinutes'] = pd.to_numeric(df['runtimeMinutes'])

# Pre-calculate genre data
all_genres = set()
df['genres'].str.split(',').apply(all_genres.update)
all_genres = sorted(list(all_genres))

# Pre-calculate year range
year_min = int(df['startYear'].min())
year_max = int(df['startYear'].max())

# Pre-calculate yearly counts
yearly_counts_full = df.groupby('startYear').size().reset_index(name='count')

text("""
## 🎯 Find Your Next Movie
Use our Movie Mood Matcher to discover films that match your preferences!
Adjust the filters below to see matching movie suggestions - they'll update automatically!
""")

# Movie finder interface
min_rating = slider("Minimum Rating:", min_val=6.0, max_val=9.0, default=7.0, step=0.1)
min_votes = slider("Minimum Number of Votes:", min_val=1000, max_val=500000, default=50000)
selected_genre = selectbox("Preferred Genre:", options=['Any'] + all_genres)
decade_options = ['Any'] + [f"{d}s" for d in range(1950, 2030, 10)]
selected_decade = selectbox("Preferred Decade:", options=decade_options)
runtime_preference = selectbox("Movie Length:", 
                             options=['Any', 'Short (< 90 min)', 
                                    'Medium (90-120 min)', 
                                    'Long (> 120 min)'])

# Use pre-filtered dataset
filtered_df = df[
    (df['averageRating'] >= min_rating) &
    (df['numVotes'] >= min_votes)
].copy()

if selected_genre != 'Any':
    filtered_df = filtered_df[filtered_df['genres'].str.contains(selected_genre, na=False)]

if selected_decade != 'Any':
    decade_start = int(selected_decade[:4])
    filtered_df = filtered_df[
        (filtered_df['startYear'] >= decade_start) &
        (filtered_df['startYear'] < decade_start + 10)
    ]

if runtime_preference == 'Short (< 90 min)':
    filtered_df = filtered_df[filtered_df['runtimeMinutes'] < 90]
elif runtime_preference == 'Medium (90-120 min)':
    filtered_df = filtered_df[
        (filtered_df['runtimeMinutes'] >= 90) &
        (filtered_df['runtimeMinutes'] <= 120)
    ]
elif runtime_preference == 'Long (> 120 min)':
    filtered_df = filtered_df[filtered_df['runtimeMinutes'] > 120]

if len(filtered_df) > 0:
    random.seed(time.time())
    movie = filtered_df.sample(n=1, random_state=int(time.time())).iloc[0]
    text(f"""
    ### 🍿 Your Recommended Movie:
    
    **{movie['primaryTitle']} ({movie['startYear']})**
    - ⭐ Rating: {movie['averageRating']}/10 ({movie['numVotes']:,} votes)
    - 🎭 Genre: {movie['genres']}
    - ⏱️ Runtime: {movie['runtimeMinutes']} minutes
    - 🎥 Directors: {movie['directors']}
    
    *Number of movies matching your criteria: {len(filtered_df)}*
    """)
else:
    text("❌ No movies found matching your criteria. Try adjusting your filters!")

text("""
## 📊 Movie Data Explorer
Explore interactive visualizations of movie trends and patterns:
""")

# Rating Distribution
text("""
### 1. Rating Distribution
See how movies are distributed across different ratings:
- The height of each bar shows how many movies received that rating
- Most highly-rated movies cluster around 6-8 rating points
""")

fig_ratings = px.histogram(
    df,
    x="averageRating",
    nbins=20,
    title="Movie Ratings Distribution",
    labels={"averageRating": "IMDB Rating", "count": "Number of Movies"},
    color_discrete_sequence=['#FFB000']
)
fig_ratings.update_layout(bargap=0.1)
plotly(fig_ratings)

text("""
### 2. Ratings Over Time
Explore how movie ratings relate to release years:
- Each point represents a movie
- Larger points indicate more viewer votes
- Hover over points for movie details
- Use the sliders below to focus on a specific time period
""")

# Sliders right before the chart
ratings_start = slider("Ratings Chart - Start Year:", min_val=year_min, max_val=year_max, default=1950, step=1)
ratings_end = slider("Ratings Chart - End Year:", min_val=year_min, max_val=year_max, default=2024, step=1)

ratings_filtered_df = df[
    (df['startYear'] >= ratings_start) & 
    (df['startYear'] <= ratings_end)
]

fig_time = px.scatter(
    ratings_filtered_df,
    x="startYear",
    y="averageRating",
    size="numVotes",
    hover_data=["primaryTitle", "runtimeMinutes", "genres"],
    title=f"Movie Ratings ({ratings_start}-{ratings_end})",
    labels={
        "startYear": "Release Year",
        "averageRating": "IMDB Rating",
        "numVotes": "Number of Votes"
    },
    opacity=0.7,
    size_max=40,
    color="numVotes",
    color_continuous_scale="Viridis",
    range_y=[5, 10],
    render_mode='webgl'
)

fig_time.update_layout(
    plot_bgcolor='white',
    width=900,
    height=600,
    xaxis=dict(
        gridcolor='lightgray',
        title_font=dict(size=14),
        tickfont=dict(size=12),
        showgrid=True
    ),
    yaxis=dict(
        gridcolor='lightgray',
        title_font=dict(size=14),
        tickfont=dict(size=12),
        showgrid=True
    ),
    scattermode='group',
    showlegend=True
)

fig_time.update_traces(
    marker=dict(
        line=dict(width=1, color='DarkSlateGrey'),
        sizemin=5
    )
)

plotly(fig_time)


text("""
### 3. Movie Length Trends
See how movie runtimes have evolved over the decades:
- Boxes show the distribution of movie lengths
- The line in each box represents the median runtime
- Points show individual movies that are unusually short or long
- Use the sliders below to focus on a specific time period
""")

# Sliders right before the chart
runtime_start = slider("Runtime Chart - Start Year:", min_val=year_min, max_val=year_max, default=1950, step=1)
runtime_end = slider("Runtime Chart - End Year:", min_val=year_min, max_val=year_max, default=2024, step=1)

runtime_filtered_df = df[
    (df['startYear'] >= runtime_start) & 
    (df['startYear'] <= runtime_end)
]

fig_runtime = px.box(
    runtime_filtered_df,
    x=runtime_filtered_df['startYear'].round(-1),
    y='runtimeMinutes',
    title=f'Movie Runtime Distribution ({runtime_start}-{runtime_end})',
    labels={'runtimeMinutes': 'Runtime (minutes)', 'startYear': 'Decade'}
)
plotly(fig_runtime)

text("""
### 4. Movie Production Volume
Track the number of movies released each year:
- Use the sliders below to focus on a specific time period
""")

# Sliders right before the chart
volume_start = slider("Production Chart - Start Year:", min_val=year_min, max_val=year_max, default=1950, step=1)
volume_end = slider("Production Chart - End Year:", min_val=year_min, max_val=year_max, default=2024, step=1)

yearly_counts = yearly_counts_full[
    (yearly_counts_full['startYear'] >= volume_start) & 
    (yearly_counts_full['startYear'] <= volume_end)
]

fig_yearly = px.line(
    yearly_counts,
    x='startYear',
    y='count',
    title=f'Movies Released per Year ({volume_start}-{volume_end})',
    labels={'count': 'Number of Movies', 'startYear': 'Release Year'}
)

fig_yearly.update_layout(
    plot_bgcolor='white',
    width=900,
    height=500,
    xaxis=dict(
        gridcolor='lightgray',
        title_font=dict(size=14),
        tickfont=dict(size=12)
    ),
    yaxis=dict(
        gridcolor='lightgray',
        title_font=dict(size=14),
        tickfont=dict(size=12)
    )
)
plotly(fig_yearly)

text("""
**Note:** This data is based on IMDB ratings and may not include all movies ever made.
The recommendations and statistics are generated based on available data.
""")
