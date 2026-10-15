import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="BIST Radar", page_icon="📈", layout="centered")

st.markdown("""
<style>
.stApp { background: #0b0f17; }
.block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 520px; }
h1, h2, h3, p, span, div, label { color: #e8ecf3; }
.title { font-size: 26px; font-weight: 800; letter-spacing: -0.5px; }
.sub { color: #8b95a7; font-size: 12px; margin-bottom: 14px; }
.card { background: #141a26; border: 1px solid #222b3d; border-radius: 16px;
        padding: 14px 16px; margin-bottom: 10px; }
.row { display: flex; justify-content: space-between; align-items: center; }
.rank { color: #8b95a7; font-size: 13px; font-weight: 700; width: 26px; }
.tk { font-size: 22px; font-weight: 800; letter-spacing: 0.5px; }
.px { color: #8b95a7; font-size: 13px; }
.pct { font-size: 18px; font-weight: 800; text-align: right; }
.lbl { color: #8b95a7; font-size: 11px; text-align: right; }
.up { color: #22c55e !important; } .dn { color: #ef4444 !important; }
.bar { height: 6px; background: #222b3d; border-radius: 4px; margin-top: 10px; }
.fill { height: 6px; border-radius: 4px; background: linear-gradient(90deg,#3b82f6,#22c55e); }
.meta { display:flex; gap:14px; margin-top:8px; color:#8b95a7; font-size:12px; }
.meta b { color:#e8ecf3; }
.grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px; }
.stat { background:#141a26; border:1px solid #222b3d; border-radius:14px; padding:12px; }
.stat .v { font-size:22px; font-weight:800; }
.stat .k { color:#8b95a7; font-size:11px; }
.warn { background:#1c1608; border:1px solid #4a3a10; border-radius:12px;
        padding:10px 12px; color:#e9c46a; font-size:12px; margin-top:14px; }
</style>
""", unsafe_allow_html=True)

TICKERS = """AKBNK ALARK ARCLK ASELS AKSEN BIMAS CIMSA DOHOL EGEEN EKGYO ENJSA ENKAI
EREGL FROTO GARAN GUBRF HALKB HEKTS ISCTR ISMEN KCHOL KONTR KORDS KRDMD MAVI MGROS
ODAS OTKAR OYAKC PETKM PGSUS SAHOL SASA SISE SOKM TAVHL TCELL THYAO TKFEN TOASO
TSKB TTKOM TUPRS ULKER VAKBN VESTL YKBNK AEFES""".split()
HORIZON = 42


@st.cache_data(ttl=3600, show_spinner="Borsa verileri indiriliyor...")
def load():
    df = yf.download([t + ".IS" for t in TICKERS], period="5y",
                     auto_adjust=True, progress=False)
    close = df["Close"].dropna(axis=1, thresh=400)
    vol = df["Volume"][close.columns]
    close.columns = [c.replace(".IS", "") for c in close.columns]
    vol.columns = close.columns
    return close, vol


def features(close, vol):
    r = lambda x: x.rank(axis=1, pct=True)
    mom63 = close.pct_change(63)
    mom21 = close.pct_change(21)
    volratio = vol.rolling(10).mean() / vol.rolling(60).mean()
    near_high = close / close.rolling(252).max()
    score = r(mom63) + r(mom21) + 0.5 * r(volratio) + r(near_high)
    return score, mom63, mom21, volratio, near_high


def backtest(close, score, top_n):
    fwd = close.shift(-HORIZON) / close - 1
    rows = []
    for i in range(252, len(close) - HORIZON, 21):
        d = close.index[i]
        s = score.iloc[i].dropna()
        if len(s) < 10:
            continue
        rows.append((d, fwd.loc[d, s.nlargest(top_n).index].mean(), fwd.loc[d].mean()))
    return pd.DataFrame(rows, columns=["tarih", "Strateji", "Tüm hisseler"]).set_index("tarih")


def cls(v):
    return "up" if v >= 0 else "dn"


st.markdown('<div class="title">📈 BIST Radar</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Momentum sıralaması · Yatırım tavsiyesi değildir</div>',
            unsafe_allow_html=True)

top_n = st.select_slider("Gösterilecek hisse sayısı", options=[3, 5, 8, 10], value=5)

close, vol = load()
score, mom63, mom21, volratio, near_high = features(close, vol)

last = pd.DataFrame({
    "skor": score.iloc[-1], "m3": mom63.iloc[-1] * 100, "m1": mom21.iloc[-1] * 100,
    "hacim": volratio.iloc[-1], "zirve": near_high.iloc[-1] * 100,
    "fiyat": close.iloc[-1],
}).dropna().sort_values("skor", ascending=False).head(top_n)

st.markdown("### 🔥 En güçlü hisseler")
for i, (tk, r) in enumerate(last.iterrows(), 1):
    w = max(5, min(100, r.skor / 3.5 * 100))
    st.markdown(f"""
    <div class="card">
      <div class="row">
        <div style="display:flex;align-items:center">
          <div class="rank">{i}</div>
          <div><div class="tk">{tk}</div><div class="px">₺{r.fiyat:,.2f}</div></div>
        </div>
        <div><div class="pct {cls(r.m3)}">{r.m3:+.1f}%</div><div class="lbl">son 3 ay</div></div>
      </div>
      <div class="bar"><div class="fill" style="width:{w:.0f}%"></div></div>
      <div class="meta">
        <span>1 ay: <b class="{cls(r.m1)}">{r.m1:+.1f}%</b></span>
        <span>Hacim: <b>{r.hacim:.1f}x</b></span>
        <span>Zirve: <b>%{r.zirve:.0f}</b></span>
      </div>
    </div>""", unsafe_allow_html=True)

bt = backtest(close, score, top_n)
st.markdown("### 🧪 Geçmiş test (2 aylık tutma)")
st.markdown(f"""
<div class="grid">
  <div class="stat"><div class="v {cls(bt['Strateji'].mean())}">{bt['Strateji'].mean():.1%}</div><div class="k">Strateji ortalaması</div></div>
  <div class="stat"><div class="v">{bt['Tüm hisseler'].mean():.1%}</div><div class="k">Tüm hisseler ortalaması</div></div>
  <div class="stat"><div class="v">{(bt['Strateji'] > bt['Tüm hisseler']).mean():.0%}</div><div class="k">Piyasayı geçme oranı</div></div>
  <div class="stat"><div class="v dn">{bt['Strateji'].min():.1%}</div><div class="k">En kötü dönem</div></div>
</div>""", unsafe_allow_html=True)
st.line_chart(bt, height=220)

st.markdown("""<div class="warn">⚠️ Yüksek skor = güçlü momentum, aynı zamanda aşırı ısınma
riski demektir. Geçmiş sonuçlar geleceği garanti etmez. Tek hisseye tüm parayı koymayın,
zarar-kes seviyesi belirleyin.</div>""", unsafe_allow_html=True)
