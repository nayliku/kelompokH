"""
Dashboard Streamlit — World Bank International Education
Proyek ADBC | Analisis Data End-to-End
Warna tema: Pink Fresh & Soft
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── KONFIGURASI HALAMAN ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Pendidikan Dunia",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── TEMA PINK FRESH ──────────────────────────────────────────────────────────
PINK_PRIMARY   = "#FF6B9D"   # Hot pink
PINK_LIGHT     = "#FFB3D1"   # Soft pink
PINK_PALE      = "#FFE4F0"   # Pastel pink (background card)
PINK_DEEP      = "#E91E8C"   # Deep rose
PINK_ACCENT    = "#FF4081"   # Accent
PINK_LAVENDER  = "#F8BBD9"   # Lavender pink
WHITE          = "#FFFFFF"
GRAY_TEXT      = "#5A4A5A"
DARK_BG        = "#FFF0F7"   # Very pale pink background

# Warna chart: pink palette + kontras
CHART_COLORS   = ["#FF6B9D", "#FF4081", "#C2185B", "#FF80AB", "#F48FB1",
                  "#AD1457", "#FF8A80", "#E040FB"]

# ── CSS KUSTOM ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');

    /* Seluruh background */
    .stApp {{
        background-color: {DARK_BG};
        font-family: 'Poppins', sans-serif;
        color: {GRAY_TEXT};
    }}

    /* Header utama */
    h1 {{
        font-family: 'Playfair Display', serif !important;
        color: {PINK_DEEP} !important;
        font-size: 2.4rem !important;
    }}
    h2, h3 {{
        color: {PINK_PRIMARY} !important;
        font-family: 'Poppins', sans-serif !important;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(160deg, {PINK_PRIMARY}, {PINK_DEEP}) !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: white !important;
    }}
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stSlider label {{
        color: white !important;
        font-weight: 500 !important;
    }}

    /* Metric card */
    div[data-testid="metric-container"] {{
        background: {WHITE};
        border: 2px solid {PINK_LIGHT};
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: 0 4px 15px rgba(255,107,157,0.15);
    }}
    div[data-testid="metric-container"] label {{
        color: {PINK_PRIMARY} !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }}
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{
        color: {PINK_DEEP} !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }}

    /* Tab */
    button[data-baseweb="tab"] {{
        font-family: 'Poppins', sans-serif !important;
        font-weight: 500 !important;
        color: {PINK_PRIMARY} !important;
        border-radius: 10px 10px 0 0 !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: {PINK_PALE} !important;
        border-bottom: 3px solid {PINK_DEEP} !important;
        color: {PINK_DEEP} !important;
        font-weight: 700 !important;
    }}

    /* Tombol */
    div[data-testid="stButton"] button {{
        background: linear-gradient(135deg, {PINK_PRIMARY}, {PINK_DEEP}) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }}
    div[data-testid="stButton"] button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(233,30,140,0.35) !important;
    }}

    /* Dataframe */
    .stDataFrame {{
        border: 2px solid {PINK_LIGHT};
        border-radius: 12px;
        overflow: hidden;
    }}

    /* Info / warning box */
    .stAlert {{
        border-radius: 12px !important;
    }}

    /* Divider */
    hr {{
        border-color: {PINK_LIGHT} !important;
    }}

    /* Expander */
    details summary {{
        color: {PINK_PRIMARY} !important;
        font-weight: 600 !important;
    }}

    /* Card custom */
    .pink-card {{
        background: {WHITE};
        border-left: 5px solid {PINK_PRIMARY};
        border-radius: 12px;
        padding: 16px 20px;
        margin: 8px 0;
        box-shadow: 0 3px 12px rgba(255,107,157,0.12);
    }}
    .pink-badge {{
        background: {PINK_PALE};
        color: {PINK_DEEP};
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 2px;
    }}
</style>
""", unsafe_allow_html=True)

# ── HELPER: MATPLOTLIB THEME PINK ───────────────────────────────────────────
def set_pink_style():
    plt.rcParams.update({
        'figure.facecolor'  : '#FFF0F7',
        'axes.facecolor'    : '#FFF8FC',
        'axes.edgecolor'    : PINK_LIGHT,
        'axes.labelcolor'   : GRAY_TEXT,
        'axes.titlecolor'   : PINK_DEEP,
        'xtick.color'       : GRAY_TEXT,
        'ytick.color'       : GRAY_TEXT,
        'grid.color'        : PINK_LIGHT,
        'grid.alpha'        : 0.6,
        'axes.grid'         : True,
        'font.family'       : 'sans-serif',
        'axes.spines.top'   : False,
        'axes.spines.right' : False,
    })

# ── LOAD DATA (BigQuery atau Cache CSV) ──────────────────────────────────────
@st.cache_data(show_spinner="⏳ Memuat data dari BigQuery...")
def load_data():
    """
    Coba koneksi BigQuery. Jika gagal (tidak ada credentials),
    gunakan data dummy supaya dashboard tetap bisa dijalankan lokal.
    """
    try:
        from google.cloud import bigquery
        PROJECT_ID = "adbc-495202"   # ← Ganti sesuai project ID kamu
        client = bigquery.Client(project=PROJECT_ID)

        query = """
        SELECT e.country_name, e.country_code, e.indicator_name, e.indicator_code,
               e.value, e.year,
               c.region, c.income_group
        FROM `bigquery-public-data.world_bank_intl_education.international_education` e
        LEFT JOIN `bigquery-public-data.world_bank_intl_education.country_summary` c
          ON e.country_code = c.country_code
        WHERE e.indicator_code IN (
            'SE.PRM.ENRR', 'SE.SEC.ENRR', 'SE.TER.ENRR',
            'SE.ADT.LITR.ZS', 'SE.XPD.TOTL.GD.ZS'
        )
        AND e.value IS NOT NULL
        LIMIT 500000
        """
        df = client.query(query).to_dataframe()
        return df, "BigQuery"
    except Exception as e:
        # Fallback: data dummy untuk demo lokal
        return _generate_dummy_data(), f"Demo (BigQuery gagal: {str(e)[:60]})"


def _generate_dummy_data():
    """Generate data dummy realistis untuk demo tanpa BigQuery."""
    np.random.seed(42)
    countries = {
        "Indonesia": ("East Asia & Pacific", "Lower middle income"),
        "India"    : ("South Asia", "Lower middle income"),
        "China"    : ("East Asia & Pacific", "Upper middle income"),
        "USA"      : ("North America", "High income"),
        "Brazil"   : ("Latin America & Caribbean", "Upper middle income"),
        "Nigeria"  : ("Sub-Saharan Africa", "Low income"),
        "Germany"  : ("Europe & Central Asia", "High income"),
        "Kenya"    : ("Sub-Saharan Africa", "Lower middle income"),
        "Mexico"   : ("Latin America & Caribbean", "Upper middle income"),
        "Egypt"    : ("Middle East & North Africa", "Lower middle income"),
        "France"   : ("Europe & Central Asia", "High income"),
        "Pakistan" : ("South Asia", "Lower middle income"),
        "Ethiopia" : ("Sub-Saharan Africa", "Low income"),
        "Vietnam"  : ("East Asia & Pacific", "Lower middle income"),
        "Argentina": ("Latin America & Caribbean", "Upper middle income"),
    }
    indicators = {
        'SE.PRM.ENRR'      : 'Enrollment SD (%)',
        'SE.SEC.ENRR'      : 'Enrollment SMP/SMA (%)',
        'SE.TER.ENRR'      : 'Enrollment PT (%)',
        'SE.ADT.LITR.ZS'   : 'Literasi Dewasa (%)',
        'SE.XPD.TOTL.GD.ZS': 'Belanja Pendidikan (% GDP)',
    }
    base_vals = {
        "Indonesia": [100, 82, 31, 94, 3.5],
        "India"    : [98,  78, 28, 74, 3.8],
        "China"    : [105, 90, 54, 96, 4.1],
        "USA"      : [101, 98, 88, 99, 5.0],
        "Brazil"   : [103, 92, 51, 93, 6.0],
        "Nigeria"  : [88,  50, 10, 62, 2.5],
        "Germany"  : [103, 99, 70, 99, 4.8],
        "Kenya"    : [90,  60, 12, 78, 5.3],
        "Mexico"   : [104, 94, 38, 95, 5.3],
        "Egypt"    : [105, 88, 35, 71, 3.7],
        "France"   : [105, 107, 65, 99, 5.5],
        "Pakistan" : [80,  40, 9,  59, 2.5],
        "Ethiopia" : [91,  38, 8,  51, 4.7],
        "Vietnam"  : [110, 87, 28, 95, 5.6],
        "Argentina": [110, 102, 80, 99, 5.8],
    }
    rows = []
    years = range(1995, 2023)
    codes = {c: c[:3].upper() for c in countries}
    ind_codes = list(indicators.keys())
    ind_labels = list(indicators.values())
    for ctry, (reg, inc) in countries.items():
        code = codes[ctry]
        for yr in years:
            for i, (ic, lbl) in enumerate(zip(ind_codes, ind_labels)):
                base  = base_vals[ctry][i]
                noise = np.random.normal(0, base * 0.03)
                trend = (yr - 1995) * 0.3 * (1 if i < 3 else 0.1)
                val   = max(0, base + noise + trend)
                rows.append({
                    "country_name"  : ctry,
                    "country_code"  : code,
                    "indicator_name": lbl,
                    "indicator_code": ic,
                    "value"         : round(val, 2),
                    "year"          : yr,
                    "region"        : reg,
                    "income_group"  : inc,
                })
    df = pd.DataFrame(rows)
    return df

# ── KONSTANTA ────────────────────────────────────────────────────────────────
INDIKATOR_MAP = {
    'SE.PRM.ENRR'      : 'Enrollment SD (%)',
    'SE.SEC.ENRR'      : 'Enrollment SMP/SMA (%)',
    'SE.TER.ENRR'      : 'Enrollment PT (%)',
    'SE.ADT.LITR.ZS'   : 'Literasi Dewasa (%)',
    'SE.XPD.TOTL.GD.ZS': 'Belanja Pendidikan (% GDP)',
}

# ── LOAD ─────────────────────────────────────────────────────────────────────
df_raw, data_source = load_data()

# Tambah kolom label
df_raw['label'] = df_raw['indicator_code'].map(INDIKATOR_MAP)
df_kunci = df_raw.copy()

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 Filter Dashboard")
    st.markdown("---")

    # Tahun
    yr_min, yr_max = int(df_kunci['year'].min()), int(df_kunci['year'].max())
    year_range = st.slider("📅 Rentang Tahun", yr_min, yr_max,
                           (max(yr_min, 2000), yr_max))

    # Region
    regions = ["Semua"] + sorted(df_kunci['region'].dropna().unique().tolist())
    sel_region = st.selectbox("🌏 Region", regions)

    # Income Group
    inc_groups = ["Semua"] + sorted(df_kunci['income_group'].dropna().unique().tolist())
    sel_income = st.selectbox("💰 Income Group", inc_groups)

    # Indikator
    sel_ind = st.multiselect(
        "📊 Indikator",
        options=list(INDIKATOR_MAP.values()),
        default=list(INDIKATOR_MAP.values())
    )

    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:0.75rem; opacity:0.85;'>
    📡 <b>Sumber data:</b><br>{data_source}
    </div>
    """, unsafe_allow_html=True)

# ── FILTER DATA ──────────────────────────────────────────────────────────────
df_filtered = df_kunci[
    (df_kunci['year'] >= year_range[0]) &
    (df_kunci['year'] <= year_range[1]) &
    (df_kunci['label'].isin(sel_ind))
].copy()

if sel_region != "Semua":
    df_filtered = df_filtered[df_filtered['region'] == sel_region]
if sel_income != "Semua":
    df_filtered = df_filtered[df_filtered['income_group'] == sel_income]

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 10px 0 20px 0;'>
    <h1 style='margin-bottom:4px;'>🌍 Dashboard Pendidikan Dunia</h1>
    <p style='color:#FF6B9D; font-size:1.05rem; font-weight:500;'>
        World Bank International Education — Analisis Data End-to-End
    </p>
</div>
""", unsafe_allow_html=True)

# ── METRICS ──────────────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric("🌐 Negara", df_filtered['country_name'].nunique())
with m2:
    st.metric("📅 Rentang Tahun", f"{year_range[0]}–{year_range[1]}")
with m3:
    st.metric("📊 Observasi", f"{len(df_filtered):,}")
with m4:
    lit = df_filtered[df_filtered['indicator_code']=='SE.ADT.LITR.ZS']['value'].mean()
    st.metric("📖 Rata-rata Literasi", f"{lit:.1f}%" if not np.isnan(lit) else "N/A")
with m5:
    enr = df_filtered[df_filtered['indicator_code']=='SE.PRM.ENRR']['value'].mean()
    st.metric("🏫 Rata-rata Enroll SD", f"{enr:.1f}%" if not np.isnan(enr) else "N/A")

st.markdown("---")

# ── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Tren Global",
    "🗺️ Perbandingan Region",
    "💡 Distribusi & Korelasi",
    "🤖 Machine Learning",
    "🗄️ Data Mentah",
])

# ╔══════════════════════════════════════════════════════════════╗
# ║  TAB 1 — TREN GLOBAL                                         ║
# ╚══════════════════════════════════════════════════════════════╝
with tab1:
    st.subheader("📈 Tren Rata-rata Global per Indikator")

    set_pink_style()
    n_ind = len(sel_ind)
    if n_ind == 0:
        st.warning("Pilih minimal 1 indikator di sidebar.")
    else:
        ncols = min(2, n_ind)
        nrows = (n_ind + 1) // 2
        fig, axes = plt.subplots(nrows, ncols, figsize=(14, 4.5 * nrows))
        axes_flat = np.array(axes).flatten() if n_ind > 1 else [axes]

        for i, lbl in enumerate(sel_ind):
            code = {v: k for k, v in INDIKATOR_MAP.items()}.get(lbl)
            data_tren = (
                df_filtered[df_filtered['label'] == lbl]
                .groupby('year')['value']
                .agg(['mean', 'median'])
                .reset_index()
                .dropna()
            )
            ax = axes_flat[i]
            color = CHART_COLORS[i % len(CHART_COLORS)]
            ax.plot(data_tren['year'], data_tren['mean'],
                    color=color, lw=2.5, marker='o', ms=3, label='Mean')
            ax.plot(data_tren['year'], data_tren['median'],
                    color=color, lw=2, ls='--', alpha=0.7, label='Median')
            ax.fill_between(data_tren['year'], data_tren['mean'],
                            data_tren['median'], alpha=0.15, color=color)
            ax.set_title(lbl, fontweight='bold', fontsize=10, color=PINK_DEEP)
            ax.set_xlabel('Tahun', fontsize=9)
            ax.set_ylabel('Nilai', fontsize=9)
            ax.legend(fontsize=8)

        # Hapus subplot kosong
        for j in range(i + 1, len(axes_flat)):
            axes_flat[j].set_visible(False)

        plt.suptitle('Tren Global Indikator Pendidikan', fontsize=13,
                     fontweight='bold', color=PINK_DEEP, y=1.02)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # Tabel tren tahunan
    with st.expander("📋 Lihat data tren tabel"):
        for lbl in sel_ind[:3]:
            tren_tbl = (
                df_filtered[df_filtered['label'] == lbl]
                .groupby('year')['value']
                .agg(Mean='mean', Median='median', Std='std', Count='count')
                .round(2)
                .reset_index()
            )
            st.markdown(f"**{lbl}**")
            st.dataframe(tren_tbl, use_container_width=True, height=220)

# ╔══════════════════════════════════════════════════════════════╗
# ║  TAB 2 — PERBANDINGAN REGION                                 ║
# ╚══════════════════════════════════════════════════════════════╝
with tab2:
    st.subheader("🗺️ Perbandingan Indikator per Region & Income Group")
    set_pink_style()

    col_left, col_right = st.columns(2)

    # ── Bar chart per Region ──
    with col_left:
        st.markdown("**Rata-rata Enrollment per Jenjang per Region**")
        enroll_codes = ['SE.PRM.ENRR', 'SE.SEC.ENRR', 'SE.TER.ENRR']
        enroll_labels = ['Enrollment SD (%)', 'Enrollment SMP/SMA (%)', 'Enrollment PT (%)']
        df_v2 = (
            df_filtered[
                df_filtered['indicator_code'].isin(enroll_codes) &
                df_filtered['region'].notna()
            ]
            .groupby(['region', 'label'])['value']
            .mean()
            .unstack('label')
            .fillna(0)
        )

        fig, ax = plt.subplots(figsize=(7, 5))
        x = np.arange(len(df_v2.index))
        w = 0.25
        bar_cols = [PINK_PRIMARY, PINK_DEEP, "#FF80AB"]
        for j, (lbl, color) in enumerate(zip(enroll_labels, bar_cols)):
            if lbl in df_v2.columns:
                ax.bar(x + j * w, df_v2[lbl], w, label=lbl,
                       color=color, alpha=0.87, edgecolor='white')
        ax.set_xticks(x + w)
        ax.set_xticklabels(
            [r.split('&')[0].strip() if '&' in r else r[:20] for r in df_v2.index],
            rotation=30, ha='right', fontsize=8
        )
        ax.axhline(100, color='gray', ls='--', lw=1, alpha=0.4)
        ax.set_title('Enrollment Rate per Region', fontweight='bold', color=PINK_DEEP)
        ax.set_ylabel('Gross Enrollment Rate (%)')
        ax.legend(fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # ── Literasi per Income Group ──
    with col_right:
        st.markdown("**Literasi Dewasa per Income Group**")
        df_lit_inc = (
            df_filtered[
                (df_filtered['indicator_code'] == 'SE.ADT.LITR.ZS') &
                df_filtered['income_group'].notna()
            ]
            .groupby('income_group')['value']
            .agg(['mean', 'std', 'count'])
            .round(2)
            .sort_values('mean', ascending=True)
        )

        fig2, ax2 = plt.subplots(figsize=(7, 5))
        colors_bar = [CHART_COLORS[i % len(CHART_COLORS)]
                      for i in range(len(df_lit_inc))]
        bars = ax2.barh(df_lit_inc.index, df_lit_inc['mean'],
                        color=colors_bar, alpha=0.85,
                        edgecolor='white', height=0.6)
        ax2.bar_label(bars, fmt='%.1f%%', padding=5, fontsize=9,
                      color=PINK_DEEP, fontweight='bold')
        ax2.set_xlabel('Rata-rata Literasi Dewasa (%)')
        ax2.set_title('Literasi Dewasa per Income Group', fontweight='bold',
                      color=PINK_DEEP)
        ax2.set_xlim(0, 110)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    # ── Statistik tabel ──
    st.markdown("**📋 Statistik Enrollment SD per Region**")
    stat_reg = (
        df_filtered[df_filtered['indicator_code'] == 'SE.PRM.ENRR']
        .groupby('region')['value']
        .agg(Mean='mean', Median='median', Std='std', Min='min', Max='max', N='count')
        .round(2)
        .sort_values('Mean', ascending=False)
        .reset_index()
    )
    st.dataframe(stat_reg.style.background_gradient(subset=['Mean'],
                 cmap='RdPu'), use_container_width=True)

# ╔══════════════════════════════════════════════════════════════╗
# ║  TAB 3 — DISTRIBUSI & KORELASI                               ║
# ╚══════════════════════════════════════════════════════════════╝
with tab3:
    st.subheader("💡 Distribusi & Korelasi Antar Indikator")
    set_pink_style()

    c1, c2 = st.columns(2)

    # ── Violin Plot ──
    with c1:
        st.markdown("**Distribusi Literasi per Income Group (Violin)**")
        df_vio = df_filtered[
            (df_filtered['indicator_code'] == 'SE.ADT.LITR.ZS') &
            df_filtered['income_group'].notna()
        ]
        if len(df_vio) > 10:
            order_vio = (df_vio.groupby('income_group')['value']
                         .median().sort_values(ascending=False).index)
            fig3, ax3 = plt.subplots(figsize=(7, 5))
            sns.violinplot(data=df_vio, x='income_group', y='value',
                           order=order_vio,
                           palette=[PINK_PRIMARY, PINK_DEEP,
                                    "#FF80AB", "#FF4081"],
                           inner='quartile', ax=ax3)
            ax3.set_xlabel('')
            ax3.set_ylabel('Literacy Rate (%)')
            ax3.set_title('Distribusi Literasi per Income Group',
                          fontweight='bold', color=PINK_DEEP)
            ax3.tick_params(axis='x', rotation=15)
            plt.tight_layout()
            st.pyplot(fig3)
            plt.close(fig3)
        else:
            st.info("Data tidak cukup untuk violin plot.")

    # ── Bubble Chart ──
    with c2:
        st.markdown("**Bubble Chart: Literasi vs Enrollment PT**")
        df_bub = (
            df_filtered[
                df_filtered['indicator_code'].isin([
                    'SE.ADT.LITR.ZS', 'SE.TER.ENRR', 'SE.XPD.TOTL.GD.ZS'
                ]) & df_filtered['income_group'].notna() &
                (df_filtered['year'] >= max(year_range[0], 2010))
            ]
            .groupby(['country_code', 'country_name', 'income_group', 'label'])['value']
            .mean()
            .unstack('label')
            .dropna()
            .reset_index()
        )

        needed_cols = ['Literasi Dewasa (%)', 'Enrollment PT (%)',
                       'Belanja Pendidikan (% GDP)']
        if all(c in df_bub.columns for c in needed_cols) and len(df_bub) > 3:
            ig_colors = {
                'High income'        : PINK_PRIMARY,
                'Upper middle income': "#FF80AB",
                'Lower middle income': PINK_DEEP,
                'Low income'         : "#C2185B",
            }
            fig4, ax4 = plt.subplots(figsize=(7, 5))
            for ig, sub in df_bub.groupby('income_group'):
                sub_c = sub.dropna(subset=needed_cols)
                if len(sub_c) > 0:
                    ax4.scatter(
                        sub_c['Literasi Dewasa (%)'],
                        sub_c['Enrollment PT (%)'],
                        s=sub_c['Belanja Pendidikan (% GDP)'] * 50,
                        alpha=0.7,
                        color=ig_colors.get(ig, PINK_LIGHT),
                        edgecolors='white', linewidth=0.8,
                        label=ig
                    )
            ax4.set_xlabel('Tingkat Literasi Dewasa (%)')
            ax4.set_ylabel('Enrollment Perguruan Tinggi (%)')
            ax4.set_title('Literasi vs Enrollment PT\n(ukuran = Belanja % GDP)',
                          fontweight='bold', color=PINK_DEEP)
            ax4.legend(fontsize=8, title='Income Group')
            plt.tight_layout()
            st.pyplot(fig4)
            plt.close(fig4)
        else:
            st.info("Data tidak cukup untuk bubble chart.")

    # ── Heatmap Korelasi ──
    st.markdown("**🔥 Heatmap Korelasi Antar Indikator**")
    df_pivot_corr = (
        df_filtered
        .groupby(['country_code', 'year', 'label'])['value']
        .mean()
        .unstack('label')
        .dropna()
    )
    if df_pivot_corr.shape[0] > 5 and df_pivot_corr.shape[1] > 1:
        corr_mat = df_pivot_corr.corr()
        fig5, ax5 = plt.subplots(figsize=(8, 5))
        cmap_pink = sns.diverging_palette(340, 10, as_cmap=True)
        sns.heatmap(corr_mat, annot=True, fmt='.2f',
                    cmap=cmap_pink, linewidths=0.8,
                    ax=ax5, vmin=-1, vmax=1,
                    cbar_kws={'label': 'Korelasi (r)'})
        ax5.set_title('Matriks Korelasi Indikator Pendidikan',
                      fontweight='bold', color=PINK_DEEP)
        plt.tight_layout()
        st.pyplot(fig5)
        plt.close(fig5)
    else:
        st.info("Data tidak cukup untuk heatmap korelasi.")

# ╔══════════════════════════════════════════════════════════════╗
# ║  TAB 4 — MACHINE LEARNING                                    ║
# ╚══════════════════════════════════════════════════════════════╝
with tab4:
    st.subheader("🤖 Machine Learning: Regresi & K-Means Clustering")

    from sklearn.linear_model     import LinearRegression
    from sklearn.preprocessing    import StandardScaler
    from sklearn.metrics          import r2_score, mean_squared_error
    from sklearn.model_selection  import train_test_split
    from sklearn.cluster          import KMeans

    # Siapkan data pivot
    df_pivot = (
        df_filtered
        .groupby(['country_code', 'country_name', 'year', 'label'])['value']
        .mean()
        .unstack('label')
        .reset_index()
    )
    df_pivot = df_pivot.groupby(['country_code', 'country_name'])[
        list(INDIKATOR_MAP.values())
    ].mean().reset_index()

    # Imputasi mean
    for col in list(INDIKATOR_MAP.values()):
        if col in df_pivot.columns:
            df_pivot[col].fillna(df_pivot[col].mean(), inplace=True)

    df_ml = df_pivot[list(INDIKATOR_MAP.values())].dropna()

    ml_col1, ml_col2 = st.columns(2)

    # ── MODEL 1: Regresi ──
    with ml_col1:
        st.markdown("### 📐 Model 1: Regresi Linier Berganda")
        st.caption("Target: Prediksi Literasi Dewasa (%)")

        feat_cols = [
            'Enrollment SD (%)', 'Enrollment SMP/SMA (%)',
            'Enrollment PT (%)', 'Belanja Pendidikan (% GDP)'
        ]
        target_col = 'Literasi Dewasa (%)'

        ok_cols = [c for c in feat_cols if c in df_ml.columns]
        if target_col in df_ml.columns and len(ok_cols) >= 2 and len(df_ml) >= 10:
            X = df_ml[ok_cols].values
            y = df_ml[target_col].values

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            sc = StandardScaler()
            X_tr_s = sc.fit_transform(X_train)
            X_te_s = sc.transform(X_test)

            reg = LinearRegression()
            reg.fit(X_tr_s, y_train)
            y_pred = reg.predict(X_te_s)
            r2   = r2_score(y_test, y_pred) if len(y_test) > 1 else float('nan')
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))

            m_r2, m_rmse, m_n = st.columns(3)
            m_r2.metric("R² Test", f"{r2:.4f}")
            m_rmse.metric("RMSE Test", f"{rmse:.2f}")
            m_n.metric("Observasi", f"{len(df_ml):,}")

            # Scatter actual vs predicted
            set_pink_style()
            fig6, ax6 = plt.subplots(figsize=(6, 4.5))
            ax6.scatter(y_test, y_pred, alpha=0.5, s=40,
                        color=PINK_PRIMARY, edgecolors='white', lw=0.5,
                        label='Test set')
            mn = min(y_test.min(), y_pred.min())
            mx = max(y_test.max(), y_pred.max())
            ax6.plot([mn, mx], [mn, mx], 'r--', lw=2, label='Sempurna')
            ax6.set_xlabel('Nilai Aktual (%)')
            ax6.set_ylabel('Nilai Prediksi (%)')
            ax6.set_title(f'Actual vs Predicted (R²={r2:.3f})',
                          fontweight='bold', color=PINK_DEEP)
            ax6.legend(fontsize=9)
            plt.tight_layout()
            st.pyplot(fig6)
            plt.close(fig6)

            # Koefisien
            coef_df = pd.DataFrame({
                'Fitur'     : ok_cols,
                'Koefisien' : reg.coef_
            }).sort_values('Koefisien')
            fig7, ax7 = plt.subplots(figsize=(6, 3))
            colors_c = [PINK_DEEP if v > 0 else "#aaa" for v in coef_df['Koefisien']]
            ax7.barh(coef_df['Fitur'], coef_df['Koefisien'],
                     color=colors_c, alpha=0.87, edgecolor='white')
            ax7.axvline(0, color='black', lw=1)
            ax7.set_title('Koefisien Regresi (Terstandarisasi)',
                          fontweight='bold', color=PINK_DEEP)
            plt.tight_layout()
            st.pyplot(fig7)
            plt.close(fig7)
        else:
            st.warning("Data tidak cukup untuk model regresi (min 10 observasi lengkap).")

    # ── MODEL 2: K-Means ──
    with ml_col2:
        st.markdown("### 🔵 Model 2: K-Means Clustering")
        st.caption("Pengelompokan negara berdasarkan profil pendidikan")

        k_slider = st.slider("Jumlah Cluster (K)", 2, 6, 4)

        cl_cols = [c for c in list(INDIKATOR_MAP.values()) if c in df_ml.columns]
        if len(df_ml) >= k_slider and len(cl_cols) >= 2:
            sc_c = StandardScaler()
            X_cl = sc_c.fit_transform(df_ml[cl_cols].values)

            # Elbow
            inertias = []
            k_max = min(min(8, len(df_ml)), 8)
            for k in range(2, k_max + 1):
                km_ = KMeans(n_clusters=k, random_state=42, n_init=10)
                km_.fit(X_cl)
                inertias.append(km_.inertia_)

            set_pink_style()
            fig8, axes_ml = plt.subplots(1, 2, figsize=(10, 4))

            # Elbow plot
            axes_ml[0].plot(range(2, k_max + 1), inertias, 'o-',
                            color=PINK_PRIMARY, lw=2.5, ms=8)
            axes_ml[0].axvline(k_slider, color=PINK_DEEP, ls='--',
                               lw=2, label=f'K={k_slider}')
            axes_ml[0].set_xlabel('Jumlah Cluster (K)')
            axes_ml[0].set_ylabel('Inertia')
            axes_ml[0].set_title('Elbow Method', fontweight='bold', color=PINK_DEEP)
            axes_ml[0].legend()

            # Fit best K
            km_best = KMeans(n_clusters=k_slider, random_state=42, n_init=10)
            labels_km = km_best.fit_predict(X_cl)
            df_ml_cl = df_ml.copy()
            df_ml_cl['Cluster'] = labels_km

            # Scatter
            if 'Literasi Dewasa (%)' in cl_cols and 'Enrollment PT (%)' in cl_cols:
                cl_colors_plot = [CHART_COLORS[i % len(CHART_COLORS)]
                                  for i in range(k_slider)]
                for cl_id in range(k_slider):
                    sub_c = df_ml_cl[df_ml_cl['Cluster'] == cl_id]
                    axes_ml[1].scatter(
                        sub_c['Literasi Dewasa (%)'],
                        sub_c['Enrollment PT (%)'],
                        s=60, alpha=0.75,
                        color=cl_colors_plot[cl_id],
                        edgecolors='white', lw=0.6,
                        label=f'Cluster {cl_id} (n={len(sub_c)})'
                    )
                axes_ml[1].set_xlabel('Literasi Dewasa (%)')
                axes_ml[1].set_ylabel('Enrollment PT (%)')
                axes_ml[1].set_title('Scatter Cluster Negara',
                                     fontweight='bold', color=PINK_DEEP)
                axes_ml[1].legend(fontsize=8)

            plt.tight_layout()
            st.pyplot(fig8)
            plt.close(fig8)

            # Profil cluster
            profile = df_ml_cl.groupby('Cluster')[cl_cols].mean().round(2)
            st.markdown("**Profil Rata-rata per Cluster:**")
            st.dataframe(
                profile.style.background_gradient(cmap='RdPu'),
                use_container_width=True
            )

            # Distribusi negara ke cluster (jika ada nama negara)
            if 'country_name' in df_pivot.columns:
                df_cl_named = df_pivot[['country_name'] + cl_cols].dropna().copy()
                df_cl_named['Cluster'] = km_best.predict(
                    sc_c.transform(df_cl_named[cl_cols].values)
                )
                with st.expander("🗂️ Daftar negara per cluster"):
                    for cl_id in range(k_slider):
                        countries_in = df_cl_named[
                            df_cl_named['Cluster'] == cl_id
                        ]['country_name'].tolist()
                        st.markdown(
                            f"**Cluster {cl_id}** ({len(countries_in)} negara): "
                            + ", ".join(countries_in[:12])
                            + ("..." if len(countries_in) > 12 else "")
                        )
        else:
            st.warning("Data tidak cukup untuk clustering.")

# ╔══════════════════════════════════════════════════════════════╗
# ║  TAB 5 — DATA MENTAH                                         ║
# ╚══════════════════════════════════════════════════════════════╝
with tab5:
    st.subheader("🗄️ Data Mentah & Ekspor")

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search = st.text_input("🔍 Cari negara...", placeholder="contoh: Indonesia")
    with col_s2:
        max_rows = st.number_input("Maks. baris", 50, 5000, 200, step=50)

    df_show = df_filtered.copy()
    if search:
        df_show = df_show[
            df_show['country_name'].str.contains(search, case=False, na=False)
        ]

    st.markdown(f"Menampilkan **{min(len(df_show), max_rows):,}** dari "
                f"**{len(df_show):,}** baris")
    st.dataframe(
        df_show.head(max_rows)[[
            'country_name', 'country_code', 'year',
            'label', 'value', 'region', 'income_group'
        ]].sort_values(['country_name', 'year']),
        use_container_width=True,
        height=400
    )

    # Ekspor CSV
    csv_data = df_show.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name="world_bank_education_filtered.csv",
        mime="text/csv"
    )

    # Statistik ringkas
    with st.expander("📊 Statistik Deskriptif Keseluruhan"):
        stats = (
            df_filtered.groupby('label')['value']
            .agg(['count', 'mean', 'median', 'std', 'min', 'max'])
            .round(2)
            .rename(columns={
                'count': 'N', 'mean': 'Mean', 'median': 'Median',
                'std': 'Std Dev', 'min': 'Min', 'max': 'Max'
            })
            .reset_index()
        )
        st.dataframe(
            stats.style.background_gradient(subset=['Mean'], cmap='RdPu'),
            use_container_width=True
        )

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style='text-align:center; color:{PINK_PRIMARY}; font-size:0.85rem; padding:8px;'>
    🎓 Dashboard Pendidikan Dunia — Proyek ADBC &nbsp;|&nbsp;
    World Bank International Education Dataset &nbsp;|&nbsp;
    Dibuat dengan Streamlit 💕
</div>
""", unsafe_allow_html=True)
