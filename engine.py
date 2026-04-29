import os
import sys
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.covariance import LedoitWolf
from sklearn.preprocessing import StandardScaler


APP_BASE_ENV = "TACTICAL_COMPAT_APP_BASE"


def app_base_dir() -> Path:
    configured_base = os.environ.get(APP_BASE_ENV)
    if configured_base:
        return Path(configured_base).resolve()

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS).resolve()

    return Path(__file__).resolve().parent


def resource_path(*parts: str) -> Path:
    return app_base_dir().joinpath(*parts)


BASE = resource_path("Todo")

# =========================
# PROTOTIPOS BASE
# =========================
PROTOTYPE_PRIMARY_PATH = BASE / "team_position_prototypes_v4/team_position_prototype_primary_formation4.csv"
PROTOTYPE_WEIGHTED_PATH = BASE / "team_position_prototypes_v4/team_position_prototype_weighted4.csv"

# =========================
# PROTOTIPOS MERGED
# =========================
MERGED_PROTOTYPE_PRIMARY_PATH = BASE / (
    "clustering_roles_merged_v4/team_position_prototypes_merged_v4/merged_team_position_prototype_primary_formation_v4.csv"
)
MERGED_PROTOTYPE_WEIGHTED_PATH = BASE / (
    "clustering_roles_merged_v4/team_position_prototypes_merged_v4/merged_team_position_prototype_weighted_v4.csv"
)

# Prototipo recomendado para la app:
# conserva formación + slot táctico específico, por ejemplo DC_1/DC_2,
# pero mantiene los grupos fusionados LAW/RAW/LWM/RWM.
MERGED_SLOT_PROTOTYPE_APP_READY_PATH = resource_path("merged_team_formation_slot_prototype_app_ready_v4.csv")

# Fallback útil cuando el CSV está junto a app.py/engine.py durante pruebas locales.
MERGED_SLOT_PROTOTYPE_APP_READY_FALLBACK_PATH = resource_path(
    "merged_team_formation_slot_prototype_app_ready_v4.csv"
)

# =========================
# MATRIZ DE JUGADORES
# =========================
PLAYER_MATRIX_FULL_PATH = Path("matrizjugadorescompleta_top10.parquet")

CANDIDATE_FEATURE_COLS = [
    "n_events_p90", "touches_p90", "passes_p90", "def_actions_p90",
    "aerials_p90", "dribbles_p90", "losses_p90", "shots_p90",
    "prog_passes_p90", "final_third_entries_p90", "box_entries_p90",
    "long_passes_p90", "switches_p90", "high_def_actions_p90", "box_shots_p90",
    "pass_acc", "avg_pass_len", "forward_pass_share", "backward_pass_share",
    "prog_pass_share", "prog_pass_completed_share", "final_third_entry_pass_share",
    "box_entry_pass_share", "short_pass_share", "long_pass_share", "switch_pass_share",
    "box_shot_share", "progression_x_mean", "mean_x", "mean_y", "mean_y_sym",
    "std_x", "std_y", "wide_left_share", "wide_right_share", "wide_share",
    "central_share", "passdir_back", "passdir_left", "passdir_right", "passdir_wide",
    "passdir_center", "opp_half_event_share", "box_touch_share", "def_action_x_mean",
    "high_def_action_share", "event_share_team", "pass_share_team", "def_share_team",
    "shot_share_team", "touch_share_team",
]

REDUCED_DROP_COLS = [
    "backward_pass_share",
    "prog_pass_completed_share",
    "long_pass_share",
    "central_share",
    "opp_half_event_share",
    "event_share_team",
]

FEATURE_SET_MAP = {
    "full": CANDIDATE_FEATURE_COLS,
    "reduced": [c for c in CANDIDATE_FEATURE_COLS if c not in REDUCED_DROP_COLS],
}

DEFAULT_MIN_HEIGHT_BY_BASE_POS = {
    "GK": 1.88,
    "DC": 1.84,
    "DL": 1.73,
    "DR": 1.73,
    "DML": 1.74,
    "DMR": 1.74,
    "DMC": 1.77,
    "MC": 1.74,
    "AMC": 1.72,
    "AML": 1.70,
    "AMR": 1.70,
    "ML": 1.70,
    "MR": 1.70,
    "FW": 1.77,
    "FWL": 1.70,
    "FWR": 1.70,
    "LEFT_WIDE_MID": 1.72,
    "RIGHT_WIDE_MID": 1.72,
    "LEFT_ATTACK_WIDE": 1.70,
    "RIGHT_ATTACK_WIDE": 1.70,
}


DEFAULT_PENALTY_PROFILES = {
    "low": {
        "foot_both": 0.99,
        "foot_wrong": 0.95,
        "height_lambda": 0.06,
        "height_tol": 0.12,
        "height_floor": 0.94,
        "value_alpha": 1.20,
        "value_floor": 0.35,
        "age_scale": 8.0,
        "age_power": 3.0,
        "age_floor": 0.60,
        "age_missing": 0.90,
    },
    "medium": {
        "foot_both": 0.98,
        "foot_wrong": 0.90,
        "height_lambda": 0.10,
        "height_tol": 0.12,
        "height_floor": 0.88,
        "value_alpha": 2.00,
        "value_floor": 0.15,
        "age_scale": 7.0,
        "age_power": 3.0,
        "age_floor": 0.50,
        "age_missing": 0.88,
    },
    "strong": {
        "foot_both": 0.96,
        "foot_wrong": 0.82,
        "height_lambda": 0.16,
        "height_tol": 0.12,
        "height_floor": 0.80,
        "value_alpha": 3.00,
        "value_floor": 0.03,
        "age_scale": 6.0,
        "age_power": 3.0,
        "age_floor": 0.40,
        "age_missing": 0.85,
    },
}

MERGED_MAP = {
    "AMR": "RIGHT_ATTACK_WIDE",
    "FWR": "RIGHT_ATTACK_WIDE",
    "AML": "LEFT_ATTACK_WIDE",
    "FWL": "LEFT_ATTACK_WIDE",
    "DMR": "RIGHT_WIDE_MID",
    "MR": "RIGHT_WIDE_MID",
    "DML": "LEFT_WIDE_MID",
    "ML": "LEFT_WIDE_MID",
}

TACTICAL_BLOCKS = {
    "progression": [
        "prog_passes_p90", "final_third_entries_p90", "box_entries_p90",
        "progression_x_mean", "prog_pass_share", "final_third_entry_pass_share",
        "box_entry_pass_share"
    ],
    "passing": [
        "passes_p90", "pass_acc", "avg_pass_len", "forward_pass_share",
        "backward_pass_share", "short_pass_share", "long_pass_share",
        "switch_pass_share", "switches_p90", "passdir_back", "passdir_left",
        "passdir_right", "passdir_wide", "passdir_center", "pass_share_team"
    ],
    "spatial": [
        "mean_x", "mean_y", "mean_y_sym", "std_x", "std_y",
        "wide_left_share", "wide_right_share", "wide_share",
        "central_share", "opp_half_event_share", "box_touch_share",
        "def_action_x_mean"
    ],
    "defensive": [
        "def_actions_p90", "aerials_p90", "high_def_actions_p90",
        "high_def_action_share", "def_share_team"
    ],
    "offensive": [
        "dribbles_p90", "shots_p90", "box_shots_p90", "box_shot_share",
        "losses_p90", "shot_share_team"
    ],
    "team_context": [
        "n_events_p90", "touches_p90", "event_share_team", "touch_share_team"
    ],
}


def load_any_table(path) -> pd.DataFrame:
    """
    Carga CSV o Parquet. Acepta una ruta única o una lista/tupla de rutas
    para permitir fallbacks entre la estructura Todo/ y archivos junto a la app.
    """
    if isinstance(path, (list, tuple)):
        attempted = []
        for candidate in path:
            candidate_path = Path(candidate)
            attempted.append(str(candidate_path))
            if candidate_path.exists():
                path = candidate_path
                break
        else:
            raise FileNotFoundError("No existe ninguna de estas rutas: " + " | ".join(attempted))
    else:
        path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"No existe: {path}")
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


class TacticalCompatibilityEngine:
    def __init__(self):
        self.prototype_sources = {
            "primary_formation": PROTOTYPE_PRIMARY_PATH,
            "weighted": PROTOTYPE_WEIGHTED_PATH,
        }

        self.merged_prototype_sources = {
            "primary_formation": MERGED_PROTOTYPE_PRIMARY_PATH,
            "weighted": MERGED_PROTOTYPE_WEIGHTED_PATH,
            "slot_app_ready": (
                MERGED_SLOT_PROTOTYPE_APP_READY_PATH,
                MERGED_SLOT_PROTOTYPE_APP_READY_FALLBACK_PATH,
            ),
        }

        self.player_path = PLAYER_MATRIX_FULL_PATH

        self._proto_cache: Dict[str, pd.DataFrame] = {}
        self._merged_proto_cache: Dict[str, pd.DataFrame] = {}
        self._players_cache: Optional[pd.DataFrame] = None

    # ======================================================
    # NORMALIZADORES / HELPERS
    # ======================================================
    @staticmethod
    def normalize_feature_set(feature_set: str = "full") -> str:
        value = str(feature_set).strip().lower()
        if value not in FEATURE_SET_MAP:
            raise ValueError(f"feature_set no válido: {feature_set}. Usa 'full' o 'reduced'.")
        return value

    @staticmethod
    def normalize_metric(metric: str = "euclidean") -> str:
        value = str(metric).strip().lower()
        if value not in {"euclidean", "manhattan", "mahalanobis"}:
            raise ValueError("metric no válido. Usa 'euclidean', 'manhattan' o 'mahalanobis'.")
        return value

    @staticmethod
    def _safe_string_series(df: pd.DataFrame, col: str) -> pd.Series:
        if col not in df.columns:
            return pd.Series(dtype="object")
        return (
            df[col]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
        )

    @staticmethod
    def add_merged_pos(df: pd.DataFrame, base_pos_col: str = "base_pos") -> pd.DataFrame:
        out = df.copy()
        if "merged_pos" not in out.columns and base_pos_col in out.columns:
            out["merged_pos"] = out[base_pos_col].astype(str).map(MERGED_MAP).fillna(out[base_pos_col].astype(str))
        elif "merged_pos" in out.columns:
            out["merged_pos"] = out["merged_pos"].astype(str)
        return out

    def get_feature_cols(self, proto_df: pd.DataFrame, players_df: pd.DataFrame, feature_set: str = "full") -> List[str]:
        feature_set = self.normalize_feature_set(feature_set)
        candidate_cols = FEATURE_SET_MAP[feature_set]
        return [c for c in candidate_cols if c in proto_df.columns and c in players_df.columns]

    def _compute_distance(self, X_players_z: np.ndarray, proto_vec: np.ndarray, metric: str) -> np.ndarray:
        metric = self.normalize_metric(metric)
        proto_mat = proto_vec.reshape(1, -1)

        if metric == "euclidean":
            return cdist(X_players_z, proto_mat, metric="euclidean").ravel()

        if metric == "manhattan":
            return cdist(X_players_z, proto_mat, metric="cityblock").ravel()

        lw = LedoitWolf()
        lw.fit(X_players_z)
        VI = lw.precision_
        return cdist(X_players_z, proto_mat, metric="mahalanobis", VI=VI).ravel()

    @staticmethod
    def _append_distance_columns(df: pd.DataFrame, dist: np.ndarray, metric: str) -> pd.DataFrame:
        out = df.copy()
        metric = str(metric).strip().lower()
        out["distance"] = dist
        out["distance_metric"] = metric

        if metric == "euclidean":
            out["distance_euclidean"] = dist
        elif metric == "manhattan":
            out["distance_manhattan"] = dist
        elif metric == "mahalanobis":
            out["distance_mahalanobis"] = dist
        return out

    @staticmethod
    def _append_scores(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["compat_score_exp_0_100"] = 100 * np.exp(-out["distance"])

        dmin = out["distance"].min()
        dmax = out["distance"].max()
        if pd.notna(dmin) and pd.notna(dmax) and dmax > dmin:
            out["compat_score_rank_0_100"] = 100 * (1 - (out["distance"] - dmin) / (dmax - dmin))
        else:
            out["compat_score_rank_0_100"] = 100.0
        return out

    @staticmethod
    def _resolve_target_row(proto: pd.DataFrame) -> Optional[pd.Series]:
        if proto.empty:
            return None
        return proto.iloc[0].copy()

    # ======================================================
    # PREPARACIÓN
    # ======================================================
    def _prepare_proto(self, df: pd.DataFrame) -> pd.DataFrame:
        proto = self.add_merged_pos(df.copy())

        # El archivo app-ready ya trae ui_slot y ui_slot_label.
        # Para que el motor sea robusto, los creamos si no existen.
        if "ui_slot" not in proto.columns:
            if "slot_id" in proto.columns:
                proto["ui_slot"] = proto["slot_id"].astype(str)
            elif "merged_pos_abbr" in proto.columns:
                proto["ui_slot"] = proto["merged_pos_abbr"].astype(str)
            elif "merged_pos" in proto.columns:
                proto["ui_slot"] = proto["merged_pos"].astype(str)
            elif "base_pos" in proto.columns:
                proto["ui_slot"] = proto["base_pos"].astype(str)

        if "merged_pos_abbr" not in proto.columns and "merged_pos" in proto.columns:
            proto["merged_pos_abbr"] = (
                proto["merged_pos"].astype(str)
                .replace({
                    "LEFT_ATTACK_WIDE": "LAW",
                    "RIGHT_ATTACK_WIDE": "RAW",
                    "LEFT_WIDE_MID": "LWM",
                    "RIGHT_WIDE_MID": "RWM",
                })
            )

        if "ui_slot_label" not in proto.columns and "ui_slot" in proto.columns:
            if "dominant_cluster" in proto.columns:
                proto["ui_slot_label"] = proto["ui_slot"].astype(str) + " — " + proto["dominant_cluster"].astype(str)
            else:
                proto["ui_slot_label"] = proto["ui_slot"].astype(str)

        numeric_cols = [c for c in CANDIDATE_FEATURE_COLS if c in proto.columns]
        for c in numeric_cols:
            proto[c] = pd.to_numeric(proto[c], errors="coerce")

        for c in [
            "team_id",
            "n_obs_dominant",
            "dominant_cluster_share",
            "mean_cluster_conf",
            "dominant_cluster_conf_mean",
            "mean_minutes_played",
            "n_matches",
            "total_weight",
            "n_formations",
            "n_slots",
            "n_base_pos",
            "cluster_support",
        ]:
            if c in proto.columns:
                proto[c] = pd.to_numeric(proto[c], errors="coerce")

        for c in ["event_team_name", "formation_final", "slot_id", "base_pos", "merged_pos", "ui_slot", "ui_slot_label"]:
            if c in proto.columns:
                proto[c] = proto[c].astype(str).str.strip()

        return proto

    def _prepare_players(self, df: pd.DataFrame) -> pd.DataFrame:
        players = self.add_merged_pos(df.copy())
        numeric_cols = [c for c in CANDIDATE_FEATURE_COLS if c in players.columns]
        for c in numeric_cols:
            players[c] = pd.to_numeric(players[c], errors="coerce")

        for c in ["height", "player_valuation", "age", "total_minutes_pos", "n_matches_pos", "team_id", "player_id"]:
            if c in players.columns:
                players[c] = pd.to_numeric(players[c], errors="coerce")

        return players

    def _get_name_col(self, df: pd.DataFrame) -> Optional[str]:
        for c in ["lineup_player_name", "player_name", "name"]:
            if c in df.columns:
                return c
        return None

    def _aggregate_players_by_name(
        self,
        players_df: pd.DataFrame,
        pos_group_col: Optional[str] = None,
    ) -> pd.DataFrame:
        df = players_df.copy()
        name_col = self._get_name_col(df)

        if name_col is None:
            return df

        df = df[df[name_col].notna()].copy()
        if df.empty:
            return players_df.copy()

        sort_cols = [c for c in ["total_minutes_pos", "n_matches_pos"] if c in df.columns]
        if sort_cols:
            df = df.sort_values(sort_cols, ascending=False)

        group_keys = [name_col]
        if pos_group_col is not None and pos_group_col in df.columns:
            group_keys.append(pos_group_col)

        mean_cols = [c for c in CANDIDATE_FEATURE_COLS if c in df.columns]
        mean_cols += [c for c in ["height", "player_valuation", "age"] if c in df.columns]

        sum_cols = [c for c in ["total_minutes_pos", "n_matches_pos"] if c in df.columns]

        first_cols = [
            c for c in [
                "player_id",
                "foot",
                "league_key",
                "team_id",
                "event_team_name",
                "base_pos",
                "merged_pos",
                "photo_path",
                "photo_url",
            ]
            if c in df.columns and c not in group_keys and c not in mean_cols and c not in sum_cols
        ]

        agg_dict = {c: "mean" for c in mean_cols}
        agg_dict.update({c: "sum" for c in sum_cols})
        agg_dict.update({c: "first" for c in first_cols})

        out = df.groupby(group_keys, as_index=False).agg(agg_dict)

        if name_col != "lineup_player_name":
            out = out.rename(columns={name_col: "lineup_player_name"})

        return out

    # ======================================================
    # CARGA
    # ======================================================
    def load_proto(self, source_name: str) -> pd.DataFrame:
        if source_name not in self.prototype_sources:
            raise ValueError(f"Fuente de prototipos no válida: {source_name}")

        if source_name not in self._proto_cache:
            raw = load_any_table(self.prototype_sources[source_name])
            self._proto_cache[source_name] = self._prepare_proto(raw)

        return self._proto_cache[source_name].copy()

    def load_proto_merged(self, source_name: str) -> pd.DataFrame:
        if source_name not in self.merged_prototype_sources:
            raise ValueError(f"Fuente de prototipos merged no válida: {source_name}")

        if source_name not in self._merged_proto_cache:
            raw = load_any_table(self.merged_prototype_sources[source_name])
            self._merged_proto_cache[source_name] = self._prepare_proto(raw)

        return self._merged_proto_cache[source_name].copy()

    def load_players(self) -> pd.DataFrame:
        if self._players_cache is None:
            raw = load_any_table(self.player_path)
            self._players_cache = self._prepare_players(raw)

        return self._players_cache.copy()

    # ======================================================
    # FILTRO GENERAL
    # ======================================================
    def filter_data(
        self,
        proto_df: pd.DataFrame,
        players_df: pd.DataFrame,
        min_proto_obs: int,
        min_dominant_share: float,
        min_player_minutes: int,
        min_player_matches: int,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        proto = proto_df.copy()
        players = players_df.copy()

        if "n_obs_dominant" in proto.columns:
            proto = proto[proto["n_obs_dominant"].fillna(0) >= min_proto_obs].copy()

        if "dominant_cluster_share" in proto.columns:
            proto = proto[proto["dominant_cluster_share"].fillna(0) >= min_dominant_share].copy()

        if "total_minutes_pos" in players.columns:
            players = players[players["total_minutes_pos"].fillna(0) >= min_player_minutes].copy()

        if "n_matches_pos" in players.columns:
            players = players[players["n_matches_pos"].fillna(0) >= min_player_matches].copy()

        return proto, players

    # ======================================================
    # UI HELPERS
    # ======================================================
    def get_team_options(self, proto_df: pd.DataFrame) -> List[str]:
        if "event_team_name" not in proto_df.columns:
            return []
        return sorted(self._safe_string_series(proto_df, "event_team_name").unique().tolist())

    def get_position_options(self, proto_df: pd.DataFrame, team_name: Optional[str] = None) -> List[str]:
        df = proto_df.copy()

        if team_name and "event_team_name" in df.columns:
            df = df[df["event_team_name"].astype(str) == str(team_name)].copy()

        if "slot_id" in df.columns:
            vals = sorted(self._safe_string_series(df, "slot_id").unique().tolist())
            if vals:
                return vals

        if "base_pos" in df.columns:
            return sorted(self._safe_string_series(df, "base_pos").unique().tolist())

        return []

    def get_merged_position_options(self, proto_df: pd.DataFrame, team_name: Optional[str] = None) -> List[str]:
        df = self.add_merged_pos(proto_df.copy())

        if team_name and "event_team_name" in df.columns:
            df = df[df["event_team_name"].astype(str) == str(team_name)].copy()

        if "merged_pos" in df.columns:
            return sorted(self._safe_string_series(df, "merged_pos").unique().tolist())

        return []

    @staticmethod
    def _slot_sort_key(value: str) -> Tuple[int, int, str]:
        """
        Orden táctico aproximado para pintar la cancha y mostrar selectores.
        """
        raw = str(value).strip()
        base = raw.split("_")[0]
        suffix = 0
        if "_" in raw:
            tail = raw.rsplit("_", 1)[-1]
            if tail.isdigit():
                suffix = int(tail)

        order = {
            "GK": 0,
            "DL": 10, "DC": 11, "DR": 12,
            "DML": 20, "DMC": 21, "DMR": 22,
            "LWM": 29, "ML": 30, "MC": 31, "MR": 32, "RWM": 33,
            "AMC": 40,
            "LAW": 50, "AML": 51, "FWL": 52,
            "FW": 53,
            "RAW": 54, "AMR": 55, "FWR": 56,
        }
        return (order.get(base, 999), suffix, raw)

    def get_formation_options(self, proto_df: pd.DataFrame, team_name: Optional[str] = None) -> List[str]:
        df = proto_df.copy()

        if team_name and "event_team_name" in df.columns:
            df = df[df["event_team_name"].astype(str) == str(team_name)].copy()

        if "formation_final" not in df.columns:
            return []

        vals = self._safe_string_series(df, "formation_final").unique().tolist()

        # Si existe n_matches, priorizamos formaciones con más soporte observado.
        if vals and "n_matches" in df.columns:
            support = (
                df.groupby("formation_final", dropna=False)["n_matches"]
                .sum()
                .sort_values(ascending=False)
            )
            ordered = [str(x) for x in support.index.tolist() if str(x) in set(map(str, vals))]
            return ordered

        return sorted([str(v) for v in vals])

    def get_slot_options(
        self,
        proto_df: pd.DataFrame,
        team_name: Optional[str] = None,
        formation_final: Optional[str] = None,
    ) -> List[str]:
        df = proto_df.copy()

        if team_name and "event_team_name" in df.columns:
            df = df[df["event_team_name"].astype(str) == str(team_name)].copy()

        if formation_final and "formation_final" in df.columns:
            df = df[df["formation_final"].astype(str) == str(formation_final)].copy()

        slot_col = "ui_slot" if "ui_slot" in df.columns else ("slot_id" if "slot_id" in df.columns else None)
        if slot_col is None:
            return self.get_merged_position_options(df, team_name=None)

        vals = self._safe_string_series(df, slot_col).unique().tolist()
        return sorted([str(v) for v in vals], key=self._slot_sort_key)

    def get_slot_row(
        self,
        proto_df: pd.DataFrame,
        team_name: str,
        formation_final: str,
        ui_slot: str,
    ) -> Optional[pd.Series]:
        df = proto_df.copy()

        if "event_team_name" in df.columns:
            df = df[df["event_team_name"].astype(str) == str(team_name)].copy()
        if "formation_final" in df.columns:
            df = df[df["formation_final"].astype(str) == str(formation_final)].copy()

        slot_col = "ui_slot" if "ui_slot" in df.columns else ("slot_id" if "slot_id" in df.columns else None)
        if slot_col is None:
            return None

        df = df[df[slot_col].astype(str) == str(ui_slot)].copy()
        if df.empty:
            return None

        # Si por alguna razón hay más de una fila, usamos la de mayor soporte.
        support_cols = [c for c in ["n_obs_dominant", "n_matches", "mean_minutes_played"] if c in df.columns]
        if support_cols:
            df = df.sort_values(support_cols, ascending=[False] * len(support_cols))

        return df.iloc[0].copy()

    def shared_feature_cols(self, proto_df: pd.DataFrame, players_df: pd.DataFrame, feature_set: str = "full") -> List[str]:
        return self.get_feature_cols(proto_df, players_df, feature_set=feature_set)

    # ======================================================
    # REGLAS AUTO
    # ======================================================
    def infer_auto_preferred_foot(self, base_pos: str, slot_or_pos: Optional[str] = None) -> Optional[str]:
        pos = str(base_pos).upper() if base_pos is not None else ""
        slot = str(slot_or_pos).upper() if slot_or_pos is not None else ""

        left_like = {"DL", "DML", "ML", "AML", "FWL", "LEFT_WIDE_MID", "LEFT_ATTACK_WIDE", "LAW", "LWM"}
        right_like = {"DR", "DMR", "MR", "AMR", "FWR", "RIGHT_WIDE_MID", "RIGHT_ATTACK_WIDE", "RAW", "RWM"}

        if pos in left_like or slot in left_like:
            return "left"
        if pos in right_like or slot in right_like:
            return "right"
        return None

    def infer_auto_min_height(self, base_pos: str) -> Optional[float]:
        return DEFAULT_MIN_HEIGHT_BY_BASE_POS.get(str(base_pos).upper(), None)

    def build_team_budget_map(self, players_df: pd.DataFrame, divisor: float = 6.0) -> pd.DataFrame:
        df = players_df.copy()

        if "player_valuation" not in df.columns or "event_team_name" not in df.columns:
            return pd.DataFrame(
                columns=[
                    "event_team_name",
                    "team_total_valuation",
                    "team_mean_valuation",
                    "n_players",
                    "max_value_target_team",
                ]
            )

        df["player_valuation"] = pd.to_numeric(df["player_valuation"], errors="coerce")

        if "player_id" in df.columns:
            dedupe_keys = ["event_team_name", "player_id"]
        elif "lineup_player_name" in df.columns:
            dedupe_keys = ["event_team_name", "lineup_player_name"]
        else:
            return pd.DataFrame(
                columns=[
                    "event_team_name",
                    "team_total_valuation",
                    "team_mean_valuation",
                    "n_players",
                    "max_value_target_team",
                ]
            )

        sort_cols = [c for c in ["total_minutes_pos", "n_matches_pos"] if c in df.columns]
        if sort_cols:
            df = df.sort_values(sort_cols, ascending=False)

        squad = df.drop_duplicates(subset=dedupe_keys, keep="first").copy()

        team_budget = (
            squad.groupby("event_team_name", as_index=False)
            .agg(
                team_total_valuation=("player_valuation", "sum"),
                team_mean_valuation=("player_valuation", "mean"),
                n_players=("player_valuation", "count"),
            )
        )

        team_budget["max_value_target_team"] = team_budget["team_total_valuation"] / float(divisor)
        return team_budget

    def get_team_budget_value(
        self,
        players_df: pd.DataFrame,
        team_name: str,
        divisor: float = 6.0,
    ) -> Tuple[float, float, float]:
        budget_map = self.build_team_budget_map(players_df, divisor=divisor)
        row = budget_map[budget_map["event_team_name"].astype(str) == str(team_name)]
        if row.empty:
            return np.nan, np.nan, np.nan
        return (
            row["team_total_valuation"].iloc[0],
            row["team_mean_valuation"].iloc[0],
            row["max_value_target_team"].iloc[0],
        )

    # ======================================================
    # SCORE TÁCTICO PURO - BASE
    # ======================================================
    def compute_for_target(
        self,
        proto_df: pd.DataFrame,
        players_df: pd.DataFrame,
        team_name: str,
        slot_or_pos: str,
        allowed_leagues: Optional[List[str]] = None,
        exclude_same_team: bool = True,
        score_method: str = "compat_score_rank_0_100",
        feature_set: str = "full",
        metric: str = "euclidean",
    ) -> Tuple[pd.DataFrame, Optional[pd.Series], List[str]]:
        feature_set = self.normalize_feature_set(feature_set)
        metric = self.normalize_metric(metric)

        proto = self.add_merged_pos(proto_df.copy())
        players = self.add_merged_pos(players_df.copy())

        if allowed_leagues and "league_key" in players.columns:
            players = players[players["league_key"].isin(allowed_leagues)].copy()

        proto = proto[proto["event_team_name"].astype(str) == str(team_name)].copy()
        if proto.empty:
            return pd.DataFrame(), None, []

        if "slot_id" in proto.columns and slot_or_pos in proto["slot_id"].astype(str).unique().tolist():
            proto = proto[proto["slot_id"].astype(str) == str(slot_or_pos)].copy()
        else:
            proto = proto[proto["base_pos"].astype(str) == str(slot_or_pos)].copy()

        if proto.empty:
            return pd.DataFrame(), None, []

        proto_row = self._resolve_target_row(proto)
        if proto_row is None:
            return pd.DataFrame(), None, []

        base_pos = str(proto_row["base_pos"])
        players = players[players["base_pos"].astype(str) == base_pos].copy()
        if players.empty:
            return pd.DataFrame(), proto_row, []

        if exclude_same_team and "team_id" in players.columns and "team_id" in proto.columns:
            target_team_id = proto["team_id"].iloc[0]
            players = players[players["team_id"] != target_team_id].copy()

        if players.empty:
            return pd.DataFrame(), proto_row, []

        players = self._aggregate_players_by_name(players, pos_group_col="base_pos")
        if players.empty:
            return pd.DataFrame(), proto_row, []

        shared_cols = self.shared_feature_cols(proto, players, feature_set=feature_set)
        if len(shared_cols) == 0:
            return pd.DataFrame(), proto_row, []

        min_required = max(10, int(0.05 * len(players)))
        valid_cols = [c for c in shared_cols if players[c].notna().sum() >= min_required]
        if len(valid_cols) < 5:
            return pd.DataFrame(), proto_row, valid_cols

        X_players = players[valid_cols].copy()
        X_players = X_players.fillna(X_players.median(numeric_only=True)).fillna(0.0)

        X_proto = proto[valid_cols].copy()
        X_proto = X_proto.fillna(X_players.median(numeric_only=True)).fillna(0.0)

        scaler = StandardScaler()
        X_players_z = scaler.fit_transform(X_players)
        X_proto_z = scaler.transform(X_proto)

        proto_vec = X_proto_z[0]
        dist = self._compute_distance(X_players_z, proto_vec, metric=metric)

        res = players.copy()
        res["prototype_team_name"] = proto_row.get("event_team_name", np.nan)
        res["prototype_slot_id"] = proto_row.get("slot_id", proto_row.get("base_pos", np.nan))
        res["prototype_base_pos"] = proto_row.get("base_pos", np.nan)
        res["prototype_cluster"] = proto_row.get("dominant_cluster", np.nan)
        res["prototype_formation"] = proto_row.get("formation_final", np.nan)
        res["n_features_used"] = len(valid_cols)
        res["feature_set"] = feature_set

        for idx, c in enumerate(valid_cols):
            res[f"z_{c}"] = X_players_z[:, idx]
            res[f"proto_z_{c}"] = X_proto_z[0, idx]

        res = self._append_distance_columns(res, dist, metric=metric)
        res = self._append_scores(res)

        res = res.sort_values(score_method, ascending=False).copy()
        res["rank"] = np.arange(1, len(res) + 1)

        return res, proto_row, valid_cols

    # ======================================================
    # SCORE TÁCTICO PURO - MERGED
    # ======================================================
    def compute_for_target_merged(
        self,
        proto_df: pd.DataFrame,
        players_df: pd.DataFrame,
        team_name: str,
        merged_pos: str,
        allowed_leagues: Optional[List[str]] = None,
        exclude_same_team: bool = True,
        score_method: str = "compat_score_rank_0_100",
        feature_set: str = "full",
        metric: str = "euclidean",
    ) -> Tuple[pd.DataFrame, Optional[pd.Series], List[str]]:
        feature_set = self.normalize_feature_set(feature_set)
        metric = self.normalize_metric(metric)

        proto = self.add_merged_pos(proto_df.copy())
        players = self.add_merged_pos(players_df.copy())

        if allowed_leagues and "league_key" in players.columns:
            players = players[players["league_key"].isin(allowed_leagues)].copy()

        proto = proto[proto["event_team_name"].astype(str) == str(team_name)].copy()
        if proto.empty:
            return pd.DataFrame(), None, []

        proto = proto[proto["merged_pos"].astype(str) == str(merged_pos)].copy()
        if proto.empty:
            return pd.DataFrame(), None, []

        proto_row = self._resolve_target_row(proto)
        if proto_row is None:
            return pd.DataFrame(), None, []

        players = players[players["merged_pos"].astype(str) == str(merged_pos)].copy()
        if players.empty:
            return pd.DataFrame(), proto_row, []

        if exclude_same_team and "team_id" in players.columns and "team_id" in proto.columns:
            target_team_id = proto["team_id"].iloc[0]
            players = players[players["team_id"] != target_team_id].copy()

        if players.empty:
            return pd.DataFrame(), proto_row, []

        players = self._aggregate_players_by_name(players, pos_group_col="merged_pos")
        if players.empty:
            return pd.DataFrame(), proto_row, []

        shared_cols = self.shared_feature_cols(proto, players, feature_set=feature_set)
        if len(shared_cols) == 0:
            return pd.DataFrame(), proto_row, []

        min_required = max(10, int(0.05 * len(players)))
        valid_cols = [c for c in shared_cols if players[c].notna().sum() >= min_required]
        if len(valid_cols) < 5:
            return pd.DataFrame(), proto_row, valid_cols

        X_players = players[valid_cols].copy()
        X_players = X_players.fillna(X_players.median(numeric_only=True)).fillna(0.0)

        X_proto = proto[valid_cols].copy()
        X_proto = X_proto.fillna(X_players.median(numeric_only=True)).fillna(0.0)

        scaler = StandardScaler()
        X_players_z = scaler.fit_transform(X_players)
        X_proto_z = scaler.transform(X_proto)

        proto_vec = X_proto_z[0]
        dist = self._compute_distance(X_players_z, proto_vec, metric=metric)

        res = players.copy()
        res["prototype_team_name"] = proto_row.get("event_team_name", np.nan)
        res["prototype_merged_pos"] = proto_row.get("merged_pos", np.nan)
        res["prototype_cluster"] = proto_row.get("dominant_cluster", np.nan)
        res["prototype_formation"] = proto_row.get("formation_final", np.nan)
        res["n_features_used"] = len(valid_cols)
        res["feature_set"] = feature_set

        for idx, c in enumerate(valid_cols):
            res[f"z_{c}"] = X_players_z[:, idx]
            res[f"proto_z_{c}"] = X_proto_z[0, idx]

        res = self._append_distance_columns(res, dist, metric=metric)
        res = self._append_scores(res)

        res = res.sort_values(score_method, ascending=False).copy()
        res["rank"] = np.arange(1, len(res) + 1)

        return res, proto_row, valid_cols

    # ======================================================
    # SCORE TÁCTICO PURO - SLOT APP READY
    # ======================================================
    def compute_for_target_slot(
        self,
        proto_df: pd.DataFrame,
        players_df: pd.DataFrame,
        team_name: str,
        formation_final: str,
        ui_slot: str,
        allowed_leagues: Optional[List[str]] = None,
        exclude_same_team: bool = True,
        score_method: str = "compat_score_rank_0_100",
        feature_set: str = "full",
        metric: str = "euclidean",
    ) -> Tuple[pd.DataFrame, Optional[pd.Series], List[str]]:
        """
        Calcula compatibilidad contra un prototipo específico:
        equipo + formación + slot táctico.

        Ejemplo:
        Arsenal + 4-3-3 + DC_1.

        Los candidatos se filtran por el grupo posicional merged del prototipo.
        Así, DC_1 y DC_2 usan candidatos DC, pero cada uno contra su propio perfil.
        """
        feature_set = self.normalize_feature_set(feature_set)
        metric = self.normalize_metric(metric)

        proto = self.add_merged_pos(proto_df.copy())
        players = self.add_merged_pos(players_df.copy())

        if allowed_leagues and "league_key" in players.columns:
            players = players[players["league_key"].isin(allowed_leagues)].copy()

        proto_row = self.get_slot_row(
            proto_df=proto,
            team_name=team_name,
            formation_final=formation_final,
            ui_slot=ui_slot,
        )
        if proto_row is None:
            return pd.DataFrame(), None, []

        # Dejamos proto como DataFrame de una fila para reutilizar el flujo.
        proto = pd.DataFrame([proto_row]).copy()

        candidate_merged_pos = proto_row.get("merged_pos", np.nan)
        candidate_base_pos = proto_row.get("base_pos", np.nan)

        if pd.notna(candidate_merged_pos) and "merged_pos" in players.columns:
            players = players[players["merged_pos"].astype(str) == str(candidate_merged_pos)].copy()
        elif pd.notna(candidate_base_pos) and "base_pos" in players.columns:
            players = players[players["base_pos"].astype(str) == str(candidate_base_pos)].copy()
        else:
            return pd.DataFrame(), proto_row, []

        if players.empty:
            return pd.DataFrame(), proto_row, []

        if exclude_same_team and "team_id" in players.columns and "team_id" in proto.columns:
            target_team_id = proto["team_id"].iloc[0]
            players = players[players["team_id"] != target_team_id].copy()

        if players.empty:
            return pd.DataFrame(), proto_row, []

        # Agrupamos por jugador dentro del grupo posicional candidato para evitar duplicados.
        group_col = "merged_pos" if "merged_pos" in players.columns else "base_pos"
        players = self._aggregate_players_by_name(players, pos_group_col=group_col)
        if players.empty:
            return pd.DataFrame(), proto_row, []

        shared_cols = self.shared_feature_cols(proto, players, feature_set=feature_set)
        if len(shared_cols) == 0:
            return pd.DataFrame(), proto_row, []

        min_required = max(10, int(0.05 * len(players)))
        valid_cols = [c for c in shared_cols if players[c].notna().sum() >= min_required]
        if len(valid_cols) < 5:
            return pd.DataFrame(), proto_row, valid_cols

        X_players = players[valid_cols].copy()
        X_players = X_players.fillna(X_players.median(numeric_only=True)).fillna(0.0)

        X_proto = proto[valid_cols].copy()
        X_proto = X_proto.fillna(X_players.median(numeric_only=True)).fillna(0.0)

        scaler = StandardScaler()
        X_players_z = scaler.fit_transform(X_players)
        X_proto_z = scaler.transform(X_proto)

        proto_vec = X_proto_z[0]
        dist = self._compute_distance(X_players_z, proto_vec, metric=metric)

        res = players.copy()
        res["prototype_team_name"] = proto_row.get("event_team_name", np.nan)
        res["prototype_formation"] = proto_row.get("formation_final", np.nan)
        res["prototype_slot_id"] = proto_row.get("slot_id", proto_row.get("ui_slot", np.nan))
        res["prototype_ui_slot"] = proto_row.get("ui_slot", proto_row.get("slot_id", np.nan))
        res["prototype_ui_slot_label"] = proto_row.get("ui_slot_label", proto_row.get("ui_slot", np.nan))
        res["prototype_base_pos"] = proto_row.get("base_pos", np.nan)
        res["prototype_merged_pos"] = proto_row.get("merged_pos", np.nan)
        res["prototype_cluster"] = proto_row.get("dominant_cluster", np.nan)
        res["n_features_used"] = len(valid_cols)
        res["feature_set"] = feature_set

        for idx, c in enumerate(valid_cols):
            res[f"z_{c}"] = X_players_z[:, idx]
            res[f"proto_z_{c}"] = X_proto_z[0, idx]

        res = self._append_distance_columns(res, dist, metric=metric)
        res = self._append_scores(res)

        res = res.sort_values(score_method, ascending=False).copy()
        res["rank"] = np.arange(1, len(res) + 1)

        return res, proto_row, valid_cols

    # ======================================================
    # PERFIL DEL PROTOTIPO SELECCIONADO
    # ======================================================
    @staticmethod
    def _feature_type_label(feature: str) -> str:
        f = str(feature)
        if f.endswith("_p90"):
            return "Por 90 minutos"
        if "share" in f or f in {"pass_acc", "wide_share", "central_share"}:
            return "Proporción / participación"
        if f.startswith("mean_") or f.endswith("_mean") or f.startswith("avg_"):
            return "Promedio / ubicación"
        if f.startswith("std_"):
            return "Dispersión espacial"
        if f.startswith("passdir_"):
            return "Dirección de pase"
        return "Variable de perfil"

    def build_prototype_profile_table(
        self,
        proto_row: Optional[pd.Series],
        valid_cols: Optional[List[str]] = None,
        include_only_candidate_features: bool = True,
    ) -> pd.DataFrame:
        """
        Convierte la fila del prototipo seleccionado en una tabla legible para la app.
        Por defecto muestra las variables candidatas del índice, marcando cuáles sí se usaron.
        """
        if proto_row is None:
            return pd.DataFrame()

        if not isinstance(proto_row, pd.Series):
            proto_row = pd.Series(proto_row)

        used_set = set(valid_cols or [])

        area_lookup = {}
        for block_name, cols in TACTICAL_BLOCKS.items():
            for c in cols:
                area_lookup[c] = block_name

        area_labels = {
            "progression": "Progresión",
            "passing": "Pase",
            "spatial": "Ocupación espacial",
            "defensive": "Defensa",
            "offensive": "Ataque",
            "team_context": "Participación en equipo",
        }

        if include_only_candidate_features:
            candidate_cols = [c for c in CANDIDATE_FEATURE_COLS if c in proto_row.index]
        else:
            candidate_cols = [
                c for c in proto_row.index
                if c not in {
                    "team_id", "event_team_name", "formation_final", "slot_id",
                    "base_pos", "merged_pos", "dominant_cluster", "ui_slot",
                    "prototype_key", "ui_slot_label", "merged_pos_abbr"
                }
            ]

        rows = []
        for c in candidate_cols:
            value = pd.to_numeric(pd.Series([proto_row.get(c, np.nan)]), errors="coerce").iloc[0]
            formatted_value = np.nan if pd.isna(value) else float(value)

            block = area_lookup.get(c, "other")
            rows.append({
                "Área táctica": area_labels.get(block, "Otras variables"),
                "Variable": c,
                "Valor del prototipo": formatted_value,
                "Usada en índice": "Sí" if c in used_set else "No",
                "Tipo": self._feature_type_label(c),
            })

        out = pd.DataFrame(rows)
        if out.empty:
            return out

        out["Valor del prototipo"] = pd.to_numeric(out["Valor del prototipo"], errors="coerce").round(4)
        out["_used_order"] = out["Usada en índice"].map({"Sí": 0, "No": 1}).fillna(2)
        out = out.sort_values(["Área táctica", "_used_order", "Variable"]).drop(columns=["_used_order"]).reset_index(drop=True)
        return out

    # ======================================================
    # BLOQUES TÁCTICOS Y SCORE COMPUESTO
    # ======================================================
    def add_block_similarity_scores(
        self,
        result_df: pd.DataFrame,
        valid_cols: List[str],
        block_scale: float = 1.5,
    ) -> pd.DataFrame:
        df = result_df.copy()
        if df.empty or len(valid_cols) == 0:
            return df

        usable_cols = [c for c in valid_cols if f"z_{c}" in df.columns and f"proto_z_{c}" in df.columns]
        if len(usable_cols) == 0:
            return df

        block_score_cols: List[str] = []
        block_feature_count_cols: List[str] = []

        for block_name, block_cols in TACTICAL_BLOCKS.items():
            cols = [c for c in block_cols if c in usable_cols]
            score_col = f"block_similarity_{block_name}_0_100"
            weight_col = f"n_features_{block_name}"

            if len(cols) == 0:
                df[score_col] = np.nan
                df[weight_col] = 0
                continue

            diffs = []
            for c in cols:
                diff = (pd.to_numeric(df[f"z_{c}"], errors="coerce") - pd.to_numeric(df[f"proto_z_{c}"], errors="coerce")).abs()
                diffs.append(diff.rename(c))

            diff_df = pd.concat(diffs, axis=1)
            mean_abs_diff_z = diff_df.mean(axis=1)

            df[score_col] = np.clip(100.0 * np.exp(-(mean_abs_diff_z / block_scale)), 0.0, 100.0)
            df[weight_col] = len(cols)

            block_score_cols.append(score_col)
            block_feature_count_cols.append(weight_col)

        if block_score_cols:
            num = np.zeros(len(df), dtype=float)
            den = np.zeros(len(df), dtype=float)

            for s_col, w_col in zip(block_score_cols, block_feature_count_cols):
                s = pd.to_numeric(df[s_col], errors="coerce").fillna(0.0).to_numpy()
                w = pd.to_numeric(df[w_col], errors="coerce").fillna(0.0).to_numpy()
                num += s * w
                den += w

            df["block_similarity_score_0_100"] = np.where(den > 0, num / den, np.nan)
        else:
            df["block_similarity_score_0_100"] = np.nan

        return df

    # ======================================================
    # DIAGNÓSTICO JUGADOR VS PROTOTIPO
    # ======================================================
    def explain_player_vs_prototype(
        self,
        result_df: pd.DataFrame,
        proto_row: pd.Series,
        valid_cols: List[str],
        player_name: str,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        if result_df.empty or proto_row is None or len(valid_cols) == 0:
            return pd.DataFrame(), pd.DataFrame()

        name_col = None
        for c in ["lineup_player_name", "player_name", "name"]:
            if c in result_df.columns:
                name_col = c
                break

        if name_col is None:
            return pd.DataFrame(), pd.DataFrame()

        player_df = result_df[result_df[name_col].astype(str) == str(player_name)].copy()
        if player_df.empty:
            return pd.DataFrame(), pd.DataFrame()

        row = player_df.iloc[0]

        records = []
        contrib_den = 0.0
        contrib_vals = {}

        for c in valid_cols:
            player_val = pd.to_numeric(pd.Series([row.get(c, np.nan)]), errors="coerce").iloc[0]
            proto_val = pd.to_numeric(pd.Series([proto_row.get(c, np.nan)]), errors="coerce").iloc[0]
            player_z = pd.to_numeric(pd.Series([row.get(f"z_{c}", np.nan)]), errors="coerce").iloc[0]
            proto_z = pd.to_numeric(pd.Series([row.get(f"proto_z_{c}", np.nan)]), errors="coerce").iloc[0]

            abs_diff = np.nan
            abs_z_diff = np.nan

            if pd.notna(player_val) and pd.notna(proto_val):
                abs_diff = abs(player_val - proto_val)

            if pd.notna(player_z) and pd.notna(proto_z):
                abs_z_diff = abs(player_z - proto_z)
                contrib = abs_z_diff ** 2
                contrib_vals[c] = contrib
                contrib_den += contrib

            records.append({
                "feature": c,
                "prototype_value": proto_val,
                "player_value": player_val,
                "abs_diff_raw": abs_diff,
                "prototype_z": proto_z,
                "player_z": player_z,
                "abs_diff_z": abs_z_diff,
            })

        variable_df = pd.DataFrame(records)

        if not variable_df.empty:
            if contrib_den > 0:
                variable_df["distance_contribution_pct"] = variable_df["feature"].map(
                    lambda x: 100.0 * contrib_vals.get(x, 0.0) / contrib_den
                )
            else:
                variable_df["distance_contribution_pct"] = 0.0

            variable_df["similarity_var_0_100"] = 100.0 * np.exp(-(variable_df["abs_diff_z"].fillna(0.0) / 1.5))
            variable_df["status"] = pd.cut(
                variable_df["abs_diff_z"].fillna(np.inf),
                bins=[-np.inf, 0.50, 1.00, np.inf],
                labels=["verde", "amarillo", "rojo"]
            )
            variable_df = variable_df.sort_values(["abs_diff_z", "feature"], ascending=[True, True]).reset_index(drop=True)

        block_records = []
        for block_name, block_cols in TACTICAL_BLOCKS.items():
            cols = [c for c in block_cols if c in valid_cols]
            if len(cols) == 0:
                continue

            sub = variable_df[variable_df["feature"].isin(cols)].copy()
            if sub.empty:
                continue

            proto_block_z_mean = pd.to_numeric(sub["prototype_z"], errors="coerce").mean()
            player_block_z_mean = pd.to_numeric(sub["player_z"], errors="coerce").mean()
            mean_abs_diff_z = pd.to_numeric(sub["abs_diff_z"], errors="coerce").mean()
            mean_signed_diff_z = player_block_z_mean - proto_block_z_mean

            block_records.append({
                "block": block_name,
                "n_features": len(cols),
                "prototype_block_z_mean": proto_block_z_mean,
                "player_block_z_mean": player_block_z_mean,
                "mean_signed_diff_z": mean_signed_diff_z,
                "mean_abs_diff_z": mean_abs_diff_z,
                "block_similarity_0_100": 100.0 * np.exp(-(mean_abs_diff_z / 1.5)),
                "distance_contribution_pct": sub["distance_contribution_pct"].sum(),
            })

        block_df = pd.DataFrame(block_records)
        if not block_df.empty:
            block_df["prototype_vs_player"] = np.where(
                block_df["mean_signed_diff_z"] > 0.15,
                "por encima",
                np.where(
                    block_df["mean_signed_diff_z"] < -0.15,
                    "por debajo",
                    "alineado"
                )
            )
            block_df = block_df.sort_values("block_similarity_0_100", ascending=False).reset_index(drop=True)

        return variable_df, block_df

    # ======================================================
    # PENALIZACIONES
    # ======================================================
    @staticmethod
    def _foot_penalty(player_foot, preferred_foot, profile):
        if preferred_foot is None:
            return 1.0
        if pd.isna(player_foot):
            return profile["foot_wrong"]

        pf = str(player_foot).strip().lower()
        rf = str(preferred_foot).strip().lower()

        if pf == rf:
            return 1.0
        if pf == "both":
            return profile["foot_both"]
        return profile["foot_wrong"]

    @staticmethod
    def _min_height_penalty(player_height, min_height, profile):
        if min_height is None:
            return 1.0
        if pd.isna(player_height):
            return profile["height_floor"]

        h = float(player_height)
        hmin = float(min_height)

        if h >= hmin:
            return 1.0

        gap = hmin - h
        frac = min(gap / profile["height_tol"], 1.0)
        pen = 1.0 - profile["height_lambda"] * frac
        return float(max(profile["height_floor"], min(1.0, pen)))

    @staticmethod
    def _max_value_penalty(player_value, max_value_target, profile):
        if max_value_target is None or pd.isna(max_value_target):
            return 1.0
        if pd.isna(player_value):
            return profile["value_floor"]

        v = float(player_value)
        vmax = float(max_value_target)

        if vmax <= 0:
            return profile["value_floor"]

        if v <= vmax:
            return 1.0

        pen = (vmax / v) ** profile["value_alpha"]
        return float(max(profile["value_floor"], min(1.0, pen)))

    @staticmethod
    def _age_range_penalty(player_age, min_age, max_age, profile):
        """
        Penalización suave por edad fuera del rango preferido.
        Penaliza desde el primer año fuera del rango, pero cae de forma no lineal:
        1 año casi no afecta, 3 años afecta moderadamente y 5-7 años afecta fuerte.
        """
        if min_age is None and max_age is None:
            return 1.0
        if pd.isna(player_age):
            return float(profile.get("age_missing", profile.get("age_floor", 0.88)))

        age = float(player_age)
        gap = 0.0
        if min_age is not None and pd.notna(min_age) and age < float(min_age):
            gap = float(min_age) - age
        elif max_age is not None and pd.notna(max_age) and age > float(max_age):
            gap = age - float(max_age)

        if gap <= 0:
            return 1.0

        scale = float(profile.get("age_scale", 7.0))
        power = float(profile.get("age_power", 3.0))
        floor = float(profile.get("age_floor", 0.50))
        pen = 1.0 / (1.0 + (gap / scale) ** power)
        return float(max(floor, min(1.0, pen)))

    def apply_penalties(
        self,
        result_df: pd.DataFrame,
        preferred_foot: Optional[str] = None,
        min_height: Optional[float] = None,
        max_value_target: Optional[float] = None,
        min_age: Optional[float] = None,
        max_age: Optional[float] = None,
        scenario_name: str = "medium",
        custom_profile: Optional[Dict[str, float]] = None,
        tactical_base_col: str = "compat_score_rank_0_100",
    ) -> pd.DataFrame:
        if result_df.empty:
            return result_df.copy()

        if tactical_base_col not in result_df.columns:
            raise ValueError(f"No existe la columna {tactical_base_col} en result_df.")

        if scenario_name == "custom":
            if custom_profile is None:
                raise ValueError("Si scenario_name='custom', debes pasar custom_profile.")
            profile = custom_profile.copy()
        else:
            profile = DEFAULT_PENALTY_PROFILES[scenario_name].copy()

        df = result_df.copy()

        foot_col = next((c for c in ["foot", "preferred_foot", "strong_foot", "player_foot"] if c in df.columns), None)
        height_col = next((c for c in ["height", "player_height"] if c in df.columns), None)
        value_col = next((c for c in ["player_valuation", "market_value", "market_value_eur", "player_market_value"] if c in df.columns), None)
        age_col = next((c for c in ["age", "player_age", "edad"] if c in df.columns), None)

        df["preferred_foot_target"] = preferred_foot
        df["min_height_target"] = min_height
        df["max_value_target"] = max_value_target
        df["min_age_target"] = min_age
        df["max_age_target"] = max_age

        if foot_col is not None:
            df["penalty_foot"] = [self._foot_penalty(f, preferred_foot, profile) for f in df[foot_col]]
        else:
            df["penalty_foot"] = 1.0

        if height_col is not None:
            df["penalty_height"] = [self._min_height_penalty(h, min_height, profile) for h in df[height_col]]
        else:
            df["penalty_height"] = 1.0

        if value_col is not None:
            df["penalty_value"] = [self._max_value_penalty(v, max_value_target, profile) for v in df[value_col]]
        else:
            df["penalty_value"] = 1.0

        if age_col is not None:
            df["penalty_age"] = [self._age_range_penalty(a, min_age, max_age, profile) for a in df[age_col]]
        else:
            df["penalty_age"] = 1.0

        df["penalty_total"] = df["penalty_foot"] * df["penalty_height"] * df["penalty_value"] * df["penalty_age"]
        df["final_scouting_score_0_100"] = df[tactical_base_col] * df["penalty_total"]
        df["score_delta"] = df[tactical_base_col] - df["final_scouting_score_0_100"]

        df = df.sort_values(
            ["final_scouting_score_0_100", "score_delta"],
            ascending=[False, False]
        ).copy()

        df["rank_scouting"] = np.arange(1, len(df) + 1)

        return df