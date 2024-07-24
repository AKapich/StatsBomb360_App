import streamlit as st
from streamlit_extras.badges import badge
from auxiliary import match_dict, matches, create_timestring, get_event_dict, create_plot, shot_freeze_frame
from statsbombpy import sb
import pandas as pd


st.set_page_config(
        page_title="Euro 2024: StatsBomb 360° Data Explorer",
        page_icon='https://raw.githubusercontent.com/AKapich/StatsBomb360_App/main/logos/eurologo.ico',
    )


st.title("Euro 2024: StatsBomb 360° Tool")
st.markdown("*Platform providing insight into StatsBomb 360° data for every Euro 2024 match*")
st.markdown("---")

st.sidebar.image("https://raw.githubusercontent.com/AKapich/StatsBomb360_App/main/logos/EURO2024.png")

# dropdown for choosing the match
st.sidebar.title("Select Match")
selected_match = st.sidebar.selectbox("Match:", match_dict.keys(), index=1)

mode = st.sidebar.selectbox("Choose mode:", ['Timestamp Slider', 'Shot Freeze Frame'])

match_id = match_dict[selected_match]
home_team = selected_match.split(' - ')[0]
away_team = selected_match.split(' - ')[1]
competition_stage = matches[matches['match_id']==match_id].iloc[0]['competition_stage']


# data
frame_df = sb.frames(match_id=match_id, fmt='dataframe')
frame_df = frame_df.rename(columns={'location': 'player_location'})
event_df = sb.events(match_id=match_id)
event_df['timestring'] = event_df.apply(create_timestring, axis=1)

df = pd.merge(frame_df, event_df, on='id', how='right')
df = df.sort_values('timestring')

if mode == 'Timestamp Slider':
    chosen_timestamp = st.select_slider("Select timestamp", options=df[(df['visible_area'].notna()) | (df['type']=='Shot')]['timestring'].unique())
    event_dict = get_event_dict(df=df, chosen_timestamp=chosen_timestamp)

    displayed_event = st.selectbox("Select event", options=event_dict.keys())
    voronoi = st.checkbox("Highlight controlled space")

    st.pyplot(create_plot(df, event_dict, chosen_timestamp, displayed_event, voronoi, home_team, away_team))

elif mode == 'Shot Freeze Frame':
    tab1, tab2 = st.tabs(["📈 Charts", "📄 Shot Info"])
    shot_info = event_df[event_df['shot_outcome'].notna()][['player', 'timestring', 'shot_outcome', 'shot_statsbomb_xg', 'shot_technique', 'shot_body_part']]
    shot_info.index = range(1, len(shot_info)+1)

    with tab1:
        shot_cols = ['player', 'team', 'timestring', 'shot_outcome', 'shot_freeze_frame', 'location', 'shot_end_location']
        shot_df = event_df[event_df['shot_outcome'].notna()][shot_cols]
        shot_df['tag'] = shot_df['player'] + ' - ' + shot_df['timestring'] + ' ( ' + shot_df['shot_outcome'] + ' )'

        tag = st.selectbox("Choose shot",options=shot_df['tag'].to_list())

        st.pyplot(shot_freeze_frame(shot_df, tag, home_team, away_team))

    with tab2:
        shot_info.columns = ["Player", "Timestamp", "Shot Outcome", "xG", "Technique", "Body Part"]
        st.dataframe(shot_info)


st.markdown('---')
st.image('https://raw.githubusercontent.com/AKapich/StatsBomb360_App/main/logos/sb_icon.png',
          caption='App made by Aleks Kapich. Data powered by StatsBomb', use_column_width=True)

# signature
st.sidebar.markdown('---')
col1, col2 = st.columns(2)
with col1:
    st.sidebar.markdown("App made by **Aleks Kapich**")
with col2:
    with st.sidebar:
        badge(type="twitter", name="AKapich")
        badge(type="github", name="AKapich")
        badge(type="buymeacoffee", name="akapich")
