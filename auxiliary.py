from statsbombpy import sb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# Data from Euro 2024
matches = sb.matches(competition_id=55, season_id=282)
match_dict = {home+' - '+away: match_id
                 for match_id, home, away
                 in zip(matches['match_id'], matches['home_team'], matches['away_team'])}


country_colors = {
    "Poland": "#ffffff",
    "Denmark": "#C60C30",
    "Portugal": "#006400",
    "Germany": "#000000",
    "France": "#0055A4",
    "Netherlands": "#E77E02",
    "Belgium": "#FFD700",
    "Spain": "#C60C30",
    "Croatia": "#FF0000",
    "England": "#002366",
    "Serbia": "#DC143C",
    "Switzerland": "#FF0000",
    "Scotland": '#006cb7',
    'Hungary': '#008d55',
    'Albania': '#ed1b24',
    'Italy': '#009247',
    'Slovenia': '#005aab',
    'Austria': '#ed1b24',
    'Slovakia': '#005aab',
    'Romania': '#ffde00',
    'Ukraine': '#005aab',
    'Turkey': '#ed1b24',
    'Georgia': '#fffffc',
    'Czech Republic': '#005aab'
}


def create_timestring(row):
    second_component = str(row['second']) if row['second'] > 9 else '0'+str(row['second'])
    minute_component = str(row['minute']) if row['minute'] > 9 else '0'+str(row['minute'])
    return minute_component + ':' + second_component


def get_event_dict(df, chosen_timestamp):
    timestamp_events = df[df['timestring']==chosen_timestamp]
    timestamp_events = timestamp_events[timestamp_events['visible_area'].notna()]

    timestamp_events['event_tag'] = timestamp_events['player'] + ': ' + timestamp_events['type']
    event_dict = dict(zip(timestamp_events['event_tag'], timestamp_events['id']))
    event_dict = {k: v for k, v in event_dict.items() if not pd.isna(k)}
    return event_dict


def create_plot(df, event_dict, chosen_timestamp, displayed_event, voronoi, home_team, away_team):
    home_color = country_colors[home_team]
    away_color = country_colors[away_team]

    frame = df[df['timestring']==chosen_timestamp]
    frame = frame[frame['id']==event_dict[displayed_event]]

    fig ,ax = plt.subplots(figsize=(13, 8),constrained_layout=False, tight_layout=True)
    fig.set_facecolor('#0e1117')
    ax.patch.set_facecolor('#0e1117')
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0e1117', line_color='#c7d5cc')
    pitch.draw(ax=ax)

    visible_area = np.array(frame.iloc[0].visible_area).reshape(-1, 2)
    polygon_color = 'None' if voronoi else 'gray'
    visible = pitch.polygon([visible_area], color=polygon_color, linestyle='-.', lw=3, ax=ax, ec='white', alpha=0.2)

    for _, row in frame.iterrows():
        if row['team'] == home_team:
            color = home_color if row['teammate'] else away_color
        elif row['team'] == away_team:
            color = away_color if row['teammate'] else home_color
        marker = 'o' if not row['keeper'] else 'D'
        size = 70
        if row['actor']:
            marker = '*'
            size = 200
        plt.scatter(
            x=row['player_location'][0],
            y=row['player_location'][1],
            color=color,
            marker=marker,
            s=size,
            edgecolors='black'
        )

    row = df[df['id']==event_dict[displayed_event]].iloc[0]
    pitch.annotate(
        displayed_event.split(': ')[0],
        xy=(row["location"][0], row["location"][1]-2),
        c='white', va='center', ha='center',
        size=9, fontweight='bold', ax=ax
    )

    if voronoi:
        team1, team2 = pitch.voronoi([loc[0] for loc in frame['player_location']], [loc[1] for loc in frame['player_location']], frame['teammate'])
        if row['team'] == away_team:
            team1, team2 = team2, team1
        t1 = pitch.polygon(team1, ax=ax, fc=home_color, ec='gray', lw=3, alpha=0.3)
        t2 = pitch.polygon(team2, ax=ax, fc=away_color, ec='gray', lw=3, alpha=0.3)
        for p1 in t1:
            p1.set_clip_path(visible[0])
        for p2 in t2:
            p2.set_clip_path(visible[0])

    if row['type'] == 'Carry':
        pitch.arrows(
            xstart=row["location"][0],
            ystart=row["location"][1],
            xend=row['carry_end_location'][0],
            yend=row['carry_end_location'][1],
            ax=ax,
            color='white',
            linestyle='--'
        )
    elif row['type'] in ['Pass', 'Shot']:
        type = 'pass' if row['type'] == 'Pass' else 'shot'
        pitch.lines(
            xstart=row["location"][0],
            ystart=row["location"][1],
            xend=row[f'{type}_end_location'][0],
            yend=row[f'{type}_end_location'][1],
            ax=ax,
            comet=True,
            color='white'
        )

    return fig


def shot_freeze_frame(shot_df, tag, home_team, away_team):
    shot = shot_df[shot_df['tag']==tag].iloc[0]
    home_color = country_colors[home_team]
    away_color = country_colors[away_team]

    fig ,ax = plt.subplots(figsize=(13, 8),constrained_layout=False, tight_layout=True)
    fig.set_facecolor('#0e1117')
    ax.patch.set_facecolor('#0e1117')
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0e1117', line_color='#c7d5cc')
    pitch.draw(ax=ax)

    for player in shot['shot_freeze_frame']:
        if shot['team'] == home_team:
            color = home_color if player['teammate'] else away_color
        elif shot['team'] == away_team:
            color = away_color if player['teammate'] else home_color
        
        plt.scatter(
            x=player['location'][0],
            y=player['location'][1],
            color=color,
            marker='o',
            s=100,
            edgecolors='black'
        )

    pitch.annotate(
        shot['player'],
        xy=(shot['location'][0], shot['location'][1]-2),
        c='white', va='center', ha='center',
        size=9, fontweight='bold', ax=ax
    )
    color = home_color if shot['team'] == home_team else away_color
    plt.scatter(
        x=shot['location'][0],
        y=shot['location'][1],
        color=color,
        marker='*',
        s=450,
        edgecolors='black'
    )
    pitch.lines(
        xstart=shot['location'][0],
        ystart=shot["location"][1],
        xend=shot['shot_end_location'][0],
        yend=shot['shot_end_location'][1],
        ax=ax,
        comet=True,
        color='white'
    )

    if shot['shot_outcome'] in ['Blocked', 'Saved']:
        color = away_color if shot['team'] == home_team else home_color
        marker='X'
        size=300
    elif shot['shot_outcome'] == 'Goal':
        color='white'
        marker='D'
        size=120
        
    plt.scatter(
        x=shot['shot_end_location'][0],
        y=shot['shot_end_location'][1],
        color=color,
        marker=marker,
        s=size,
        edgecolors='black'
    )
        
    return fig
