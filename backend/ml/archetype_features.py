POSITION_NAMES = {
    "D": "Defender",
    "M": "Midfielder",
    "F": "Forward",
}


ARCHETYPE_FEATURES = {

    "D": [
        "passes_total_per90",
        "pass_accuracy_pct",

        "tackles_per90",
        "blocks_per90",
        "interceptions_per90",

        "duels_total_per90",
        "duel_win_pct",

        "dribbles_attempted_per90",
        "dribble_success_pct",

        "key_passes_per90",
        "shots_total_per90",

        "fouls_committed_per90",
        "dribbled_past_per90",
    ],

    "M": [
        "passes_total_per90",
        "pass_accuracy_pct",

        "key_passes_per90",
        "assists_per90",

        "tackles_per90",
        "interceptions_per90",

        "duels_total_per90",
        "duel_win_pct",

        "dribbles_attempted_per90",
        "dribble_success_pct",

        "shots_total_per90",
        "goals_per90",

        "fouls_drawn_per90",
    ],

    "F": [
        "shots_total_per90",
        "key_passes_per90",
        "passes_total_per90",
        "dribbles_attempted_per90",
        "duels_total_per90",
        "fouls_drawn_per90",
    ],
}