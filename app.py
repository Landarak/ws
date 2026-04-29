import warnings
warnings.filterwarnings("ignore")

import hashlib
import html
from typing import Any
import pandas as pd
import streamlit as st

from engine import TacticalCompatibilityEngine

st.set_page_config(
    page_title="ScoutFit | Compatibilidad táctica",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
:root{--navy:#12325d;--muted:#61708a;--teal:#13b5b1;--teal-dark:#078b8b;--border:rgba(18,50,93,.14);--shadow:0 10px 24px rgba(18,50,93,.07)}
.stApp{background:radial-gradient(circle at 0% 12%,rgba(19,181,177,.12) 0,rgba(19,181,177,0) 25%),linear-gradient(180deg,#fff 0%,#f7fbff 55%,#fff 100%)}
.main .block-container{max-width:1540px;padding:.55rem 1.1rem .35rem 1.1rem}
[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none}.main .block-container [data-testid="stVerticalBlock"]{gap:.42rem}h1,h2,h3,h4,h5,h6,p,label,span,div{color:var(--navy)}
.sf-header{display:flex;align-items:center;gap:.8rem;margin-bottom:.35rem}.sf-logo{width:52px;height:52px;border-radius:16px;display:grid;place-items:center;background:linear-gradient(135deg,rgba(19,181,177,.16),rgba(18,50,93,.07));border:1px solid rgba(19,181,177,.32);box-shadow:0 10px 22px rgba(19,181,177,.14);font-size:1.55rem}.sf-title{margin:0;line-height:1.02;font-size:clamp(1.85rem,2.15vw,2.35rem);font-weight:950;letter-spacing:-.045em}.sf-subtitle{margin-top:.08rem;color:var(--muted);font-size:.94rem;font-weight:520}
.sf-panel-head{display:flex;align-items:flex-start;gap:.55rem;margin-bottom:.48rem}.sf-panel-icon{width:32px;height:32px;min-width:32px;border-radius:10px;display:grid;place-items:center;background:rgba(19,181,177,.11);border:1px solid rgba(19,181,177,.27);color:var(--teal-dark);font-weight:900}.sf-panel-title{font-size:1.02rem;line-height:1.12;font-weight:900;color:var(--navy)}.sf-panel-subtitle{margin-top:.12rem;color:var(--muted);font-size:.80rem;line-height:1.30}.search-note{margin-top:.34rem;border-radius:12px;padding:.46rem .56rem;border:1px solid rgba(19,181,177,.25);background:rgba(19,181,177,.08);color:#075c64;font-weight:800;font-size:.78rem}
.stSelectbox label,.stNumberInput label,.stCheckbox label{font-size:.86rem!important}.stSelectbox,.stNumberInput,.stCheckbox{margin-bottom:.08rem}div[data-testid="stButton"]>button{min-height:40px!important;border-radius:13px!important;font-weight:850!important}div[data-testid="stButton"]>button[kind="primary"]{background:linear-gradient(135deg,#15b8b1,#0ca4be)!important;border:0!important;color:#fff!important;box-shadow:0 10px 20px rgba(19,181,177,.20)!important}.stDownloadButton button{border-radius:12px!important;border-color:rgba(19,181,177,.42)!important;color:var(--teal-dark)!important;font-weight:850!important;min-height:36px!important}
.pitch-wrap{padding:.05rem 0 0 0}.pitch-field{position:relative;width:100%;height:172px;overflow:hidden;border-radius:13px;border:3px solid rgba(255,255,255,.96);background:linear-gradient(90deg,transparent 49.72%,rgba(255,255,255,.86) 49.92%,rgba(255,255,255,.86) 50.08%,transparent 50.28%),radial-gradient(circle at 50% 50%,transparent 0 39px,rgba(255,255,255,.78) 40px 42px,transparent 43px),repeating-linear-gradient(90deg,rgba(76,150,49,.96) 0px,rgba(76,150,49,.96) 68px,rgba(52,116,36,.96) 68px,rgba(52,116,36,.96) 136px),linear-gradient(180deg,rgba(255,255,255,.06),rgba(0,0,0,.08));box-shadow:inset 0 0 28px rgba(0,0,0,.12),0 8px 18px rgba(18,50,93,.10)}.pitch-field:before,.pitch-field:after{content:"";position:absolute;top:22%;width:14%;height:56%;border:2px solid rgba(255,255,255,.78);z-index:1;pointer-events:none}.pitch-field:before{left:-2px;border-left:0}.pitch-field:after{right:-2px;border-right:0}.six-left,.six-right{position:absolute;top:36%;width:6%;height:28%;border:2px solid rgba(255,255,255,.76);z-index:2;pointer-events:none}.six-left{left:-2px;border-left:0}.six-right{right:-2px;border-right:0}.pitch-dot{position:absolute;width:6px;height:6px;border-radius:999px;background:rgba(255,255,255,.80);transform:translate(-50%,-50%);z-index:2}.dot-left{left:15%;top:50%}.dot-center{left:50%;top:50%}.dot-right{left:85%;top:50%}.pos-chip{position:absolute;z-index:5;transform:translate(-50%,-50%);min-width:49px;height:31px;padding:0 .58rem;border-radius:8px;border:1px solid rgba(18,50,93,.16);background:rgba(255,255,255,.96);color:var(--navy)!important;display:inline-flex;align-items:center;justify-content:center;white-space:nowrap;line-height:1;font-size:.77rem;font-weight:950;text-decoration:none!important;box-shadow:0 6px 13px rgba(18,50,93,.15);transition:all .15s ease}.pos-chip:hover{transform:translate(-50%,-50%) translateY(-1px);border-color:rgba(19,181,177,.64);box-shadow:0 0 0 3px rgba(19,181,177,.14),0 7px 16px rgba(18,50,93,.18);color:var(--teal-dark)!important}.pos-chip.selected{background:linear-gradient(135deg,#13b5b1,#0aa8c9);border-color:rgba(255,255,255,.95);color:#fff!important;box-shadow:0 0 0 4px rgba(19,181,177,.26),0 0 16px rgba(19,181,177,.62)}.pitch-note{text-align:center;margin-top:.38rem;color:var(--muted);font-size:.80rem}.pitch-note b{color:var(--teal-dark)}
.result-banner{display:flex;align-items:center;gap:.8rem;border-radius:16px;border:1px solid rgba(19,181,177,.26);background:linear-gradient(135deg,rgba(219,247,252,.88),rgba(244,252,255,.94));box-shadow:0 8px 20px rgba(19,181,177,.07);padding:.58rem .75rem;margin:.48rem 0 .38rem 0}.target-icon{width:42px;height:42px;min-width:42px;border-radius:999px;display:grid;place-items:center;background:rgba(19,181,177,.13);border:1px solid rgba(19,181,177,.32);color:var(--teal-dark);font-size:1.15rem;font-weight:950}.result-title{font-weight:950;font-size:1.18rem;color:var(--navy);letter-spacing:-.02em}.result-text{margin:.12rem 0 0 0;color:var(--muted);font-size:.88rem}.result-text b{color:var(--teal-dark)}
.candidate-card,.score-card,.stat-card,.metric-strip-card{border-radius:16px;border:1px solid var(--border);background:rgba(255,255,255,.94);box-shadow:0 8px 20px rgba(18,50,93,.05)}.candidate-card{padding:.65rem .75rem;min-height:104px}.candidate-card-flex{display:flex;align-items:center;gap:.75rem}.avatar-placeholder{width:60px;height:60px;border-radius:999px;display:grid;place-items:center;background:linear-gradient(135deg,#e7f8fa,#f6fbff);border:1px solid rgba(19,181,177,.28);color:var(--teal-dark);font-size:1.12rem;font-weight:950}.mini-label{color:var(--muted);font-size:.74rem;font-weight:800;text-transform:uppercase;letter-spacing:.04em}.candidate-name{font-size:1.20rem;font-weight:950;line-height:1.1;color:var(--navy);margin-top:.08rem}.candidate-meta{color:var(--muted);font-size:.85rem;margin-top:.12rem}.position-pill{display:inline-flex;align-items:center;justify-content:center;min-width:38px;height:22px;margin-top:.28rem;border-radius:8px;border:1px solid rgba(19,181,177,.34);background:rgba(19,181,177,.08);color:var(--teal-dark);font-weight:900;font-size:.75rem;padding:0 .42rem}.score-card,.stat-card{min-height:104px;padding:.65rem .58rem;text-align:center;display:flex;flex-direction:column;justify-content:center}.score-label,.stat-label{color:var(--muted);font-size:.74rem;font-weight:800;line-height:1.2}.big-score{color:var(--teal-dark);font-size:2.0rem;font-weight:950;line-height:1.0;margin-top:.25rem}.score-status{color:var(--teal-dark);font-size:.88rem;font-weight:900;margin-top:.12rem}.stat-value{color:var(--navy);font-weight:900;font-size:.94rem;line-height:1.15;margin-top:.25rem;word-break:break-word}.stat-value.accent{color:var(--teal-dark);font-size:1.10rem}.metric-strip-card{min-height:54px;padding:.50rem .72rem;display:flex;align-items:center;gap:.55rem}.metric-strip-icon{width:34px;height:34px;border-radius:11px;display:grid;place-items:center;background:rgba(19,181,177,.10);color:var(--teal-dark);font-weight:900}.metric-strip-label{color:var(--muted);font-size:.72rem;font-weight:800;line-height:1.1}.metric-strip-value{color:var(--navy);font-size:1.0rem;font-weight:950;line-height:1.1}.section-head{display:flex;align-items:center;gap:.55rem;margin-top:.10rem;margin-bottom:.10rem}.section-title{color:var(--navy);font-weight:950;font-size:1.05rem;line-height:1.1}.section-subtitle{color:var(--muted);font-size:.80rem;line-height:1.15;margin-top:.04rem}.footer-note{text-align:center;margin-top:.25rem;color:var(--muted);font-size:.78rem}div[data-testid="stDataFrame"]{border-radius:14px!important;overflow:hidden!important;border:1px solid rgba(148,163,184,.18)}div[data-testid="stAlert"]{padding:.35rem .55rem}
@media(max-width:1440px){.main .block-container{max-width:98vw;padding-left:.75rem;padding-right:.75rem}.pitch-field{height:158px}.candidate-card,.score-card,.stat-card{min-height:96px}.candidate-name{font-size:1.10rem}.big-score{font-size:1.78rem}.metric-strip-card{min-height:50px;padding:.42rem .62rem}}@media(max-width:1100px){.pitch-field{height:180px}}

/* ===== Ajuste final: dashboard compacto y cancha con posiciones absolutas ===== */
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"],
#MainMenu,
footer{
    display:none!important;
    visibility:hidden!important;
    height:0!important;
    min-height:0!important;
    max-height:0!important;
    overflow:hidden!important;
}
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main,
.main{
    padding-top:0!important;
    margin-top:0!important;
}
[data-testid="stMainBlockContainer"],
.block-container,
.main .block-container{
    max-width:1560px!important;
    padding:.08rem .85rem .08rem .85rem!important;
    margin-top:0!important;
}
.main .block-container [data-testid="stVerticalBlock"]{
    gap:.22rem!important;
}
div[data-testid="stHorizontalBlock"]{
    gap:.45rem!important;
}

/* Tres paneles superiores con misma altura */
.st-key-config_panel,
.st-key-pitch_panel,
.st-key-pref_panel,
.st-key-config_panel [data-testid="stVerticalBlockBorderWrapper"],
.st-key-pitch_panel [data-testid="stVerticalBlockBorderWrapper"],
.st-key-pref_panel [data-testid="stVerticalBlockBorderWrapper"],
.st-key-config_panel[data-testid="stVerticalBlockBorderWrapper"],
.st-key-pitch_panel[data-testid="stVerticalBlockBorderWrapper"],
.st-key-pref_panel[data-testid="stVerticalBlockBorderWrapper"]{
    height:262px!important;
    min-height:262px!important;
    max-height:262px!important;
    overflow:hidden!important;
    border-radius:14px!important;
}

/* Panel del campo: sin título, sin texto inferior */
.st-key-pitch_panel .sf-panel-head,
.pitch-note{
    display:none!important;
}
.st-key-pitch_panel [data-testid="stVerticalBlockBorderWrapper"],
.st-key-pitch_panel[data-testid="stVerticalBlockBorderWrapper"]{
    padding:.10rem!important;
}

/* Cancha absoluta: ocupa todo el recuadro central */
.st-key-pitch_abs_area{
    position:relative!important;
    width:100%!important;
    height:224px!important;
    min-height:224px!important;
    max-height:224px!important;
    margin:0!important;
    padding:0!important;
    overflow:hidden!important;
    border-radius:13px!important;
    border:3px solid rgba(255,255,255,.96)!important;
    background:
        linear-gradient(90deg, transparent 49.72%, rgba(255,255,255,.88) 49.92%, rgba(255,255,255,.88) 50.08%, transparent 50.28%),
        radial-gradient(circle at 50% 50%, transparent 0 39px, rgba(255,255,255,.80) 40px 42px, transparent 43px),
        repeating-linear-gradient(90deg, rgba(76,150,49,.96) 0px, rgba(76,150,49,.96) 86px, rgba(52,116,36,.96) 86px, rgba(52,116,36,.96) 172px),
        linear-gradient(180deg, rgba(255,255,255,.06), rgba(0,0,0,.08));
    box-shadow:inset 0 0 26px rgba(0,0,0,.12),0 8px 18px rgba(18,50,93,.10)!important;
}
.st-key-pitch_abs_area:before,
.st-key-pitch_abs_area:after{
    content:"";
    position:absolute;
    top:24%;
    width:14%;
    height:52%;
    border:2px solid rgba(255,255,255,.80);
    z-index:0;
    pointer-events:none;
}
.st-key-pitch_abs_area:before{left:0;border-left:0;}
.st-key-pitch_abs_area:after{right:0;border-right:0;}

.st-key-pitch_abs_area [data-testid="stVerticalBlock"]{
    position:absolute!important;
    inset:0!important;
    width:100%!important;
    height:100%!important;
    margin:0!important;
    padding:0!important;
}

/* Botones como chips tácticos */
.st-key-pitch_abs_area [class*="st-key-pitchpos_"]{
    position:absolute!important;
    z-index:5!important;
    width:auto!important;
    margin:0!important;
    transform:translate(-50%, -50%)!important;
}
.st-key-pitch_abs_area [class*="st-key-pitchpos_"] div[data-testid="stButton"]{
    margin:0!important;
    padding:0!important;
}
.st-key-pitch_abs_area [class*="st-key-pitchpos_"] button{
    width:auto!important;
    min-width:44px!important;
    height:28px!important;
    min-height:28px!important;
    padding:0 .48rem!important;
    border-radius:8px!important;
    font-size:.72rem!important;
    line-height:1!important;
    font-weight:950!important;
    background:rgba(255,255,255,.96)!important;
    color:var(--navy)!important;
    border:1px solid rgba(18,50,93,.18)!important;
    box-shadow:0 6px 13px rgba(18,50,93,.15)!important;
}
.st-key-pitch_abs_area [class*="st-key-pitchpos_"] button[kind="primary"],
.st-key-pitch_abs_area [class*="st-key-pitchpos_"] button[data-testid="baseButton-primary"]{
    background:linear-gradient(135deg,#13b5b1,#0aa8c9)!important;
    color:#fff!important;
    border-color:rgba(255,255,255,.95)!important;
    box-shadow:0 0 0 3px rgba(19,181,177,.24),0 0 14px rgba(19,181,177,.58)!important;
}

/* Coordenadas tácticas absolutas */
.st-key-pitchpos_GK{left:6.5%;top:50%;}
.st-key-pitchpos_DL{left:16%;top:20%;}
.st-key-pitchpos_DC{left:25%;top:50%;}
.st-key-pitchpos_DR{left:16%;top:80%;}
.st-key-pitchpos_DML{left:24%;top:24%;}
.st-key-pitchpos_DMR{left:24%;top:76%;}
.st-key-pitchpos_DMC{left:38%;top:50%;}
.st-key-pitchpos_MC{left:50%;top:50%;}
.st-key-pitchpos_AMC{left:68%;top:50%;}
.st-key-pitchpos_LEFT_WIDE_MID{left:50%;top:78%;}
.st-key-pitchpos_RIGHT_WIDE_MID{left:50%;top:22%;}
.st-key-pitchpos_ML{left:50%;top:78%;}
.st-key-pitchpos_MR{left:50%;top:22%;}
.st-key-pitchpos_LEFT_ATTACK_WIDE{left:76%;top:20%;}
.st-key-pitchpos_RIGHT_ATTACK_WIDE{left:76%;top:80%;}
.st-key-pitchpos_AML{left:76%;top:20%;}
.st-key-pitchpos_AMR{left:76%;top:80%;}
.st-key-pitchpos_FWL{left:84%;top:35%;}
.st-key-pitchpos_FWR{left:84%;top:65%;}
.st-key-pitchpos_FW{left:91.5%;top:50%;}

/* Compactación general */
.sf-header{margin-bottom:.12rem!important;}
.sf-logo{width:38px!important;height:38px!important;font-size:1.15rem!important;}
.sf-title{font-size:1.45rem!important;}
.sf-subtitle{font-size:.78rem!important;margin-top:0!important;}
.sf-panel-head{margin-bottom:.20rem!important;}
.result-banner{padding:.38rem .58rem!important;margin:.25rem 0 .20rem 0!important;}
.candidate-card,.score-card,.stat-card{min-height:72px!important;padding:.42rem .55rem!important;}
.avatar-placeholder{width:44px!important;height:44px!important;font-size:.95rem!important;}
.candidate-name{font-size:1rem!important;}
.big-score{font-size:1.55rem!important;}
.metric-strip-card{min-height:38px!important;padding:.30rem .54rem!important;}
div[data-testid="stDataFrame"]{max-height:320px!important;}


/* ===== Corrección final: cancha centrada y preferencias sin recorte ===== */
.st-key-config_panel,
.st-key-pitch_panel,
.st-key-pref_panel,
.st-key-config_panel [data-testid="stVerticalBlockBorderWrapper"],
.st-key-pitch_panel [data-testid="stVerticalBlockBorderWrapper"],
.st-key-pref_panel [data-testid="stVerticalBlockBorderWrapper"],
.st-key-config_panel[data-testid="stVerticalBlockBorderWrapper"],
.st-key-pitch_panel[data-testid="stVerticalBlockBorderWrapper"],
.st-key-pref_panel[data-testid="stVerticalBlockBorderWrapper"]{
    height:262px!important;
    min-height:262px!important;
    max-height:262px!important;
    overflow:hidden!important;
}

.st-key-pitch_panel [data-testid="stVerticalBlockBorderWrapper"],
.st-key-pitch_panel[data-testid="stVerticalBlockBorderWrapper"]{
    padding:.10rem!important;
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
}

.st-key-pitch_panel [data-testid="stVerticalBlock"]{
    height:100%!important;
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
}

.st-key-pitch_abs_area{
    width:96%!important;
    height:224px!important;
    min-height:224px!important;
    max-height:224px!important;
    margin:auto!important;
    padding:0!important;
    align-self:center!important;
}

.st-key-pref_panel [data-testid="stVerticalBlockBorderWrapper"],
.st-key-pref_panel[data-testid="stVerticalBlockBorderWrapper"]{
    padding:.58rem .70rem!important;
}

.st-key-pref_panel .sf-panel-head{
    margin-bottom:.24rem!important;
}

.st-key-pref_panel .stCheckbox{
    margin-bottom:.28rem!important;
}

.st-key-pref_panel div[data-baseweb="select"]>div{
    min-height:35px!important;
}

.st-key-pref_panel div[data-testid="stTextInput"] input,
.st-key-pref_panel div[data-testid="stNumberInput"] input{
    min-height:34px!important;
}

.st-key-pref_panel label{
    margin-bottom:.08rem!important;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

@st.cache_resource(show_spinner=False)
def get_engine():
    return TacticalCompatibilityEngine()

engine = get_engine()

PROTOTYPE_SOURCE = "weighted"
METRIC = "euclidean"
SCORE_METHOD = "compat_score_rank_0_100"
FEATURE_SET = "full"
PENALTY_PROFILE = "medium"
ALLOWED_LEAGUES = None
DEFAULT_SHORTLIST_SIZE = 50

POSITION_LABELS = {"LEFT_ATTACK_WIDE":"LAW","LEFT_WIDE_MID":"LWM","RIGHT_ATTACK_WIDE":"RAW","RIGHT_WIDE_MID":"RWM"}
BLOCK_LABELS = {"progression":"Progresión","passing":"Pase","spatial":"Ocupación espacial","defensive":"Defensa","offensive":"Ataque","team_context":"Participación en equipo"}
FOOT_LABELS = {"left":"Izquierdo","right":"Derecho","both":"Ambos","none":"Cualquiera","nan":"No disponible","":"No disponible"}
POSITION_DESCRIPTIONS = {"GK":"Portero","DC":"Defensa central","DL":"Lateral izquierdo","DR":"Lateral derecho","DMC":"Mediocentro defensivo","MC":"Mediocentro","AMC":"Mediocampista ofensivo","FW":"Delantero centro","LEFT_ATTACK_WIDE":"Atacante de banda izquierda","RIGHT_ATTACK_WIDE":"Atacante de banda derecha","LEFT_WIDE_MID":"Volante/carrilero izquierdo","RIGHT_WIDE_MID":"Volante/carrilero derecho","AML":"Extremo izquierdo","AMR":"Extremo derecho","FWL":"Delantero izquierdo","FWR":"Delantero derecho","ML":"Volante izquierdo","MR":"Volante derecho","DML":"Carrilero izquierdo","DMR":"Carrilero derecho"}
PITCH_COORDS = {"GK":(8,50),"DL":(18,24),"DC":(28,50),"DR":(18,76),"DML":(24,24),"DMR":(24,76),"DMC":(38,50),"MC":(50,50),"AMC":(61,24),"ML":(57,76),"MR":(73,76),"LEFT_WIDE_MID":(61,76),"RIGHT_WIDE_MID":(73,76),"AML":(78,24),"AMR":(78,76),"LEFT_ATTACK_WIDE":(78,24),"RIGHT_ATTACK_WIDE":(78,76),"FWL":(86,34),"FWR":(86,66),"FW":(92,50)}

def name_col_for(df: pd.DataFrame) -> str | None:
    for col in ["lineup_player_name", "player_name", "name"]:
        if col in df.columns:
            return col
    return None

def distance_column_for(df: pd.DataFrame) -> str:
    if "distance_euclidean" in df.columns:
        return "distance_euclidean"
    if "distance" in df.columns:
        return "distance"
    return ""

def get_player_name(row: pd.Series) -> str:
    for col in ["lineup_player_name", "player_name", "name"]:
        if col in row.index and pd.notna(row[col]):
            return str(row[col])
    return "Jugador no disponible"

def player_initials(name: str) -> str:
    parts = [p for p in str(name).replace("-", " ").strip().split() if p]
    if not parts:
        return "JD"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return f"{parts[0][0]}{parts[-1][0]}".upper()

def money_short(value: Any) -> str:
    value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(value):
        return "No disponible"
    if abs(value) >= 1_000_000:
        return f"€{value / 1_000_000:.1f} M"
    if abs(value) >= 1_000:
        return f"€{value / 1_000:.0f} K"
    return f"€{value:.0f}"

def format_foot(value: Any) -> str:
    if pd.isna(value):
        return "No disponible"
    raw = str(value).strip().lower()
    return FOOT_LABELS.get(raw, str(value))

def format_group_pos(value: Any) -> str:
    if pd.isna(value):
        return "No disponible"
    raw = str(value).strip()
    return POSITION_LABELS.get(raw, raw)

def format_height(value: Any) -> str:
    numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric_value):
        return "No disponible"
    return f"{numeric_value:.2f} m"

def safe_score(value: Any) -> float | None:
    score = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(score):
        return None
    return float(score)

def score_status(value: Any) -> str:
    score = safe_score(value)
    if score is None:
        return "No disponible"
    if score >= 85:
        return "Excelente"
    if score >= 75:
        return "Muy buen encaje"
    if score >= 65:
        return "Buen encaje"
    return "A revisar"

def final_ranking_display(df: pd.DataFrame) -> pd.DataFrame:
    player_col = name_col_for(df)
    if player_col is None:
        return pd.DataFrame()
    required = [player_col,"event_team_name","merged_pos","player_valuation","foot","height","final_scouting_score_0_100"]
    available = [col for col in required if col in df.columns]
    out = df[available].copy()
    out = out.rename(columns={player_col:"Jugador","event_team_name":"Club","merged_pos":"Grupo posicional","player_valuation":"Valor de mercado","foot":"Pie","height":"Altura","final_scouting_score_0_100":"Score final"})
    if "Grupo posicional" in out.columns:
        out["Grupo posicional"] = out["Grupo posicional"].map(format_group_pos)
    if "Pie" in out.columns:
        out["Pie"] = out["Pie"].map(format_foot)
    if "Altura" in out.columns:
        out["Altura"] = out["Altura"].map(format_height)
    if "Valor de mercado" in out.columns:
        out["Valor de mercado"] = out["Valor de mercado"].map(money_short)
    if "Score final" in out.columns:
        out["Score final"] = pd.to_numeric(out["Score final"], errors="coerce").round(1)
    final_order = ["Jugador","Club","Grupo posicional","Valor de mercado","Pie","Altura","Score final"]
    return out[[col for col in final_order if col in out.columns]]

def build_context_key(*items: Any) -> str:
    return hashlib.md5("|".join(str(x) for x in items).encode("utf-8")).hexdigest()[:16]

def block_display(block_df: pd.DataFrame) -> pd.DataFrame:
    if block_df.empty:
        return block_df
    out = block_df.copy()
    out["Área"] = out["block"].map(BLOCK_LABELS).fillna(out["block"])
    out["Ajuste"] = pd.to_numeric(out["block_similarity_0_100"], errors="coerce").round(1)
    out["Lectura"] = out["prototype_vs_player"].replace({"por encima":"Por encima del prototipo","por debajo":"Por debajo del prototipo","alineado":"Alineado con el prototipo"})
    return out[["Área","Ajuste","Lectura"]]

def get_inferred_base_position(proto_df: pd.DataFrame, team_name: str, merged_pos: str) -> str | None:
    preview = proto_df[(proto_df["event_team_name"].astype(str) == str(team_name)) & (proto_df["merged_pos"].astype(str) == str(merged_pos))].copy()
    if preview.empty:
        return None
    if "base_pos" in preview.columns and preview["base_pos"].notna().any():
        return str(preview["base_pos"].mode().iloc[0])
    return str(merged_pos)

def position_description(value: Any) -> str:
    if pd.isna(value):
        return ""
    return POSITION_DESCRIPTIONS.get(str(value).strip(), "Grupo posicional")

def get_query_position() -> str | None:
    try:
        value = st.query_params.get("pos", None)
    except Exception:
        return None
    if isinstance(value, list):
        return str(value[0]) if value else None
    return str(value) if value is not None else None

def panel_head(icon: str, title: str, subtitle: str) -> None:
    st.markdown(f"""
    <div class="sf-panel-head"><div class="sf-panel-icon">{html.escape(icon)}</div><div>
    <div class="sf-panel-title">{html.escape(title)}</div><div class="sf-panel-subtitle">{html.escape(subtitle)}</div>
    </div></div>
    """, unsafe_allow_html=True)


def keyed_container(border: bool = False, key: str | None = None):
    try:
        return st.container(border=border, key=key)
    except TypeError:
        return st.container(border=border)


def set_pending_position(pos: str) -> None:
    st.session_state["pending_merged_pos"] = str(pos)

def render_position_pitch(position_options: list[str], selected_position: str) -> str:
    available_positions = [str(pos) for pos in position_options]
    available_set = set(available_positions)

    if selected_position not in available_set and available_positions:
        selected_position = available_positions[0]
        st.session_state["pending_merged_pos"] = selected_position

    selected_position = str(st.session_state.get("pending_merged_pos", selected_position))
    if selected_position not in available_set and available_positions:
        selected_position = available_positions[0]
        st.session_state["pending_merged_pos"] = selected_position

    with keyed_container(border=False, key="pitch_abs_area"):
        for pos in available_positions:
            st.button(
                format_group_pos(pos),
                key=f"pitchpos_{pos}",
                on_click=set_pending_position,
                args=(pos,),
                type="primary" if pos == selected_position else "secondary",
                use_container_width=False,
                help=position_description(pos),
            )

    return str(st.session_state.get("pending_merged_pos", selected_position))

def render_shortlist_dataframe(display_df: pd.DataFrame) -> list[int]:
    if display_df.empty:
        st.info("No hay candidatos disponibles para mostrar.")
        return []
    try:
        table_event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=212,
            on_select="rerun",
            selection_mode="single-row",
            column_config={
                "Jugador": st.column_config.TextColumn("Jugador", width="medium"),
                "Club": st.column_config.TextColumn("Club", width="medium"),
                "Grupo posicional": st.column_config.TextColumn("Grupo posicional", width="small"),
                "Valor de mercado": st.column_config.TextColumn("Valor de mercado", width="small"),
                "Pie": st.column_config.TextColumn("Pie", width="small"),
                "Altura": st.column_config.TextColumn("Altura", width="small"),
                "Score final": st.column_config.ProgressColumn("Score final", min_value=0.0, max_value=100.0, format="%.1f", width="medium"),
            },
            key="shortlist_table",
        )
    except TypeError:
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=224)
        st.caption("Actualiza Streamlit para seleccionar filas directamente desde la tabla.")
        return []
    selection = table_event.get("selection", {}) if isinstance(table_event, dict) else {}
    rows = selection.get("rows", []) if isinstance(selection, dict) else []
    return list(rows) if rows is not None else []

def compute_ranking(proto_df, players_df, team_name, merged_pos, exclude_same_team, preferred_foot, min_height, max_value_target):
    raw_df, proto_row, valid_cols = engine.compute_for_target_merged(
        proto_df=proto_df,
        players_df=players_df,
        team_name=team_name,
        merged_pos=merged_pos,
        allowed_leagues=ALLOWED_LEAGUES,
        exclude_same_team=exclude_same_team,
        score_method=SCORE_METHOD,
        feature_set=FEATURE_SET,
        metric=METRIC,
    )
    if raw_df.empty:
        return raw_df, raw_df.copy(), proto_row, valid_cols
    raw_df = engine.add_block_similarity_scores(raw_df, valid_cols, block_scale=1.5)
    distance_col = distance_column_for(raw_df)
    sort_cols, ascending = [SCORE_METHOD], [False]
    if distance_col:
        sort_cols.append(distance_col)
        ascending.append(True)
    raw_df = raw_df.sort_values(sort_cols, ascending=ascending).copy()
    raw_df["rank_distance"] = range(1, len(raw_df) + 1)
    final_df = engine.apply_penalties(
        result_df=raw_df,
        preferred_foot=preferred_foot,
        min_height=min_height,
        max_value_target=max_value_target,
        scenario_name=PENALTY_PROFILE,
        tactical_base_col=SCORE_METHOD,
    )
    return raw_df, final_df, proto_row, valid_cols


def render_player_detail_content(selected_player: str, selected_row: pd.Series, raw_df: pd.DataFrame, proto_row: pd.Series, valid_cols: list[str]):
    selected_score = safe_score(selected_row.get("final_scouting_score_0_100"))
    selected_score_text = f"{selected_score:.1f}" if selected_score is not None else "NA"
    selected_base_score = safe_score(selected_row.get(SCORE_METHOD))
    selected_base_score_text = f"{selected_base_score:.1f}" if selected_base_score is not None else "NA"
    group_text = format_group_pos(selected_row.get("merged_pos", "Grupo no disponible"))
    st.markdown(f"""
    <div class="candidate-card" style="margin-bottom:.6rem;"><div class="mini-label">Candidato seleccionado</div>
    <div class="candidate-name">{html.escape(selected_player)}</div><div class="candidate-meta">{html.escape(str(selected_row.get('event_team_name', 'Club no disponible')))} · {html.escape(group_text)}</div></div>
    """, unsafe_allow_html=True)
    d1, d2, d3, d4 = st.columns(4)
    with d1: st.metric("Score final", selected_score_text)
    with d2: st.metric("Score táctico", selected_base_score_text)
    with d3: st.metric("Valor", money_short(selected_row.get("player_valuation", pd.NA)))
    with d4: st.metric("Altura", format_height(selected_row.get("height", pd.NA)))
    _, block_df = engine.explain_player_vs_prototype(raw_df, proto_row, valid_cols, selected_player)
    readable_blocks = block_display(block_df)
    if readable_blocks.empty:
        st.info("No hay diagnóstico disponible para este jugador.")
        return
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("### Áreas de mayor encaje")
        st.dataframe(readable_blocks.sort_values("Ajuste", ascending=False).head(3), use_container_width=True, hide_index=True, column_config={"Ajuste": st.column_config.ProgressColumn("Ajuste", min_value=0, max_value=100, format="%.1f")})
    with c2:
        st.markdown("### Áreas a revisar")
        st.dataframe(readable_blocks.sort_values("Ajuste", ascending=True).head(3), use_container_width=True, hide_index=True, column_config={"Ajuste": st.column_config.ProgressColumn("Ajuste", min_value=0, max_value=100, format="%.1f")})
    with st.expander("Ver todas las áreas tácticas", expanded=False):
        st.dataframe(readable_blocks.sort_values("Ajuste", ascending=False), use_container_width=True, hide_index=True, column_config={"Ajuste": st.column_config.ProgressColumn("Ajuste", min_value=0, max_value=100, format="%.1f")})


def make_player_detail_dialog():
    if hasattr(st, "dialog"):
        try:
            return st.dialog("Detalle táctico del jugador", width="large")(render_player_detail_content)
        except TypeError:
            return st.dialog("Detalle táctico del jugador")(render_player_detail_content)
    return render_player_detail_content

render_player_detail_dialog = make_player_detail_dialog()

# ======================================================
# CARGA DE DATOS
# ======================================================
try:
    players_df = engine.load_players()
    proto_df = engine.load_proto_merged(PROTOTYPE_SOURCE)
except Exception as exc:
    st.error("No fue posible cargar los datos de la aplicación.")
    st.exception(exc)
    st.stop()

team_options = engine.get_team_options(proto_df)
if not team_options:
    st.warning("No hay clubes disponibles para consultar.")
    st.stop()

st.markdown("""
<div class="sf-header"><div class="sf-logo">⚽</div><div><div class="sf-title">ScoutFit</div>
<div class="sf-subtitle">Compatibilidad táctica y ciencia de datos para el scouting profesional</div></div></div>
""", unsafe_allow_html=True)

if "pending_team_name" not in st.session_state or st.session_state["pending_team_name"] not in team_options:
    st.session_state["pending_team_name"] = team_options[0]
if "pending_exclude_same_team" not in st.session_state:
    st.session_state["pending_exclude_same_team"] = True
if "pending_use_preferences" not in st.session_state:
    st.session_state["pending_use_preferences"] = True

team_default_idx = team_options.index(st.session_state["pending_team_name"])
config_col, pitch_col, pref_col = st.columns([0.92, 1.65, 0.92], gap="small")

with config_col:
    with keyed_container(border=True, key="config_panel"):
        panel_head("⌕", "Configuración de búsqueda", "Define el club objetivo y lanza la búsqueda.")
        team_name = st.selectbox("Club objetivo", team_options, index=team_default_idx, key="team_select_widget")
        exclude_same_team = st.checkbox("Excluir jugadores del club objetivo", value=bool(st.session_state.get("pending_exclude_same_team", True)), key="exclude_same_team_widget")
        search_clicked = st.button("🔎 Buscar jugadores", type="primary", use_container_width=True)


if team_name != st.session_state.get("pending_team_name"):
    st.session_state["pending_team_name"] = team_name
    st.session_state.pop("pending_merged_pos", None)

position_options = engine.get_merged_position_options(proto_df, team_name)
if not position_options:
    st.warning("No hay grupos posicionales disponibles para ese club.")
    st.stop()
if st.session_state.get("pending_merged_pos") not in position_options:
    st.session_state["pending_merged_pos"] = position_options[0]

with pitch_col:
    with keyed_container(border=True, key="pitch_panel"):
        merged_pos = render_position_pitch(position_options, st.session_state["pending_merged_pos"])

inferred_base_pos = get_inferred_base_position(proto_df, team_name, merged_pos)
auto_preferred_foot = engine.infer_auto_preferred_foot(inferred_base_pos, merged_pos)
auto_min_height = engine.infer_auto_min_height(inferred_base_pos) if inferred_base_pos else None
_, _, max_value_target_team = engine.get_team_budget_value(players_df, team_name, divisor=6.0)

with pref_col:
    with keyed_container(border=True, key="pref_panel"):
        panel_head("☰", "Preferencias de scouting", "Ajusta criterios prácticos sobre el score final.")
        use_scouting_preferences = st.checkbox("Aplicar preferencias", value=bool(st.session_state.get("pending_use_preferences", True)), key="use_preferences_widget")
        if use_scouting_preferences:
            foot_options = ["none", "left", "right", "both"]
            default_foot = auto_preferred_foot if auto_preferred_foot in foot_options else "none"
            pref_key_suffix = build_context_key(team_name, merged_pos)
            foot_choice = st.selectbox("Pie deseado", foot_options, index=foot_options.index(default_foot), format_func=lambda x: FOOT_LABELS.get(x, x), key=f"foot_choice_{pref_key_suffix}")
            preferred_foot = None if foot_choice == "none" else foot_choice
            pref_c1, pref_c2 = st.columns([1, 1], gap="small")
            with pref_c1:
                min_height = st.number_input("Altura mínima", min_value=1.50, max_value=2.20, value=float(auto_min_height) if auto_min_height is not None else 1.75, step=0.01, key=f"min_height_{pref_key_suffix}")
            with pref_c2:
                default_budget = float(max_value_target_team) if pd.notna(max_value_target_team) else 10_000_000.0
                max_value_target = st.number_input("Presupuesto máximo", min_value=0.0, value=default_budget, step=500_000.0, key=f"max_value_{pref_key_suffix}")
        else:
            preferred_foot = None
            min_height = None
            max_value_target = None

# ======================================================
# APLICAR BÚSQUEDA SOLO AL OPRIMIR BOTÓN
# ======================================================
first_run = "applied_context" not in st.session_state
shortlist_size = DEFAULT_SHORTLIST_SIZE

if search_clicked or first_run:
    st.session_state["applied_team_name"] = team_name
    st.session_state["applied_merged_pos"] = merged_pos
    st.session_state["applied_shortlist_size"] = shortlist_size
    st.session_state["applied_exclude_same_team"] = exclude_same_team
    st.session_state["applied_preferred_foot"] = preferred_foot
    st.session_state["applied_min_height"] = min_height
    st.session_state["applied_max_value_target"] = max_value_target
    st.session_state["selected_candidate_idx"] = None

applied_team_name = st.session_state.get("applied_team_name", team_name)
applied_merged_pos = st.session_state.get("applied_merged_pos", merged_pos)
applied_shortlist_size = int(st.session_state.get("applied_shortlist_size", shortlist_size))
applied_exclude_same_team = bool(st.session_state.get("applied_exclude_same_team", exclude_same_team))
applied_preferred_foot = st.session_state.get("applied_preferred_foot", preferred_foot)
applied_min_height = st.session_state.get("applied_min_height", min_height)
applied_max_value_target = st.session_state.get("applied_max_value_target", max_value_target)

pending_context = build_context_key(team_name, merged_pos, shortlist_size, exclude_same_team, preferred_foot, min_height, max_value_target)
applied_context = build_context_key(applied_team_name, applied_merged_pos, applied_shortlist_size, applied_exclude_same_team, applied_preferred_foot, applied_min_height, applied_max_value_target)
st.session_state["applied_context"] = applied_context


# ======================================================
# CÁLCULO CON CACHE DE SESIÓN
# ======================================================
ranking_context = build_context_key(applied_team_name, applied_merged_pos, applied_exclude_same_team, applied_preferred_foot, applied_min_height, applied_max_value_target)
if st.session_state.get("ranking_context") != ranking_context:
    with st.spinner("Buscando candidatos compatibles..."):
        raw_df, final_df, proto_row, valid_cols = compute_ranking(proto_df, players_df, applied_team_name, applied_merged_pos, applied_exclude_same_team, applied_preferred_foot, applied_min_height, applied_max_value_target)
    st.session_state["ranking_context"] = ranking_context
    st.session_state["ranking_raw_df"] = raw_df
    st.session_state["ranking_final_df"] = final_df
    st.session_state["ranking_proto_row"] = proto_row
    st.session_state["ranking_valid_cols"] = valid_cols
else:
    raw_df = st.session_state.get("ranking_raw_df", pd.DataFrame())
    final_df = st.session_state.get("ranking_final_df", pd.DataFrame())
    proto_row = st.session_state.get("ranking_proto_row", None)
    valid_cols = st.session_state.get("ranking_valid_cols", [])

if raw_df.empty or final_df.empty:
    st.warning("No se encontraron candidatos para esta búsqueda.")
    st.stop()

shortlist_df = final_df.head(applied_shortlist_size).copy().reset_index(drop=True)
shortlist_display = final_ranking_display(shortlist_df)


top = shortlist_df.iloc[0]
top_player = get_player_name(top)
top_score = safe_score(top.get("final_scouting_score_0_100"))
top_score_text = f"{top_score:.0f}%" if top_score is not None else "NA"
top_distance_score = safe_score(top.get(SCORE_METHOD))

rec_col, score_col, club_col, foot_col, value_col, height_col = st.columns([2.45, 1.35, 1.10, .92, 1.10, .92], gap="small")
with rec_col:
    st.markdown(f"""
    <div class="candidate-card"><div class="candidate-card-flex"><div class="avatar-placeholder">{html.escape(player_initials(top_player))}</div><div>
    <div class="mini-label">Mejor candidato recomendado</div><div class="candidate-name">{html.escape(top_player)}</div>
    <div class="candidate-meta">{html.escape(str(top.get('event_team_name', 'Club no disponible')))}</div>
    <div class="position-pill">{html.escape(format_group_pos(top.get('merged_pos', applied_merged_pos)))}</div></div></div></div>
    """, unsafe_allow_html=True)
with score_col:
    st.markdown(f"<div class='score-card'><div class='score-label'>Score final de compatibilidad</div><div class='big-score'>{html.escape(top_score_text)}</div><div class='score-status'>{html.escape(score_status(top_score))}</div></div>", unsafe_allow_html=True)
with club_col:
    st.markdown(f"<div class='stat-card'><div class='stat-label'>Club actual</div><div class='stat-value'>{html.escape(str(top.get('event_team_name', 'NA')))}</div></div>", unsafe_allow_html=True)
with foot_col:
    st.markdown(f"<div class='stat-card'><div class='stat-label'>Pie</div><div class='stat-value'>{html.escape(format_foot(top.get('foot', pd.NA)))}</div></div>", unsafe_allow_html=True)
with value_col:
    st.markdown(f"<div class='stat-card'><div class='stat-label'>Valor de mercado</div><div class='stat-value accent'>{html.escape(money_short(top.get('player_valuation', pd.NA)))}</div></div>", unsafe_allow_html=True)
with height_col:
    st.markdown(f"<div class='stat-card'><div class='stat-label'>Altura</div><div class='stat-value accent'>{html.escape(format_height(top.get('height', pd.NA)))}</div></div>", unsafe_allow_html=True)

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4, gap="small")
avg_top = pd.to_numeric(shortlist_df["final_scouting_score_0_100"], errors="coerce").mean()


section_left, section_right = st.columns([1, .24], gap="small")
with section_left:
    st.markdown("""
    <div class="section-head"><div class="sf-panel-icon">☷</div><div><div class="section-title">Shortlist recomendada</div>
    <div class="section-subtitle">Haz clic en cualquier fila para ver el detalle táctico del jugador.</div></div></div>
    """, unsafe_allow_html=True)
with section_right:
    if not shortlist_display.empty:
        csv_data = shortlist_display.to_csv(index=False).encode("utf-8")
        safe_team = str(applied_team_name).replace(" ", "_")
        safe_pos = format_group_pos(applied_merged_pos).replace(" ", "_")

selection_context = build_context_key(ranking_context, applied_shortlist_size)
if st.session_state.get("selection_context") != selection_context:
    st.session_state["selection_context"] = selection_context
    st.session_state["selected_candidate_idx"] = None
selected_display_row = st.session_state.get("selected_candidate_idx")
if not isinstance(selected_display_row, int) or selected_display_row < 0 or selected_display_row >= len(shortlist_df):
    selected_display_row = None
    st.session_state["selected_candidate_idx"] = None

if shortlist_display.empty:
    st.info("No hay columnas disponibles para mostrar la shortlist.")
else:
    selected_rows = render_shortlist_dataframe(shortlist_display)
    if selected_rows:
        selected_display_row = int(selected_rows[0])
        st.session_state["selected_candidate_idx"] = selected_display_row
    player_col = name_col_for(shortlist_df)
    if selected_display_row is None or player_col is None:
        st.caption("Selecciona cualquier fila del ranking para abrir el detalle táctico del jugador.")
    else:
        selected_player = str(shortlist_df.iloc[selected_display_row][player_col])
        selected_row = shortlist_df.iloc[selected_display_row]
        render_player_detail_dialog(selected_player, selected_row, raw_df, proto_row, valid_cols)
        if not hasattr(st, "dialog"):
            st.caption("Tu versión de Streamlit no soporta ventanas emergentes; por eso el detalle se muestra debajo de la tabla.")

st.markdown("<div class='footer-note'>ScoutFit · Herramienta de apoyo para reclutamiento basada en compatibilidad sistema-jugador.</div>", unsafe_allow_html=True)
