import streamlit as st
import pandas as pd
import altair as alt


# Function to filter the dataframe by genres selected, can be reused for other filters if added
def filter_by_genre(df, selected_genre):
    if "All" in selected_genre:
        return df.copy()
    return df[df["genres"].isin(selected_genre)]


# Function to display the tables and charts
def display_table_chart(table, chart):
    col1, col2 = st.columns(2)
    with col2:
        st.subheader("Table")
        with st.spinner("Loading tables..."):
            st.dataframe(table)

    with col1:
        st.subheader("Chart")
        with st.spinner("Loading charts..."):
            st.altair_chart(chart, use_container_width=True)


# Function for problem 4, allows for dynamic reviews filtering
def top5_filter(top5_filter):
    return (
        movie_stats[movie_stats["count"] >= top5_filter]
        .sort_values(by="avg_rating", ascending=False)
        .head(5)
    )


st.set_page_config(
    page_title="Movie Dashboard",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded",
)

alt.themes.enable("dark")

df_reshaped = pd.read_csv("data/movie_ratings.csv")

with st.sidebar:
    st.title("🎥🍿 Movie Dashboard")

    # Genre filter selection
    genre_list = ["All"] + sorted(df_reshaped["genres"].unique())
    selected_genre = st.multiselect("Select genres (Default: All)", genre_list, "All")

    # Theme selection
    color_theme_list = [
        "blues",
        "cividis",
        "greens",
        "inferno",
        "magma",
        "plasma",
        "reds",
        "rainbow",
        "turbo",
        "viridis",
    ]
    selected_color_theme = st.selectbox("Select a color theme", color_theme_list)

# -----------------------------------------------------------------------------

st.divider()
st.header("1. What's the breakdown of genres for the movies that were rated?")
st.subheader("Genre Ratings Breakdown")

# Apply Genre Filters
df1 = df_reshaped.assign(genres=df_reshaped["genres"].str.split("|")).explode("genres")
df1_filter = filter_by_genre(df1, selected_genre)

# Filter for Rating Data
genre_counts = df1["genres"].value_counts().reset_index()
genre_counts.columns = ["genres", "count"]
genre_counts = genre_counts.sort_values(by="count", ascending=False)

# Create and display chart and table
bar_chart = (
    alt.Chart(df1_filter)
    .mark_bar()
    .encode(
        x=alt.X("genres", sort="-y", title="Genre"),
        y=alt.Y("count(rating)", title="Number of Ratings"),
        color=alt.Color(
            "rating", title="Rating", scale=alt.Scale(scheme=selected_color_theme)
        ),
        tooltip=["genres", "rating", "count()"],
    )
    .properties(width=700, height=400)
)


display_table_chart(genre_counts, bar_chart)
st.text("""
        note: i cheated a little bit here, 
        the chart is for the entire dataframe (so i can get the individual rating scales for each genre)
        the table is a filtered dataframe which just returns the total # of ratings per genre
        """)
with st.expander("View the chart for the filtered dataset:"):
    bar_chart2 = (
    alt.Chart(genre_counts)
    .mark_bar()
    .encode(
        x=alt.X("genres", sort="-y", title="Genre"),
        y=alt.Y("count", title="Number of Ratings"),
        tooltip=["genres", "count"],
    )
    .properties(width=700, height=400)
    )
    st.altair_chart(bar_chart2, use_container_width=True)
    
    
    
# -----------------------------------------------------------------------------

st.divider()
st.header("2. Which genres have the highest viewer satisfaction (highest ratings)?")
st.subheader("Genre Ratings Breakdown")

# Apply Genre Filters
df2_filter = filter_by_genre(df1, selected_genre)

# Filter Viewer Satisfaction Rate
genre_satisfaction = df2_filter.groupby("genres")["rating"].mean().reset_index()
genre_satisfaction.columns = ["genre", "avg_rating"]
genre_satisfaction = genre_satisfaction.sort_values(by="avg_rating", ascending=False)

# Create and display chart and table
bar_chart = (
    alt.Chart(genre_satisfaction)
    .mark_bar()
    .encode(
        x=alt.X("genre", sort="-y", title="Genre"),
        y=alt.Y("avg_rating", title="Average Rating"),
        color=alt.Color(
            "avg_rating",
            title="Average Rating",
            scale=alt.Scale(scheme=selected_color_theme),
        ),
        tooltip=["genre", "avg_rating"],
    )
    .properties(width=700, height=400)
)


display_table_chart(genre_satisfaction, bar_chart)

# -----------------------------------------------------------------------------

st.divider()
st.header("3. How does mean rating change across movie release years?")
st.subheader("Mean Rating Across Movie Release Years")

# Apply Genre Filters
df3_filter = filter_by_genre(df1, selected_genre)

# Filter Mean Ratings
yearly_ratings = df3_filter.groupby("year")["rating"].mean().reset_index()

# Create and display chart and table
line_chart = (
    alt.Chart(yearly_ratings)
    .mark_line(point=True)
    .encode(
        x=alt.X("year:O", title="Release Year"),
        y=alt.Y("rating:Q", title="Mean Rating"),
        tooltip=["year", "rating"],
    )
    .properties(width=800, height=400)
)

display_table_chart(yearly_ratings, line_chart)

# -----------------------------------------------------------------------------

st.divider()
st.header(
    "4. What are the 5 best-rated movies that have at least 50 ratings? At least 150 ratings?"
)

# Apply Genre Filters
df4_filter = filter_by_genre(df1, selected_genre)

# Filter best rated movies
movie_stats = (
    df4_filter.groupby("title")
    .agg(avg_rating=("rating", "mean"), count=("rating", "count"))
    .reset_index()
)
# Create and display chart and table

col1, col2 = st.columns(2)

# Reviews >=50
with col1:
    st.subheader("At least 50 ratings")
    st.dataframe(top5_filter(50))

#Reviews >=150
with col2:
    st.subheader("At least 150 ratings")
    st.dataframe(top5_filter(150))

# Custom rating top 5 limit
st.subheader("Filter by any number of ratings!")
custom_rating_limit = st.slider("Top 5 movies with # >= of ratings", 0, 3000, 1500)

top5_over_custom = top5_filter(custom_rating_limit)
st.dataframe(top5_over_custom)
