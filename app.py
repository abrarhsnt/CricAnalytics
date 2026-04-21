import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="CricAnalytics", layout="wide")
st.title("CricAnalytics – Advanced Cricket Dashboard")

# ------------------------------------------------------------
# Load data with column checks
# ------------------------------------------------------------
@st.cache_data
def load_data():
    matches = pd.read_csv("matches.csv")
    deliveries = pd.read_csv("deliveries.csv")
    
    # Check required columns
    required_del_cols = ['match_id', 'batter', 'bowler', 'batsman_runs', 'total_runs', 'is_wicket']
    missing = [col for col in required_del_cols if col not in deliveries.columns]
    if missing:
        st.error(f"Missing columns in deliveries.csv: {missing}. Please ensure you have the full IPL dataset.")
        st.stop()
    
    # Merge to add match metadata
    merged = deliveries.merge(matches[['id', 'season', 'city', 'venue', 'team1', 'team2']],
                              left_on='match_id', right_on='id', how='left')
    return merged

df = load_data()

# Create match label
df['match_label'] = df.apply(lambda row: f"{row['team1']} vs {row['team2']} ({row['season']}) - {row['city']}", axis=1)

# Sidebar team filter
teams = sorted(set(df['team1'].unique()) | set(df['team2'].unique()))
selected_team = st.sidebar.selectbox("Select Team", ["All"] + teams)

if selected_team != "All":
    df_filtered = df[(df['team1'] == selected_team) | (df['team2'] == selected_team)]
else:
    df_filtered = df

# ------------------------------------------------------------
# TABS
# ------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Batters", "Bowlers", "Match Progression"])

# ------------------- TAB 1: BATTERS -------------------------
with tab1:
    st.subheader("Batter Performance")
    
    opp_teams = sorted(df_filtered['team2'].unique())  # opposition teams
    selected_opp = st.selectbox("Filter by opposition", ["All"] + opp_teams, key="batter_opp")
    
    if selected_opp != "All":
        batter_df = df_filtered[df_filtered['team2'] == selected_opp]
    else:
        batter_df = df_filtered
    
    # Compute metrics
    batter_group = batter_df.groupby('batter')
    runs = batter_group['batsman_runs'].sum()
    balls = batter_group.size()
    fours = batter_df[batter_df['batsman_runs'] == 4].groupby('batter').size()
    sixes = batter_df[batter_df['batsman_runs'] == 6].groupby('batter').size()
    dots = batter_df[batter_df['batsman_runs'] == 0].groupby('batter').size()
    
    batter_stats = pd.DataFrame({
        'runs': runs,
        'balls': balls,
        'fours': fours,
        'sixes': sixes,
        'dot_balls': dots
    }).fillna(0)
    
    batter_stats['strike_rate'] = (batter_stats['runs'] / batter_stats['balls']) * 100
    batter_stats['dot_percent'] = (batter_stats['dot_balls'] / batter_stats['balls']) * 100
    batter_stats = batter_stats[batter_stats['balls'] >= 20].sort_values('runs', ascending=False)
    
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(batter_stats.head(20))
    with col2:
        fig = px.bar(batter_stats.head(10), x=batter_stats.head(10).index, y='runs', title="Top Batters", color='strike_rate')
        st.plotly_chart(fig, use_container_width=True)

# ------------------- TAB 2: BOWLERS -------------------------
with tab2:
    st.subheader("Bowler Performance")
    
    bowler_group = df_filtered.groupby('bowler')
    wickets = df_filtered[df_filtered['is_wicket'] == 1].groupby('bowler').size()
    runs_conceded = bowler_group['total_runs'].sum()
    balls_bowled = bowler_group.size()
    dot_balls = df_filtered[df_filtered['total_runs'] == 0].groupby('bowler').size()
    
    bowler_stats = pd.DataFrame({
        'wickets': wickets,
        'runs': runs_conceded,
        'balls': balls_bowled,
        'dot_balls': dot_balls
    }).fillna(0)
    
    bowler_stats['economy'] = (bowler_stats['runs'] / bowler_stats['balls']) * 6
    bowler_stats['dot_percent'] = (bowler_stats['dot_balls'] / bowler_stats['balls']) * 100
    bowler_stats = bowler_stats[bowler_stats['balls'] >= 30].sort_values('wickets', ascending=False)
    
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(bowler_stats.head(20))
    with col2:
        fig = px.bar(bowler_stats.head(10), x=bowler_stats.head(10).index, y='wickets', title="Top Wicket Takers", color='economy')
        st.plotly_chart(fig, use_container_width=True)

# ------------------- TAB 3: MATCH PROGRESSION ----------------
# ------------------- TAB 3: MATCH PROGRESSION (FIXED) ----------------
with tab3:
    st.subheader("Match Run Flow")
    
    # Get unique matches with labels
    match_options = df_filtered[['match_id', 'match_label']].drop_duplicates()
    selected_label = st.selectbox("Select Match", match_options['match_label'].tolist())
    selected_match_id = match_options[match_options['match_label'] == selected_label]['match_id'].values[0]
    
    # Get innings available for this match
    match_data_full = df_filtered[df_filtered['match_id'] == selected_match_id]
    innings_list = sorted(match_data_full['inning'].unique())
    selected_inning = st.selectbox("Select Innings", innings_list)
    
    # Filter to that innings
    match_data = match_data_full[match_data_full['inning'] == selected_inning]
    
    # Now calculate cumulative runs over overs WITHIN this innings
    over_runs = match_data.groupby('over')['total_runs'].sum().cumsum().reset_index()
    over_runs.columns = ['over', 'cumulative_runs']
    
    # Also compute runs per over (optional, for debugging)
    runs_per_over = match_data.groupby('over')['total_runs'].sum().reset_index()
    runs_per_over.columns = ['over', 'runs_in_over']
    
    fig = px.line(over_runs, x='over', y='cumulative_runs', 
                  title=f"{selected_label} - Innings {selected_inning} - Cumulative Runs",
                  labels={'over': 'Over Number', 'cumulative_runs': 'Total Runs So Far'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Optional: Show runs per over as bar chart for debugging
    if st.checkbox("Show runs per over (debug)"):
        fig2 = px.bar(runs_per_over, x='over', y='runs_in_over', 
                      title=f"Runs scored in each over - Innings {selected_inning}")
        st.plotly_chart(fig2, use_container_width=True)