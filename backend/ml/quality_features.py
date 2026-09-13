# ============================================================
# FutBud Quality Configuration
#
# Archetype model:
#     What type of player are you?
#
# Quality model:
#     How well do you perform that role?
# ============================================================


QUALITY_FEATURES = {

    # ========================================================
    # DEFENDERS
    # ========================================================

    "positional_cb": [
        "pass_accuracy_pct",
        "duel_win_pct",
        "blocks_per90",
        "interceptions_per90",
        "tackles_per90",
        "dribbled_past_per90",
    ],

    "stopper_cb": [
        "duel_win_pct",
        "tackles_per90",
        "interceptions_per90",
        "blocks_per90",
        "pass_accuracy_pct",
        "dribbled_past_per90",
    ],

    "high_intensity_fullback": [
        "duel_win_pct",
        "dribble_success_pct",
        "tackles_per90",
        "interceptions_per90",
        "key_passes_per90",
        "assists_per90",
    ],

    "creative_fullback": [
        "key_passes_per90",
        "assists_per90",
        "dribble_success_pct",
        "pass_accuracy_pct",
        "duel_win_pct",
        "interceptions_per90",
    ],


    # ========================================================
    # CENTRAL MIDFIELDERS
    # ========================================================

    # DM / 6
    "defensive_midfielder": [
        "duel_win_pct",
        "tackles_per90",
        "interceptions_per90",
        "pass_accuracy_pct",
        "dribble_success_pct",
    ],

    # CM / 8
    "box_to_box_midfielder": [
        "dribble_success_pct",
        "duel_win_pct",
        "pass_accuracy_pct",
        "goals_per90",
        "assists_per90",
        "tackles_per90",
        "interceptions_per90",
    ],

    # AM / 10
    "attacking_midfielder": [
        "key_passes_per90",
        "assists_per90",
        "goals_per90",
        "shot_accuracy_pct",
        "pass_accuracy_pct",
        "dribble_success_pct",
    ],


    # ========================================================
    # WIDE-ORIENTED MIDFIELDERS
    # ========================================================

    "six_eight_hybrid": [
        "duel_win_pct",
        "tackles_per90",
        "interceptions_per90",
        "dribble_success_pct",
        "fouls_drawn_per90",
        "pass_accuracy_pct",
    ],

    "eight_ten_hybrid": [
        "key_passes_per90",
        "assists_per90",
        "goals_per90",
        "shot_accuracy_pct",
        "dribble_success_pct",
        "pass_accuracy_pct",
    ],


    # ========================================================
    # FORWARDS
    # ========================================================

    "traditional_9": [
        "goals_per90",
        "shot_accuracy_pct",
        "shots_total_per90",
        "duel_win_pct",
        "key_passes_per90",
    ],

    "direct_winger": [
        "dribble_success_pct",
        "goals_per90",
        "shot_accuracy_pct",
        "fouls_drawn_per90",
        "key_passes_per90",
    ],

    "linking_winger": [
        "key_passes_per90",
        "assists_per90",
        "pass_accuracy_pct",
        "goals_per90",
        "shot_accuracy_pct",
    ],
}


# ============================================================
# ROLE-SPECIFIC WEIGHTS
#
# All weights for an archetype sum to 1.0.
# ============================================================

QUALITY_WEIGHTS = {

    "positional_cb": {
        "pass_accuracy_pct": 0.25,
        "duel_win_pct": 0.20,
        "blocks_per90": 0.15,
        "interceptions_per90": 0.15,
        "tackles_per90": 0.10,
        "dribbled_past_per90": 0.15,
    },

    "stopper_cb": {
        "duel_win_pct": 0.25,
        "tackles_per90": 0.20,
        "interceptions_per90": 0.20,
        "blocks_per90": 0.15,
        "pass_accuracy_pct": 0.10,
        "dribbled_past_per90": 0.10,
    },

    "high_intensity_fullback": {
        "duel_win_pct": 0.15,
        "dribble_success_pct": 0.15,
        "tackles_per90": 0.20,
        "interceptions_per90": 0.15,
        "key_passes_per90": 0.20,
        "assists_per90": 0.15,
    },

    "creative_fullback": {
        "key_passes_per90": 0.25,
        "assists_per90": 0.20,
        "dribble_success_pct": 0.15,
        "pass_accuracy_pct": 0.15,
        "duel_win_pct": 0.10,
        "interceptions_per90": 0.15,
    },

    "defensive_midfielder": {
        "duel_win_pct": 0.25,
        "tackles_per90": 0.25,
        "interceptions_per90": 0.25,
        "pass_accuracy_pct": 0.20,
        "dribble_success_pct": 0.05,
    },

    "box_to_box_midfielder": {
        "dribble_success_pct": 0.15,
        "duel_win_pct": 0.15,
        "pass_accuracy_pct": 0.15,
        "goals_per90": 0.15,
        "assists_per90": 0.10,
        "tackles_per90": 0.15,
        "interceptions_per90": 0.15,
    },

    "attacking_midfielder": {
        "key_passes_per90": 0.25,
        "assists_per90": 0.20,
        "goals_per90": 0.20,
        "shot_accuracy_pct": 0.10,
        "pass_accuracy_pct": 0.10,
        "dribble_success_pct": 0.15,
    },

    "six_eight_hybrid": {
        "duel_win_pct": 0.20,
        "tackles_per90": 0.20,
        "interceptions_per90": 0.20,
        "dribble_success_pct": 0.15,
        "fouls_drawn_per90": 0.10,
        "pass_accuracy_pct": 0.15,
    },

    "eight_ten_hybrid": {
        "key_passes_per90": 0.25,
        "assists_per90": 0.15,
        "goals_per90": 0.20,
        "shot_accuracy_pct": 0.10,
        "dribble_success_pct": 0.15,
        "pass_accuracy_pct": 0.15,
    },

    "traditional_9": {
        "goals_per90": 0.35,
        "shot_accuracy_pct": 0.25,
        "shots_total_per90": 0.20,
        "duel_win_pct": 0.10,
        "key_passes_per90": 0.10,
    },

    "direct_winger": {
        "dribble_success_pct": 0.30,
        "goals_per90": 0.25,
        "shot_accuracy_pct": 0.15,
        "fouls_drawn_per90": 0.15,
        "key_passes_per90": 0.15,
    },

    "linking_winger": {
        "key_passes_per90": 0.30,
        "assists_per90": 0.25,
        "pass_accuracy_pct": 0.15,
        "goals_per90": 0.15,
        "shot_accuracy_pct": 0.15,
    },
}


# ============================================================
# LOWER IS BETTER
# ============================================================

LOWER_IS_BETTER = {
    "dribbled_past_per90",
    "fouls_committed_per90",
}


# ============================================================
# DISPLAY NAMES
# ============================================================

ARCHETYPE_DISPLAY_NAMES = {

    "positional_cb":
        "Positional Center Back",

    "stopper_cb":
        "Stopper Center Back",

    "high_intensity_fullback":
        "High-Intensity Fullback",

    "creative_fullback":
        "Creative Fullback",

    "defensive_midfielder":
        "Defensive Midfielder (DM / 6)",

    "box_to_box_midfielder":
        "Box-to-Box Midfielder (CM / 8)",

    "attacking_midfielder":
        "Attacking Midfielder (AM / 10)",

    "six_eight_hybrid":
        "6/8 Hybrid",

    "eight_ten_hybrid":
        "8/10 Hybrid",

    "traditional_9":
        "Traditional No. 9",

    "direct_winger":
        "Direct Forward",

    "linking_winger":
        "Linking Forward",
}