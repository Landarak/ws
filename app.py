import warnings
warnings.filterwarnings("ignore")

import base64
import hashlib
import html
from pathlib import Path
from typing import Any
import pandas as pd
import streamlit as st

from engine import TacticalCompatibilityEngine
from urllib.parse import quote
import streamlit.components.v1 as components

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
.candidate-card,.score-card,.stat-card,.metric-strip-card{border-radius:16px;border:1px solid var(--border);background:rgba(255,255,255,.94);box-shadow:0 8px 20px rgba(18,50,93,.05)}.candidate-card{padding:.65rem .75rem;min-height:104px}.candidate-card-flex{display:flex;align-items:center;gap:.75rem}.avatar-placeholder{width:60px;height:60px;border-radius:999px;display:grid;place-items:center;background:linear-gradient(135deg,#e7f8fa,#f6fbff);border:1px solid rgba(19,181,177,.28);color:var(--teal-dark);font-size:1.12rem;font-weight:950}.mini-label{color:var(--muted);font-size:.74rem;font-weight:800;text-transform:uppercase;letter-spacing:.04em}.candidate-name{font-size:1.20rem;font-weight:950;line-height:1.1;color:var(--navy);margin-top:.08rem}.candidate-meta{color:var(--muted);font-size:.85rem;margin-top:.12rem}.position-pill{display:inline-flex;align-items:center;justify-content:center;min-width:38px;height:22px;margin-top:.28rem;border-radius:8px;border:1px solid rgba(19,181,177,.34);background:rgba(19,181,177,.08);color:var(--teal-dark);font-weight:900;font-size:.75rem;padding:0 .42rem}.score-card,.stat-card{min-height:104px;padding:.65rem .58rem;text-align:center;display:flex;flex-direction:column;justify-content:center}.score-label,.stat-label{color:var(--muted);font-size:.74rem;font-weight:800;line-height:1.2}.big-score{color:var(--teal-dark);font-size:2.0rem;font-weight:950;line-height:1.0;margin-top:.25rem}.score-status{color:var(--teal-dark);font-size:.88rem;font-weight:900;margin-top:.12rem}.stat-value{color:var(--navy);font-weight:900;font-size:.94rem;line-height:1.15;margin-top:.25rem;word-break:break-word}.stat-value.accent{color:var(--teal-dark);font-size:1.10rem}.metric-strip-card{min-height:54px;padding:.50rem .72rem;display:flex;align-items:center;gap:.55rem}.metric-strip-icon{width:34px;height:34px;border-radius:11px;display:grid;place-items:center;background:rgba(19,181,177,.10);color:var(--teal-dark);font-weight:900}.metric-strip-label{color:var(--muted);font-size:.72rem;font-weight:800;line-height:1.1}.metric-strip-value{color:var(--navy);font-size:1.0rem;font-weight:950;line-height:1.1}.section-head{display:flex;align-items:center;gap:.55rem;margin-top:.10rem;margin-bottom:.10rem;transform:translateY(-6px);}.section-title{color:var(--navy);font-weight:950;font-size:1.05rem;line-height:1.1}.section-subtitle{color:var(--muted);font-size:.80rem;line-height:1.15;margin-top:.04rem}.footer-note{text-align:center;margin-top:.25rem;color:var(--muted);font-size:.78rem}div[data-testid="stDataFrame"]{border-radius:14px!important;overflow:hidden!important;border:1px solid rgba(148,163,184,.18)}div[data-testid="stAlert"]{padding:.35rem .55rem}
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
    height:330px!important;
    min-height:330px!important;
    max-height:330px!important;
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
        linear-gradient(180deg, rgba(0,0,0,1), rgba(0,0,0,1)),
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
    height:330px!important;
    min-height:330px!important;
    max-height:330px!important;
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


/* ===== Shortlist tipo tarjetas clickeables ===== */
[class*="st-key-shortlist_card_"]{
    position:relative!important;
    width:100%!important;
    min-height:48px!important;
    margin-bottom:.28rem!important;
}

[class*="st-key-shortlist_card_"] pre,
[class*="st-key-shortlist_card_"] code{
    display:none!important;
}

.shortlist-card{
    position:relative;
    display:grid;
    grid-template-columns:42px 46px minmax(190px,1.45fr) 78px 82px 112px 96px 88px minmax(210px,.95fr);
    align-items:center;
    gap:.72rem;
    width:100%;
    min-height:48px;
    padding:.36rem .66rem;
    border-radius:16px;
    border:1px solid rgba(18,50,93,.12);
    background:rgba(255,255,255,.96);
    box-shadow:0 7px 18px rgba(18,50,93,.045);
    transition:transform .14s ease, box-shadow .14s ease, border-color .14s ease, background .14s ease;
}

[class*="st-key-shortlist_card_"]:hover .shortlist-card{
    transform:translateY(-1px);
    border-color:rgba(19,181,177,.34);
    box-shadow:0 10px 24px rgba(18,50,93,.075);
    background:linear-gradient(180deg,#ffffff 0%,#f7fcff 100%);
}

.shortlist-card.selected{
    border-color:rgba(19,181,177,.64);
    background:linear-gradient(135deg,rgba(219,247,252,.82),rgba(255,255,255,.96));
    box-shadow:0 0 0 3px rgba(19,181,177,.13),0 10px 24px rgba(18,50,93,.07);
}

.shortlist-rank{
    width:30px;
    height:30px;
    border-radius:999px;
    display:grid;
    place-items:center;
    background:rgba(19,181,177,.11);
    color:var(--teal-dark);
    font-size:.82rem;
    font-weight:950;
}

.shortlist-avatar,
.candidate-photo,
.detail-avatar-img{
    border-radius:999px;
    object-fit:cover;
    object-position:center;
    display:block;
    overflow:hidden;
    background:linear-gradient(135deg,var(--navy-2),var(--navy));
    border:1px solid rgba(201,161,67,.44);
    box-shadow:0 7px 15px rgba(6,43,79,.14);
}

.shortlist-avatar{
    width:38px;
    height:38px;
    color:#fff;
    display:grid;
    place-items:center;
    font-size:.78rem;
    font-weight:950;
}

.candidate-photo{
    width:44px!important;
    height:44px!important;
    min-width:44px!important;
    color:#fff;
    display:grid;
    place-items:center;
    font-size:.95rem;
    font-weight:950;
}

.detail-avatar-img{
    width:58px;
    height:58px;
    min-width:58px;
}

.shortlist-player-name{
    color:var(--navy);
    font-weight:950;
    font-size:.96rem;
    line-height:1.08;
}

.shortlist-player-sub{
    color:var(--muted);
    font-size:.73rem;
    margin-top:.12rem;
    line-height:1.1;
}

.shortlist-field{
    min-width:0;
}

.shortlist-label{
    color:var(--muted);
    font-size:.61rem;
    font-weight:850;
    text-transform:uppercase;
    letter-spacing:.035em;
    line-height:1;
    margin-bottom:.20rem;
}

.shortlist-value{
    color:var(--navy);
    font-size:.82rem;
    font-weight:800;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}

.shortlist-pill{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    min-width:38px;
    height:22px;
    border-radius:8px;
    padding:0 .42rem;
    border:1px solid rgba(19,181,177,.35);
    background:rgba(19,181,177,.08);
    color:var(--teal-dark);
    font-size:.76rem;
    font-weight:950;
}

.shortlist-score-top{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:.55rem;
    color:var(--muted);
    font-size:.68rem;
    font-weight:850;
    margin-bottom:.24rem;
}

.shortlist-score-top b{
    color:var(--navy);
    font-size:.82rem;
    font-weight:950;
}

.shortlist-score-track{
    height:8px;
    border-radius:999px;
    background:#e7eef6;
    overflow:hidden;
}

.shortlist-score-fill{
    height:100%;
    border-radius:999px;
    background:linear-gradient(90deg,#13b5b1,#1769aa);
}

/* Botón invisible exactamente encima de SU tarjeta */
[class*="st-key-shortlist_card_"] [class*="st-key-open_shortlist_detail_"]{
    position:absolute!important;
    inset:0!important;
    z-index:30!important;
    width:100%!important;
    height:100%!important;
    margin:0!important;
    padding:0!important;
}

[class*="st-key-shortlist_card_"] [class*="st-key-open_shortlist_detail_"] div[data-testid="stButton"]{
    width:100%!important;
    height:100%!important;
    margin:0!important;
    padding:0!important;
}

[class*="st-key-shortlist_card_"] [class*="st-key-open_shortlist_detail_"] button{
    width:100%!important;
    height:100%!important;
    min-height:100%!important;
    opacity:0!important;
    cursor:pointer!important;
    padding:0!important;
    margin:0!important;
    border:0!important;
    background:transparent!important;
    box-shadow:none!important;
}

@media(max-width:1200px){
    .shortlist-card{
        grid-template-columns:30px 34px minmax(150px,1.35fr) 58px 64px 82px 76px 70px minmax(130px,.9fr);
        gap:.45rem;
        padding:.55rem .58rem;
    }
    .shortlist-label{font-size:.55rem}
    .shortlist-value,.shortlist-score-top b{font-size:.74rem}
    .shortlist-player-name{font-size:.86rem}
}


/* ===== Estado inicial antes de la primera búsqueda ===== */
.start-guide{
    margin-top:.55rem;
    border-radius:18px;
    border:1px solid rgba(19,181,177,.30);
    background:
        radial-gradient(circle at 8% 16%, rgba(19,181,177,.18), transparent 28%),
        linear-gradient(135deg, rgba(219,247,252,.88), rgba(255,255,255,.96));
    box-shadow:0 12px 28px rgba(18,50,93,.07);
    padding:1.05rem 1.15rem;
}
.start-guide-main{
    display:grid;
    grid-template-columns:56px 1fr;
    gap:.85rem;
    align-items:start;
}
.start-guide-icon{
    width:50px;
    height:50px;
    border-radius:999px;
    display:grid;
    place-items:center;
    background:rgba(19,181,177,.13);
    border:1px solid rgba(19,181,177,.34);
    color:var(--teal-dark);
    font-size:1.35rem;
    font-weight:950;
}
.start-guide-title{
    color:var(--navy);
    font-size:1.22rem;
    font-weight:950;
    line-height:1.1;
    margin-bottom:.20rem;
}
.start-guide-text{
    color:var(--muted);
    font-size:.88rem;
    line-height:1.35;
    max-width:980px;
}
.start-guide-current{
    display:flex;
    flex-wrap:wrap;
    gap:.45rem;
    margin-top:.62rem;
}
.start-guide-chip{
    display:inline-flex;
    align-items:center;
    gap:.35rem;
    padding:.35rem .55rem;
    border-radius:999px;
    background:rgba(255,255,255,.86);
    border:1px solid rgba(18,50,93,.12);
    color:var(--navy);
    font-weight:850;
    font-size:.78rem;
}
.start-guide-chip b{
    color:var(--teal-dark);
}
.start-guide-steps{
    display:grid;
    grid-template-columns:repeat(3, minmax(0, 1fr));
    gap:.65rem;
    margin-top:.85rem;
}
.start-guide-step{
    border-radius:14px;
    background:rgba(255,255,255,.84);
    border:1px solid rgba(18,50,93,.10);
    padding:.70rem .75rem;
}
.start-guide-step-num{
    width:24px;
    height:24px;
    border-radius:999px;
    display:inline-grid;
    place-items:center;
    background:rgba(19,181,177,.12);
    color:var(--teal-dark);
    font-weight:950;
    font-size:.72rem;
    margin-bottom:.35rem;
}
.start-guide-step-title{
    color:var(--navy);
    font-size:.86rem;
    font-weight:950;
    margin-bottom:.14rem;
}
.start-guide-step-text{
    color:var(--muted);
    font-size:.74rem;
    line-height:1.25;
}
.start-guide-callout{
    margin-top:.75rem;
    border-radius:13px;
    padding:.55rem .70rem;
    background:rgba(19,181,177,.09);
    border:1px solid rgba(19,181,177,.22);
    color:#075c64;
    font-size:.80rem;
    font-weight:850;
}
@media(max-width:1000px){
    .start-guide-steps{grid-template-columns:1fr;}
}
/* ===== Compactar espacio vertical superior ===== */

/* Quita aire arriba de toda la app */
[data-testid="stMainBlockContainer"],
.block-container,
.main .block-container{
    padding-top:0!important;
    margin-top:0!important;
}

/* Acerca el título ScoutFit a los paneles */
.sf-header{
    margin-top:-1.2rem!important;
    margin-bottom:-.10rem!important;
}

/* Reduce separación entre bloques principales */
.main .block-container [data-testid="stVerticalBlock"]{
    gap:.12rem!important;
}

/* Acerca el bloque de resultados/guía a la fila de búsqueda */
.start-guide{
    margin-top:.25rem!important;
}

.result-banner{
    margin-top:.15rem!important;
}

/* Acerca las tarjetas de candidato a la parte superior */
.candidate-card,
.score-card,
.stat-card{
    margin-top:0!important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ======================================================
# IDENTIDAD VISUAL SCOUTFIT
# Paleta basada en el logo: azul marino, fucsia y dorado.
# ======================================================
BRAND_CSS = """
<style>
:root{
    --navy:#062B4F!important;
    --navy-2:#021B33!important;
    --pink:#F00655!important;
    --pink-dark:#C90046!important;
    --gold:#C9A143!important;
    --gold-dark:#9A741B!important;
    --gold-soft:#F4E6B4!important;
    --muted:#687386!important;
    --border:rgba(6,43,79,.14)!important;
    --shadow:0 10px 26px rgba(6,43,79,.08)!important;
}

.stApp{
    background:
        radial-gradient(circle at 4% 12%, rgba(240,6,85,.10) 0, rgba(240,6,85,0) 26%),
        radial-gradient(circle at 92% 8%, rgba(201,161,67,.16) 0, rgba(201,161,67,0) 22%),
        radial-gradient(circle at 100% 82%, rgba(6,43,79,.08) 0, rgba(6,43,79,0) 28%),
        linear-gradient(180deg,#ffffff 0%,#f7f8fb 54%,#ffffff 100%)!important;
}

.stApp:before{
    content:"";
    position:fixed;
    right:-145px;
    top:70px;
    width:390px;
    height:390px;
    border-radius:999px;
    border:30px solid rgba(240,6,85,.065);
    pointer-events:none;
    z-index:0;
}

.stApp:after{
    content:"";
    position:fixed;
    left:-155px;
    bottom:-145px;
    width:360px;
    height:360px;
    border-radius:999px;
    border:28px solid rgba(201,161,67,.085);
    pointer-events:none;
    z-index:0;
}

[data-testid="stMainBlockContainer"],
.block-container,
.main .block-container{
    position:relative!important;
    z-index:1!important;
}

h1,h2,h3,h4,h5,h6,p,label,span,div{color:var(--navy)}

.sf-header{
    display:flex!important;
    align-items:center!important;
    gap:.72rem!important;
    margin-top:-1.05rem!important;
    margin-bottom:.02rem!important;
    padding:.10rem .05rem .20rem .05rem!important;
}

.sf-logo-img-wrap{
    width:46px!important;
    height:46px!important;
    min-width:46px!important;
    border-radius:15px!important;
    display:grid!important;
    place-items:center!important;
    overflow:hidden!important;
    background:linear-gradient(135deg,#ffffff,#f7f8fb)!important;
    border:1px solid rgba(201,161,67,.48)!important;
    box-shadow:0 10px 22px rgba(6,43,79,.12)!important;
}

.sf-logo-img{
    width:100%!important;
    height:100%!important;
    object-fit:cover!important;
    object-position:center!important;
    transform:scale(1.22)!important;
}

.sf-logo-fallback{
    width:46px!important;
    height:46px!important;
    min-width:46px!important;
    border-radius:15px!important;
    display:grid!important;
    place-items:center!important;
    background:
        radial-gradient(circle at 72% 22%, rgba(201,161,67,.95) 0 6px, transparent 7px),
        linear-gradient(135deg,var(--navy-2),var(--navy))!important;
    border:1px solid rgba(201,161,67,.54)!important;
    box-shadow:0 10px 22px rgba(6,43,79,.14)!important;
    color:#fff!important;
    font-weight:950!important;
    letter-spacing:-.08em!important;
}

.sf-title{
    margin:0!important;
    line-height:1!important;
    font-size:clamp(1.52rem,2vw,2.10rem)!important;
    font-weight:950!important;
    letter-spacing:-.052em!important;
}

.sf-title-navy{color:var(--navy)!important;}
.sf-title-pink{color:var(--pink)!important;}

.sf-subtitle{
    margin-top:.03rem!important;
    color:var(--muted)!important;
    font-size:.79rem!important;
    font-weight:620!important;
}

.sf-panel-icon,
.start-guide-icon,
.metric-strip-icon{
    background:rgba(201,161,67,.14)!important;
    border:1px solid rgba(201,161,67,.34)!important;
    color:var(--gold-dark)!important;
}

.search-note,
.start-guide-callout{
    border-color:rgba(201,161,67,.30)!important;
    background:rgba(201,161,67,.10)!important;
    color:#6f5213!important;
}

div[data-testid="stButton"]>button{
    border-radius:13px!important;
    font-weight:900!important;
}

div[data-testid="stButton"]>button[kind="primary"]{
    background:linear-gradient(135deg,var(--pink),var(--pink-dark))!important;
    border:0!important;
    color:#fff!important;
    box-shadow:0 10px 22px rgba(240,6,85,.23)!important;
}

div[data-testid="stButton"]>button[kind="primary"]:hover{
    filter:brightness(1.03)!important;
    box-shadow:0 12px 26px rgba(240,6,85,.28)!important;
}

.stDownloadButton button{
    border-color:rgba(201,161,67,.55)!important;
    color:var(--gold-dark)!important;
    font-weight:900!important;
}

.st-key-config_panel [data-testid="stVerticalBlockBorderWrapper"],
.st-key-pitch_panel [data-testid="stVerticalBlockBorderWrapper"],
.st-key-pref_panel [data-testid="stVerticalBlockBorderWrapper"],
.st-key-config_panel[data-testid="stVerticalBlockBorderWrapper"],
.st-key-pitch_panel[data-testid="stVerticalBlockBorderWrapper"],
.st-key-pref_panel[data-testid="stVerticalBlockBorderWrapper"]{
    border:1px solid rgba(6,43,79,.12)!important;
    box-shadow:0 10px 26px rgba(6,43,79,.06)!important;
    background:rgba(255,255,255,.96)!important;
}

.st-key-pitch_abs_area{
    border:3px solid rgba(255,255,255,.96)!important;
    background:
        linear-gradient(90deg, transparent 49.72%, rgba(255,255,255,.86) 49.92%, rgba(255,255,255,.86) 50.08%, transparent 50.28%),
        radial-gradient(circle at 50% 50%, transparent 0 39px, rgba(255,255,255,.75) 40px 42px, transparent 43px),
        radial-gradient(circle at 16% 24%, rgba(201,161,67,.18), transparent 24%),
        radial-gradient(circle at 84% 76%, rgba(240,6,85,.18), transparent 26%),
        linear-gradient(135deg,var(--navy-2),var(--navy))!important;
    box-shadow:inset 0 0 30px rgba(0,0,0,.20),0 10px 24px rgba(6,43,79,.18)!important;
}

.st-key-pitch_abs_area [class*="st-key-pitchpos_"] button{
    background:rgba(255,255,255,.97)!important;
    color:var(--navy)!important;
    border:1px solid rgba(201,161,67,.46)!important;
    box-shadow:0 7px 15px rgba(6,43,79,.18)!important;
}

.st-key-pitch_abs_area [class*="st-key-pitchpos_"] button:hover{
    border-color:var(--pink)!important;
    color:var(--pink)!important;
    box-shadow:0 0 0 3px rgba(240,6,85,.12),0 8px 18px rgba(6,43,79,.20)!important;
}

.st-key-pitch_abs_area [class*="st-key-pitchpos_"] button[kind="primary"],
.st-key-pitch_abs_area [class*="st-key-pitchpos_"] button[data-testid="baseButton-primary"]{
    background:linear-gradient(135deg,var(--pink),var(--pink-dark))!important;
    color:#fff!important;
    border-color:rgba(255,255,255,.95)!important;
    box-shadow:0 0 0 3px rgba(240,6,85,.18),0 0 16px rgba(240,6,85,.48)!important;
}

.candidate-card,
.score-card,
.stat-card,
.metric-strip-card{
    border-radius:18px!important;
    border:1px solid rgba(6,43,79,.12)!important;
    background:linear-gradient(180deg,#ffffff 0%,#f8fafc 100%)!important;
    box-shadow:0 10px 26px rgba(6,43,79,.07)!important;
}

.avatar-placeholder{
    background:
        radial-gradient(circle at 75% 24%, rgba(201,161,67,.90) 0 5px, transparent 6px),
        linear-gradient(135deg,var(--navy-2),var(--navy))!important;
    border:1px solid rgba(201,161,67,.42)!important;
    color:#fff!important;
}

.position-pill,
.shortlist-pill{
    border:1px solid rgba(240,6,85,.28)!important;
    background:rgba(240,6,85,.07)!important;
    color:var(--pink-dark)!important;
}

.big-score{
    color:var(--pink)!important;
}

.score-status,
.stat-value.accent{
    color:var(--gold-dark)!important;
}

.result-banner{
    border:1px solid rgba(201,161,67,.26)!important;
    background:linear-gradient(135deg,rgba(255,255,255,.96),rgba(244,230,180,.20))!important;
    box-shadow:0 8px 20px rgba(6,43,79,.055)!important;
}

.target-icon{
    background:rgba(201,161,67,.14)!important;
    border:1px solid rgba(201,161,67,.35)!important;
    color:var(--gold-dark)!important;
}

.result-text b{
    color:var(--pink)!important;
}

.shortlist-card{
    border:1px solid rgba(6,43,79,.12)!important;
    background:rgba(255,255,255,.97)!important;
    box-shadow:0 8px 20px rgba(6,43,79,.05)!important;
}

[class*="st-key-shortlist_card_"]:hover .shortlist-card{
    border-color:rgba(240,6,85,.30)!important;
    background:linear-gradient(180deg,#ffffff 0%,#fbf7fa 100%)!important;
    box-shadow:0 12px 26px rgba(6,43,79,.08)!important;
}

.shortlist-card.selected{
    border-color:rgba(240,6,85,.58)!important;
    background:linear-gradient(135deg,rgba(240,6,85,.06),rgba(255,255,255,.98))!important;
    box-shadow:0 0 0 3px rgba(240,6,85,.10),0 10px 24px rgba(6,43,79,.07)!important;
}

.shortlist-rank{
    background:rgba(201,161,67,.16)!important;
    color:var(--gold-dark)!important;
}

.shortlist-score-fill{
    background:linear-gradient(90deg,var(--pink),var(--gold))!important;
}

.start-guide{
    border:1px solid rgba(201,161,67,.32)!important;
    background:
        radial-gradient(circle at 8% 16%, rgba(240,6,85,.13), transparent 28%),
        radial-gradient(circle at 92% 20%, rgba(201,161,67,.16), transparent 24%),
        linear-gradient(135deg,#ffffff,#f8fafc)!important;
    box-shadow:0 12px 28px rgba(6,43,79,.07)!important;
}

.start-guide-chip b,
.section-title,
.candidate-name,
.shortlist-player-name{
    color:var(--navy)!important;
}

.start-guide-step-num{
    background:rgba(240,6,85,.10)!important;
    color:var(--pink-dark)!important;
}

div[data-testid="stDataFrame"]{
    border:1px solid rgba(6,43,79,.12)!important;
}

.footer-note{
    color:var(--muted)!important;
}
</style>
"""
st.markdown(BRAND_CSS, unsafe_allow_html=True)

ENHANCED_THEME_CSS = """
<style>
:root{--app-bg-1:#07192b!important;--app-bg-2:#0a2343!important;--app-bg-3:#11192a!important;}
.stApp{
    background:
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='320' height='320' viewBox='0 0 320 320'><g fill='none' stroke='%23ffffff' stroke-opacity='.055' stroke-width='2'><rect x='38' y='95' width='244' height='130' rx='10'/><line x1='160' y1='95' x2='160' y2='225'/><circle cx='160' cy='160' r='26'/><path d='M38 125 h32 v70 h-32'/><path d='M282 125 h-32 v70 h32'/><path d='M26 140 h22 v40 h-22'/><path d='M294 140 h-22 v40 h22'/><path d='M72 60 L120 104 L170 82 L210 130 L258 108'/><circle cx='72' cy='60' r='4' fill='%23ffffff' fill-opacity='.07'/><circle cx='120' cy='104' r='4' fill='%23ffffff' fill-opacity='.07'/><circle cx='170' cy='82' r='4' fill='%23ffffff' fill-opacity='.07'/><circle cx='210' cy='130' r='4' fill='%23ffffff' fill-opacity='.07'/><circle cx='258' cy='108' r='4' fill='%23ffffff' fill-opacity='.07'/></g></svg>"),
        radial-gradient(circle at 8% 14%, rgba(240,6,85,.14) 0, rgba(240,6,85,0) 22%),
        radial-gradient(circle at 88% 8%, rgba(201,161,67,.15) 0, rgba(201,161,67,0) 20%),
        radial-gradient(circle at 90% 88%, rgba(255,255,255,.04) 0, rgba(255,255,255,0) 18%),
        linear-gradient(135deg,var(--app-bg-1) 0%, var(--app-bg-2) 52%, var(--app-bg-3) 100%)!important;
    background-size:320px 320px, auto, auto, auto, auto!important;
    background-attachment:fixed!important;
}
.stApp:before{
    border-color:rgba(240,6,85,.10)!important;
    width:420px!important;
    height:420px!important;
    right:-170px!important;
    top:110px!important;
}
.stApp:after{
    border-color:rgba(201,161,67,.12)!important;
}
.st-key-config_panel [data-testid="stVerticalBlockBorderWrapper"],
.st-key-pitch_panel [data-testid="stVerticalBlockBorderWrapper"],
.st-key-pref_panel [data-testid="stVerticalBlockBorderWrapper"],
.st-key-config_panel[data-testid="stVerticalBlockBorderWrapper"],
.st-key-pitch_panel[data-testid="stVerticalBlockBorderWrapper"],
.st-key-pref_panel[data-testid="stVerticalBlockBorderWrapper"],
.candidate-card,.score-card,.stat-card,.metric-strip-card,.shortlist-card,.start-guide{
    background:linear-gradient(180deg,rgba(255,255,255,.97),rgba(248,250,252,.95))!important;
    backdrop-filter:blur(8px)!important;
}
.section-title,.result-title,.sf-panel-title,.candidate-name,.shortlist-player-name,.stat-value,.metric-strip-value{color:var(--navy)!important;}
.footer-note,.section-subtitle,.result-text,.candidate-meta,.sf-subtitle,.mini-label,.shortlist-player-sub,.shortlist-label,.score-label,.stat-label{color:#d9dfec!important;}
.candidate-card .mini-label,.score-card .score-label,.stat-card .stat-label,.shortlist-label,.candidate-meta,.shortlist-player-sub,.section-subtitle,.result-text,.footer-note,.metric-strip-label{color:var(--muted)!important;}
.prototype-context-card{
    border-radius:18px;
    border:1px solid rgba(201,161,67,.26);
    background:linear-gradient(135deg,rgba(255,255,255,.96),rgba(244,230,180,.12));
    box-shadow:0 10px 26px rgba(6,43,79,.08);
    padding:.84rem .95rem;
    margin:.10rem 0 .45rem 0;
}
.prototype-context-title{font-size:.98rem;font-weight:950;color:var(--navy);margin-bottom:.18rem;}
.prototype-context-text{font-size:.82rem;line-height:1.35;color:var(--muted);}
.prototype-chip-row{display:flex;flex-wrap:wrap;gap:.42rem;margin-top:.55rem;}
.prototype-chip{display:inline-flex;align-items:center;gap:.34rem;padding:.34rem .52rem;border-radius:999px;background:rgba(255,255,255,.90);border:1px solid rgba(6,43,79,.10);font-size:.74rem;font-weight:850;color:var(--navy);}
.prototype-chip b{color:var(--pink);font-weight:950;}
.detail-hero{border-radius:18px;border:1px solid rgba(201,161,67,.26);background:linear-gradient(135deg,rgba(255,255,255,.98),rgba(244,230,180,.14));box-shadow:0 10px 26px rgba(6,43,79,.08);padding:.92rem 1rem;margin:.10rem 0 .6rem 0;}
.detail-hero-top{display:flex;align-items:center;gap:.78rem;justify-content:space-between;flex-wrap:wrap;}
.detail-identity{display:flex;align-items:center;gap:.72rem;}
.detail-avatar{width:58px;height:58px;border-radius:999px;display:grid;place-items:center;background:linear-gradient(135deg,var(--navy-2),var(--navy));color:#fff;border:1px solid rgba(201,161,67,.44);font-weight:950;font-size:1.08rem;box-shadow:0 8px 18px rgba(6,43,79,.18);}
.detail-name{font-size:1.22rem;font-weight:950;color:var(--navy);line-height:1.02;}
.detail-sub{font-size:.84rem;color:var(--muted);margin-top:.14rem;}
.detail-badges{display:flex;flex-wrap:wrap;gap:.4rem;justify-content:flex-end;}
.detail-badge{display:inline-flex;align-items:center;gap:.28rem;padding:.36rem .56rem;border-radius:999px;font-size:.75rem;font-weight:900;border:1px solid rgba(6,43,79,.10);background:rgba(255,255,255,.92);color:var(--navy);}
.detail-badge.strong{border-color:rgba(240,6,85,.22);background:rgba(240,6,85,.08);color:var(--pink-dark);}
.detail-badge.gold{border-color:rgba(201,161,67,.28);background:rgba(201,161,67,.12);color:var(--gold-dark);}
.detail-hero-summary{margin-top:.65rem;font-size:.86rem;color:var(--muted);line-height:1.36;}
.detail-kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.55rem;margin:.15rem 0 .35rem 0;}
.detail-kpi{border-radius:16px;border:1px solid rgba(6,43,79,.10);background:rgba(255,255,255,.92);padding:.62rem .64rem;box-shadow:0 8px 18px rgba(6,43,79,.05);}
.detail-kpi-label{font-size:.68rem;font-weight:850;line-height:1.1;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);}
.detail-kpi-value{font-size:1.18rem;font-weight:950;color:var(--navy);margin-top:.18rem;line-height:1.05;}
.detail-kpi-sub{font-size:.76rem;color:var(--muted);margin-top:.18rem;line-height:1.16;}
.detail-diagnosis{border-radius:16px;border:1px solid rgba(201,161,67,.24);background:linear-gradient(135deg,rgba(255,255,255,.96),rgba(244,230,180,.16));padding:.78rem .82rem;box-shadow:0 8px 20px rgba(6,43,79,.05);}
.detail-section-title{font-size:.90rem;font-weight:950;color:var(--navy);margin-bottom:.2rem;}
.detail-section-text{font-size:.83rem;color:var(--muted);line-height:1.38;}
.detail-block-stack{display:flex;flex-direction:column;gap:.48rem;margin-top:.12rem;}
.detail-block-card{border-radius:16px;border:1px solid rgba(6,43,79,.10);background:rgba(255,255,255,.95);padding:.72rem .78rem;box-shadow:0 8px 18px rgba(6,43,79,.05);}
.detail-block-card.positive{border-color:rgba(201,161,67,.30);background:linear-gradient(135deg,rgba(255,255,255,.98),rgba(244,230,180,.14));}
.detail-block-card.warning{border-color:rgba(240,6,85,.22);background:linear-gradient(135deg,rgba(255,255,255,.98),rgba(240,6,85,.06));}
.detail-block-head{display:flex;align-items:flex-start;justify-content:space-between;gap:.6rem;}
.detail-block-name{font-size:.90rem;font-weight:950;color:var(--navy);line-height:1.1;}
.detail-block-reading{font-size:.75rem;color:var(--muted);margin-top:.12rem;line-height:1.18;}
.detail-block-score{font-size:1.02rem;font-weight:950;color:var(--navy);}
.detail-progress{height:8px;border-radius:999px;background:#e7eef6;overflow:hidden;margin-top:.52rem;}
.detail-progress-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,var(--pink),var(--gold));}
.detail-pill{display:inline-flex;align-items:center;padding:.28rem .45rem;border-radius:999px;font-size:.70rem;font-weight:900;}
.detail-pill.ok{background:rgba(201,161,67,.14);color:var(--gold-dark);}
.detail-pill.review{background:rgba(240,6,85,.10);color:var(--pink-dark);}
.preference-card{border-radius:16px;border:1px solid rgba(6,43,79,.10);background:rgba(255,255,255,.94);padding:.75rem .82rem;box-shadow:0 8px 18px rgba(6,43,79,.05);}
.preference-impact-number{font-size:1.55rem;font-weight:950;color:var(--pink);line-height:1;}
.preference-impact-caption{font-size:.77rem;color:var(--muted);margin-top:.15rem;}
.preference-item{display:flex;align-items:flex-start;justify-content:space-between;gap:.6rem;padding:.46rem 0;border-bottom:1px solid rgba(6,43,79,.08);}
.preference-item:last-child{border-bottom:none;padding-bottom:0;}
.preference-name{font-size:.80rem;font-weight:900;color:var(--navy);}
.preference-target{font-size:.73rem;color:var(--muted);margin-top:.08rem;}
.preference-value{font-size:.78rem;font-weight:850;color:var(--navy);text-align:right;}
.preference-status{display:inline-flex;align-items:center;padding:.24rem .42rem;border-radius:999px;font-size:.68rem;font-weight:900;white-space:nowrap;}
.preference-status.ok{background:rgba(201,161,67,.15);color:var(--gold-dark);}
.preference-status.bad{background:rgba(240,6,85,.10);color:var(--pink-dark);}
.preference-status.neutral{background:rgba(6,43,79,.08);color:var(--navy);}
@media(max-width:1100px){.detail-kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr));}}
</style>
"""
st.markdown(ENHANCED_THEME_CSS, unsafe_allow_html=True)
CONTRAST_FIX_CSS = """
<style>
/* ===== Corrección de contraste sobre fondo oscuro ===== */

/* Título principal: Scout en blanco, Fit en rosado */
.sf-title-navy{
    color:#ffffff!important;
}

.sf-title-pink{
    color:var(--pink)!important;
}

.sf-subtitle{
    color:rgba(255,255,255,.88)!important;
}

/* Títulos y subtítulos de paneles superiores */
.st-key-config_panel .sf-panel-title,
.st-key-pref_panel .sf-panel-title,
.st-key-pitch_panel .sf-panel-title{
    color:#ffffff!important;
}

.st-key-config_panel .sf-panel-subtitle,
.st-key-pref_panel .sf-panel-subtitle,
.st-key-pitch_panel .sf-panel-subtitle{
    color:rgba(255,255,255,.72)!important;
}

/* Labels de parámetros: Club, formación, pie, altura, presupuesto */
.st-key-config_panel [data-testid="stWidgetLabel"],
.st-key-pref_panel [data-testid="stWidgetLabel"],
.st-key-config_panel [data-testid="stWidgetLabel"] p,
.st-key-pref_panel [data-testid="stWidgetLabel"] p,
.st-key-config_panel label,
.st-key-pref_panel label,
.st-key-config_panel label p,
.st-key-pref_panel label p{
    color:rgba(255,255,255,.86)!important;
    font-weight:800!important;
}

/* Texto de checkboxes: excluir jugadores / aplicar preferencias */
.st-key-config_panel .stCheckbox,
.st-key-pref_panel .stCheckbox,
.st-key-config_panel .stCheckbox label,
.st-key-pref_panel .stCheckbox label,
.st-key-config_panel .stCheckbox label p,
.st-key-pref_panel .stCheckbox label p,
.st-key-config_panel .stCheckbox span,
.st-key-pref_panel .stCheckbox span{
    color:rgba(255,255,255,.86)!important;
}

/* Textos dentro de botones principales */
.st-key-config_panel div[data-testid="stButton"] button,
.st-key-config_panel div[data-testid="stButton"] button p,
.st-key-config_panel div[data-testid="stButton"] button span{
    color:#ffffff!important;
}

/* Título de la shortlist sobre fondo oscuro */
.section-title{
    color:#ffffff!important;
}

.section-subtitle{
    color:rgba(255,255,255,.72)!important;
}

/* Botón de descarga */
.stDownloadButton button,
.stDownloadButton button p,
.stDownloadButton button span{
    color:var(--navy)!important;
}

/* Footer sobre fondo oscuro */
.footer-note{
    color:rgba(255,255,255,.62)!important;
}
</style>
"""
st.markdown(CONTRAST_FIX_CSS, unsafe_allow_html=True)
def load_logo_data_uri(path: str | None = None) -> str:
    """Carga el logo local si existe. Si no existe, usa el logo embebido dentro de la app."""
    candidate_paths = []
    if path:
        candidate_paths.append(path)
    candidate_paths.extend([
        "assets/scoutfit_logo.png",
        "assets/scoutfit_logo.jpg",
        "assets/scoutfit_logo.webp",
        "scoutfit_logo.png",
        "scoutfit_logo.jpg",
        "scoutfit_logo.webp",
        "logo.png",
        "logo.jpg",
        "logo.webp",
    ])

    for candidate in candidate_paths:
        logo_path = Path(candidate)
        if not logo_path.exists():
            continue
        mime = "image/png"
        if logo_path.suffix.lower() in {".jpg", ".jpeg"}:
            mime = "image/jpeg"
        elif logo_path.suffix.lower() == ".webp":
            mime = "image/webp"
        encoded = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
        return f"data:{mime};base64,{encoded}"
    return EMBEDDED_LOGO_DATA_URI or ""

# Placeholder global para inyectar coordenadas dinámicas sin meter un elemento invisible dentro del panel de la cancha.
pitch_coord_css_anchor = st.empty()

@st.cache_resource(show_spinner=False)
def get_engine():
    return TacticalCompatibilityEngine()

engine = get_engine()

PROTOTYPE_SOURCE = "slot_app_ready"
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
# ======================================================
# COORDENADAS DE CANCHA POR FORMACIÓN
# x = avance horizontal: 0 defensa propia, 100 ataque
# y = carril vertical: 0 izquierda, 100 derecha
# ======================================================

GENERIC_SLOT_COORDS = {
    "GK": (7, 50),

    "DL": (25, 20),
    "DC": (25, 50),
    "DC_1": (25, 35),
    "DC_2": (25, 50),
    "DC_3": (25, 65),
    "DR": (25, 80),

    "DMC": (42, 50),
    "DMC_1": (43, 42),
    "DMC_2": (43, 58),

    "LWM": (55, 18),
    "MC": (55, 50),
    "MC_1": (55, 34),
    "MC_2": (55, 50),
    "MC_3": (55, 66),
    "RWM": (55, 82),

    "AMC": (70, 50),
    "AMC_1": (70, 42),
    "AMC_2": (70, 58),

    "LAW": (82, 18),
    "FW": (91, 50),
    "FW_1": (89, 42),
    "FW_2": (89, 58),
    "RAW": (82, 82),
}


FORMATION_SLOT_COORDS = {
    "3-2-4-1": {
        "GK": (7, 50),

        "DC_1": (25, 30),
        "DC_2": (25, 50),
        "DC_3": (25, 70),

        "DMC_1": (43, 42),
        "DMC_2": (43, 58),

        "LAW": (70, 18),
        "AMC_1": (70, 42),
        "AMC_2": (70, 58),
        "RAW": (70, 82),

        "FW": (91, 50),
    },

    "3-4-2-1": {
        "GK": (7, 50),

        "DC_1": (25, 30),
        "DC_2": (25, 50),
        "DC_3": (25, 70),

        "LWM": (50, 18),
        "MC_1": (50, 42),
        "MC_2": (50, 58),
        "RWM": (50, 82),

        "AMC_1": (70, 42),
        "AMC_2": (70, 58),

        "FW": (91, 50),
    },

    "3-4-3": {
        "GK": (7, 50),

        "DC_1": (25, 30),
        "DC_2": (25, 50),
        "DC_3": (25, 70),

        "LWM": (50, 18),
        "MC_1": (50, 42),
        "MC_2": (50, 58),
        "RWM": (50, 82),

        "LAW": (82, 18),
        "FW": (82, 50),
        "RAW": (82, 82),
    },

"3-5-2": {
    "GK": (7, 50),

    # Línea de 3 centrales
    "DC_1": (25, 30),
    "DC_2": (25, 50),
    "DC_3": (25, 70),

    # Línea de 5 mediocampistas / carrileros
    # Todos quedan en la misma X, pero con más separación en Y
    "LWM": (55, 12),
    "DMC": (55, 48),
    "MC_1": (55, 30),
    "MC_2": (55, 66),
    "MC_3": (55, 48),
    "RWM": (55, 88),

    # Si alguna versión de 3-5-2 trae AMC, se adelanta un poco
    # para no montarse sobre los MC.
    "AMC": (70, 50),

    # Línea de 2 delanteros
    "FW_1": (89, 42),
    "FW_2": (89, 58),

    # Fallback por si aparece FW en vez de FW_1/FW_2
    "FW": (89, 50),
},

    "4-1-2-1-2": {
        "GK": (7, 50),

        "DL": (25, 20),
        "DC_1": (25, 42),
        "DC_2": (25, 58),
        "DR": (25, 80),

        "DMC": (42, 50),

        "MC_1": (56, 40),
        "MC_2": (56, 60),

        "AMC": (70, 50),

        "FW_1": (89, 42),
        "FW_2": (89, 58),
    },

    "4-1-4-1": {
        "GK": (7, 50),

        "DL": (25, 20),
        "DC_1": (25, 42),
        "DC_2": (25, 58),
        "DR": (25, 80),

        "DMC": (42, 50),

        "LWM": (62, 18),
        "MC_1": (62, 42),
        "MC_2": (62, 58),
        "RWM": (62, 82),

        "FW": (91, 50),
    },

    "4-2-2-2": {
        "GK": (7, 50),

        "DL": (25, 20),
        "DC_1": (25, 42),
        "DC_2": (25, 58),
        "DR": (25, 80),

        "DMC_1": (44, 42),
        "DMC_2": (44, 58),

        "AMC_1": (68, 42),
        "AMC_2": (68, 58),

        "FW_1": (89, 42),
        "FW_2": (89, 58),
    },

    "4-2-3-1": {
        "GK": (7, 50),

        "DL": (25, 20),
        "DC_1": (25, 42),
        "DC_2": (25, 58),
        "DR": (25, 80),

        "DMC_1": (43, 42),
        "DMC_2": (43, 58),

        "LAW": (70, 18),
        "AMC": (70, 50),
        "RAW": (70, 82),

        "FW": (91, 50),
    },

    "4-3-1-2": {
        "GK": (7, 50),

        "DL": (25, 20),
        "DC_1": (25, 42),
        "DC_2": (25, 58),
        "DR": (25, 80),

        "MC_1": (57, 34),
        "MC_2": (57, 50),
        "MC_3": (57, 66),

        "AMC": (70, 50),

        "FW_1": (89, 42),
        "FW_2": (89, 58),
    },

    "4-3-3": {
        "GK": (7, 50),

        "DL": (25, 20),
        "DC_1": (25, 42),
        "DC_2": (25, 58),
        "DR": (25, 80),

        "MC_1": (57, 34),
        "MC_2": (57, 50),
        "MC_3": (57, 66),

        "LAW": (82, 18),
        "FW": (82, 50),
        "RAW": (82, 82),
    },

    "4-4-1-1": {
        "GK": (7, 50),

        "DL": (25, 20),
        "DC_1": (25, 42),
        "DC_2": (25, 58),
        "DR": (25, 80),

        "LWM": (55, 18),
        "MC_1": (55, 42),
        "MC_2": (55, 58),
        "RWM": (55, 82),

        "AMC": (72, 50),

        "FW": (91, 50),
    },

    "4-4-2": {
        "GK": (7, 50),

        "DL": (25, 20),
        "DC_1": (25, 42),
        "DC_2": (25, 58),
        "DR": (25, 80),

        "LWM": (55, 18),
        "MC_1": (55, 42),
        "MC_2": (55, 58),
        "RWM": (55, 82),

        "FW_1": (89, 42),
        "FW_2": (89, 58),
    },

    "4-5-1": {
        "GK": (7, 50),

        "DL": (25, 20),
        "DC_1": (25, 42),
        "DC_2": (25, 58),
        "DR": (25, 80),

        "LWM": (56, 16),
        "MC_1": (56, 36),
        "MC_2": (56, 50),
        "MC_3": (56, 64),
        "RWM": (56, 84),

        "FW": (91, 50),
    },

    "5-3-2": {
        "GK": (7, 50),

        "DL": (25, 16),
        "DC_1": (25, 34),
        "DC_2": (25, 50),
        "DC_3": (25, 66),
        "DR": (25, 84),

        "MC_1": (58, 36),
        "MC_2": (58, 50),
        "MC_3": (58, 64),

        "FW_1": (89, 42),
        "FW_2": (89, 58),
    },

    "5-4-1": {
        "GK": (7, 50),

        "DL": (25, 16),
        "DC_1": (25, 34),
        "DC_2": (25, 50),
        "DC_3": (25, 66),
        "DR": (25, 84),

        "LWM": (58, 18),
        "MC_1": (58, 42),
        "MC_2": (58, 58),
        "RWM": (58, 82),

        "FW": (91, 50),
    },
}
def inject_pitch_coords_css(formation_final: str, available_positions: list[str]) -> None:
    coords = FORMATION_SLOT_COORDS.get(str(formation_final), GENERIC_SLOT_COORDS)

    css_lines = ["<style>"]

    for pos in available_positions:
        pos = str(pos)
        x, y = coords.get(pos, GENERIC_SLOT_COORDS.get(pos, (50, 50)))
        css_lines.append(
            f".st-key-pitchpos_{pos}"
            "{"
            f"left:{x}%!important;"
            f"top:{y}%!important;"
            "}"
        )

    css_lines.append("</style>")
    css_text = "\n".join(css_lines)
    target = globals().get("pitch_coord_css_anchor", None)
    if target is not None:
        target.markdown(css_text, unsafe_allow_html=True)
    else:
        st.markdown(css_text, unsafe_allow_html=True)
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

def format_age(value: Any) -> str:
    numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric_value):
        return "No disponible"
    return f"{int(round(float(numeric_value)))} años"

def _local_image_to_data_uri(path_value: Any) -> str:
    if pd.isna(path_value):
        return ""
    raw = str(path_value).strip()
    if not raw or raw.lower() in {"nan", "none", "null"}:
        return ""

    raw_path = Path(raw)
    candidates = [raw_path]
    if not raw_path.is_absolute():
        candidates.extend([
            Path.cwd() / raw,
            Path(__file__).resolve().parent / raw,
        ])

    for candidate in candidates:
        try:
            if candidate.exists() and candidate.is_file():
                suffix = candidate.suffix.lower()
                mime = "image/png"
                if suffix in {".jpg", ".jpeg"}:
                    mime = "image/jpeg"
                elif suffix == ".webp":
                    mime = "image/webp"
                encoded = base64.b64encode(candidate.read_bytes()).decode("utf-8")
                return f"data:{mime};base64,{encoded}"
        except Exception:
            continue
    return ""

def player_photo_src(row: pd.Series | dict[str, Any] | None) -> str:
    if row is None:
        return ""

    for col in ["photo_path", "Foto", "player_photo_path"]:
        try:
            value = row.get(col, pd.NA)
        except AttributeError:
            value = pd.NA
        src = _local_image_to_data_uri(value)
        if src:
            return src

    for col in ["photo_url", "Foto URL", "image_url"]:
        try:
            value = row.get(col, pd.NA)
        except AttributeError:
            value = pd.NA
        if pd.notna(value):
            raw = str(value).strip()
            if raw.lower().startswith(("http://", "https://")):
                return raw
    return ""

def avatar_html(player_name: str, row: pd.Series | dict[str, Any] | None = None, class_name: str = "avatar-placeholder") -> str:
    src = player_photo_src(row)
    alt = html.escape(str(player_name), quote=True)
    if src:
        return f'<img src="{html.escape(src, quote=True)}" class="{html.escape(class_name)}" alt="{alt}">'
    return f'<div class="{html.escape(class_name)}">{html.escape(player_initials(player_name))}</div>'

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

    required = [
        player_col,
        "event_team_name",
        "merged_pos",
        "age",
        "player_valuation",
        "foot",
        "height",
        "photo_path",
        "photo_url",
        "final_scouting_score_0_100",
    ]
    available = [col for col in required if col in df.columns]
    out = df[available].copy()
    out = out.rename(
        columns={
            player_col: "Jugador",
            "event_team_name": "Club",
            "merged_pos": "Grupo posicional",
            "age": "Edad",
            "player_valuation": "Valor de mercado",
            "foot": "Pie",
            "height": "Altura",
            "photo_path": "Foto",
            "photo_url": "Foto URL",
            "final_scouting_score_0_100": "Score final",
        }
    )

    if "Grupo posicional" in out.columns:
        out["Grupo posicional"] = out["Grupo posicional"].map(format_group_pos)
    if "Edad" in out.columns:
        out["Edad"] = out["Edad"].map(format_age)
    if "Pie" in out.columns:
        out["Pie"] = out["Pie"].map(format_foot)
    if "Altura" in out.columns:
        out["Altura"] = out["Altura"].map(format_height)
    if "Valor de mercado" in out.columns:
        out["Valor de mercado"] = out["Valor de mercado"].map(money_short)
    if "Score final" in out.columns:
        out["Score final"] = pd.to_numeric(out["Score final"], errors="coerce").round(1)

    final_order = [
        "Jugador",
        "Club",
        "Foto",
        "Foto URL",
        "Grupo posicional",
        "Edad",
        "Valor de mercado",
        "Pie",
        "Altura",
        "Score final",
    ]
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


def tactical_diagnosis_text(readable_blocks: pd.DataFrame) -> str:
    if readable_blocks.empty:
        return "No fue posible construir un diagnóstico táctico para este jugador con la información disponible."
    ranked = readable_blocks.copy()
    ranked["Ajuste"] = pd.to_numeric(ranked["Ajuste"], errors="coerce")
    ranked = ranked.dropna(subset=["Ajuste"]).sort_values("Ajuste", ascending=False)
    if ranked.empty:
        return "No fue posible construir un diagnóstico táctico para este jugador con la información disponible."
    top_areas = ranked.head(2)["Área"].tolist()
    low_areas = ranked.sort_values("Ajuste", ascending=True).head(2)["Área"].tolist()
    mean_score = ranked["Ajuste"].mean()
    if mean_score >= 82:
        overall = "El ajuste global frente al prototipo del club es alto"
    elif mean_score >= 72:
        overall = "El ajuste global frente al prototipo del club es competitivo"
    else:
        overall = "El ajuste global frente al prototipo del club requiere revisión"
    strengths = ", ".join(top_areas) if top_areas else "las áreas principales"
    concerns = ", ".join(low_areas) if low_areas else "algunas áreas secundarias"
    return (
        f"{overall}. El jugador destaca especialmente en {strengths}. "
        f"Las mayores diferencias con el perfil buscado aparecen en {concerns}. "
        f"Esto sugiere que su encaje puede ser más inmediato en las fases donde domina sus fortalezas, "
        f"mientras que las áreas más débiles deberían revisarse antes de una decisión final."
    )


def get_score_bucket(score: float | None) -> str:
    if score is None:
        return "Sin calificación"
    if score >= 85:
        return "Ajuste élite"
    if score >= 75:
        return "Ajuste alto"
    if score >= 65:
        return "Ajuste medio"
    return "Ajuste en revisión"


def infer_decision_profile(final_score: float | None, impact_delta: float | None, preference_rows: list[dict[str, str]]) -> str:
    fails = sum(1 for row in preference_rows if row.get("status_key") == "bad")
    if final_score is None:
        return "Perfil no concluyente"
    if final_score >= 85 and fails == 0:
        return "Prioridad alta"
    if final_score >= 75 and fails <= 1:
        return "Seguimiento recomendado"
    if final_score >= 65:
        return "Apuesta contextual"
    return "Revisión profunda"


def build_preference_rows(selected_row: pd.Series) -> tuple[list[dict[str, str]], float | None]:
    rows: list[dict[str, str]] = []
    preferred_foot = st.session_state.get("applied_preferred_foot")
    min_height = st.session_state.get("applied_min_height")
    max_value_target = st.session_state.get("applied_max_value_target")
    min_age = st.session_state.get("applied_min_age")
    max_age = st.session_state.get("applied_max_age")

    selected_score = safe_score(selected_row.get("final_scouting_score_0_100"))
    base_score = safe_score(selected_row.get(SCORE_METHOD))
    impact_delta = None
    if selected_score is not None and base_score is not None:
        impact_delta = round(selected_score - base_score, 1)

    player_foot_raw = str(selected_row.get("foot", "")).strip().lower()
    player_foot_text = format_foot(selected_row.get("foot", pd.NA))
    if preferred_foot:
        foot_ok = player_foot_raw == str(preferred_foot).lower() or player_foot_raw == "both"
        rows.append({
            "criterion": "Pie dominante",
            "target": FOOT_LABELS.get(str(preferred_foot).lower(), str(preferred_foot)),
            "actual": player_foot_text,
            "status": "Cumple" if foot_ok else "No cumple",
            "status_key": "ok" if foot_ok else "bad",
        })

    actual_height = pd.to_numeric(pd.Series([selected_row.get("height", pd.NA)]), errors="coerce").iloc[0]
    if min_height is not None:
        height_ok = pd.notna(actual_height) and float(actual_height) >= float(min_height)
        rows.append({
            "criterion": "Altura mínima",
            "target": f"{float(min_height):.2f} m",
            "actual": format_height(actual_height),
            "status": "Cumple" if height_ok else "No cumple",
            "status_key": "ok" if height_ok else "bad",
        })

    actual_value = pd.to_numeric(pd.Series([selected_row.get("player_valuation", pd.NA)]), errors="coerce").iloc[0]
    if max_value_target is not None:
        value_ok = pd.notna(actual_value) and float(actual_value) <= float(max_value_target)
        rows.append({
            "criterion": "Presupuesto máximo",
            "target": money_short(max_value_target),
            "actual": money_short(actual_value),
            "status": "Dentro del presupuesto" if value_ok else "Supera el presupuesto",
            "status_key": "ok" if value_ok else "bad",
        })

    actual_age = pd.to_numeric(pd.Series([selected_row.get("age", pd.NA)]), errors="coerce").iloc[0]
    if min_age is not None and max_age is not None:
        age_ok = pd.notna(actual_age) and float(min_age) <= float(actual_age) <= float(max_age)
        gap = 0.0
        if pd.notna(actual_age):
            if float(actual_age) < float(min_age):
                gap = float(min_age) - float(actual_age)
            elif float(actual_age) > float(max_age):
                gap = float(actual_age) - float(max_age)

        if age_ok:
            age_status = "Cumple"
            status_key = "ok"
        elif gap >= 5:
            age_status = "Penalización fuerte"
            status_key = "bad"
        else:
            age_status = "Penalización leve"
            status_key = "neutral"

        rows.append({
            "criterion": "Rango de edad",
            "target": f"{int(min_age)}-{int(max_age)} años",
            "actual": format_age(actual_age),
            "status": age_status,
            "status_key": status_key,
        })

    if not rows:
        rows.append({
            "criterion": "Preferencias de scouting",
            "target": "No activadas",
            "actual": "Score final igual al score táctico",
            "status": "Sin restricciones",
            "status_key": "neutral",
        })

    return rows, impact_delta


def detail_metric_card(label: str, value: str, subtitle: str = "") -> str:
    return (
        f'<div class="detail-kpi">'
        f'<div class="detail-kpi-label">{html.escape(label)}</div>'
        f'<div class="detail-kpi-value">{html.escape(value)}</div>'
        f'<div class="detail-kpi-sub">{html.escape(subtitle)}</div>'
        f'</div>'
    )


def detail_block_card(area: str, score: Any, lectura: str, tone: str = "positive") -> str:
    numeric_score = pd.to_numeric(pd.Series([score]), errors="coerce").iloc[0]
    score_text = "NA" if pd.isna(numeric_score) else f"{float(numeric_score):.1f}"
    width = 0 if pd.isna(numeric_score) else max(0, min(100, float(numeric_score)))
    pill_class = "ok" if tone == "positive" else "review"
    pill_text = "Fortaleza" if tone == "positive" else "A revisar"
    return (
        f'<div class="detail-block-card {tone}">'
        f'  <div class="detail-block-head">'
        f'    <div>'
        f'      <div class="detail-block-name">{html.escape(str(area))}</div>'
        f'      <div class="detail-block-reading">{html.escape(str(lectura))}</div>'
        f'    </div>'
        f'    <div style="text-align:right">'
        f'      <div class="detail-block-score">{html.escape(score_text)}</div>'
        f'      <div class="detail-pill {pill_class}">{pill_text}</div>'
        f'    </div>'
        f'  </div>'
        f'  <div class="detail-progress"><div class="detail-progress-fill" style="width:{width:.1f}%"></div></div>'
        f'</div>'
    )


def get_inferred_base_position(proto_df: pd.DataFrame, team_name: str, formation_final: str, ui_slot: str) -> str | None:
    preview = proto_df.copy()
    if "event_team_name" in preview.columns:
        preview = preview[preview["event_team_name"].astype(str) == str(team_name)].copy()
    if "formation_final" in preview.columns:
        preview = preview[preview["formation_final"].astype(str) == str(formation_final)].copy()
    slot_col = "ui_slot" if "ui_slot" in preview.columns else ("slot_id" if "slot_id" in preview.columns else None)
    if slot_col is not None:
        preview = preview[preview[slot_col].astype(str) == str(ui_slot)].copy()
    if preview.empty:
        return None
    if "base_pos" in preview.columns and preview["base_pos"].notna().any():
        return str(preview["base_pos"].mode().iloc[0])
    return str(ui_slot)

def position_description(value: Any) -> str:
    if pd.isna(value):
        return ""
    raw = str(value).strip()
    if raw in {"LAW", "RAW", "LWM", "RWM"}:
        return {
            "LAW": "Atacante de banda izquierda",
            "RAW": "Atacante de banda derecha",
            "LWM": "Volante/carrilero izquierdo",
            "RWM": "Volante/carrilero derecho",
        }[raw]
    if "_" in raw:
        base, num = raw.rsplit("_", 1)
        base_desc = POSITION_DESCRIPTIONS.get(base, base)
        return f"{base_desc} {num}"
    return POSITION_DESCRIPTIONS.get(raw, "Slot táctico")

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
    st.session_state["pending_slot"] = str(pos)


def set_selected_candidate_idx(idx: int) -> None:
    st.session_state["selected_candidate_idx"] = int(idx)

def render_position_pitch(
    position_options: list[str],
    selected_position: str,
    formation_final: str,
) -> str:
    available_positions = [str(pos) for pos in position_options]
    available_set = set(available_positions)

    if selected_position not in available_set and available_positions:
        selected_position = available_positions[0]

    selected_position = str(st.session_state.get("pending_slot", selected_position))

    if selected_position not in available_set and available_positions:
        selected_position = available_positions[0]

    st.session_state["pending_slot"] = selected_position

    coords = FORMATION_SLOT_COORDS.get(str(formation_final), GENERIC_SLOT_COORDS)

    css_lines = [
        "<style>",
        """
        .st-key-pitch_abs_area{
            position:relative!important;
            width:96%!important;
            height:224px!important;
            min-height:224px!important;
            max-height:224px!important;
            margin:auto!important;
            padding:0!important;
            overflow:hidden!important;
            border-radius:13px!important;
            border:3px solid rgba(255,255,255,.96)!important;
            background:
                linear-gradient(90deg, transparent 49.72%, rgba(255,255,255,.86) 49.92%, rgba(255,255,255,.86) 50.08%, transparent 50.28%),
                radial-gradient(circle at 50% 50%, transparent 0 39px, rgba(255,255,255,.75) 40px 42px, transparent 43px),
                radial-gradient(circle at 16% 24%, rgba(201,161,67,.18), transparent 24%),
                radial-gradient(circle at 84% 76%, rgba(240,6,85,.18), transparent 26%),
                linear-gradient(135deg,var(--navy-2),var(--navy))!important;
            box-shadow:inset 0 0 30px rgba(0,0,0,.20),0 10px 24px rgba(6,43,79,.18)!important;
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

        .st-key-pitch_abs_area:before{
            left:0;
            border-left:0;
        }

        .st-key-pitch_abs_area:after{
            right:0;
            border-right:0;
        }

        .st-key-pitch_radio_selector{
            position:absolute!important;
            inset:0!important;
            width:100%!important;
            height:100%!important;
            margin:0!important;
            padding:0!important;
            z-index:5!important;
        }

        .st-key-pitch_radio_selector label,
        .st-key-pitch_radio_selector div,
        .st-key-pitch_radio_selector p{
            margin:0!important;
            padding:0!important;
        }

        .st-key-pitch_radio_selector div[role="radiogroup"]{
            position:absolute!important;
            inset:0!important;
            width:100%!important;
            height:100%!important;
        }

        .st-key-pitch_radio_selector div[role="radiogroup"] > label{
            position:absolute!important;
            z-index:10!important;
            transform:translate(-50%, -50%)!important;
            min-width:44px!important;
            height:28px!important;
            padding:0 .48rem!important;
            border-radius:8px!important;
            display:inline-flex!important;
            align-items:center!important;
            justify-content:center!important;
            background:rgba(255,255,255,.97)!important;
            color:var(--navy)!important;
            border:1px solid rgba(201,161,67,.46)!important;
            box-shadow:0 7px 15px rgba(6,43,79,.18)!important;
            cursor:pointer!important;
            transition:transform .12s ease, box-shadow .12s ease, border-color .12s ease, color .12s ease!important;
        }

        .st-key-pitch_radio_selector div[role="radiogroup"] > label:hover{
            transform:translate(-50%, -50%) translateY(-1px)!important;
            border-color:var(--pink)!important;
            color:var(--pink)!important;
            box-shadow:0 0 0 3px rgba(240,6,85,.12),0 8px 18px rgba(6,43,79,.20)!important;
        }

        .st-key-pitch_radio_selector div[role="radiogroup"] > label:has(input:checked){
            background:linear-gradient(135deg,var(--pink),var(--pink-dark))!important;
            color:#fff!important;
            border-color:rgba(255,255,255,.95)!important;
            box-shadow:0 0 0 3px rgba(240,6,85,.18),0 0 16px rgba(240,6,85,.48)!important;
        }

        .st-key-pitch_radio_selector div[role="radiogroup"] > label > div:first-child{
            display:none!important;
        }

        .st-key-pitch_radio_selector div[role="radiogroup"] > label p{
            font-size:.72rem!important;
            font-weight:950!important;
            line-height:1!important;
            color:inherit!important;
            white-space:nowrap!important;
        }
        """
    ]

    for i, pos in enumerate(available_positions, start=1):
        x, y = coords.get(pos, GENERIC_SLOT_COORDS.get(pos, (50, 50)))
        css_lines.append(
            f"""
            .st-key-pitch_radio_selector div[role="radiogroup"] > label:nth-child({i}){{
                left:{x}%!important;
                top:{y}%!important;
            }}
            """
        )

    css_lines.append("</style>")
    st.markdown("\n".join(css_lines), unsafe_allow_html=True)

    with keyed_container(border=False, key="pitch_abs_area"):
        selected_slot = st.radio(
            "Selecciona una posición",
            options=available_positions,
            index=available_positions.index(selected_position),
            format_func=format_group_pos,
            key="pitch_radio_selector",
            label_visibility="collapsed",
        )

    st.session_state["pending_slot"] = selected_slot

    return str(selected_slot)

def render_shortlist_dataframe(display_df: pd.DataFrame) -> list[int]:
    if display_df.empty:
        st.info("No hay candidatos disponibles para mostrar.")
        return []

    selected_idx = st.session_state.get("selected_candidate_idx", None)
    clicked_rows: list[int] = []

    for idx, row in display_df.reset_index(drop=True).iterrows():
        player = html.escape(str(row.get("Jugador", "Jugador no disponible")))
        club = html.escape(str(row.get("Club", "Club no disponible")))
        group = html.escape(str(row.get("Grupo posicional", "")))
        age = html.escape(str(row.get("Edad", "")))
        value = html.escape(str(row.get("Valor de mercado", "")))
        foot = html.escape(str(row.get("Pie", "")))
        height = html.escape(str(row.get("Altura", "")))
        avatar = avatar_html(str(row.get("Jugador", "Jugador no disponible")), row, "shortlist-avatar")

        score_value = pd.to_numeric(pd.Series([row.get("Score final", None)]), errors="coerce").iloc[0]
        score_text = "NA" if pd.isna(score_value) else f"{float(score_value):.1f}"
        score_width = 0 if pd.isna(score_value) else max(0, min(100, float(score_value)))

        selected_class = " selected" if isinstance(selected_idx, int) and selected_idx == idx else ""

        card_html = (
            f'<div class="shortlist-card{selected_class}">'
            f'<div class="shortlist-rank">{idx + 1}</div>'
            f'{avatar}'
            f'<div class="shortlist-player">'
            f'<div class="shortlist-player-name">{player}</div>'
            f'<div class="shortlist-player-sub">{club}</div>'
            f'</div>'
            f'<div class="shortlist-field">'
            f'<div class="shortlist-label">Edad</div>'
            f'<div class="shortlist-value">{age}</div>'
            f'</div>'
            f'<div class="shortlist-field">'
            f'<div class="shortlist-label">Grupo</div>'
            f'<div class="shortlist-pill">{group}</div>'
            f'</div>'
            f'<div class="shortlist-field">'
            f'<div class="shortlist-label">Valor</div>'
            f'<div class="shortlist-value">{value}</div>'
            f'</div>'
            f'<div class="shortlist-field">'
            f'<div class="shortlist-label">Pie</div>'
            f'<div class="shortlist-value">{foot}</div>'
            f'</div>'
            f'<div class="shortlist-field">'
            f'<div class="shortlist-label">Altura</div>'
            f'<div class="shortlist-value">{height}</div>'
            f'</div>'
            f'<div class="shortlist-score">'
            f'<div class="shortlist-score-top"><span>Score final</span><b>{score_text}</b></div>'
            f'<div class="shortlist-score-track">'
            f'<div class="shortlist-score-fill" style="width:{score_width:.1f}%"></div>'
            f'</div>'
            f'</div>'
            f'</div>'
        )

        with keyed_container(border=False, key=f"shortlist_card_{idx}"):
            st.markdown(card_html, unsafe_allow_html=True)

            if st.button(
                f"Ver detalle de {player}",
                key=f"open_shortlist_detail_{idx}",
                on_click=set_selected_candidate_idx,
                args=(idx,),
                use_container_width=True,
            ):
                clicked_rows = [idx]

    return clicked_rows

def compute_ranking(proto_df, players_df, team_name, formation_final, ui_slot, exclude_same_team, preferred_foot, min_height, max_value_target, min_age, max_age):
    raw_df, proto_row, valid_cols = engine.compute_for_target_slot(
        proto_df=proto_df,
        players_df=players_df,
        team_name=team_name,
        formation_final=formation_final,
        ui_slot=ui_slot,
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
        min_age=min_age,
        max_age=max_age,
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
    profile_label = infer_decision_profile(selected_score, None, [])

    _, block_df = engine.explain_player_vs_prototype(raw_df, proto_row, valid_cols, selected_player)
    readable_blocks = block_display(block_df)
    diagnosis_text = tactical_diagnosis_text(readable_blocks)
    preference_rows, impact_delta = build_preference_rows(selected_row)
    profile_label = infer_decision_profile(selected_score, impact_delta, preference_rows)

    delta_text = "Sin cambios"
    if impact_delta is not None:
        delta_text = f"{impact_delta:+.1f} pts"

    hero_html = f"""
    <div class="detail-hero">
        <div class="detail-hero-top">
            <div class="detail-identity">
                {avatar_html(selected_player, selected_row, "detail-avatar detail-avatar-img")}
                <div>
                    <div class="detail-name">{html.escape(selected_player)}</div>
                    <div class="detail-sub">{html.escape(str(selected_row.get('event_team_name', 'Club no disponible')))} · {html.escape(group_text)}</div>
                </div>
            </div>
            <div class="detail-badges">
                <div class="detail-badge strong">Score final · {html.escape(selected_score_text)}</div>
                <div class="detail-badge gold">{html.escape(score_status(selected_score))}</div>
                <div class="detail-badge">{html.escape(profile_label)}</div>
            </div>
        </div>
        <div class="detail-hero-summary">{html.escape(diagnosis_text)}</div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(detail_metric_card("Score táctico", selected_base_score_text, "Ajuste puro contra el prototipo"), unsafe_allow_html=True)
    with k2:
        st.markdown(detail_metric_card("Impacto de preferencias", delta_text, "Diferencia entre score táctico y score final"), unsafe_allow_html=True)
    with k3:
        st.markdown(detail_metric_card("Valor de mercado", money_short(selected_row.get("player_valuation", pd.NA)), "Referencia económica del candidato"), unsafe_allow_html=True)
    with k4:
        st.markdown(detail_metric_card("Altura", format_height(selected_row.get("height", pd.NA)), "Dato físico disponible en la base"), unsafe_allow_html=True)
    with k5:
        st.markdown(detail_metric_card("Edad", format_age(selected_row.get("age", pd.NA)), "Edad del candidato"), unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Resumen", "Bloques tácticos", "Detalle completo"])

    with tab1:
        c1, c2 = st.columns([1.1, .95], gap="medium")
        with c1:
            st.markdown(
                f"""
                <div class="detail-diagnosis">
                    <div class="detail-section-title">Lectura táctica</div>
                    <div class="detail-section-text">{html.escape(diagnosis_text)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            applied_team_name = st.session_state.get("applied_team_name", "Club objetivo")
            applied_formation = st.session_state.get("applied_formation", "Formación")
            applied_slot = st.session_state.get("applied_slot", "Slot")
            inferred_role = get_inferred_base_position(proto_df, applied_team_name, applied_formation, applied_slot) if "proto_df" in globals() else applied_slot
            proto_context_html = f"""
            <div class="prototype-context-card" style="margin-top:.55rem;">
                <div class="prototype-context-title">Contexto del prototipo buscado</div>
                <div class="prototype-context-text">La comparación se realizó contra el perfil dominante del club y slot seleccionados. Esto ayuda a interpretar por qué el jugador aparece como candidato dentro del sistema objetivo.</div>
                <div class="prototype-chip-row">
                    <div class="prototype-chip">Club: <b>{html.escape(str(applied_team_name))}</b></div>
                    <div class="prototype-chip">Formación: <b>{html.escape(str(applied_formation))}</b></div>
                    <div class="prototype-chip">Slot: <b>{html.escape(format_group_pos(applied_slot))}</b></div>
                    <div class="prototype-chip">Rol base: <b>{html.escape(position_description(inferred_role or applied_slot))}</b></div>
                </div>
            </div>
            """
            st.markdown(proto_context_html, unsafe_allow_html=True)

        with c2:
            impact_number = "0.0"
            if impact_delta is not None:
                impact_number = f"{impact_delta:+.1f}"
            st.markdown(
                f"""
                <div class="preference-card">
                    <div class="detail-section-title">Impacto de preferencias</div>
                    <div class="preference-impact-number">{html.escape(impact_number)}</div>
                    <div class="preference-impact-caption">Variación del score táctico al aplicar pie, altura, presupuesto y edad.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            pref_html = ['<div class="preference-card" style="margin-top:.55rem;">', '<div class="detail-section-title">Chequeo de criterios</div>']
            for row in preference_rows:
                pref_html.append(
                    f'<div class="preference-item">'
                    f'  <div>'
                    f'    <div class="preference-name">{html.escape(str(row.get("criterion", "Criterio")))}</div>'
                    f'    <div class="preference-target">Objetivo: {html.escape(str(row.get("target", "")))}</div>'
                    f'  </div>'
                    f'  <div style="text-align:right">'
                    f'    <div class="preference-value">{html.escape(str(row.get("actual", "")))}</div>'
                    f'    <div class="preference-status {html.escape(str(row.get("status_key", "neutral")))}">{html.escape(str(row.get("status", "")))}</div>'
                    f'  </div>'
                    f'</div>'
                )
            pref_html.append('</div>')
            st.markdown("".join(pref_html), unsafe_allow_html=True)

    with tab2:
        if readable_blocks.empty:
            st.info("No hay diagnóstico disponible para este jugador.")
        else:
            strengths = readable_blocks.sort_values("Ajuste", ascending=False).head(3)
            concerns = readable_blocks.sort_values("Ajuste", ascending=True).head(3)
            left, right = st.columns(2, gap="medium")
            with left:
                st.markdown("<div class='detail-section-title'>Áreas de mayor encaje</div>", unsafe_allow_html=True)
                blocks_html = ['<div class="detail-block-stack">']
                for _, row in strengths.iterrows():
                    blocks_html.append(detail_block_card(row.get("Área", "Área"), row.get("Ajuste", 0), row.get("Lectura", ""), tone="positive"))
                blocks_html.append('</div>')
                st.markdown("".join(blocks_html), unsafe_allow_html=True)
            with right:
                st.markdown("<div class='detail-section-title'>Áreas a revisar</div>", unsafe_allow_html=True)
                blocks_html = ['<div class="detail-block-stack">']
                for _, row in concerns.iterrows():
                    blocks_html.append(detail_block_card(row.get("Área", "Área"), row.get("Ajuste", 0), row.get("Lectura", ""), tone="warning"))
                blocks_html.append('</div>')
                st.markdown("".join(blocks_html), unsafe_allow_html=True)

    with tab3:
        if readable_blocks.empty:
            st.info("No hay detalle completo disponible.")
        else:
            st.dataframe(
                readable_blocks.sort_values("Ajuste", ascending=False),
                use_container_width=True,
                hide_index=True,
                column_config={"Ajuste": st.column_config.ProgressColumn("Ajuste", min_value=0, max_value=100, format="%.1f")},
            )
            st.caption("Ajuste mide cercanía del jugador al prototipo del club en cada bloque táctico. La lectura indica la dirección de la diferencia frente al perfil buscado.")


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

logo_data_uri = load_logo_data_uri()
if logo_data_uri:
    logo_html = f'<div class="sf-logo-img-wrap"><img src="{logo_data_uri}" class="sf-logo-img" alt="ScoutFit logo"></div>'
else:
    logo_html = '<div class="sf-logo-fallback">SF</div>'

st.markdown(f"""
<div class="sf-header">
    {logo_html}
    <div>
        <div class="sf-title"><span class="sf-title-navy">Scout</span><span class="sf-title-pink">Fit</span></div>
        <div class="sf-subtitle">Compatibilidad táctica y ciencia de datos para scouting profesional</div>
    </div>
</div>
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
        panel_head("⌕", "Configuración de búsqueda", "Define club, formación y lanza la búsqueda.")

        # Club y formación en la misma fila para que el botón no se recorte
        club_col, form_col = st.columns([1, 1], gap="small")

        with club_col:
            team_name = st.selectbox(
                "Club objetivo",
                team_options,
                index=team_default_idx,
                key="team_select_widget",
            )

        if team_name != st.session_state.get("pending_team_name"):
            st.session_state["pending_team_name"] = team_name
            st.session_state.pop("pending_formation", None)
            st.session_state.pop("pending_slot", None)

        formation_options = engine.get_formation_options(proto_df, team_name)
        if not formation_options:
            st.warning("No hay formaciones disponibles para ese club.")
            st.stop()

        if st.session_state.get("pending_formation") not in formation_options:
            st.session_state["pending_formation"] = formation_options[0]

        formation_default_idx = formation_options.index(st.session_state["pending_formation"])

        with form_col:
            formation_final = st.selectbox(
                "Formación objetivo",
                formation_options,
                index=formation_default_idx,
                key="formation_select_widget",
            )

        if formation_final != st.session_state.get("pending_formation"):
            st.session_state["pending_formation"] = formation_final
            st.session_state.pop("pending_slot", None)

        exclude_same_team = st.checkbox(
            "Excluir jugadores del club objetivo",
            value=bool(st.session_state.get("pending_exclude_same_team", True)),
            key="exclude_same_team_widget",
        )

        search_clicked = st.button(
            "🔎 Buscar jugadores",
            type="primary",
            use_container_width=True,
        )

position_options = engine.get_slot_options(proto_df, team_name, formation_final)
if not position_options:
    st.warning("No hay slots disponibles para ese club y formación.")
    st.stop()

if st.session_state.get("pending_slot") not in position_options:
    st.session_state["pending_slot"] = position_options[0]

with pitch_col:
    with keyed_container(border=True, key="pitch_panel"):
        selected_slot = render_position_pitch(position_options, st.session_state["pending_slot"], formation_final)

inferred_base_pos = get_inferred_base_position(proto_df, team_name, formation_final, selected_slot)
auto_preferred_foot = engine.infer_auto_preferred_foot(inferred_base_pos, selected_slot)
auto_min_height = engine.infer_auto_min_height(inferred_base_pos) if inferred_base_pos else None
_, _, max_value_target_team = engine.get_team_budget_value(players_df, team_name, divisor=6.0)

with pref_col:
    with keyed_container(border=True, key="pref_panel"):
        panel_head("☰", "Preferencias de scouting", "Ajusta criterios prácticos sobre el score final.")
        use_scouting_preferences = st.checkbox("Aplicar preferencias", value=bool(st.session_state.get("pending_use_preferences", True)), key="use_preferences_widget")
        if use_scouting_preferences:
            foot_options = ["none", "left", "right", "both"]
            default_foot = auto_preferred_foot if auto_preferred_foot in foot_options else "none"
            pref_key_suffix = build_context_key(team_name, formation_final, selected_slot)
            foot_choice = st.selectbox("Pie deseado", foot_options, index=foot_options.index(default_foot), format_func=lambda x: FOOT_LABELS.get(x, x), key=f"foot_choice_{pref_key_suffix}")
            preferred_foot = None if foot_choice == "none" else foot_choice
            pref_c1, pref_c2 = st.columns([1, 1], gap="small")
            with pref_c1:
                min_height = st.number_input(
                    "Altura mínima",
                    min_value=1.50,
                    max_value=2.20,
                    value=float(auto_min_height) if auto_min_height is not None else 1.75,
                    step=0.01,
                    key=f"min_height_{pref_key_suffix}",
                )
            with pref_c2:
                default_budget = float(max_value_target_team) if pd.notna(max_value_target_team) else 10_000_000.0
                default_budget_m = round(default_budget / 1_000_000, 1)
                max_value_target_m = st.number_input(
                    "Presupuesto máx. (€M)",
                    min_value=0.0,
                    value=float(default_budget_m),
                    step=0.5,
                    key=f"max_value_m_{pref_key_suffix}",
                )
                max_value_target = float(max_value_target_m) * 1_000_000

            min_age, max_age = st.slider(
                "Rango de edad",
                min_value=15,
                max_value=45,
                value=(18, 30),
                step=1,
                key=f"age_range_{pref_key_suffix}",
            )
        else:
            preferred_foot = None
            min_height = None
            max_value_target = None
            min_age = None
            max_age = None

# ======================================================
# APLICAR BÚSQUEDA SOLO AL OPRIMIR BOTÓN
# ======================================================
if "has_searched" not in st.session_state:
    st.session_state["has_searched"] = False

shortlist_size = DEFAULT_SHORTLIST_SIZE

if search_clicked:
    st.session_state["has_searched"] = True
    st.session_state["applied_team_name"] = team_name
    st.session_state["applied_formation"] = formation_final
    st.session_state["applied_slot"] = selected_slot
    st.session_state["applied_shortlist_size"] = shortlist_size
    st.session_state["applied_exclude_same_team"] = exclude_same_team
    st.session_state["applied_preferred_foot"] = preferred_foot
    st.session_state["applied_min_height"] = min_height
    st.session_state["applied_max_value_target"] = max_value_target
    st.session_state["applied_min_age"] = min_age
    st.session_state["applied_max_age"] = max_age
    st.session_state["selected_candidate_idx"] = None

if not st.session_state.get("has_searched", False):
    selected_club_txt = html.escape(str(team_name))
    selected_formation_txt = html.escape(str(formation_final))
    selected_pos_txt = html.escape(format_group_pos(selected_slot))
    selected_pos_desc = html.escape(position_description(selected_slot))
    pref_status = "activadas" if use_scouting_preferences else "desactivadas"

    start_guide_html = (
        f'<div class="start-guide">'
        f'<div class="start-guide-main">'
        f'<div class="start-guide-icon">◎</div>'
        f'<div>'
        f'<div class="start-guide-title">Empieza una búsqueda de compatibilidad táctica</div>'
        f'<div class="start-guide-text">'
        f'Selecciona el club objetivo, marca una posición en la cancha y ajusta las preferencias de scouting. '
        f'Cuando oprimas <b>Buscar jugadores</b>, aparecerán el mejor candidato recomendado, las métricas y la shortlist.'
        f'</div>'
        f'<div class="start-guide-current">'
        f'<div class="start-guide-chip">Club seleccionado: <b>{selected_club_txt}</b></div>'
        f'<div class="start-guide-chip">Formación: <b>{selected_formation_txt}</b></div>'
        f'<div class="start-guide-chip">Slot marcado: <b>{selected_pos_txt}</b> · {selected_pos_desc}</div>'
        f'<div class="start-guide-chip">Preferencias: <b>{pref_status}</b></div>'
        f'</div>'
        f'</div>'
        f'</div>'
        f'<div class="start-guide-steps">'
        f'<div class="start-guide-step">'
        f'<div class="start-guide-step-num">1</div>'
        f'<div class="start-guide-step-title">Elige el club</div>'
        f'<div class="start-guide-step-text">Usa la tarjeta de configuración para definir el sistema del equipo objetivo.</div>'
        f'</div>'
        f'<div class="start-guide-step">'
        f'<div class="start-guide-step-num">2</div>'
        f'<div class="start-guide-step-title">Marca un slot</div>'
        f'<div class="start-guide-step-text">Haz clic en la cancha para enfocar la búsqueda en el rol táctico exacto disponible.</div>'
        f'</div>'
        f'<div class="start-guide-step">'
        f'<div class="start-guide-step-num">3</div>'
        f'<div class="start-guide-step-title">Lanza el scouting</div>'
        f'<div class="start-guide-step-text">Oprime Buscar jugadores para calcular compatibilidad, ranking y detalle táctico.</div>'
        f'</div>'
        f'</div>'
        f'<div class="start-guide-callout">'
        f'Tip: puedes cambiar posición, pie, altura, edad o presupuesto antes de buscar. '
        f'Los resultados solo se calculan cuando oprimes el botón.'
        f'</div>'
        f'</div>'
    )

    st.markdown(start_guide_html, unsafe_allow_html=True)
    st.markdown("<div class='footer-note'>ScoutFit · Herramienta de apoyo para reclutamiento basada en compatibilidad sistema-jugador.</div>", unsafe_allow_html=True)
    st.stop()

applied_team_name = st.session_state.get("applied_team_name", team_name)
applied_formation = st.session_state.get("applied_formation", formation_final)
applied_slot = st.session_state.get("applied_slot", selected_slot)
applied_shortlist_size = int(st.session_state.get("applied_shortlist_size", shortlist_size))
applied_exclude_same_team = bool(st.session_state.get("applied_exclude_same_team", exclude_same_team))
applied_preferred_foot = st.session_state.get("applied_preferred_foot", preferred_foot)
applied_min_height = st.session_state.get("applied_min_height", min_height)
applied_max_value_target = st.session_state.get("applied_max_value_target", max_value_target)
applied_min_age = st.session_state.get("applied_min_age", min_age)
applied_max_age = st.session_state.get("applied_max_age", max_age)

pending_context = build_context_key(team_name, formation_final, selected_slot, shortlist_size, exclude_same_team, preferred_foot, min_height, max_value_target, min_age, max_age)
applied_context = build_context_key(applied_team_name, applied_formation, applied_slot, applied_shortlist_size, applied_exclude_same_team, applied_preferred_foot, applied_min_height, applied_max_value_target, applied_min_age, applied_max_age)
st.session_state["applied_context"] = applied_context


# ======================================================
# CÁLCULO CON CACHE DE SESIÓN
# ======================================================
ranking_context = build_context_key(applied_team_name, applied_formation, applied_slot, applied_exclude_same_team, applied_preferred_foot, applied_min_height, applied_max_value_target, applied_min_age, applied_max_age)
if st.session_state.get("ranking_context") != ranking_context:
    with st.spinner("Buscando candidatos compatibles..."):
        raw_df, final_df, proto_row, valid_cols = compute_ranking(proto_df, players_df, applied_team_name, applied_formation, applied_slot, applied_exclude_same_team, applied_preferred_foot, applied_min_height, applied_max_value_target, applied_min_age, applied_max_age)
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

rec_col, score_col, club_col, age_col, foot_col, value_col, height_col = st.columns([2.25, 1.20, 1.00, .78, .82, 1.02, .82], gap="small")
with rec_col:
    top_avatar = avatar_html(top_player, top, "candidate-photo")
    st.markdown(f"""
    <div class="candidate-card"><div class="candidate-card-flex">{top_avatar}<div>
    <div class="mini-label">Mejor candidato recomendado</div><div class="candidate-name">{html.escape(top_player)}</div>
    <div class="candidate-meta">{html.escape(str(top.get('event_team_name', 'Club no disponible')))}</div>
    <div class="position-pill">{html.escape(format_group_pos(top.get('merged_pos', applied_slot)))}</div></div></div></div>
    """, unsafe_allow_html=True)
with score_col:
    st.markdown(f"<div class='score-card'><div class='score-label'>Score final de compatibilidad</div><div class='big-score'>{html.escape(top_score_text)}</div><div class='score-status'>{html.escape(score_status(top_score))}</div></div>", unsafe_allow_html=True)
with club_col:
    st.markdown(f"<div class='stat-card'><div class='stat-label'>Club actual</div><div class='stat-value'>{html.escape(str(top.get('event_team_name', 'NA')))}</div></div>", unsafe_allow_html=True)
with age_col:
    st.markdown(f"<div class='stat-card'><div class='stat-label'>Edad</div><div class='stat-value accent'>{html.escape(format_age(top.get('age', pd.NA)))}</div></div>", unsafe_allow_html=True)
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
    <div class="section-subtitle">Haz clic en cualquier candidato para ver el detalle táctico del jugador.
    
    </div></div></div>
    """, unsafe_allow_html=True)
    

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
        st.session_state["selected_candidate_idx"] = None
        if not hasattr(st, "dialog"):
            st.caption("Tu versión de Streamlit no soporta ventanas emergentes; por eso el detalle se muestra debajo de la tabla.")

st.markdown("<div class='footer-note'>ScoutFit · Herramienta de apoyo para reclutamiento basada en compatibilidad sistema-jugador.</div>", unsafe_allow_html=True)
