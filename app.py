import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Black Panter", page_icon="🐆", layout="centered")

CSS = """
<style>
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.stApp {
  background: linear-gradient(160deg, #e6e2b4 0%, #cfc982 50%, #aaa157 100%);
  background-attachment: fixed;
}
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 560px; }
.stApp, .stApp p, .stApp span, .stApp label, .stApp div { color: #2b2a14; }
.hero { text-align: center; margin-bottom: 18px; }
.hero .logo { font-size: 44px; line-height: 1; }
.hero .name { font-size: 34px; font-weight: 900; letter-spacing: 1px; color: #2b2a14; }
.hero .tag { font-size: 13px; color: #5d5828; margin-top: 2px; }
.sec { font-size: 16px; font-weight: 800; margin: 20px 0 8px; color: #2b2a14; }
.top3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.pick { background: rgba(255,252,232,.6); border: 1px solid rgba(80,70,20,.18);
        border-radius: 16px; padding: 10px 8px; text-align: center; }
.pick .t { font-weight: 900; font-size: 16px; }
.pick .p { font-size: 12px; color: #5d5828; }
.pick .g { font-weight: 800; font-size: 15px; margin-top: 2px; }
.tbl-wrap { overflow-x: auto; border-radius: 18px; background: rgba(255,252,232,.6);
            border: 1px solid rgba(80,70,20,.18); box-shadow: 0 6px 24px rgba(60,50,10,.12); }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th { text-align: right; padding: 10px 12px; font-size: 11px; letter-spacing: .5px;
     text-transform: uppercase; color: #6b6531; white-space: nowrap; }
td { padding: 11px 12px; text-align: right; border-top: 1px solid rgba(80,70,20,.12);
     font-variant-numeric: tabular-nums; white-space: nowrap; }
th:first-child, td:first-child { text-align: left; position: sticky; left: 0;
     background: rgba(240,236,196,.97); }
.tk { font-weight: 900; letter-spacing: .5px; }
.up { color: #2e7d32 !important; font-weight: 700; }
.dn { color: #b3261e !important; font-weight: 700; }
.note { font-size: 11px; color: #5d5828; margin-top: 14px; text-align: center; }
div[role="radiogroup"] label p { color: #2b2a14 !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

TICKERS = """AKBNK ALARK ARCLK ASELS AKSEN BIMAS CIMSA DOHOL EGEEN EKGYO ENJSA ENKAI
EREGL FROTO GARAN GUBRF HALKB HEKTS ISCTR ISMEN KCHOL KONTR KORDS KRDMD MAVI MGROS
ODAS OTKAR OYAKC PETKM PGSUS SAHOL SASA SISE SOKM TAVHL TCELL THYAO TKFEN TOASO
TSKB TTKOM TUPRS ULKER VAKBN VESTL YKBNK AEFES""".split()


@st.cache_data(ttl=900, show_spinner="Borsa İstanbul verileri alınıyor...")
def load():
    syms = [t + ".IS" for t in TICKERS]
    close, vol = pd.DataFrame(), pd.DataFrame()
    try:
        df = yf.download(syms, period="1y", auto_adjust=True,
                         progress=False, threads=True)
        close, vol = df["Close"], df["Volume"]
    except Exception:
        pass
    if close.empty or close.dropna(how="all").empty:
        cs, vs = {}, {}
        for s in syms:
            try:
                h = yf.Ticker(s).history(period="1y", auto_adjust=True)
                if len(h) > 70:
                    cs[s], vs[s] = h["Close"], h["Volume"]
            except Exception:
                continue
        close, vol = pd.DataFrame(cs), pd.DataFrame(vs)
    if close.empty:
        return close, vol
    close = close.dropna(axis=1, thresh=100).ffill()
    vol = vol[close.columns]
    close.columns = [c.replace(".IS", "") for c in close.columns]
    vol.columns = close.columns
    return close, vol


def cls(v):
    return "up" if v >= 0 else "dn"


st.markdown("""
<div class="hero">
  <div class="logo">🐆</div>
  <div class="name">BLACK PANTER</div>
  <div class="tag">Borsa İstanbul · Hisseler ve Fiyat Tablosu</div>
</div>""", unsafe_allow_html=True)

close, vol = load()
if close.empty or len(close) < 70:
    st.error("Borsa verileri şu an alınamadı. Birkaç dakika sonra tekrar deneyin.")
    st.button("Tekrar dene", on_click=st.cache_data.clear)
    st.stop()

last = close.iloc[-1]
data = pd.DataFrame({
    "fiyat": last,
    "gun": (last / close.iloc[-2] - 1) * 100,
    "m1": (last / close.iloc[-22] - 1) * 100,
    "m3": (last / close.iloc[-64] - 1) * 100,
})
volratio = vol.rolling(10).mean().iloc[-1] / vol.rolling(60).mean().iloc[-1]
near_high = last / close.rolling(200, min_periods=60).max().iloc[-1]
rk = lambda s: s.rank(pct=True)
data["skor"] = rk(data.m3) + rk(data.m1) + 0.5 * rk(volratio) + rk(near_high)
data = data.dropna()

st.markdown('<div class="sec">🔥 Öne çıkan momentum</div>', unsafe_allow_html=True)
top = data.sort_values("skor", ascending=False).head(3)
picks = "".join(
    f'<div class="pick"><div class="t">{tk}</div><div class="p">₺{r.fiyat:,.2f}</div>'
    f'<div class="g {cls(r.m3)}">{r.m3:+.1f}%</div><div class="p">3 ay</div></div>'
    for tk, r in top.iterrows())
st.markdown(f'<div class="top3">{picks}</div>', unsafe_allow_html=True)

st.markdown('<div class="sec">📊 Tüm hisseler</div>', unsafe_allow_html=True)
sort = st.radio("Sırala", ["Skor", "Günlük", "1 Ay", "3 Ay", "A-Z"],
                horizontal=True, label_visibility="collapsed")
key = {"Skor": ("skor", False), "Günlük": ("gun", False), "1 Ay": ("m1", False),
       "3 Ay": ("m3", False)}
if sort == "A-Z":
    view = data.sort_index()
else:
    view = data.sort_values(key[sort][0], ascending=key[sort][1])

rows = "".join(
    f'<tr><td class="tk">{tk}</td><td>₺{r.fiyat:,.2f}</td>'
    f'<td class="{cls(r.gun)}">{r.gun:+.2f}%</td>'
    f'<td class="{cls(r.m1)}">{r.m1:+.1f}%</td>'
    f'<td class="{cls(r.m3)}">{r.m3:+.1f}%</td></tr>'
    for tk, r in view.iterrows())
st.markdown(
    '<div class="tbl-wrap"><table><thead><tr><th>Hisse</th><th>Fiyat</th>'
    '<th>Gün</th><th>1 Ay</th><th>3 Ay</th></tr></thead>'
    f'<tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="note">Son veri: {close.index[-1].strftime("%d.%m.%Y")} · '
    'Veriler gecikmeli olabilir · Yatırım tavsiyesi değildir</div>',
    unsafe_allow_html=True)
