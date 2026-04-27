import warnings
warnings.filterwarnings("ignore")

import hashlib

import pandas as pd
import streamlit as st

from engine import TacticalCompatibilityEngine


# ======================================================
# CONFIGURACIÓN DEL PRODUCTO
# ======================================================
st.set_page_config(
    page_title="ScoutFit | Compatibilidad táctica",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2.4rem;
        max-width: 1400px;
    }
    .hero {
        padding: 1.6rem 1.8rem;
        border-radius: 24px;
        background: linear-gradient(135deg, #07111f 0%, #12346f 55%, #0f766e 100%);
        color: white;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.18);
    }
    .hero h1 {
        margin: 0 0 .35rem 0;
        font-size: 2.2rem;
        line-height: 1.1;
        letter-spacing: -0.03em;
    }
    .hero p {
        margin: .25rem 0 0 0;
        max-width: 920px;
        color: rgba(255,255,255,.86);
        font-size: 1rem;
        line-height: 1.5;
    }
    .pill {
        display: inline-block;
        padding: .25rem .65rem;
        border-radius: 999px;
        background: rgba(255,255,255,.13);
        border: 1px solid rgba(255,255,255,.16);
        font-size: .78rem;
        margin-bottom: .75rem;
        color: rgba(255,255,255,.9);
    }
    .card {
        padding: 1.05rem 1.15rem;
        border-radius: 18px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        background: rgba(248, 250, 252, 0.76);
        margin-top: .85rem;
        margin-bottom: .9rem;
    }
    .candidate-card {
        padding: 1.2rem 1.25rem;
        border-radius: 20px;
        border: 1px solid rgba(34, 197, 94, 0.30);
        background: linear-gradient(135deg, rgba(240, 253, 244, .95), rgba(236, 253, 245, .78));
        min-height: 178px;
    }
    .candidate-name {
        font-size: 1.55rem;
        font-weight: 750;
        line-height: 1.2;
        color: #052e16;
        margin-top: .15rem;
    }
    .muted {
        color: #64748b;
        font-size: .9rem;
        line-height: 1.45;
    }
    .big-score {
        font-size: 2.1rem;
        font-weight: 800;
        color: #14532d;
        line-height: 1.1;
        margin-top: .3rem;
    }
    .mini-label {
        font-size: .78rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: .05em;
        font-weight: 700;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.35rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def get_engine():
    return TacticalCompatibilityEngine()


engine = get_engine()


# ======================================================
# CONSTANTES INTERNAS
# ======================================================
PROTOTYPE_SOURCE = "weighted"
METRIC = "euclidean"
SCORE_METHOD = "compat_score_rank_0_100"
FEATURE_SET = "full"
PENALTY_PROFILE = "medium"
ALLOWED_LEAGUES = None

BLOCK_LABELS = {
    "progression": "Progresión",
    "passing": "Pase",
    "spatial": "Ocupación espacial",
    "defensive": "Defensa",
    "offensive": "Ataque",
    "team_context": "Participación en equipo",
}

FOOT_LABELS = {
    "left": "Izquierdo",
    "right": "Derecho",
    "both": "Ambos",
    "none": "Sin preferencia",
    "nan": "No disponible",
    "": "No disponible",
}


# ======================================================
# HELPERS
# ======================================================
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


def money_short(value) -> str:
    value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(value):
        return "No disponible"
    if abs(value) >= 1_000_000:
        return f"€{value / 1_000_000:.1f} M"
    if abs(value) >= 1_000:
        return f"€{value / 1_000:.0f} K"
    return f"€{value:.0f}"


def format_foot(value) -> str:
    if pd.isna(value):
        return "No disponible"
    raw = str(value).strip().lower()
    return FOOT_LABELS.get(raw, str(value))


def safe_score(value) -> float | None:
    score = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(score):
        return None
    return float(score)


def final_ranking_display(df: pd.DataFrame) -> pd.DataFrame:
    player_col = name_col_for(df)
    if player_col is None:
        return pd.DataFrame()

    required = [
        player_col,
        "event_team_name",
        "merged_pos",
        "player_valuation",
        "foot",
        "height",
        "final_scouting_score_0_100",
    ]
    available = [col for col in required if col in df.columns]
    out = df[available].copy()

    rename_map = {
        player_col: "Jugador",
        "event_team_name": "Club",
        "merged_pos": "Grupo posicional",
        "player_valuation": "Valor de mercado",
        "foot": "Pie",
        "height": "Altura",
        "final_scouting_score_0_100": "Score final",
    }
    out = out.rename(columns=rename_map)

    if "Pie" in out.columns:
        out["Pie"] = out["Pie"].map(format_foot)
    if "Altura" in out.columns:
        out["Altura"] = out["Altura"].map(format_height)
    if "Valor de mercado" in out.columns:
        out["Valor de mercado"] = out["Valor de mercado"].map(money_short)
    if "Score final" in out.columns:
        out["Score final"] = pd.to_numeric(out["Score final"], errors="coerce").round(1)

    final_order = ["Jugador", "Club", "Grupo posicional", "Valor de mercado", "Pie", "Altura", "Score final"]
    return out[[col for col in final_order if col in out.columns]]


def build_selection_context(
    team_name: str,
    merged_pos: str,
    shortlist_size: int,
    exclude_same_team: bool,
    preferred_foot=None,
    min_height=None,
    max_value_target=None,
) -> str:
    raw = f"{team_name}|{merged_pos}|{shortlist_size}|{exclude_same_team}|{preferred_foot}|{min_height}|{max_value_target}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]


def get_query_value(key: str):
    try:
        value = st.query_params.get(key, None)
    except Exception:
        value = st.experimental_get_query_params().get(key, [None])

    if isinstance(value, list):
        return value[0] if value else None
    return value


def get_selected_candidate_index(context_key: str, max_rows: int) -> int | None:
    selected_context = get_query_value("selected_context")
    if str(selected_context) != str(context_key):
        return None

    selected_raw = get_query_value("selected_candidate")
    try:
        selected_idx = int(selected_raw)
    except (TypeError, ValueError):
        return None

    if 0 <= selected_idx < max_rows:
        return selected_idx
    return None


def clear_selected_candidate_query_params():
    st.session_state["selected_candidate_idx"] = None


def format_height(value) -> str:
    numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric_value):
        return "NA"
    return f"{numeric_value:.2f} m"


def render_clickable_shortlist_table(display_df: pd.DataFrame, shortlist_df: pd.DataFrame):
    """Renderiza una shortlist clicable con componentes nativos de Streamlit.

    La versión HTML no podía actualizar el estado de Python de forma confiable.
    Cada fila se presenta como un botón ancho para que el clic sí abra el detalle.
    """
    if display_df.empty:
        st.info("No hay candidatos disponibles para mostrar.")
        return

    st.markdown(
        """
        <style>
        div[data-testid="stButton"] > button {
            min-height: 58px;
            justify-content: flex-start;
            text-align: left;
            border-radius: 14px;
            border: 1px solid rgba(148, 163, 184, 0.35);
            background: #ffffff;
            color: #0f172a;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
            padding: 0.75rem 1rem;
            white-space: normal;
        }
        div[data-testid="stButton"] > button:hover {
            border-color: rgba(37, 99, 235, 0.55);
            background: #f0f9ff;
            color: #0f172a;
        }
        div[data-testid="stButton"] > button:active {
            background: #dbeafe;
        }
        .row-header {
            display: grid;
            grid-template-columns: 2.0fr 1.5fr 1.35fr .95fr .75fr .75fr .8fr;
            gap: .75rem;
            padding: 0 .9rem .35rem .9rem;
            color: #64748b;
            font-size: .72rem;
            text-transform: uppercase;
            letter-spacing: .04em;
            font-weight: 800;
        }
        </style>
        <div class="row-header">
            <span>Jugador</span>
            <span>Club</span>
            <span>Grupo</span>
            <span>Valor</span>
            <span>Pie</span>
            <span>Altura</span>
            <span>Score</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for idx, row in display_df.reset_index(drop=True).iterrows():
        player = str(row.get("Jugador", "Jugador no disponible"))
        club = str(row.get("Club", "Club no disponible"))
        group = str(row.get("Grupo posicional", "Grupo no disponible"))
        value_text = money_short(row.get("Valor de mercado", pd.NA))
        foot = str(row.get("Pie", "NA"))
        height_text = format_height(row.get("Altura", pd.NA))
        score = safe_score(row.get("Score final", pd.NA))
        score_text = f"{score:.1f}" if score is not None else "NA"

        label = (
            f"{idx + 1}. {player}  |  {club}  |  {group}  |  "
            f"{value_text}  |  {foot}  |  {height_text}  |  Score {score_text}"
        )

        if st.button(label, key=f"candidate_row_{idx}", use_container_width=True):
            st.session_state["selected_candidate_idx"] = idx
            st.rerun()



def render_shortlist_dataframe(display_df: pd.DataFrame) -> list[int]:
    """Tabla limpia y seleccionable por fila completa.

    Usa el componente nativo de Streamlit para conservar el estilo visual de tabla,
    pero permite abrir el detalle al seleccionar cualquier fila.
    """
    if display_df.empty:
        st.info("No hay candidatos disponibles para mostrar.")
        return []

    table_event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=min(640, 58 + 48 * len(display_df)),
        on_select="rerun",
        selection_mode="single-row",
        key="shortlist_table",
        column_config={
            "Jugador": st.column_config.TextColumn("Jugador", width="medium"),
            "Club": st.column_config.TextColumn("Club", width="small"),
            "Grupo posicional": st.column_config.TextColumn("Grupo posicional", width="small"),
            "Valor de mercado": st.column_config.TextColumn("Valor de mercado", width="small"),
            "Pie": st.column_config.TextColumn("Pie", width="small"),
            "Altura": st.column_config.TextColumn("Altura", width="small"),
            "Score final": st.column_config.ProgressColumn(
                "Score final",
                min_value=0.0,
                max_value=100.0,
                format="%.1f",
                width="medium",
            ),
        },
    )

    if isinstance(table_event, dict):
        selection = table_event.get("selection", {})
        rows = selection.get("rows", []) if isinstance(selection, dict) else []
        return list(rows) if rows is not None else []

    selection = getattr(table_event, "selection", None)
    if selection is not None:
        rows = getattr(selection, "rows", [])
        return list(rows) if rows is not None else []

    return []

def block_display(block_df: pd.DataFrame) -> pd.DataFrame:
    if block_df.empty:
        return block_df
    out = block_df.copy()
    out["Área"] = out["block"].map(BLOCK_LABELS).fillna(out["block"])
    out["Ajuste"] = pd.to_numeric(out["block_similarity_0_100"], errors="coerce").round(1)
    out["Lectura"] = out["prototype_vs_player"].replace({
        "por encima": "Por encima del prototipo",
        "por debajo": "Por debajo del prototipo",
        "alineado": "Alineado con el prototipo",
    })
    return out[["Área", "Ajuste", "Lectura"]]


def extract_selected_rows(table_event) -> list[int]:
    if table_event is None:
        return []

    selection = getattr(table_event, "selection", None)
    if selection is not None:
        rows = getattr(selection, "rows", [])
        return list(rows) if rows is not None else []

    if isinstance(table_event, dict):
        selection_dict = table_event.get("selection", {})
        rows = selection_dict.get("rows", [])
        return list(rows) if rows is not None else []

    return []


def get_inferred_base_position(proto_df: pd.DataFrame, team_name: str, merged_pos: str) -> str | None:
    preview = proto_df[
        (proto_df["event_team_name"].astype(str) == str(team_name))
        & (proto_df["merged_pos"].astype(str) == str(merged_pos))
    ].copy()

    if preview.empty:
        return None
    if "base_pos" in preview.columns and preview["base_pos"].notna().any():
        return str(preview["base_pos"].mode().iloc[0])
    return str(merged_pos)


def compute_ranking(
    proto_df: pd.DataFrame,
    players_df: pd.DataFrame,
    team_name: str,
    merged_pos: str,
    exclude_same_team: bool,
    preferred_foot: str | None,
    min_height: float | None,
    max_value_target: float | None,
):
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

    # Los bloques se calculan únicamente para explicar el ajuste, no para ordenar el ranking.
    raw_df = engine.add_block_similarity_scores(
        result_df=raw_df,
        valid_cols=valid_cols,
        block_scale=1.5,
    )

    distance_col = distance_column_for(raw_df)
    sort_cols = [SCORE_METHOD]
    ascending = [False]
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


# ======================================================
# VENTANA DE DETALLE DEL JUGADOR
# ======================================================
def render_player_detail_content(
    selected_player: str,
    selected_row: pd.Series,
    raw_df: pd.DataFrame,
    proto_row: pd.Series,
    valid_cols: list[str],
):
    selected_score = safe_score(selected_row.get("final_scouting_score_0_100"))
    selected_score_text = f"{selected_score:.1f}" if selected_score is not None else "NA"
    selected_base_score = safe_score(selected_row.get(SCORE_METHOD))
    selected_base_score_text = f"{selected_base_score:.1f}" if selected_base_score is not None else "NA"

    st.markdown(
        f"""
        <div class="card" style="margin-top:0;">
            <div class="mini-label">Candidato seleccionado</div>
            <div class="candidate-name" style="font-size:1.35rem;color:#0f172a;">{selected_player}</div>
            <div class="muted">
                {selected_row.get('event_team_name', 'Club no disponible')} · {selected_row.get('merged_pos', 'Grupo no disponible')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    d1, d2, d3, d4 = st.columns(4)
    with d1:
        st.metric("Score final", selected_score_text)
    with d2:
        st.metric("Score táctico", selected_base_score_text)
    with d3:
        st.metric("Valor", money_short(selected_row.get("player_valuation", pd.NA)))
    with d4:
        height_value = pd.to_numeric(pd.Series([selected_row.get("height", pd.NA)]), errors="coerce").iloc[0]
        st.metric("Altura", f"{height_value:.2f} m" if pd.notna(height_value) else "NA")

    diag_context = st.session_state.get("ranking_context", "default")
    cache_key = f"{diag_context}|{selected_player}"
    diag_cache = st.session_state.setdefault("player_diag_cache", {})

    if cache_key not in diag_cache:
        with st.spinner("Cargando detalle táctico..."):
            _, block_df = engine.explain_player_vs_prototype(
                result_df=raw_df,
                proto_row=proto_row,
                valid_cols=valid_cols,
                player_name=selected_player,
            )
            diag_cache[cache_key] = block_df
    else:
        block_df = diag_cache[cache_key]

    readable_blocks = block_display(block_df)
    if readable_blocks.empty:
        st.info("No hay diagnóstico disponible para este jugador.")
        return

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("### Áreas de mayor encaje")
        st.dataframe(
            readable_blocks.sort_values("Ajuste", ascending=False).head(3),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ajuste": st.column_config.ProgressColumn("Ajuste", min_value=0, max_value=100, format="%.1f"),
            },
        )
    with c2:
        st.markdown("### Áreas a revisar")
        st.dataframe(
            readable_blocks.sort_values("Ajuste", ascending=True).head(3),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ajuste": st.column_config.ProgressColumn("Ajuste", min_value=0, max_value=100, format="%.1f"),
            },
        )

    with st.expander("Ver todas las áreas tácticas", expanded=False):
        st.dataframe(
            readable_blocks.sort_values("Ajuste", ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ajuste": st.column_config.ProgressColumn("Ajuste", min_value=0, max_value=100, format="%.1f"),
            },
        )

    if st.button("Cerrar detalle", use_container_width=True):
        clear_selected_candidate_query_params()
        st.rerun()



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


# ======================================================
# SIDEBAR: BÚSQUEDA DE CLIENTE
# ======================================================
st.sidebar.title("ScoutFit")
st.sidebar.caption("Shortlist táctica para decisiones de reclutamiento.")

team_name = st.sidebar.selectbox("Club objetivo", team_options)
position_options = engine.get_merged_position_options(proto_df, team_name)
if not position_options:
    st.warning("No hay grupos posicionales disponibles para ese club.")
    st.stop()

merged_pos = st.sidebar.selectbox("Grupo posicional buscado", position_options)
shortlist_size = st.sidebar.slider("Tamaño de la shortlist", min_value=5, max_value=50, value=20, step=5)
exclude_same_team = st.sidebar.checkbox("Excluir jugadores del club objetivo", value=True)

inferred_base_pos = get_inferred_base_position(proto_df, team_name, merged_pos)
auto_preferred_foot = engine.infer_auto_preferred_foot(inferred_base_pos, merged_pos)
auto_min_height = engine.infer_auto_min_height(inferred_base_pos) if inferred_base_pos else None
_, _, max_value_target_team = engine.get_team_budget_value(players_df, team_name, divisor=6.0)

with st.sidebar.expander("Preferencias de scouting", expanded=False):
    st.caption("Estas preferencias ajustan el score final. El encaje táctico base se calcula por distancia Euclidiana.")

    use_scouting_preferences = st.checkbox("Aplicar preferencias", value=True)

    if use_scouting_preferences:
        foot_options = ["none", "left", "right", "both"]
        default_foot = auto_preferred_foot if auto_preferred_foot in foot_options else "none"
        foot_choice = st.selectbox(
            "Pie deseado",
            foot_options,
            index=foot_options.index(default_foot),
            format_func=lambda x: FOOT_LABELS.get(x, x),
        )
        preferred_foot = None if foot_choice == "none" else foot_choice

        min_height = st.number_input(
            "Altura mínima",
            min_value=1.50,
            max_value=2.20,
            value=float(auto_min_height) if auto_min_height is not None else 1.75,
            step=0.01,
        )

        max_value_target = st.number_input(
            "Presupuesto máximo por jugador",
            min_value=0.0,
            value=float(max_value_target_team) if pd.notna(max_value_target_team) else 10_000_000.0,
            step=500_000.0,
        )
    else:
        preferred_foot = None
        min_height = None
        max_value_target = None


# ======================================================
# CÁLCULO
# ======================================================
ranking_context = build_selection_context(
    team_name=team_name,
    merged_pos=merged_pos,
    shortlist_size=shortlist_size,
    exclude_same_team=exclude_same_team,
    preferred_foot=preferred_foot,
    min_height=min_height,
    max_value_target=max_value_target,
)

if st.session_state.get("ranking_context") != ranking_context:
    with st.spinner("Buscando candidatos compatibles..."):
        raw_df, final_df, proto_row, valid_cols = compute_ranking(
            proto_df=proto_df,
            players_df=players_df,
            team_name=team_name,
            merged_pos=merged_pos,
            exclude_same_team=exclude_same_team,
            preferred_foot=preferred_foot,
            min_height=min_height,
            max_value_target=max_value_target,
        )
    st.session_state["ranking_context"] = ranking_context
    st.session_state["player_diag_cache"] = {}
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

shortlist_df = final_df.head(shortlist_size).copy().reset_index(drop=True)
shortlist_display = final_ranking_display(shortlist_df)


# ======================================================
# HERO
# ======================================================
st.markdown(
    f"""
    <div class="hero">
        <div class="pill">Scouting basado en compatibilidad táctica</div>
        <h1>Encuentra jugadores que encajan con el sistema de {team_name}</h1>
        <p>
        Shortlist para <b>{merged_pos}</b>. El ranking prioriza jugadores cuyo perfil estadístico se aproxima
        al prototipo táctico del club y ajusta el resultado con criterios prácticos de scouting.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ======================================================
# RECOMENDACIÓN PRINCIPAL
# ======================================================
top = shortlist_df.iloc[0]
top_player = get_player_name(top)
top_score = safe_score(top.get("final_scouting_score_0_100"))
top_score_text = f"{top_score:.1f}" if top_score is not None else "NA"
top_distance_score = safe_score(top.get(SCORE_METHOD))

left, right = st.columns([1.25, 1])
with left:
    st.markdown(
        f"""
        <div class="candidate-card">
            <div class="mini-label">Mejor candidato recomendado</div>
            <div class="candidate-name">{top_player}</div>
            <div class="muted">{top.get('event_team_name', 'Club no disponible')} · {top.get('merged_pos', merged_pos)}</div>
            <div class="big-score">{top_score_text}</div>
            <div class="muted">Score final de compatibilidad</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    k1, k2 = st.columns(2)
    with k1:
        st.metric("Club actual", str(top.get("event_team_name", "NA")))
        st.metric("Pie", format_foot(top.get("foot", pd.NA)))
    with k2:
        st.metric("Valor de mercado", money_short(top.get("player_valuation", pd.NA)))
        height_value = pd.to_numeric(pd.Series([top.get("height", pd.NA)]), errors="coerce").iloc[0]
        st.metric("Altura", f"{height_value:.2f} m" if pd.notna(height_value) else "NA")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Candidatos evaluados", len(final_df))
with m2:
    st.metric("Score táctico base", f"{top_distance_score:.1f}" if top_distance_score is not None else "NA")
with m3:
    avg_top = pd.to_numeric(shortlist_df["final_scouting_score_0_100"], errors="coerce").mean()
    st.metric("Promedio shortlist", f"{avg_top:.1f}" if pd.notna(avg_top) else "NA")
with m4:
    st.metric("Método", "Euclidiana")


# ======================================================
# SHORTLIST + DETALLE AL SELECCIONAR
# ======================================================
st.markdown("## Shortlist recomendada")
st.caption("Haz clic sobre cualquier fila del ranking para abrir el detalle táctico del jugador.")

if st.session_state.get("selection_context") != ranking_context:
    st.session_state["selection_context"] = ranking_context
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
        st.session_state["selected_candidate_idx"] = int(selected_rows[0])
        selected_display_row = int(selected_rows[0])

    csv_data = shortlist_display.to_csv(index=False).encode("utf-8")
    safe_team = str(team_name).replace(" ", "_")
    safe_pos = str(merged_pos).replace(" ", "_")
    st.download_button(
        "Descargar shortlist",
        data=csv_data,
        file_name=f"shortlist_{safe_team}_{safe_pos}.csv",
        mime="text/csv",
    )

    player_col = name_col_for(shortlist_df)
    if selected_display_row is None or player_col is None:
        st.info("Selecciona cualquier fila del ranking para abrir el detalle táctico del jugador.")
    else:
        selected_player = str(shortlist_df.iloc[selected_display_row][player_col])
        selected_row = shortlist_df.iloc[selected_display_row]
        render_player_detail_dialog(
            selected_player=selected_player,
            selected_row=selected_row,
            raw_df=raw_df,
            proto_row=proto_row,
            valid_cols=valid_cols,
        )
        if not hasattr(st, "dialog"):
            st.caption("Tu versión de Streamlit no soporta ventanas emergentes; por eso el detalle se muestra debajo de la tabla.")

st.markdown("---")
st.caption("ScoutFit · Herramienta de apoyo para reclutamiento basada en compatibilidad sistema-jugador.")
