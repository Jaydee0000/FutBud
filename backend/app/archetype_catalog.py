"""Presentation metadata for the frozen FutBud v1 archetypes.

The keys in this module match the persisted model outputs. Rating weights are
deliberately not defined here: the rankings API reads the generated weights
from ``player_season_rating_metrics``.
"""


ARCHETYPE_GROUPS = (
    {
        "key": "defenders",
        "name": "Defenders",
        "position": "D",
        "archetypes": (
            "positional_cb",
            "stopper_cb",
            "high_intensity_fullback",
            "creative_fullback",
        ),
    },
    {
        "key": "midfielders",
        "name": "Midfielders",
        "position": "M",
        "archetypes": (
            "defensive_midfielder",
            "box_to_box_midfielder",
            "attacking_midfielder",
            "six_eight_hybrid",
            "eight_ten_hybrid",
        ),
    },
    {
        "key": "forwards",
        "name": "Forwards",
        "position": "F",
        "archetypes": (
            "traditional_9",
            "direct_winger",
            "linking_winger",
        ),
    },
)


POSITION_GROUP_DESCRIPTIONS = {
    "D": (
        "Compare every rated defender, then narrow the ranking to a "
        "specific defensive archetype if needed."
    ),
    "M": (
        "Compare every rated midfielder, then narrow the ranking to a "
        "specific midfield archetype if needed."
    ),
    "F": (
        "Compare every rated forward, then narrow the ranking to a "
        "specific forward archetype if needed."
    ),
}


ARCHETYPE_METADATA = {
    "positional_cb": {
        "name": "Positional Center Back",
        "shortName": "Positional CB",
        "description": (
            "A center back focused on positioning, ball security, "
            "defensive reliability, and controlled buildup."
        ),
    },
    "stopper_cb": {
        "name": "Stopper Center Back",
        "shortName": "Stopper CB",
        "description": (
            "A more aggressive center back profile with higher defensive "
            "intervention and direct duel involvement."
        ),
    },
    "high_intensity_fullback": {
        "name": "High-Intensity Fullback",
        "shortName": "High-Intensity FB",
        "description": (
            "A fullback with strong defensive activity and frequent "
            "forward involvement."
        ),
    },
    "creative_fullback": {
        "name": "Creative Fullback",
        "shortName": "Creative FB",
        "description": (
            "A wide defender who contributes heavily to chance creation, "
            "passing, and progression."
        ),
    },
    "defensive_midfielder": {
        "name": "Defensive Midfielder",
        "shortName": "Defensive Midfielder",
        "description": (
            "A deeper midfielder focused on defensive control, ball "
            "recovery, and possession security."
        ),
    },
    "box_to_box_midfielder": {
        "name": "Box-to-Box Midfielder",
        "shortName": "Box-to-Box",
        "description": (
            "A high-involvement midfielder contributing across defensive, "
            "transitional, and attacking phases."
        ),
    },
    "attacking_midfielder": {
        "name": "Attacking Midfielder",
        "shortName": "Attacking Midfielder",
        "description": (
            "An advanced midfielder centered on creativity, chance "
            "creation, and attacking involvement."
        ),
    },
    "six_eight_hybrid": {
        "name": "6/8 Hybrid",
        "shortName": "6/8 Hybrid",
        "description": (
            "A midfielder combining deeper defensive responsibilities "
            "with progressive and box-to-box involvement."
        ),
    },
    "eight_ten_hybrid": {
        "name": "8/10 Hybrid",
        "shortName": "8/10 Hybrid",
        "description": (
            "A midfielder combining central progression with advanced "
            "creative involvement."
        ),
    },
    "traditional_9": {
        "name": "Traditional No. 9",
        "shortName": "Traditional No. 9",
        "description": (
            "A central forward primarily focused on finishing and direct "
            "attacking output."
        ),
    },
    "direct_winger": {
        "name": "Direct Forward",
        "shortName": "Direct Forward",
        "description": (
            "A forward profile emphasizing direct attacking actions, "
            "carries, dribbling, and goal threat."
        ),
    },
    "linking_winger": {
        "name": "Linking Forward",
        "shortName": "Linking Forward",
        "description": (
            "A forward who combines attacking output with more passing, "
            "buildup, and chance-creation involvement."
        ),
    },
}


METRIC_DISPLAY_NAMES = {
    "assists_per90": "Assists",
    "blocks_per90": "Blocks",
    "dribble_success_pct": "Dribble Success",
    "dribbled_past_per90": "Avoiding Being Dribbled Past",
    "duel_win_pct": "Duel Win Rate",
    "fouls_drawn_per90": "Fouls Drawn",
    "goals_per90": "Goals",
    "interceptions_per90": "Interceptions",
    "key_passes_per90": "Key Passes",
    "pass_accuracy_pct": "Pass Accuracy",
    "shot_accuracy_pct": "Shot Accuracy",
    "shots_total_per90": "Shots",
    "tackles_per90": "Tackles",
}


def metric_display_name(feature: str) -> str:
    """Return a stable readable name, including for future stored metrics."""

    return METRIC_DISPLAY_NAMES.get(
        feature,
        feature.replace("_per90", "").replace("_pct", "").replace("_", " ").title(),
    )


def archetype_group(archetype_key: str):
    for group in ARCHETYPE_GROUPS:
        if archetype_key in group["archetypes"]:
            return group

    return None
