import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import streamlit as st

st.set_page_config(
    page_title="Bike Rental Dashboard",
    page_icon="🚴",
    layout="wide"
)

# ── Load Data ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    day_df = pd.read_csv("dashboard/day.csv")
    hour_df = pd.read_csv("dashboard/hour.csv")

    for df in [day_df, hour_df]:
        df['dteday'] = pd.to_datetime(df['dteday'])
        df['season_label'] = df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
        df['weather_label'] = df['weathersit'].map({
            1:'clear', 2:'misty/cloudy',
            3:'light rain/light snow', 4:'heavy rain/heavy snow'
        })
        df['year_label'] = df['yr'].map({0: 2011, 1: 2012})
        df['weekday_label'] = df['weekday'].map({
            0:'sunday', 1:'monday', 2:'tuesday', 3:'wednesday',
            4:'thursday', 5:'friday', 6:'saturday'
        })
        df['temp_c'] = df['temp'] * 41
        df['atemp_c'] = df['atemp'] * 50

    return day_df, hour_df

day_df, hour_df = load_data()

with st.sidebar:
    st.markdown("## 🚴 Filter Data")
    st.markdown("---")
    tahun = st.multiselect("Filter Tahun", [2011, 2012], default=[2011, 2012])

filtered_day = day_df[day_df['year_label'].isin(tahun)]
filtered_hour = hour_df[hour_df['year_label'].isin(tahun)]

# ── Helper formatter ──────────────────────────────────────────
def fmt(ax, axis='y'):
    f = plt.FuncFormatter(lambda x, _: f'{x:,.0f}')
    if axis == 'y':
        ax.yaxis.set_major_formatter(f)
    else:
        ax.xaxis.set_major_formatter(f)

st.title("🚴 Dashboard Penyewaan Sepeda")
st.markdown("---")

total = filtered_day['cnt'].sum()
avg = filtered_day['cnt'].mean()
peak = filtered_day['cnt'].max()
growth = (
    (day_df[day_df['year_label']==2012]['cnt'].sum() -
     day_df[day_df['year_label']==2011]['cnt'].sum()) /
    day_df[day_df['year_label']==2011]['cnt'].sum() * 100
)

c1, c2, c3, c4 = st.columns(4)
for col, val, label in zip(
    [c1, c2, c3, c4],
    [f"{total:,.0f}", f"{avg:,.0f}", f"{peak:,.0f}", f"+{growth:.1f}%"],
    ["Total Penyewaan", "Rata-rata/Hari", "Puncak/Hari", "Pertumbuhan 2011→2012"]
):
    col.markdown(f"""
    <div class="metric-card">
        <p class="metric-value">{val}</p>
        <p class="metric-label">{label}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabel ringkasan
tren = day_df.groupby(by='yr')['cnt'].agg(['sum','mean','max','min'])
tren.index = [2011, 2012]
tren.columns = ['Jumlah', 'Rata-Rata/Hari', 'Maksimal/Hari', 'Minimal/Hari']
growth_total = (tren.loc[2012,'Jumlah'] - tren.loc[2011,'Jumlah']) / tren.loc[2011,'Jumlah'] * 100

st.markdown(f"### 📊 Pertumbuhan total 2011 → 2012: **+{growth_total:.1f}%**")
st.dataframe(tren.style.format('{:,.0f}'), use_container_width=True)
st.markdown("<br>", unsafe_allow_html=True)

# Chart bulanan
monthly = filtered_day.groupby(['year_label','mnth'])['cnt'].sum().reset_index()
fig, ax = plt.subplots(figsize=(12, 5))
colors = {2011:'#4C72B0', 2012:'#DD8452'}
for yr, grp in monthly.groupby('year_label'):
    ax.plot(grp['mnth'], grp['cnt'], marker='o', lw=2.5, color=colors[yr], label=str(yr))
    ax.fill_between(grp['mnth'], grp['cnt'], alpha=0.1, color=colors[yr])
ax.set_xticks(range(1,13))
ax.set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
fmt(ax)
ax.set_title('Total Penyewaan Sepeda per Bulan (2011 vs 2012)', fontsize=14, fontweight='bold')
ax.set_xlabel('Bulan')
ax.set_ylabel('Total Penyewaan')
ax.legend(title='Tahun')
ax.spines[['top','right']].set_visible(False)
plt.tight_layout()
st.pyplot(fig)
plt.close()


st.markdown("<br>", unsafe_allow_html=True)

st.markdown("## 🌤️ Pengaruh Musim & Cuaca")
st.markdown("---")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

season_order = ['Spring', 'Summer', 'Fall', 'Winter']
season_stats = filtered_day.groupby('season_label')['cnt'].mean().reindex(season_order)
colors_season = ['#b5d4f4', '#378add', '#185fa5', '#85b7eb']
axes[0].bar(season_stats.index, season_stats.values, color=colors_season, edgecolor='none', width=0.6)
axes[0].set_title('Musim vs Rata-rata Penyewaan', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Musim')
axes[0].set_ylabel('Rata-rata Penyewaan/Hari')
fmt(axes[0])
axes[0].spines[['top','right']].set_visible(False)

weather_order = ['clear', 'misty/cloudy', 'light rain/light snow']
weather_stats = filtered_day.groupby('weather_label')['cnt'].mean().reindex(weather_order)
colors_weather = ['#1d9e75', '#5dcaa5', '#9fe1cb']
axes[1].bar(weather_stats.index, weather_stats.values, color=colors_weather, edgecolor='none', width=0.5)
axes[1].set_title('Cuaca vs Rata-rata Penyewaan', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Kondisi Cuaca')
axes[1].set_ylabel('Rata-rata Penyewaan/Hari')
fmt(axes[1])
axes[1].spines[['top','right']].set_visible(False)

plt.suptitle('Pengaruh Kondisi Lingkungan terhadap Penyewaan', fontsize=13, fontweight='bold')
plt.tight_layout()
st.pyplot(fig)
plt.close()


st.markdown("<br>", unsafe_allow_html=True)

st.markdown("## 🕐 Pola Penyewaan per Jam")
st.markdown("---")

hourly = filtered_hour.groupby('hr')['cnt'].mean().round(0)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

top5 = hourly.nlargest(5).sort_values(ascending=True)
axes[0].barh(top5.index.astype(str) + ':00', top5.values, color='#185fa5', edgecolor='none')
axes[0].set_title('Top 5 Jam Tersibuk', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Rata-rata Penyewaan/Jam')
axes[0].set_ylabel('Jam')
fmt(axes[0], axis='x')
axes[0].spines[['top','right']].set_visible(False)

bot5 = hourly.nsmallest(5).sort_values(ascending=False)
axes[1].barh(bot5.index.astype(str) + ':00', bot5.values, color='#9fe1cb', edgecolor='none')
axes[1].set_title('Top 5 Jam Tersepi', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Rata-rata Penyewaan/Jam')
axes[1].set_ylabel('Jam')
fmt(axes[1], axis='x')
axes[1].spines[['top','right']].set_visible(False)

plt.suptitle('Distribusi Penyewaan Sepeda per Jam', fontsize=13, fontweight='bold')
plt.tight_layout()
st.pyplot(fig)
plt.close()

# Full hourly chart
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### Rata-rata Penyewaan Seluruh Jam (0–23)")
fig2, ax2 = plt.subplots(figsize=(12, 4))
hourly_all = filtered_hour.groupby('hr')['cnt'].mean()
ax2.plot(hourly_all.index, hourly_all.values, color='#185fa5', lw=2, marker='o', ms=4)
ax2.fill_between(hourly_all.index, hourly_all.values, alpha=0.1, color='#185fa5')
ax2.set_xticks(range(0, 24))
ax2.set_xlabel('Jam')
ax2.set_ylabel('Rata-rata Penyewaan')
fmt(ax2)
ax2.spines[['top','right']].set_visible(False)
plt.tight_layout()
st.pyplot(fig2)
plt.close()
