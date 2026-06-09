import io
import random
from datetime import datetime

import streamlit as st
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo

st.set_page_config(
    page_title="MIDI Pad Generator",
    page_icon="🎹",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700;800&display=swap');

    :root {
        --bg0: #060914;
        --bg1: #0b1220;
        --panel: rgba(12, 20, 34, 0.94);
        --panel2: rgba(16, 27, 45, 0.98);
        --text: #f9fbff;
        --muted: #cdd7ea;
        --cyan: #5ee7ff;
        --blue: #7aa2ff;
        --pink: #ff7ad9;
        --lime: #d7ff75;
        --orange: #ffbd5a;
        --border: rgba(126, 166, 255, 0.42);
    }

    html, body, [class*="css"], .stApp {
        font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 8%, rgba(94, 231, 255, 0.20), transparent 28%),
            radial-gradient(circle at 85% 16%, rgba(122, 162, 255, 0.18), transparent 30%),
            radial-gradient(circle at 52% 95%, rgba(255, 189, 90, 0.10), transparent 34%),
            linear-gradient(135deg, var(--bg0) 0%, var(--bg1) 48%, #090d18 100%);
        color: var(--text) !important;
    }

    h1, h2, h3, h4, h5, h6, p, label, span, div, small {
        color: var(--text) !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(5, 12, 25, 0.98), rgba(9, 18, 35, 0.98)) !important;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * {
        color: var(--text) !important;
    }

    .hero-card {
        border: 1px solid var(--border);
        background: linear-gradient(135deg, rgba(13, 23, 40, 0.98), rgba(17, 31, 53, 0.92));
        border-radius: 26px;
        padding: 26px 30px;
        box-shadow: 0 22px 70px rgba(0,0,0,0.38), 0 0 34px rgba(122, 162, 255, 0.10);
        margin-bottom: 16px;
    }

    .hero-title {
        font-size: 2.55rem;
        line-height: 1.03;
        font-weight: 900;
        letter-spacing: -0.055em;
        margin-bottom: 10px;
        color: #ffffff !important;
        text-shadow: 0 0 18px rgba(122, 162, 255, 0.22);
    }

    .hero-subtitle {
        color: var(--muted) !important;
        font-size: 1.06rem;
        max-width: 980px;
        font-weight: 500;
    }

    .mini-card {
        border: 1px solid rgba(69, 243, 255, 0.32);
        background: linear-gradient(135deg, rgba(10, 22, 42, 0.94), rgba(16, 31, 58, 0.86));
        border-radius: 22px;
        padding: 18px;
        min-height: 112px;
        box-shadow: 0 14px 46px rgba(0,0,0,0.28);
    }

    .mini-title {
        font-size: 0.78rem;
        color: var(--cyan) !important;
        text-transform: uppercase;
        letter-spacing: 0.13em;
        font-weight: 800;
    }

    .mini-value {
        font-size: 1.42rem;
        font-weight: 800;
        color: #ffffff !important;
        margin-top: 8px;
    }

    .chord-box {
        background: rgba(3, 9, 20, 0.88);
        border: 1px solid rgba(69, 243, 255, 0.28);
        border-radius: 17px;
        padding: 14px 16px;
        font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.96rem;
        color: #ffffff !important;
        margin-bottom: 8px;
        box-shadow: inset 0 0 18px rgba(69, 243, 255, 0.045);
    }

    .viz-shell {
        border: 1px solid rgba(69, 243, 255, 0.34);
        background:
            linear-gradient(135deg, rgba(3, 9, 20, 0.92), rgba(10, 22, 42, 0.88)),
            repeating-linear-gradient(90deg, rgba(255,255,255,0.035) 0px, rgba(255,255,255,0.035) 1px, transparent 1px, transparent 64px);
        border-radius: 24px;
        padding: 18px;
        margin: 14px 0 24px 0;
        box-shadow: 0 18px 58px rgba(0,0,0,0.36), inset 0 0 28px rgba(69, 243, 255, 0.035);
    }

    .viz-title {
        color: #ffffff !important;
        font-size: 1.05rem;
        font-weight: 800;
        letter-spacing: -0.015em;
        margin-bottom: 12px;
    }

    .viz-track-label {
        color: var(--cyan) !important;
        font-weight: 800;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin: 14px 0 8px 0;
    }

    .viz-row {
        display: flex;
        gap: 7px;
        align-items: stretch;
        width: 100%;
        overflow-x: auto;
        padding-bottom: 6px;
    }

    .viz-block {
        min-width: 58px;
        flex: 1;
        border-radius: 14px;
        padding: 10px 8px;
        border: 1px solid rgba(255,255,255,0.14);
        background: linear-gradient(180deg, rgba(69, 243, 255, 0.28), rgba(79, 140, 255, 0.12));
        box-shadow: 0 0 18px rgba(69, 243, 255, 0.12);
        position: relative;
        min-height: 78px;
    }

    .viz-block.voicy {
        background: linear-gradient(180deg, rgba(255, 79, 216, 0.32), rgba(91, 124, 255, 0.13));
        box-shadow: 0 0 18px rgba(255, 79, 216, 0.13);
    }

    .viz-block.normal {
        background: linear-gradient(180deg, rgba(199, 255, 79, 0.22), rgba(69, 243, 255, 0.10));
        box-shadow: 0 0 18px rgba(199, 255, 79, 0.10);
    }

    .viz-step {
        color: rgba(255,255,255,0.72) !important;
        font-size: 0.72rem;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .viz-name {
        color: #ffffff !important;
        font-size: 0.84rem;
        font-weight: 800;
        line-height: 1.12;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .viz-range {
        position: absolute;
        left: 8px;
        right: 8px;
        bottom: 8px;
        height: 6px;
        border-radius: 999px;
        background: rgba(255,255,255,0.18);
        overflow: hidden;
    }

    .viz-range-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, var(--cyan), var(--pink));
        box-shadow: 0 0 12px rgba(69,243,255,0.45);
    }

    .viz-note-cloud {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 12px;
    }

    .viz-note-pill {
        color: #ffffff !important;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(69, 243, 255, 0.22);
        border-radius: 999px;
        padding: 4px 8px;
        font-size: 0.76rem;
        font-weight: 800;
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 15px !important;
        border: 1px solid rgba(69, 243, 255, 0.72) !important;
        background: linear-gradient(135deg, #3b82f6 0%, #7c9cff 52%, #ffbd5a 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        min-height: 48px;
        text-shadow: 0 1px 1px rgba(0,0,0,0.45);
        box-shadow: 0 10px 28px rgba(0, 212, 255, 0.16);
    }

    .stButton > button *, .stDownloadButton > button * {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        border: 1px solid #ffffff !important;
        filter: brightness(1.12) saturate(1.12);
        box-shadow: 0 0 26px rgba(69, 243, 255, 0.32);
    }

    /* Streamlit select boxes: closed state */
    div[data-baseweb="select"] > div {
        background: var(--panel2) !important;
        border: 1px solid rgba(69, 243, 255, 0.50) !important;
        border-radius: 14px !important;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.04);
    }

    div[data-baseweb="select"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    div[data-baseweb="select"] svg {
        fill: var(--cyan) !important;
        color: var(--cyan) !important;
    }

    /* Streamlit select menu dropdown options */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background: #07111f !important;
        border: 1px solid rgba(69, 243, 255, 0.45) !important;
        color: #ffffff !important;
    }

    li[role="option"], li[role="option"] div, li[role="option"] span {
        background: #07111f !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.35), rgba(255, 79, 216, 0.26)) !important;
        color: #ffffff !important;
    }

    /* Text inputs, number inputs, sliders, checkboxes */
    input, textarea {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background: var(--panel2) !important;
    }

    .stSlider label, .stSelectbox label, .stNumberInput label, .stCheckbox label {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    .stCheckbox span, .stCheckbox div, .stMarkdown, .stInfo, .stAlert {
        color: #ffffff !important;
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] div {
        color: #ffffff !important;
    }

    .stCaption, [data-testid="stCaptionContainer"] {
        color: var(--muted) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

NOTE_MAP = {
    "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
    "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11
}
NOTE_NAMES = list(NOTE_MAP.keys())

MODES = {
    "ionian": [0, 2, 4, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
    "minor_pentatonic": [0, 3, 5, 7, 10],
}

PRESET_DESCRIPTIONS = {
    "standard": "Balanced default chord motion.",
    "ambient": "Soft floating pads with open drift.",
    "weird": "Off-center harmonic movement.",
    "dark": "Minor-weighted fog chords.",
    "dystopian": "Tense uneasy futuristic harmony.",
    "jazz": "Richer more colorful chord movement.",
    "emotional": "Melancholic but musical chord flow.",
    "uplifting": "Brighter rising harmonic movement.",
    "sad": "Tender descending minor flavor.",
    "introspective": "Reflective inward-looking harmony.",
    "spacey": "Suspended cosmic drift.",
    "am_fmhead": "Radiohead-ish left-turn harmonic color.",
    "boards_of_canada": "Nostalgic hazy analog memory chords.",
    "autechre": "Abstract mechanical harmonic shapes.",
    "bjork": "Art-pop cinematic movement.",
    "alan_parsons_nucleus": "Classic synthic widescreen motion.",
    "gas": "Foggy hypnotic slow bloom.",
    "ross_154": "Deep reflective dubby atmosphere.",
    "detroit_electro": "Machine-soul electro pads.",
    "aux88_fast": "Punchier faster electro stabs and pads.",
    "drexciya_deep": "Aquatic deep electro melancholy.",
    "machine_soul": "Warm emotive Detroit chord glow.",
    "nathan_fake": "Melodic euphoric psychedelic lift.",
    "border_community": "Psychedelic melodic techno emotion.",
    "james_holden": "Spiraling suspended trippy harmony.",
    "underworld": "Big emotional driving pad motion.",
    "underworld_jumbo": "Warm widescreen melancholic lift.",
    "underworld_born_slippy": "Urgent anthem-like rave melancholy.",
    "underworld_pearls_girl": "Dreamy nocturnal rolling sadness.",
    "underworld_snake": "Darker hypnotic suspended tension.",
    "underworld_deep_arch": "Long tunnel pads with slow emotional pressure.",
    "underworld_dirty_epic": "Moody spoken-night-drive chord movement.",
    "vril": "Reduced deep dub-techno haze.",
    "giegling": "Soft wistful minimal house dreaminess.",
    "tin_man_constant_confusion": "Two separate pad layers: revolving fog bed plus voicy bloom pad.",
    "donato_dozzy": "Hypnotic circular techno pads with restrained emotional motion.",
    "david_alvarado_mayasongs": "Warm deep-house pad colors inspired by Mayasongs: spiritual, smoky, lush, and rolling.",
    "cio_dor": "Deep smoky techno elegy, spectral and feminine but cold.",
    "soundtrack_noir": "Dark film-noir pads with minor suspense.",
    "soundtrack_scifi": "Wide sci-fi suspended chords and cosmic dread.",
    "soundtrack_japanese_old_film": "Quiet ghost-memory cinema mood, soft but unsettling.",
    "soundtrack_horror_ambient": "Tense slow dread, clustered and unresolved.",
    "soundtrack_lost_city": "Ancient lonely widescreen atmosphere.",
    "soundtrack_vhs_dream": "Washed nostalgic tape-score progression.",
}

PROGRESSIONS = {
    "standard": [[0, 5, 6, 4], [0, 3, 4, 6], [0, 4, 5, 3]],
    "ambient": [[0, 2, 5, 3], [0, 4, 2, 6], [0, 5, 3, 5], [0, 2, 4, 2]],
    "weird": [[0, 1, 6, 3], [2, 6, 1, 5], [0, 3, 1, 6], [0, 6, 2, 1]],
    "dark": [[0, 6, 5, 4], [0, 3, 6, 2], [0, 5, 3, 2], [0, 1, 5, 4]],
    "dystopian": [[0, 1, 6, 2], [0, 6, 1, 5], [2, 1, 6, 0], [0, 3, 1, 6]],
    "jazz": [[0, 2, 5, 1], [0, 4, 1, 5], [2, 5, 1, 4], [0, 3, 6, 2]],
    "emotional": [[0, 4, 5, 3], [0, 3, 5, 4], [0, 5, 4, 3], [0, 2, 5, 4]],
    "uplifting": [[0, 4, 5, 6], [0, 3, 4, 5], [0, 5, 6, 4], [0, 2, 4, 5]],
    "sad": [[0, 3, 4, 3], [0, 5, 3, 4], [0, 2, 3, 1], [0, 6, 5, 3]],
    "introspective": [[0, 3, 2, 3], [0, 5, 2, 4], [0, 2, 4, 3], [0, 3, 5, 2]],
    "spacey": [[0, 2, 1, 5], [0, 6, 2, 5], [0, 1, 2, 6], [0, 4, 2, 1]],
    "am_fmhead": [[0, 5, 2, 6], [0, 3, 5, 4], [0, 1, 5, 2], [0, 3, 2, 6]],
    "boards_of_canada": [[0, 2, 4, 2], [0, 3, 5, 3], [0, 2, 5, 4], [0, 6, 4, 2]],
    "autechre": [[0, 1, 5, 2], [0, 6, 2, 1], [0, 3, 1, 6], [2, 6, 1, 4]],
    "bjork": [[0, 4, 1, 5], [0, 3, 6, 2], [0, 5, 1, 4], [0, 2, 6, 5]],
    "alan_parsons_nucleus": [[0, 4, 2, 5], [0, 5, 3, 6], [0, 2, 4, 1], [0, 6, 4, 5]],
    "gas": [[0, 5, 4, 5], [0, 5, 3, 5], [0, 4, 5, 4], [0, 2, 5, 2]],
    "ross_154": [[0, 5, 3, 5], [0, 6, 5, 3], [0, 3, 5, 6], [0, 4, 5, 3]],
    "detroit_electro": [[0, 6, 5, 6], [0, 2, 6, 5], [0, 5, 6, 4], [0, 3, 6, 0], [0, 6, 0, 5], [0, 4, 5, 4]],
    "aux88_fast": [[0, 6, 5, 4], [0, 4, 6, 5], [0, 6, 0, 5], [0, 5, 6, 5], [0, 3, 6, 4]],
    "drexciya_deep": [[0, 6, 5, 6], [0, 1, 6, 5], [0, 2, 6, 5], [0, 6, 3, 5], [0, 3, 6, 0]],
    "machine_soul": [[0, 4, 5, 4], [0, 5, 6, 4], [0, 2, 5, 6], [0, 3, 5, 4], [0, 6, 5, 4]],
    "nathan_fake": [[0, 2, 5, 6], [0, 4, 6, 5], [0, 2, 4, 6], [0, 5, 6, 3], [0, 3, 5, 6]],
    "border_community": [[0, 2, 5, 4], [0, 4, 5, 2], [0, 5, 3, 4], [0, 2, 4, 5], [0, 3, 5, 2]],
    "james_holden": [[0, 2, 6, 4], [0, 1, 5, 6], [0, 3, 6, 4], [0, 2, 5, 1], [0, 6, 3, 4]],
    "underworld": [[0, 5, 6, 4], [0, 6, 5, 4], [0, 3, 5, 4], [0, 2, 5, 6], [0, 5, 3, 4]],
    "underworld_jumbo": [[0, 5, 6, 4], [0, 3, 5, 4], [0, 5, 4, 3], [0, 2, 5, 4], [0, 4, 5, 3]],
    "underworld_born_slippy": [[0, 6, 5, 4], [0, 5, 6, 4], [0, 3, 6, 4], [0, 6, 4, 5], [0, 4, 6, 5]],
    "underworld_pearls_girl": [[0, 5, 3, 4], [0, 3, 5, 2], [0, 2, 5, 4], [0, 5, 4, 2], [0, 4, 2, 5]],
    "underworld_snake": [[0, 1, 5, 4], [0, 3, 6, 4], [0, 2, 5, 1], [0, 6, 3, 4], [0, 1, 6, 5]],
    "underworld_deep_arch": [[0, 5, 0, 6], [0, 6, 5, 6], [0, 3, 5, 6], [0, 5, 2, 6]],
    "underworld_dirty_epic": [[0, 3, 5, 4], [0, 6, 5, 3], [0, 2, 5, 4], [0, 5, 3, 2]],
    "vril": [[0, 5, 3, 5], [0, 6, 5, 3], [0, 3, 5, 6], [0, 5, 4, 5], [0, 6, 4, 3]],
    "giegling": [[0, 2, 5, 3], [0, 4, 5, 3], [0, 3, 5, 2], [0, 2, 4, 5], [0, 5, 3, 4]],
    "tin_man_constant_confusion": [[0, 6, 0, 6], [0, 5, 0, 5], [0, 6, 5, 6], [0, 3, 0, 3]],
    "donato_dozzy": [[0, 5, 0, 5], [0, 6, 0, 5], [0, 2, 0, 5], [0, 5, 3, 5], [0, 6, 5, 6]],
    "david_alvarado_mayasongs": [[0, 2, 5, 4], [0, 5, 3, 4], [0, 4, 2, 5], [0, 3, 5, 2], [0, 6, 5, 4], [0, 2, 4, 3]],
    "cio_dor": [[0, 3, 5, 3], [0, 6, 3, 5], [0, 2, 5, 3], [0, 5, 1, 3], [0, 6, 4, 3]],
    "soundtrack_noir": [[0, 3, 6, 2], [0, 1, 5, 4], [0, 5, 3, 1], [0, 6, 2, 3]],
    "soundtrack_scifi": [[0, 1, 5, 1], [0, 6, 2, 6], [0, 4, 1, 5], [0, 2, 6, 1]],
    "soundtrack_japanese_old_film": [[0, 2, 3, 2], [0, 5, 3, 5], [0, 6, 2, 3], [0, 3, 1, 2]],
    "soundtrack_horror_ambient": [[0, 1, 0, 6], [0, 6, 1, 6], [0, 3, 1, 6], [0, 1, 5, 1]],
    "soundtrack_lost_city": [[0, 5, 2, 5], [0, 6, 4, 5], [0, 3, 6, 5], [0, 5, 1, 5]],
    "soundtrack_vhs_dream": [[0, 2, 4, 2], [0, 5, 3, 5], [0, 4, 2, 3], [0, 6, 4, 2]],
}

STYLE_DEFAULTS = {
    "tin_man_constant_confusion": {"root": "A", "mode": "aeolian", "tempo": 121, "length": 2, "blocks": 4, "voicing": "open", "velocity": 72, "sus2": True},
    "donato_dozzy": {"root": "D", "mode": "dorian", "tempo": 126, "length": 4, "blocks": 6, "voicing": "open", "velocity": 68, "sus2": True},
    "david_alvarado_mayasongs": {"root": "G", "mode": "dorian", "tempo": 123, "length": 4, "blocks": 5, "voicing": "wide", "velocity": 74, "sus2": True},
    "cio_dor": {"root": "F", "mode": "aeolian", "tempo": 123, "length": 4, "blocks": 5, "voicing": "wide", "velocity": 64, "sus2": True},
    "soundtrack_noir": {"root": "D", "mode": "harmonic_minor", "tempo": 82, "length": 8, "blocks": 4, "voicing": "low_cluster", "velocity": 70, "sus2": False},
    "soundtrack_scifi": {"root": "C", "mode": "lydian", "tempo": 74, "length": 8, "blocks": 4, "voicing": "wide", "velocity": 62, "sus2": True},
    "soundtrack_japanese_old_film": {"root": "A", "mode": "minor_pentatonic", "tempo": 72, "length": 8, "blocks": 4, "voicing": "open", "velocity": 60, "sus2": True},
    "soundtrack_horror_ambient": {"root": "C", "mode": "phrygian", "tempo": 66, "length": 8, "blocks": 4, "voicing": "low_cluster", "velocity": 58, "sus2": True},
    "soundtrack_lost_city": {"root": "E", "mode": "dorian", "tempo": 78, "length": 8, "blocks": 5, "voicing": "wide", "velocity": 65, "sus2": True},
    "soundtrack_vhs_dream": {"root": "A", "mode": "aeolian", "tempo": 88, "length": 4, "blocks": 5, "voicing": "open", "velocity": 66, "sus2": True},
}

def note_name(note):
    return NOTE_NAMES[note % 12]

def normalize_chord(chord):
    return sorted(dict.fromkeys(int(n) for n in chord))

def clamp_chord_range(chord, low=24, high=108):
    fitted = []
    for note in chord:
        n = int(note)
        while n < low:
            n += 12
        while n > high:
            n -= 12
        fitted.append(n)
    return normalize_chord(fitted)

def chord_to_names(chord):
    return "  ".join(f"{note_name(n)}{(n // 12) - 1}" for n in chord)


def chord_short_name(chord):
    if not chord:
        return "—"
    names = [note_name(n) for n in chord]
    root = names[0]
    color = ""
    intervals = sorted({(n - chord[0]) % 12 for n in chord})
    if 3 in intervals and 10 in intervals:
        color = "m7"
    elif 3 in intervals:
        color = "min"
    elif 4 in intervals and 10 in intervals:
        color = "7"
    elif 4 in intervals:
        color = "maj"
    if 2 in intervals or 14 in [(n - chord[0]) for n in chord]:
        color += " sus/add9"
    return f"{root} {color}".strip()


def pitch_range_percent(chord):
    if not chord:
        return 8
    span = max(chord) - min(chord)
    return max(10, min(100, int((span / 36) * 100)))


def note_cloud(chords):
    notes = []
    for chord in chords:
        for note in chord:
            label = f"{note_name(note)}{(note // 12) - 1}"
            if label not in notes:
                notes.append(label)
    return notes[:32]


def render_performance_view(
    title,
    tracks,
    base_velocity=84,
    velocity_random=0,
    humanize_timing=0,
    length_random=0.0,
    strum_amount=0,
    visual_seed=777,
):
    st.markdown("## 🔭 Performance View")
    st.markdown(
        f"""
        <div style="
            border:1px solid rgba(69,243,255,0.50);
            background:linear-gradient(135deg, rgba(1,8,18,0.96), rgba(8,20,38,0.94));
            border-radius:26px;
            padding:14px 16px;
            margin:8px 0 12px 0;
            box-shadow:0 20px 70px rgba(0,0,0,0.42);
        ">
            <div style="font-size:1.55rem; font-weight:900; color:#ffffff;">{title}</div>
            <div style="font-size:0.98rem; font-weight:800; color:#dbeafe; margin-top:6px;">
                Big readable view: orange = note length, lime = velocity, cyan = timing/strum movement.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    seed_int = int(float(visual_seed) * 1000) if isinstance(visual_seed, float) else int(visual_seed)

    for track_index, (track_name, chords, kind) in enumerate(tracks):
        color = "#ff4fd8" if kind == "voicy" else "#45f3ff" if kind == "fog" else "#c7ff4f"
        track_seed = seed_int + track_index * 100000 + sum(ord(c) for c in track_name)

        st.markdown(
            f"""
            <div style="
                margin-top:12px;
                margin-bottom:6px;
                color:{color};
                font-size:0.98rem;
                font-weight:900;
                letter-spacing:0.02em;
                text-transform:uppercase;
            ">
                {track_name}
            </div>
            """,
            unsafe_allow_html=True,
        )

        cols_per_row = 4
        for row_start in range(0, len(chords), cols_per_row):
            row_chords = chords[row_start:row_start + cols_per_row]
            cols = st.columns(len(row_chords))

            for offset, chord in enumerate(row_chords):
                step = row_start + offset
                chord_rng = random.Random(track_seed + step * 991)
                length_push = 1.0
                if length_random > 0:
                    length_push = chord_rng.uniform(max(0.20, 1.0 - length_random), 1.0 + length_random)

                notes_html = []
                for note_index, note in enumerate(chord):
                    note_seed = track_seed + step * 1009 + note * 17 + note_index * 131
                    note_rng = random.Random(note_seed)

                    timing_px = 0
                    timing_label = 0
                    if humanize_timing > 0:
                        timing_label = note_rng.randint(-humanize_timing, humanize_timing)

                    strum_label = note_index * strum_amount
                    visual_velocity = int(base_velocity)
                    if velocity_random > 0:
                        visual_velocity = max(1, min(127, visual_velocity + note_rng.randint(-velocity_random, velocity_random)))

                    note_length_push = length_push
                    if length_random > 0:
                        note_length_push *= note_rng.uniform(max(0.30, 1.0 - (length_random * 0.55)), 1.0 + (length_random * 0.55))
                    length_pct = max(10, min(100, int(note_length_push * 65)))
                    vel_pct = max(5, min(100, int((visual_velocity / 127) * 100)))
                    label = f"{note_name(note)}{(note // 12) - 1}"

                    notes_html.append(
                        f"""
                        <div style="
                            display:grid;
                            grid-template-columns:52px 1fr 42px;
                            align-items:center;
                            gap:7px;
                            margin:4px 0;
                            padding:5px 7px;
                            border-radius:10px;
                            background:rgba(255,255,255,0.055);
                            border-left:3px solid #45f3ff;
                        ">
                            <div style="font-size:1.02rem; font-weight:900; color:#ffffff;">{label}</div>
                            <div>
                                <div style="height:6px; width:{length_pct}%; max-width:100%; background:#ffb020; border-radius:999px; box-shadow:0 0 12px rgba(255,176,32,0.35);"></div>
                                <div style="height:4px; width:{vel_pct}%; background:#c7ff4f; border-radius:999px; margin-top:4px; box-shadow:0 0 10px rgba(199,255,79,0.30);"></div>
                            </div>
                            <div style="font-size:0.62rem; line-height:1.05; color:#dbeafe; font-weight:900;">
                                V{visual_velocity}<br>
                                T{timing_label:+}<br>
                                S{strum_label}
                            </div>
                        </div>
                        """
                    )

                chord_name = chord_short_name(chord)
                low_note = f"{note_name(min(chord))}{(min(chord) // 12) - 1}"
                high_note = f"{note_name(max(chord))}{(max(chord) // 12) - 1}"

                with cols[offset]:
                    st.markdown(
                        f"""
                        <div style="
                            border:1px solid rgba(69,243,255,0.42);
                            background:linear-gradient(135deg, rgba(2,10,23,0.98), rgba(9,24,45,0.95));
                            border-radius:18px;
                            padding:11px;
                            margin-bottom:6px;
                            min-height:170px;
                            box-shadow:0 14px 44px rgba(0,0,0,0.32);
                        ">
                            <div style="display:flex; justify-content:space-between; align-items:center; gap:10px;">
                                <div style="font-size:0.82rem; font-weight:900; color:#45f3ff; letter-spacing:0.12em;">STEP {step + 1:02d}</div>
                                <div style="font-size:0.76rem; font-weight:900; color:#c5d4ef;">{low_note} → {high_note}</div>
                            </div>
                            <div style="font-size:1.12rem; font-weight:900; color:#ffffff; margin-top:5px; margin-bottom:7px;">
                                {chord_name}
                            </div>
                            {''.join(notes_html)}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    st.markdown(
        """
        <div style="
            display:flex;
            flex-wrap:wrap;
            gap:10px;
            margin:12px 0 20px 0;
            font-weight:900;
            color:#ffffff;
        ">
            <span style="background:rgba(255,176,32,0.22); border:1px solid rgba(255,176,32,0.5); padding:7px 12px; border-radius:999px;">Orange = length</span>
            <span style="background:rgba(199,255,79,0.18); border:1px solid rgba(199,255,79,0.45); padding:7px 12px; border-radius:999px;">Lime = velocity</span>
            <span style="background:rgba(69,243,255,0.16); border:1px solid rgba(69,243,255,0.45); padding:7px 12px; border-radius:999px;">T = timing drift</span>
            <span style="background:rgba(255,79,216,0.16); border:1px solid rgba(255,79,216,0.45); padding:7px 12px; border-radius:999px;">S = strum offset</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


import random
# --- NEW FUNCTION: render_piano_roll ---
def render_piano_roll(title, tracks, length_beats=8, base_velocity=84, velocity_random=0, humanize_timing=0, length_random=0.0, strum_amount=0, visual_seed=777):
    all_notes = []
    for _track_name, chords, _kind in tracks:
        for chord in chords:
            all_notes.extend(chord)

    if not all_notes:
        st.warning("No MIDI notes available for piano roll.")
        return

    min_note = max(24, min(all_notes) - 2)
    max_note = min(108, max(all_notes) + 2)
    note_rows = list(range(max_note, min_note - 1, -1))

    row_h = 26
    label_w = 72
    step_w = 118
    top_h = 38
    automation_h = 104
    track_gap = 42
    width = label_w + max(1, max(len(chords) for _, chords, _ in tracks)) * step_w + 40
    roll_h = len(note_rows) * row_h
    total_h = top_h + sum(roll_h + automation_h + track_gap for _ in tracks) + 30
    seed_int = int(float(visual_seed) * 1000) if isinstance(visual_seed, float) else int(visual_seed)

    def y_for_note(note, base_y):
        return base_y + note_rows.index(note) * row_h

    def color_for_kind(kind):
        if kind == "voicy":
            return "#ff4fd8"
        if kind == "fog":
            return "#45f3ff"
        return "#c7ff4f"

    svg = []
    svg.append(f"""
    <div style="border:1px solid rgba(69,243,255,0.62); border-radius:18px; padding:22px; background:rgba(1,6,15,0.96); box-shadow:0 18px 58px rgba(0,0,0,0.44); margin:18px 0; overflow-x:auto;">
    <div style="color:#ffffff; font-weight:900; font-size:1.65rem; margin-bottom:8px;">🎹 {title}</div>
    <div style="color:#dbeafe; font-weight:800; font-size:1rem; margin-bottom:16px;">White MIDI labels show pitch. Thin cyan line = note length, lime start line = timing/strum, lime underline = velocity. Increase Length variation and click Generate to see cyan lines change.</div>
    <svg width="{width}" height="{total_h}" viewBox="0 0 {width} {total_h}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="noteGrad" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0%" stop-color="#45f3ff" stop-opacity="0.92"/>
          <stop offset="100%" stop-color="#ff4fd8" stop-opacity="0.86"/>
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="2.8" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
    """)

    y_cursor = top_h
    for track_index, (track_name, chords, kind) in enumerate(tracks):
        track_seed = seed_int + track_index * 100000 + sum(ord(c) for c in track_name)
        max_steps = max(1, len(chords))
        grid_w = max_steps * step_w

        svg.append(f"<text x='0' y='{y_cursor - 12}' fill='#45f3ff' font-size='16' font-weight='900'>{track_name}</text>")

        # Piano roll background and horizontal note lanes
        for idx, note in enumerate(note_rows):
            y = y_cursor + idx * row_h
            is_black = note_name(note) in {"C#", "D#", "F#", "G#", "A#"}
            bg = "rgba(69,243,255,0.105)" if is_black else "rgba(255,255,255,0.035)"
            svg.append(f"<rect x='{label_w}' y='{y}' width='{grid_w}' height='{row_h}' fill='{bg}'/>")
            if note % 12 == 0 or idx == 0 or idx == len(note_rows) - 1:
                label = f"{note_name(note)}{(note // 12) - 1}"
                svg.append(f"<text x='4' y='{y + 13}' fill='#e7f2ff' font-size='15' font-weight='900'>{label}</text>")
            svg.append(f"<line x1='{label_w}' y1='{y}' x2='{label_w + grid_w}' y2='{y}' stroke='rgba(255,255,255,0.080)' stroke-width='1'/>")

        # Vertical time grid
        for step in range(max_steps + 1):
            x = label_w + step * step_w
            stroke = "rgba(69,243,255,0.34)" if step % 4 == 0 else "rgba(255,255,255,0.09)"
            svg.append(f"<line x1='{x}' y1='{y_cursor}' x2='{x}' y2='{y_cursor + roll_h}' stroke='{stroke}' stroke-width='1'/>")
            if step < max_steps:
                svg.append(f"<text x='{x + 5}' y='{y_cursor - 5}' fill='#dbeafe' font-size='12' font-weight='900'>Step {step + 1}</text>")

        # MIDI notes
        for step, chord in enumerate(chords):
            step_x = label_w + step * step_w
            chord_rng = random.Random(track_seed + step * 991)
            length_push = 1.0
            if length_random > 0:
                length_push = chord_rng.uniform(max(0.20, 1.0 - length_random), 1.0 + length_random)

            for note_index, note in enumerate(chord):
                if note < min_note or note > max_note:
                    continue
                note_rng = random.Random(track_seed + step * 1009 + note * 17 + note_index * 131)

                timing_offset_px = 0
                if humanize_timing > 0:
                    timing_offset_px = note_rng.randint(-humanize_timing, humanize_timing) / 80 * 18

                strum_px = (note_index * strum_amount) / 80 * 24
                x = step_x + 6 + timing_offset_px + strum_px
                base_note_w = step_w - 18
                note_length_push = length_push
                if length_random > 0:
                    note_length_push *= note_rng.uniform(max(0.30, 1.0 - (length_random * 0.55)), 1.0 + (length_random * 0.55))
                note_w = max(10, min(step_w - 8, base_note_w * note_length_push - max(0, timing_offset_px) - strum_px))

                y = y_for_note(note, y_cursor) + 3
                h = row_h - 6
                velocity_seed = (step + 1) * 1009 + note * 17 + len(chord) * 31
                visual_velocity = int(base_velocity)
                if velocity_random > 0:
                    visual_velocity = max(1, min(127, visual_velocity + note_rng.randint(-velocity_random, velocity_random)))
                vel_opacity = 0.38 + (visual_velocity / 127) * 0.58
                vel_bar_w = max(5, int(note_w * (visual_velocity / 127)))
                label = f"{note_name(note)}{(note // 12) - 1}"
                length_pct = int((note_w / max(1, step_w - 18)) * 100)
                tail_w = max(6, note_w)

                # Orange tail = visible note length variation.
                svg.append(f"<line x1='{x}' y1='{y + 2}' x2='{x + tail_w}' y2='{y + 2}' stroke='#ffb020' stroke-width='4.5' opacity='0.98' stroke-linecap='butt'/>")

                # Lime vertical line = exact note start / strum / timing drift.
                svg.append(f"<line x1='{x}' y1='{y - 4}' x2='{x}' y2='{y + h + 4}' stroke='#c7ff4f' stroke-width='1.8' opacity='0.98'/>")

                # Thin cyan duration line = note length. Kept thin so it does not become a capsule.
                svg.append(f"<line x1='{x}' y1='{y + 5}' x2='{x + note_w}' y2='{y + 5}' stroke='#45f3ff' stroke-width='3.2' opacity='0.98' stroke-linecap='butt'/>")

                # Lime underline = velocity strength.
                svg.append(f"<line x1='{x}' y1='{y + h - 1}' x2='{x + vel_bar_w}' y2='{y + h - 1}' stroke='#c7ff4f' stroke-width='3.2' opacity='0.98' stroke-linecap='butt'/>")

                # Bright readable MIDI note label, slightly larger than the duration line.
                svg.append(f"<text x='{x + 3}' y='{y + 11}' fill='#ffffff' font-size='15' font-weight='900'>{label}</text>")

                # Small length marker when there is room.
                if note_w > 54:
                    svg.append(f"<text x='{x + note_w - 28}' y='{y + 10}' fill='#dffcff' font-size='8.5' font-weight='900'>{length_pct}%</text>")

        # Automation lane background
        auto_y = y_cursor + roll_h + 22
        svg.append(f"<text x='0' y='{auto_y - 8}' fill='#ff4fd8' font-size='11' font-weight='900'>Automation</text>")
        svg.append(f"<rect x='{label_w}' y='{auto_y}' width='{grid_w}' height='{automation_h - 28}' rx='10' fill='rgba(255,255,255,0.035)' stroke='rgba(255,79,216,0.28)'/>")

        # Automation curves: filter brightness and bloom/spread
        points_filter = []
        points_bloom = []
        for step in range(max_steps):
            x = label_w + step * step_w + step_w / 2
            # filter opens early for Tin Man, otherwise gently waves
            if kind == "voicy":
                val = 0.25 + min(0.65, step / max(1, max_steps - 1) * 0.65)
            elif kind == "fog":
                val = 0.36 + 0.10 * ((step % 4) / 3)
            else:
                val = 0.42 + 0.22 * (0.5 + 0.5 * random.Random(step + len(chords)).random())
            y = auto_y + (automation_h - 34) * (1 - val)
            points_filter.append(f"{x},{y}")

            spread = min(0.92, max(0.18, pitch_range_percent(chords[step]) / 100))
            y2 = auto_y + (automation_h - 34) * (1 - spread)
            points_bloom.append(f"{x},{y2}")

        if len(points_filter) > 1:
            svg.append(f"<polyline points='{' '.join(points_filter)}' fill='none' stroke='#45f3ff' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/>")
            svg.append(f"<polyline points='{' '.join(points_bloom)}' fill='none' stroke='#ff4fd8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' opacity='0.78'/>")
        for pt in points_filter:
            x, y = pt.split(',')
            svg.append(f"<circle cx='{x}' cy='{y}' r='3.2' fill='#45f3ff'/>")

        svg.append(f"<text x='{label_w}' y='{auto_y + automation_h - 8}' fill='#45f3ff' font-size='10' font-weight='800'>cyan = filter brightness</text>")
        svg.append(f"<text x='{label_w + 170}' y='{auto_y + automation_h - 8}' fill='#ff4fd8' font-size='10' font-weight='800'>pink = spread / bloom</text>")
        svg.append(f"<text x='{label_w + 330}' y='{auto_y + automation_h - 8}' fill='#c7ff4f' font-size='10' font-weight='800'>cyan = length · orange = length · lime = start / velocity</text>")

        y_cursor += roll_h + automation_h + track_gap

    svg.append("</svg></div>")
    st.markdown("".join(svg), unsafe_allow_html=True)


def render_pad_visualizer(title, tracks):
    st.markdown("## 🌌 Pad Visualizer")
    st.markdown(f"**{title}**")

    for track_name, chords, kind in tracks:
        st.markdown(f"### {'🟦' if kind == 'normal' else '🟪' if kind == 'voicy' else '🟩'} {track_name}")

        if not chords:
            st.warning("No chords generated yet.")
            continue

        cols_per_row = 4
        for row_start in range(0, len(chords), cols_per_row):
            row_chords = chords[row_start:row_start + cols_per_row]
            cols = st.columns(len(row_chords))
            for offset, chord in enumerate(row_chords):
                i = row_start + offset + 1
                short = chord_short_name(chord)
                names = chord_to_names(chord)
                width = pitch_range_percent(chord)
                low_note = f"{note_name(min(chord))}{(min(chord) // 12) - 1}"
                high_note = f"{note_name(max(chord))}{(max(chord) // 12) - 1}"

                with cols[offset]:
                    st.markdown(
                        f"""
                        <div style="
                            border:1px solid rgba(69,243,255,0.55);
                            background:linear-gradient(135deg, rgba(5,16,32,0.98), rgba(18,42,74,0.92));
                            border-radius:18px;
                            padding:14px;
                            min-height:154px;
                            box-shadow:0 0 22px rgba(69,243,255,0.10);
                        ">
                            <div style="color:#45f3ff !important; font-weight:900; font-size:0.78rem; letter-spacing:0.12em;">STEP {i:02d}</div>
                            <div style="color:#ffffff !important; font-weight:900; font-size:1.25rem; margin-top:6px;">{short}</div>
                            <div style="color:#dbeafe !important; font-weight:700; font-size:0.78rem; margin-top:8px; line-height:1.25;">{names}</div>
                            <div style="margin-top:12px; height:10px; width:100%; background:rgba(255,255,255,0.16); border-radius:999px; overflow:hidden;">
                                <div style="height:10px; width:{width}%; background:linear-gradient(90deg,#45f3ff,#ff4fd8); border-radius:999px;"></div>
                            </div>
                            <div style="color:#c5d4ef !important; font-weight:800; font-size:0.72rem; margin-top:8px;">Range: {low_note} → {high_note}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        cloud = note_cloud(chords)
        if cloud:
            st.markdown("**Note cloud**")
            st.markdown(
                " ".join(
                    f"<span style='display:inline-block; margin:3px; padding:5px 10px; border-radius:999px; background:rgba(255,255,255,0.10); border:1px solid rgba(69,243,255,0.35); color:#ffffff !important; font-weight:800;'>{n}</span>"
                    for n in cloud
                ),
                unsafe_allow_html=True,
            )

    st.divider()

def build_scale(root, mode, octave):
    base = NOTE_MAP[root] + ((octave + 1) * 12)
    return [base + i for i in MODES[mode]]

def build_chord(scale, degree, add7=True, add9=True, sus2=False, omit5=False):
    expanded = []
    for octave_shift in range(4):
        expanded.extend([n + (12 * octave_shift) for n in scale])

    degree = degree % len(scale)
    chord = [expanded[degree], expanded[degree + 2], expanded[degree + 4], expanded[degree + 6]]
    root = chord[0]

    if sus2 and len(chord) > 1:
        chord[1] = root + 2
    if omit5 and len(chord) > 2:
        del chord[2]
    if add7:
        chord.append(root + 10)
    if add9:
        chord.append(root + 14)

    return normalize_chord(chord)

def apply_voicing(chord, voicing):
    chord = normalize_chord(chord)

    if voicing == "open":
        return normalize_chord([n + (12 if i % 2 else 0) for i, n in enumerate(chord)])
    if voicing == "wide":
        return normalize_chord([n + (12 if i > 0 else 0) + (12 if i > 2 else 0) for i, n in enumerate(chord)])
    if voicing == "high":
        return normalize_chord([n + 12 for n in chord])
    if voicing == "low_cluster":
        return normalize_chord([n - 12 if i > 1 else n for i, n in enumerate(chord)])

    return chord

def generate_normal_chords(root, mode, octave, preset, blocks, flow, voicing, add7, add9, sus2, omit5):
    scale = build_scale(root, mode, octave)
    patterns = PROGRESSIONS[preset]

    if flow == "single":
        selected = [random.choice(patterns)] * blocks
    elif flow == "sequence":
        start = random.randint(0, len(patterns) - 1)
        selected = [patterns[(start + i) % len(patterns)] for i in range(blocks)]
    else:
        selected = [random.choice(patterns) for _ in range(blocks)]

    chords = []
    for pattern in selected:
        for degree in pattern:
            chord = build_chord(scale, degree, add7, add9, sus2, omit5)
            chords.append(clamp_chord_range(apply_voicing(chord, voicing), 36, 96))

    return chords

def make_tin_man_fog_chords(root_name, octave, blocks):
    root = NOTE_MAP[root_name] + ((octave + 1) * 12)

    chord_a = normalize_chord([root, root + 3, root + 7, root + 10, root + 14])

    chord_b_options = [
        normalize_chord([root - 2, root + 2, root + 5, root + 9, root + 12]),
        normalize_chord([root - 4, root, root + 3, root + 7, root + 10]),
        normalize_chord([root - 5, root - 1, root + 2, root + 5, root + 9]),
    ]

    chord_b = random.choice(chord_b_options)
    chords = []

    for i in range(max(1, blocks) * 4):
        chord = chord_a if i % 2 == 0 else chord_b

        if i % 4 == 3 and random.random() > 0.5:
            chord = normalize_chord(chord[:-1] + [chord[-1] + random.choice([-2, 1, 2])])

        chords.append(clamp_chord_range(chord, 36, 84))

    return chords

def make_tin_man_voicy_chords(fog_chords):
    voicy = []

    for i, chord in enumerate(fog_chords):
        mid = [n for n in chord if 48 <= n <= 84] or chord[:]
        lifted = [n + 12 if n < 60 else n for n in sorted(mid)[-4:]]

        if i % 4 == 1 and lifted:
            lifted[-1] += 2
        elif i % 4 == 2 and len(lifted) >= 2:
            lifted[-2] -= 1
        elif i % 4 == 3 and lifted:
            lifted[-1] -= 2

        if random.random() > 0.55 and lifted:
            lifted.append(lifted[-1] + random.choice([5, 7]))

        voicy.append(clamp_chord_range(normalize_chord(lifted), 55, 96))

    return voicy

def add_chord_sequence_to_track(
    track,
    chord_sequence,
    base_ticks,
    velocity,
    overlap,
    stagger_ticks=0,
    bloom=False,
    humanize_timing=0,
    velocity_random=0,
    length_random=0.0,
    strum_amount=0,
):
    note_pairs = []

    for chord_index, chord in enumerate(chord_sequence):
        chord_start = chord_index * base_ticks
        chord_len_multiplier = 1.0
        if length_random > 0:
            chord_len_multiplier = random.uniform(max(0.20, 1.0 - length_random), 1.0 + length_random)

        for note_index, note in enumerate(chord):
            timing_offset = random.randint(-humanize_timing, humanize_timing) if humanize_timing > 0 else 0
            strum_offset = note_index * strum_amount
            start = max(0, chord_start + strum_offset + timing_offset)
            note_len_multiplier = chord_len_multiplier
            if length_random > 0:
                note_len_multiplier *= random.uniform(max(0.30, 1.0 - (length_random * 0.55)), 1.0 + (length_random * 0.55))
            duration = int(base_ticks * overlap * note_len_multiplier)

            if bloom:
                duration = int(duration * random.uniform(0.72, 1.28))
                start += random.randint(0, max(1, int(base_ticks * 0.05)))

            vel = int(velocity)
            if velocity_random > 0:
                vel = max(1, min(127, vel + random.randint(-velocity_random, velocity_random)))

            note_pairs.append((start, "on", note, vel))
            note_pairs.append((start + max(60, duration), "off", note, 0))

    note_pairs.sort(key=lambda x: (x[0], 0 if x[1] == "off" else 1))

    previous_time = 0
    for event_time, event_type, note, vel in note_pairs:
        delta = max(0, event_time - previous_time)

        if event_type == "on":
            track.append(Message("note_on", note=note, velocity=vel, time=delta))
        else:
            track.append(Message("note_off", note=note, velocity=0, time=delta))

        previous_time = event_time

def make_tin_man_midi(root, octave, blocks, tempo, length, velocity, humanize_timing=0, velocity_random=0, length_random=0.0, strum_amount=0):
    mid = MidiFile()

    fog_track = MidiTrack()
    voicy_track = MidiTrack()

    mid.tracks.append(fog_track)
    mid.tracks.append(voicy_track)

    fog_track.append(MetaMessage("track_name", name="Tin Man Fog Pad - two chord bed", time=0))
    voicy_track.append(MetaMessage("track_name", name="Tin Man Voicy Bloom Pad - opening layer", time=0))

    fog_track.append(MetaMessage("set_tempo", tempo=bpm2tempo(int(tempo)), time=0))
    voicy_track.append(MetaMessage("set_tempo", tempo=bpm2tempo(int(tempo)), time=0))

    ticks = 480
    base = int(ticks * 4 * float(length))

    fog_chords = make_tin_man_fog_chords(root, octave, blocks)
    voicy_chords = make_tin_man_voicy_chords(fog_chords)

    add_chord_sequence_to_track(
        fog_track,
        fog_chords,
        base,
        max(45, int(velocity * 0.78)),
        1.18,
        stagger_ticks=8,
        bloom=False,
        humanize_timing=humanize_timing,
        velocity_random=velocity_random,
        length_random=length_random,
        strum_amount=strum_amount,
    )

    add_chord_sequence_to_track(
        voicy_track,
        voicy_chords,
        base,
        max(38, int(velocity * 0.62)),
        1.45,
        stagger_ticks=18,
        bloom=True,
        humanize_timing=humanize_timing,
        velocity_random=velocity_random,
        length_random=length_random,
        strum_amount=strum_amount,
    )

    buffer = io.BytesIO()
    mid.save(file=buffer)
    buffer.seek(0)

    return buffer.getvalue(), fog_chords, voicy_chords

def make_normal_midi(chords, tempo, length, velocity, humanize_timing=0, velocity_random=0, length_random=0.0, strum_amount=0):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage("track_name", name="Generated Pad Chords", time=0))
    track.append(MetaMessage("set_tempo", tempo=bpm2tempo(int(tempo)), time=0))

    ticks = 480
    base = int(ticks * 4 * float(length))

    add_chord_sequence_to_track(
        track,
        chords,
        base,
        int(velocity),
        1.0,
        stagger_ticks=0,
        bloom=False,
        humanize_timing=humanize_timing,
        velocity_random=velocity_random,
        length_random=length_random,
        strum_amount=strum_amount,
    )

    buffer = io.BytesIO()
    mid.save(file=buffer)
    buffer.seek(0)

    return buffer.getvalue()

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">🎹 MIDI Pad Generator</div>
        <div class="hero-subtitle">
        Generate expressive MIDI pad progressions, cinematic chords, dub-techno atmospheres,
        humanized voicings, random lengths, random velocities, and Ableton-ready MIDI exports.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Controls")

    if st.button("🎲 Randomize all settings", use_container_width=True):
        random_preset = random.choice(list(PROGRESSIONS.keys()))
        random_defaults = STYLE_DEFAULTS.get(random_preset, {})
        st.session_state["preset"] = random_preset
        st.session_state["root"] = random_defaults.get("root", random.choice(NOTE_NAMES))
        st.session_state["mode"] = random_defaults.get("mode", random.choice(list(MODES.keys())))
        st.session_state["octave"] = random.choice([1, 2, 3, 4])
        st.session_state["tempo"] = random_defaults.get("tempo", random.randint(72, 138))
        st.session_state["length"] = random_defaults.get("length", random.choice([1, 2, 4, 8]))
        st.session_state["blocks"] = random_defaults.get("blocks", random.choice([2, 3, 4, 5, 6, 8]))
        st.session_state["flow"] = random.choice(["single", "sequence", "random"])
        st.session_state["voicing"] = random_defaults.get("voicing", random.choice(["close", "open", "wide", "high", "low_cluster"]))
        st.session_state["velocity"] = random_defaults.get("velocity", random.randint(54, 108))
        st.session_state["add7"] = random.choice([True, True, False])
        st.session_state["add9"] = random.choice([True, True, False])
        st.session_state["sus2"] = random_defaults.get("sus2", random.choice([True, False]))
        st.session_state["omit5"] = random.choice([False, False, True])
        st.session_state["humanize_enabled"] = random.choice([True, True, False])
        st.session_state["random_velocities"] = True
        st.session_state["random_lengths"] = True
        st.session_state["strum_enabled"] = random.choice([True, True, False])
        st.session_state["humanize_timing"] = random.randint(0, 48)
        st.session_state["velocity_random"] = random.randint(8, 48)
        st.session_state["length_random"] = round(random.uniform(0.15, 1.20), 2)
        st.session_state["strum_amount"] = random.randint(0, 42)
        st.session_state["last_seed"] = datetime.now().timestamp()

    preset_options = list(PROGRESSIONS.keys())
    default_preset = st.session_state.get("preset", "ambient")

    preset = st.selectbox(
        "Progression preset",
        preset_options,
        index=preset_options.index(default_preset),
        key="preset",
    )

    defaults = STYLE_DEFAULTS.get(preset, {})
    default_root = defaults.get("root", "A" if preset == "tin_man_constant_confusion" else "C")
    default_mode = defaults.get("mode", "aeolian")
    default_tempo = defaults.get("tempo", 121 if preset == "tin_man_constant_confusion" else 120)
    default_length = defaults.get("length", 2)
    default_blocks = defaults.get("blocks", 4)
    default_voicing = defaults.get("voicing", "open")
    default_velocity = defaults.get("velocity", 72 if preset == "tin_man_constant_confusion" else 84)
    default_sus2 = defaults.get("sus2", preset == "tin_man_constant_confusion")

    root = st.selectbox(
        "Root",
        NOTE_NAMES,
        index=NOTE_NAMES.index(default_root) if default_root in NOTE_NAMES else 0,
        key="root",
    )

    mode_names = list(MODES.keys())
    mode = st.selectbox(
        "Mode",
        mode_names,
        index=mode_names.index(default_mode) if default_mode in mode_names else mode_names.index("aeolian"),
        key="mode",
    )

    octave = st.selectbox("Octave", [1, 2, 3, 4, 5], index=2, key="octave")
    tempo = st.slider("Tempo", 60, 180, int(default_tempo), key="tempo")
    length_options = [1, 2, 4, 8, 16]
    length = st.selectbox("Chord length", length_options, index=length_options.index(default_length) if default_length in length_options else 1, key="length")
    block_options = [1, 2, 3, 4, 5, 6, 8, 12, 16]
    blocks = st.selectbox("Progression blocks", block_options, index=block_options.index(default_blocks) if default_blocks in block_options else 3, key="blocks")
    flow = st.selectbox("Flow", ["single", "sequence", "random"], index=0, key="flow")
    voicing_options = ["close", "open", "wide", "high", "low_cluster"]
    voicing = st.selectbox("Voicing", voicing_options, index=voicing_options.index(default_voicing) if default_voicing in voicing_options else 1, key="voicing")
    velocity = st.slider("Velocity", 40, 127, int(default_velocity), key="velocity")

    st.divider()

    add7 = st.checkbox("Add 7th", value=True, key="add7")
    add9 = st.checkbox("Add 9th", value=True, key="add9")
    sus2 = st.checkbox("Sus2 color", value=bool(default_sus2), key="sus2")
    omit5 = st.checkbox("Hollow / omit 5th", value=False, key="omit5")

    st.divider()
    st.subheader("Humanize")
    humanize_enabled = st.checkbox("Human feel", value=True, key="humanize_enabled")
    random_velocities = st.checkbox("Random velocities", value=True, key="random_velocities")
    random_lengths = st.checkbox("Random lengths", value=True, key="random_lengths")
    strum_enabled = st.checkbox("Soft chord strum", value=True, key="strum_enabled")

    if humanize_enabled:
        humanize_timing = st.slider("Timing drift", 0, 80, 16, help="Tiny note timing movement in MIDI ticks.", key="humanize_timing")
    else:
        humanize_timing = 0

    if random_velocities:
        velocity_random = st.slider(
            "Random velocity amount",
            0,
            60,
            24,
            help="Bigger values create clearly different MIDI velocities per note.",
            key="velocity_random",
        )
    else:
        velocity_random = 0

    if random_lengths:
        length_random = st.slider(
            "Random length amount",
            0.0,
            1.50,
            0.65,
            0.05,
            help="Bigger values create clearly shorter/longer MIDI notes per chord/note.",
            key="length_random",
        )
    else:
        length_random = 0.0

    if strum_enabled:
        strum_amount = st.slider("Strum / spread", 0, 80, 12, help="Spreads notes in each chord by a tiny amount.", key="strum_amount")
    else:
        strum_amount = 0

st.markdown(
    f"""
    <div class="mini-card">
        <div class="mini-title">Selected Mode</div>
        <div class="mini-value">{preset}</div>
        <p style="color:#dbeafe !important; margin-top:8px; font-weight:700;">{PRESET_DESCRIPTIONS.get(preset, "")}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"<div class='mini-card'><div class='mini-title'>Root / Mode</div><div class='mini-value'>{root} {mode}</div></div>",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"<div class='mini-card'><div class='mini-title'>Tempo</div><div class='mini-value'>{tempo} BPM</div></div>",
        unsafe_allow_html=True,
    )

with col3:
    export_type = "2 MIDI tracks" if preset == "tin_man_constant_confusion" else "1 MIDI track"
    st.markdown(
        f"<div class='mini-card'><div class='mini-title'>Export</div><div class='mini-value'>{export_type}</div></div>",
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <div class="mini-card" style="margin-top:14px;">
        <div class="mini-title">Humanize Engine</div>
        <div class="mini-value">{'ON' if humanize_enabled or random_velocities or random_lengths or strum_enabled else 'OFF'}</div>
        <p style="color:#dbeafe !important; margin-top:8px; font-weight:700;">
        Timing ±{humanize_timing} ticks · Velocity ±{velocity_random} · Length ±{int(length_random * 100)}% · Strum {strum_amount} ticks
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

st.divider()
st.info("Use 🎲 Randomize all settings for a full surprise patch, or tweak controls manually. Click Generate New Variation to redraw the MIDI with the current settings.")

if st.button("▶ Generate New Variation — update piano roll", use_container_width=True):
    seed = datetime.now().timestamp()
    random.seed(seed)
    st.session_state["last_seed"] = seed
else:
    if "last_seed" not in st.session_state:
        st.session_state["last_seed"] = 777
    random.seed(st.session_state["last_seed"])

if preset == "tin_man_constant_confusion":
    midi_bytes, fog_chords, voicy_chords = make_tin_man_midi(
        root,
        octave,
        int(blocks),
        int(tempo),
        float(length),
        int(velocity),
        humanize_timing=humanize_timing,
        velocity_random=velocity_random,
        length_random=length_random,
        strum_amount=strum_amount,
    )

    filename = f"{root}_{mode}_two_layer_fog_pad_{blocks}blocks_{length}L_{tempo}BPM.mid"

    render_pad_visualizer(
        "Pad Visualizer — Two-Layer Fog Pad",
        [
            ("Fog Pad / two-chord bed", fog_chords, "fog"),
            ("Voicy Bloom Pad / opening layer", voicy_chords, "voicy"),
        ],
    )

    with st.expander("🎹 Detailed piano roll / automation view", expanded=False):
        render_piano_roll(
            "Piano Roll + Automation — Two-Layer Fog Pad",
            [
                ("Fog Pad / two-chord bed", fog_chords, "fog"),
                ("Voicy Bloom Pad / opening layer", voicy_chords, "voicy"),
            ],
            length_beats=float(length) * 4,
            base_velocity=int(velocity),
            velocity_random=velocity_random,
            humanize_timing=humanize_timing,
            length_random=length_random,
            strum_amount=strum_amount,
            visual_seed=st.session_state.get("last_seed", 777),
        )

    render_performance_view(
        "Performance View — Two-Layer Fog Pad",
        [
            ("Fog Pad / two-chord bed", fog_chords, "fog"),
            ("Voicy Bloom Pad / opening layer", voicy_chords, "voicy"),
        ],
        base_velocity=int(velocity),
        velocity_random=velocity_random,
        humanize_timing=humanize_timing,
        length_random=length_random,
        strum_amount=strum_amount,
        visual_seed=st.session_state.get("last_seed", 777),
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Pad 1: Fog Pad / two-chord bed")
        for i, chord in enumerate(fog_chords, start=1):
            st.markdown(
                f"<div class='chord-box'>{i:02d}. {chord_to_names(chord)}</div>",
                unsafe_allow_html=True,
            )

    with right:
        st.subheader("Pad 2: Voicy Bloom Pad / opening layer")
        for i, chord in enumerate(voicy_chords, start=1):
            st.markdown(
                f"<div class='chord-box'>{i:02d}. {chord_to_names(chord)}</div>",
                unsafe_allow_html=True,
            )

    st.download_button(
        "⇩ Download Two-Layer Pad MIDI",
        data=midi_bytes,
        file_name=filename,
        mime="audio/midi",
        use_container_width=True,
    )

    st.success(
        f"Randomization applied: timing ±{humanize_timing} ticks, random velocity ±{velocity_random}, random length {int(length_random * 100)}%, strum {strum_amount} ticks."
    )

    st.info(
        "Ableton idea: Track 1 gets a deep filtered pad. Track 2 gets a brighter animated layer with Auto Filter opening quickly and settling back down."
    )

else:
    chords = generate_normal_chords(
        root,
        mode,
        octave,
        preset,
        int(blocks),
        flow,
        voicing,
        add7,
        add9,
        sus2,
        omit5,
    )

    midi_bytes = make_normal_midi(
        chords,
        tempo,
        length,
        velocity,
        humanize_timing=humanize_timing,
        velocity_random=velocity_random,
        length_random=length_random,
        strum_amount=strum_amount,
    )
    filename = f"{root}_{mode}_{preset}_{flow}_{voicing}_{blocks}blocks_{length}L_{tempo}BPM.mid"

    render_pad_visualizer(
        "Pad Visualizer — Generated Progression",
        [("Generated Pad Chords", chords, "normal")],
    )

    with st.expander("🎹 Detailed piano roll / automation view", expanded=False):
        render_piano_roll(
            "Piano Roll + Automation — Generated Progression",
            [("Generated Pad Chords", chords, "normal")],
            length_beats=float(length) * 4,
            base_velocity=int(velocity),
            velocity_random=velocity_random,
            humanize_timing=humanize_timing,
            length_random=length_random,
            strum_amount=strum_amount,
            visual_seed=st.session_state.get("last_seed", 777),
        )

    render_performance_view(
        "Performance View — Generated Progression",
        [("Generated Pad Chords", chords, "normal")],
        base_velocity=int(velocity),
        velocity_random=velocity_random,
        humanize_timing=humanize_timing,
        length_random=length_random,
        strum_amount=strum_amount,
        visual_seed=st.session_state.get("last_seed", 777),
    )

    st.subheader("Generated Chords")

    for i, chord in enumerate(chords, start=1):
        st.markdown(
            f"<div class='chord-box'>{i:02d}. {chord_to_names(chord)}</div>",
            unsafe_allow_html=True,
        )

    st.download_button(
        "⇩ Download MIDI",
        data=midi_bytes,
        file_name=filename,
        mime="audio/midi",
        use_container_width=True,
    )

    st.success(
        f"Randomization applied: timing ±{humanize_timing} ticks, random velocity ±{velocity_random}, random length {int(length_random * 100)}%, strum {strum_amount} ticks."
    )

    if preset == "david_alvarado_mayasongs":
        st.info("Ableton idea: use a warm analog or house-style pad, chorus/ensemble, long plate reverb, gentle delay, and slow filter movement. Keep it smoky, spiritual, and rolling.")
    elif preset in {"donato_dozzy", "cio_dor", "vril", "gas", "ross_154"}:
        st.info("Ableton idea: use a dark filtered pad, long reverb, subtle chorus, and slow Auto Filter movement. Keep the chord changes restrained and hypnotic.")
    elif preset.startswith("soundtrack_"):
        st.info("Ableton idea: use a soft pad or string-like synth, long release, slow filter opening, and heavy atmospheric reverb. Let the chords breathe like a film scene.")
    elif preset.startswith("underworld"):
        st.info("Ableton idea: layer a warm wide pad with a pulsing rhythmic synth. Automate filter brightness over 16–32 bars for emotional lift.")

st.caption("MIDI Pad Generator · Safe Streamlit web version · No Tkinter or native Mac window dependencies.")
