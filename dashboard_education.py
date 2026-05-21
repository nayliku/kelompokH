"""
Dashboard Streamlit — World Bank International Education
Proyek ADBC | Analisis Data End-to-End
Tema: Pink Fresh
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Pendidikan Dunia",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── WARNA ────────────────────────────────────────────────────────────────────
PINK_PRIMARY  = "#FF6B9D"
PINK_LIGHT    = "#FFB3D1"
PINK_PALE     = "#FFE4F0"
PINK_DEEP     = "#E91E8C"
WHITE         = "#FFFFFF"
GRAY_TEXT     = "#5A4A5A"
DARK_BG       = "#FFF0F7"
CHART_COLORS  = ["#FF6B9D","#E91E8C","#C2185B","#FF80AB","#F48FB1","#AD1457","#FF8A80","#E040FB"]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');

.stApp {{
    background-color: {DARK_BG};
    font-family: 'Poppins', sans-serif;
    color: {GRAY_TEXT};
}}
h1 {{
    font-family: 'Playfair Display', serif !important;
    color: {PINK_DEEP} !important;
    font-size: 2.4rem !important;
}}
h2, h3 {{ color: {PINK_PRIMARY} !important; }}

/* Sidebar background */
section[data-testid="stSidebar"] {{
    background: linear-gradient(160deg, {PINK_PRIMARY}, {PINK_DEEP}) !important;
}}
/* Label sidebar */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span:not([data-baseweb]),
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    color: white !important;
    font-weight: 600 !important;
}}
/* Box dropdown sidebar */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div:first-child {{
    background-color: rgba(255,255,255,0.95) !important;
    border: 2px solid rgba(255,255,255,0.5) !important;
    border-radius: 10px !important;
}}
section[data-testid="stSidebar"] div[data-baseweb="select"] span,
section[data-testid="stSidebar"] div[data-baseweb="select"] div[class*="singleValue"],
section[data-testid="stSidebar"] div[data-baseweb="select"] input {{
    color: {PINK_DEEP} !important;
}}
/* Tag multiselect */
section[data-testid="stSidebar"] span[data-baseweb="tag"] {{
    background-color: {PINK_PALE} !important;
}}
section[data-testid="stSidebar"] span[data-baseweb="tag"] span {{
    color: {PINK_DEEP} !important;
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
    font-weight: 500 !important;
    color: {PINK_PRIMARY} !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    background-color: {PINK_PALE} !important;
    border-bottom: 3px solid {PINK_DEEP} !important;
    color: {PINK_DEEP} !important;
    font-weight: 700 !important;
}}
/* Download button */
div[data-testid="stDownloadButton"] button {{
    background: linear-gradient(135deg, {PINK_PRIMARY}, {PINK_DEEP}) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}}
hr {{ border-color: {PINK_LIGHT} !important; }}
</style>
""", unsafe_allow_html=True)

# ── MATPLOTLIB PINK STYLE ─────────────────────────────────────────────────────
def set_pink_style():
    plt.rcParams.update({
        'figure.facecolor' : '#FFF0F7',
        'axes.facecolor'   : '#FFF8FC',
        'axes.edgecolor'   : PINK_LIGHT,
        'axes.labelcolor'  : GRAY_TEXT,
        'axes.titlecolor'  : PINK_DEEP,
        'xtick.color'      : GRAY_TEXT,
        'ytick.color'      : GRAY_TEXT,
        'grid.color'       : PINK_LIGHT,
        'grid.alpha'       : 0.5,
        'axes.grid'        : True,
        'axes.spines.top'  : False,
        'axes.spines.right': False,
    })

# ── INDIKATOR ─────────────────────────────────────────────────────────────────
INDIKATOR_MAP = {
    'SE.PRM.ENRR'       : 'Enrollment SD (%)',
    'SE.SEC.ENRR'       : 'Enrollment SMP/SMA (%)',
    'SE.TER.ENRR'       : 'Enrollment PT (%)',
    'SE.ADT.LITR.ZS'    : 'Literasi Dewasa (%)',
    'SE.XPD.TOTL.GD.ZS' : 'Belanja Pendidikan (% GDP)',
}
ALL_LABELS = list(INDIKATOR_MAP.values())

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Memuat data...")
def load_data():
    import os
    csv_path = "world_bank_education.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        return df, "CSV Lokal (world_bank_education.csv)"
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project="adbc-495202")
        query = """
        SELECT e.country_name, e.country_code, e.indicator_code,
               e.value, e.year, c.region, c.income_group
        FROM `bigquery-public-data.world_bank_intl_education.international_education` e
        LEFT JOIN `bigquery-public-data.world_bank_intl_education.country_summary` c
            ON e.country_code = c.country_code
        WHERE e.indicator_code IN (
            'SE.PRM.ENRR','SE.SEC.ENRR','SE.TER.ENRR',
            'SE.ADT.LITR.ZS','SE.XPD.TOTL.GD.ZS')
        AND e.value IS NOT NULL
        LIMIT 500000
        """
        df = client.query(query).to_dataframe()
        return df, "BigQuery"
    except Exception:
        return _dummy_data(), "Demo (letakkan world_bank_education.csv di folder yang sama)"


def _dummy_data():
    np.random.seed(42)
    rows = []
    ctry = {"Indonesia":("IDN","East Asia & Pacific","Lower middle income"),
            "USA":("USA","North America","High income"),
            "Nigeria":("NGA","Sub-Saharan Africa","Low income"),
            "Germany":("DEU","Europe & Central Asia","High income"),
            "Brazil":("BRA","Latin America & Caribbean","Upper middle income")}
    bases = {"Indonesia":[100,82,31,94,3.5],"USA":[101,98,88,99,5.0],
             "Nigeria":[88,50,10,62,2.5],"Germany":[103,99,70,99,4.8],
             "Brazil":[103,92,51,93,6.0]}
    for yr in range(1995,2020):
        for name,(code,reg,inc) in ctry.items():
            for i,(ic,lbl) in enumerate(INDIKATOR_MAP.items()):
                val = max(0, bases[name][i] + np.random.normal(0,2))
                rows.append(dict(country_name=name,country_code=code,
                                 indicator_code=ic,value=round(val,2),
                                 year=yr,region=reg,income_group=inc))
    return pd.DataFrame(rows)


# ── INIT ──────────────────────────────────────────────────────────────────────
df_raw, data_source = load_data()
df_raw['label'] = df_raw['indicator_code'].map(INDIKATOR_MAP)
df_kunci = df_raw.copy()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Filter Dashboard")
    st.markdown("---")

    yr_min = int(df_kunci['year'].min())
    yr_max = int(df_kunci['year'].max())
    year_range = st.slider("Rentang Tahun", yr_min, yr_max,
                           (max(yr_min, 2000), yr_max))

    regions    = ["Semua"] + sorted(df_kunci['region'].dropna().unique().tolist())
    sel_region = st.selectbox("Region", regions)

    inc_groups = ["Semua"] + sorted(df_kunci['income_group'].dropna().unique().tolist())
    sel_income = st.selectbox("Income Group", inc_groups)

    sel_ind = st.multiselect("Indikator", options=ALL_LABELS, default=ALL_LABELS)

    st.markdown("---")
    st.markdown(f"<div style='font-size:0.75rem;opacity:0.85;'>Sumber data:<br><b>{data_source}</b></div>",
                unsafe_allow_html=True)

# ── FILTER ────────────────────────────────────────────────────────────────────
df_f = df_kunci[
    (df_kunci['year']  >= year_range[0]) &
    (df_kunci['year']  <= year_range[1]) &
    (df_kunci['label'].isin(sel_ind if sel_ind else ALL_LABELS))
].copy()
if sel_region != "Semua":
    df_f = df_f[df_f['region'] == sel_region]
if sel_income != "Semua":
    df_f = df_f[df_f['income_group'] == sel_income]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:10px 0 20px 0;'>
<h1 style='margin-bottom:4px;'>Dashboard Pendidikan Dunia</h1>
<p style='color:#FF6B9D;font-size:1rem;font-weight:500;'>
World Bank International Education — Analisis Data End-to-End</p>
</div>""", unsafe_allow_html=True)

# ── METRICS ───────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Negara",   df_f['country_name'].nunique())
c2.metric("Tahun",    f"{year_range[0]}–{year_range[1]}")
c3.metric("Observasi",f"{len(df_f):,}")
_lit = df_f[df_f['indicator_code']=='SE.ADT.LITR.ZS']['value'].mean()
c4.metric("Rata-rata Literasi", f"{_lit:.1f}%" if not np.isnan(_lit) else "N/A")
_enr = df_f[df_f['indicator_code']=='SE.PRM.ENRR']['value'].mean()
c5.metric("Rata-rata Enroll SD", f"{_enr:.1f}%" if not np.isnan(_enr) else "N/A")

st.markdown("---")

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Tren Global",
    "Perbandingan Region",
    "Distribusi & Korelasi",
    "Machine Learning",
    "Data Mentah",
])

# ═══════════════════════════════════════════════════════
#  TAB 1 — TREN GLOBAL
# ═══════════════════════════════════════════════════════
with tab1:
    st.subheader("Tren Rata-rata Global per Indikator")
    aktif = sel_ind if sel_ind else ALL_LABELS
    if not aktif:
        st.warning("Pilih minimal 1 indikator.")
    else:
        set_pink_style()
        ncols = min(2, len(aktif))
        nrows = (len(aktif) + 1) // 2
        fig, axes = plt.subplots(nrows, ncols, figsize=(14, 4.5 * nrows))
        axes_flat = np.array(axes).flatten() if len(aktif) > 1 else [axes]

        for i, lbl in enumerate(aktif):
            tren = (df_f[df_f['label'] == lbl]
                    .groupby('year')['value']
                    .agg(['mean','median']).reset_index().dropna())
            ax = axes_flat[i]
            color = CHART_COLORS[i % len(CHART_COLORS)]
            if len(tren):
                ax.plot(tren['year'], tren['mean'],   color=color, lw=2.5,
                        marker='o', ms=3, label='Mean')
                ax.plot(tren['year'], tren['median'], color=color, lw=2,
                        ls='--', alpha=0.7, label='Median')
                ax.fill_between(tren['year'], tren['mean'], tren['median'],
                                alpha=0.15, color=color)
            ax.set_title(lbl, fontweight='bold', fontsize=10)
            ax.set_xlabel('Tahun', fontsize=9)
            ax.set_ylabel('Nilai',  fontsize=9)
            ax.legend(fontsize=8)

        for j in range(len(aktif), len(axes_flat)):
            axes_flat[j].set_visible(False)

        plt.suptitle('Tren Global Indikator Pendidikan', fontsize=13,
                     fontweight='bold', color=PINK_DEEP, y=1.01)
        plt.tight_layout()
        st.pyplot(fig); plt.close(fig)

    with st.expander("Lihat data tren tabel"):
        for lbl in aktif[:3]:
            tbl = (df_f[df_f['label']==lbl]
                   .groupby('year')['value']
                   .agg(Mean='mean',Median='median',Std='std',Count='count')
                   .round(2).reset_index())
            st.markdown(f"**{lbl}**")
            st.dataframe(tbl, use_container_width=True, height=200)

# ═══════════════════════════════════════════════════════
#  TAB 2 — PERBANDINGAN REGION
# ═══════════════════════════════════════════════════════
with tab2:
    st.subheader("Perbandingan Indikator per Region & Income Group")
    set_pink_style()
    cl, cr = st.columns(2)

    # Bar chart enrollment per region
    with cl:
        st.markdown("**Rata-rata Enrollment per Jenjang per Region**")
        enroll_codes  = ['SE.PRM.ENRR','SE.SEC.ENRR','SE.TER.ENRR']
        enroll_labels = ['Enrollment SD (%)','Enrollment SMP/SMA (%)','Enrollment PT (%)']
        df_v2 = (df_f[df_f['indicator_code'].isin(enroll_codes) & df_f['region'].notna()]
                 .groupby(['region','label'])['value'].mean()
                 .unstack('label').fillna(0))

        if df_v2.empty or len(df_v2) == 0:
            st.info("Tidak ada data untuk filter ini.")
        else:
            fig, ax = plt.subplots(figsize=(7, 5))
            x = np.arange(len(df_v2))
            w = 0.25
            for j,(lbl,col) in enumerate(zip(enroll_labels,
                                             [PINK_PRIMARY, PINK_DEEP, "#FF80AB"])):
                if lbl in df_v2.columns:
                    ax.bar(x + j*w, df_v2[lbl], w, label=lbl,
                           color=col, alpha=0.87, edgecolor='white')
            ax.set_xticks(x + w)
            ax.set_xticklabels(
                [r.split('&')[0].strip()[:18] for r in df_v2.index],
                rotation=30, ha='right', fontsize=8)
            ax.axhline(100, color='gray', ls='--', lw=1, alpha=0.4)
            ax.set_title('Enrollment Rate per Region', fontweight='bold')
            ax.set_ylabel('Gross Enrollment Rate (%)')
            ax.legend(fontsize=8)
            plt.tight_layout(); st.pyplot(fig); plt.close(fig)

    # Literasi per income group
    with cr:
        st.markdown("**Literasi Dewasa per Income Group**")
        df_lit = (df_f[(df_f['indicator_code']=='SE.ADT.LITR.ZS') &
                       df_f['income_group'].notna()]
                  .groupby('income_group')['value']
                  .agg(['mean','std','count']).round(2)
                  .sort_values('mean', ascending=True))

        if df_lit.empty:
            st.info("Tidak ada data untuk filter ini.")
        else:
            fig2, ax2 = plt.subplots(figsize=(7, 5))
            colors_b = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(df_lit))]
            bars = ax2.barh(df_lit.index, df_lit['mean'],
                            color=colors_b, alpha=0.85,
                            edgecolor='white', height=0.6)
            ax2.bar_label(bars, fmt='%.1f%%', padding=5, fontsize=9,
                          color=PINK_DEEP, fontweight='bold')
            ax2.set_xlabel('Rata-rata Literasi Dewasa (%)')
            ax2.set_title('Literasi Dewasa per Income Group', fontweight='bold')
            ax2.set_xlim(0, 115)
            plt.tight_layout(); st.pyplot(fig2); plt.close(fig2)

    # Tabel statistik
    st.markdown("**Statistik Enrollment SD per Region**")
    stat_reg = (df_f[df_f['indicator_code']=='SE.PRM.ENRR']
                .groupby('region')['value']
                .agg(Mean='mean',Median='median',Std='std',Min='min',Max='max',N='count')
                .round(2).sort_values('Mean', ascending=False).reset_index())
    if stat_reg.empty:
        st.info("Tidak ada data.")
    else:
        st.dataframe(stat_reg.style.background_gradient(subset=['Mean'], cmap='RdPu'),
                     use_container_width=True)

# ═══════════════════════════════════════════════════════
#  TAB 3 — DISTRIBUSI & KORELASI
# ═══════════════════════════════════════════════════════
with tab3:
    st.subheader("Distribusi & Korelasi Antar Indikator")
    set_pink_style()
    c1, c2 = st.columns(2)

    # Violin
    with c1:
        st.markdown("**Distribusi Literasi per Income Group**")
        df_vio = df_f[(df_f['indicator_code']=='SE.ADT.LITR.ZS') &
                      df_f['income_group'].notna()]
        if len(df_vio) < 10:
            st.info("Data tidak cukup untuk violin plot.")
        else:
            order_vio = (df_vio.groupby('income_group')['value']
                         .median().sort_values(ascending=False).index)
            fig3, ax3 = plt.subplots(figsize=(7, 5))
            sns.violinplot(data=df_vio, x='income_group', y='value',
                           order=order_vio,
                           palette=[PINK_PRIMARY, PINK_DEEP, "#FF80AB", "#FF4081"],
                           inner='quartile', ax=ax3)
            ax3.set_xlabel('')
            ax3.set_ylabel('Literacy Rate (%)')
            ax3.set_title('Distribusi Literasi per Income Group', fontweight='bold')
            ax3.tick_params(axis='x', rotation=15)
            plt.tight_layout(); st.pyplot(fig3); plt.close(fig3)

    # Bubble chart
    with c2:
        st.markdown("**Bubble Chart: Literasi vs Enrollment PT**")
        needed = ['Literasi Dewasa (%)','Enrollment PT (%)','Belanja Pendidikan (% GDP)']
        df_bub = (df_f[df_f['indicator_code'].isin(
                          ['SE.ADT.LITR.ZS','SE.TER.ENRR','SE.XPD.TOTL.GD.ZS']) &
                       df_f['income_group'].notna()]
                  .groupby(['country_code','country_name','income_group','label'])['value']
                  .mean().unstack('label').reset_index())
        df_bub.columns.name = None

        missing_cols = [c for c in needed if c not in df_bub.columns]
        if missing_cols or len(df_bub) < 3:
            st.info("Data tidak cukup untuk bubble chart dengan filter ini.")
        else:
            df_bub = df_bub.dropna(subset=needed)
            ig_colors = {'High income':PINK_PRIMARY,'Upper middle income':"#FF80AB",
                         'Lower middle income':PINK_DEEP,'Low income':"#C2185B"}
            fig4, ax4 = plt.subplots(figsize=(7, 5))
            for ig, sub in df_bub.groupby('income_group'):
                ax4.scatter(sub['Literasi Dewasa (%)'], sub['Enrollment PT (%)'],
                            s=sub['Belanja Pendidikan (% GDP)']*50, alpha=0.7,
                            color=ig_colors.get(ig, PINK_LIGHT),
                            edgecolors='white', lw=0.8, label=ig)
            ax4.set_xlabel('Tingkat Literasi Dewasa (%)')
            ax4.set_ylabel('Enrollment Perguruan Tinggi (%)')
            ax4.set_title('Literasi vs Enrollment PT\n(ukuran = Belanja % GDP)',
                          fontweight='bold')
            ax4.legend(fontsize=8, title='Income Group')
            plt.tight_layout(); st.pyplot(fig4); plt.close(fig4)

    # Heatmap korelasi
    st.markdown("**Heatmap Korelasi Antar Indikator**")
    df_corr_pivot = (df_f.groupby(['country_code','year','label'])['value']
                     .mean().unstack('label').dropna())
    df_corr_pivot.columns.name = None

    if df_corr_pivot.shape[0] < 5 or df_corr_pivot.shape[1] < 2:
        st.info("Data tidak cukup untuk heatmap korelasi.")
    else:
        fig5, ax5 = plt.subplots(figsize=(8, 5))
        cmap_pink = sns.diverging_palette(340, 10, as_cmap=True)
        sns.heatmap(df_corr_pivot.corr(), annot=True, fmt='.2f',
                    cmap=cmap_pink, linewidths=0.8, ax=ax5,
                    vmin=-1, vmax=1, cbar_kws={'label':'Korelasi (r)'})
        ax5.set_title('Matriks Korelasi Indikator Pendidikan', fontweight='bold')
        plt.tight_layout(); st.pyplot(fig5); plt.close(fig5)

# ═══════════════════════════════════════════════════════
#  TAB 4 — MACHINE LEARNING
# ═══════════════════════════════════════════════════════
with tab4:
    st.subheader("Machine Learning: Regresi & K-Means Clustering")

    from sklearn.linear_model    import LinearRegression
    from sklearn.preprocessing   import StandardScaler
    from sklearn.metrics         import r2_score, mean_squared_error
    from sklearn.model_selection import train_test_split
    from sklearn.cluster         import KMeans

    # ── Buat pivot per negara (rata-rata semua tahun) ──────────────────────
    df_piv = (df_f.groupby(['country_code','country_name','label'])['value']
              .mean().unstack('label').reset_index())
    df_piv.columns.name = None

    # Hanya ambil kolom label yang tersedia di pivot
    avail_labels = [c for c in ALL_LABELS if c in df_piv.columns]

    # Imputasi mean
    for col in avail_labels:
        df_piv[col] = df_piv[col].fillna(df_piv[col].mean())

    df_ml = df_piv[avail_labels].dropna()

    ml_c1, ml_c2 = st.columns(2)

    # ── Regresi ────────────────────────────────────────────────────────────
    with ml_c1:
        st.markdown("### Model 1: Regresi Linier Berganda")
        st.caption("Target: Prediksi Literasi Dewasa (%)")

        feat_cols  = [c for c in ['Enrollment SD (%)','Enrollment SMP/SMA (%)',
                                   'Enrollment PT (%)','Belanja Pendidikan (% GDP)']
                      if c in df_ml.columns]
        target_col = 'Literasi Dewasa (%)'

        if target_col not in df_ml.columns:
            st.warning("Indikator 'Literasi Dewasa (%)' tidak tersedia di filter ini.")
        elif len(feat_cols) < 2 or len(df_ml) < 10:
            st.warning(f"Data tidak cukup untuk regresi (tersedia {len(df_ml)} baris).")
        else:
            X = df_ml[feat_cols].values
            y = df_ml[target_col].values
            X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
            sc = StandardScaler()
            reg = LinearRegression()
            reg.fit(sc.fit_transform(X_tr), y_tr)
            y_pred = reg.predict(sc.transform(X_te))
            r2   = r2_score(y_te, y_pred) if len(y_te) > 1 else float('nan')
            rmse = float(np.sqrt(mean_squared_error(y_te, y_pred)))

            m1,m2,m3 = st.columns(3)
            m1.metric("R² Test",    f"{r2:.4f}"  if not np.isnan(r2) else "N/A")
            m2.metric("RMSE Test",  f"{rmse:.2f}")
            m3.metric("Observasi",  f"{len(df_ml):,}")

            set_pink_style()
            fig6, axes6 = plt.subplots(1, 2, figsize=(10, 4))

            # Actual vs Predicted
            axes6[0].scatter(y_te, y_pred, alpha=0.55, s=45,
                             color=PINK_PRIMARY, edgecolors='white', lw=0.5)
            mn,mx = min(y_te.min(),y_pred.min()), max(y_te.max(),y_pred.max())
            axes6[0].plot([mn,mx],[mn,mx],'r--',lw=2)
            axes6[0].set_xlabel('Nilai Aktual (%)')
            axes6[0].set_ylabel('Nilai Prediksi (%)')
            axes6[0].set_title(f'Actual vs Predicted (R²={r2:.3f})', fontweight='bold')

            # Koefisien
            coef_s = pd.Series(reg.coef_, index=feat_cols).sort_values()
            colors_c = [PINK_DEEP if v > 0 else "#aaa" for v in coef_s]
            axes6[1].barh(coef_s.index, coef_s.values, color=colors_c,
                          alpha=0.87, edgecolor='white')
            axes6[1].axvline(0, color='black', lw=1)
            axes6[1].set_title('Koefisien Regresi', fontweight='bold')
            axes6[1].set_xlabel('Koefisien (standardized)')

            plt.tight_layout(); st.pyplot(fig6); plt.close(fig6)

    # ── K-Means ────────────────────────────────────────────────────────────
    with ml_c2:
        st.markdown("### Model 2: K-Means Clustering")
        st.caption("Pengelompokan negara berdasarkan profil pendidikan")

        cl_cols = [c for c in avail_labels if c in df_ml.columns]

        if len(df_ml) < 4 or len(cl_cols) < 2:
            st.warning(f"Data tidak cukup untuk clustering (tersedia {len(df_ml)} baris).")
        else:
            k_max    = min(6, len(df_ml))
            k_slider = st.slider("Jumlah Cluster (K)", 2, k_max, min(4, k_max))

            sc_c  = StandardScaler()
            X_cl  = sc_c.fit_transform(df_ml[cl_cols].values)

            # Elbow
            inertias = [KMeans(n_clusters=k, random_state=42, n_init=10)
                        .fit(X_cl).inertia_ for k in range(2, k_max+1)]

            km_best = KMeans(n_clusters=k_slider, random_state=42, n_init=10)
            cluster_labels = km_best.fit_predict(X_cl)
            df_ml_cl = df_ml.copy()
            df_ml_cl['Cluster'] = cluster_labels

            set_pink_style()
            fig8, axes8 = plt.subplots(1, 2, figsize=(10, 4))

            # Elbow plot
            axes8[0].plot(range(2, k_max+1), inertias, 'o-',
                          color=PINK_PRIMARY, lw=2.5, ms=8)
            axes8[0].axvline(k_slider, color=PINK_DEEP, ls='--', lw=2,
                             label=f'K={k_slider}')
            axes8[0].set_xlabel('Jumlah Cluster (K)')
            axes8[0].set_ylabel('Inertia')
            axes8[0].set_title('Elbow Method', fontweight='bold')
            axes8[0].legend()

            # Scatter cluster
            x_ax = 'Literasi Dewasa (%)' if 'Literasi Dewasa (%)' in cl_cols else cl_cols[0]
            y_ax = 'Enrollment PT (%)'   if 'Enrollment PT (%)'   in cl_cols else cl_cols[1]
            for cl_id in range(k_slider):
                sub = df_ml_cl[df_ml_cl['Cluster']==cl_id]
                axes8[1].scatter(sub[x_ax], sub[y_ax], s=60, alpha=0.75,
                                 color=CHART_COLORS[cl_id % len(CHART_COLORS)],
                                 edgecolors='white', lw=0.6,
                                 label=f'Cluster {cl_id} (n={len(sub)})')
            axes8[1].set_xlabel(x_ax)
            axes8[1].set_ylabel(y_ax)
            axes8[1].set_title('Scatter Cluster Negara', fontweight='bold')
            axes8[1].legend(fontsize=8)

            plt.tight_layout(); st.pyplot(fig8); plt.close(fig8)

            # Profil cluster
            st.markdown("**Profil Rata-rata per Cluster:**")
            profile = df_ml_cl.groupby('Cluster')[cl_cols].mean().round(2)
            st.dataframe(profile.style.background_gradient(cmap='RdPu'),
                         use_container_width=True)

            # Daftar negara per cluster
            df_named = df_piv[['country_name'] + cl_cols].dropna().copy()
            df_named['Cluster'] = KMeans(n_clusters=k_slider, random_state=42,
                                         n_init=10).fit_predict(
                sc_c.transform(df_named[cl_cols].values))
            with st.expander("Daftar negara per cluster"):
                for cl_id in range(k_slider):
                    names = df_named[df_named['Cluster']==cl_id]['country_name'].tolist()
                    st.markdown(f"**Cluster {cl_id}** ({len(names)} negara): " +
                                ", ".join(names[:15]) +
                                ("..." if len(names)>15 else ""))

# ═══════════════════════════════════════════════════════
#  TAB 5 — DATA MENTAH
# ═══════════════════════════════════════════════════════
with tab5:
    st.subheader("Data Mentah & Ekspor")

    cs, cn = st.columns([3,1])
    with cs:
        search = st.text_input("Cari negara...", placeholder="contoh: Indonesia")
    with cn:
        max_rows = st.number_input("Maks. baris", 50, 5000, 300, step=50)

    df_show = df_f.copy()
    if search:
        df_show = df_show[df_show['country_name'].str.contains(search, case=False, na=False)]

    show_cols = [c for c in ['country_name','country_code','year','label',
                              'value','region','income_group'] if c in df_show.columns]
    st.markdown(f"Menampilkan **{min(len(df_show), max_rows):,}** dari **{len(df_show):,}** baris")
    st.dataframe(df_show[show_cols].head(max_rows).sort_values(['country_name','year']),
                 use_container_width=True, height=420)

    st.download_button(
        label="Download CSV",
        data=df_show.to_csv(index=False).encode('utf-8'),
        file_name="world_bank_education_filtered.csv",
        mime="text/csv"
    )

    with st.expander("Statistik Deskriptif"):
        stats = (df_f.groupby('label')['value']
                 .agg(N='count', Mean='mean', Median='median',
                      Std='std', Min='min', Max='max')
                 .round(2).reset_index())
        st.dataframe(stats.style.background_gradient(subset=['Mean'], cmap='RdPu'),
                     use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style='text-align:center;color:{PINK_PRIMARY};font-size:0.85rem;padding:8px;'>
Dashboard Pendidikan Dunia — Proyek ADBC &nbsp;|&nbsp;
World Bank International Education Dataset &nbsp;|&nbsp; Dibuat dengan Streamlit
</div>""", unsafe_allow_html=True)
