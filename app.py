import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="BIST Tarayıcı", page_icon="📈", layout="centered")

TICKERS = """AKBNK ALARK ARCLK ASELS AKSEN BIMAS CIMSA DOHOL EGEEN EKGYO ENJSA ENKAI
EREGL FROTO GARAN GUBRF HALKB HEKTS ISCTR ISMEN KCHOL KONTR KORDS KRDMD MAVI MGROS
ODAS OTKAR OYAKC PETKM PGSUS SAHOL SASA SISE SOKM TAVHL TCELL THYAO TKFEN TOASO
TSKB TTKOM TUPRS ULKER VAKBN VESTL YKBNK AEFES""".split()


@st.cache_data(ttl=3600, show_spinner="Veriler indiriliyor...")
def load():
    df = yf.download([t + ".IS" for t in TICKERS], period="5y",
                     auto_adjust=True, progress=False)
    close = df["Close"].dropna(axis=1, thresh=400)
    vol = df["Volume"][close.columns]
    return close, vol


def features(close, vol):
    r = lambda x: x.rank(axis=1, pct=True)
    mom63 = close.pct_change(63)
    mom21 = close.pct_change(21)
    volratio = vol.rolling(10).mean() / vol.rolling(60).mean()
    near_high = close / close.rolling(252).max()
    score = r(mom63) + r(mom21) + 0.5 * r(volratio) + r(near_high)
    return score, mom63, mom21, volratio, near_high


def backtest(close, score, horizon, top_n):
    fwd = close.shift(-horizon) / close - 1
    rows = []
    for i in range(252, len(close) - horizon, 21):
        d = close.index[i]
        s = score.iloc[i].dropna()
        if len(s) < 10:
            continue
        rows.append((d, fwd.loc[d, s.nlargest(top_n).index].mean(), fwd.loc[d].mean()))
    return pd.DataFrame(rows, columns=["tarih", "strateji", "tum_hisseler"]).set_index("tarih")


st.title("📈 BIST Momentum Tarayıcı")
st.caption("Araştırma aracıdır, yatırım tavsiyesi değildir. Geçmiş performans geleceği garanti etmez.")

top_n = st.slider("Sepetteki hisse sayısı", 1, 10, 5)
horizon = 42

close, vol = load()
score, mom63, mom21, volratio, near_high = features(close, vol)

last = pd.DataFrame({
    "Skor": score.iloc[-1],
    "3 ay %": mom63.iloc[-1] * 100,
    "1 ay %": mom21.iloc[-1] * 100,
    "Hacim oranı": volratio.iloc[-1],
    "Zirveye yakınlık": near_high.iloc[-1],
}).dropna().sort_values("Skor", ascending=False)

st.subheader("En yüksek skorlu hisseler")
st.dataframe(last.head(10).round(2), use_container_width=True)

st.subheader("Geriye dönük test")
bt = backtest(close, score, horizon, top_n)
c1, c2 = st.columns(2)
c1.metric("Strateji ort. (2 ay)", f"{bt.strateji.mean():.1%}")
c2.metric("Tüm hisseler ort.", f"{bt.tum_hisseler.mean():.1%}")
c3, c4 = st.columns(2)
c3.metric("Piyasayı geçme oranı", f"{(bt.strateji > bt.tum_hisseler).mean():.0%}")
c4.metric("En kötü dönem", f"{bt.strateji.min():.1%}")
st.line_chart(bt)

st.info("Skor yüksek = güçlü momentum; aşırı ısınma riski de taşır. "
        "Tek hisse yerine sepet ve zarar-kes seviyesi düşünün.")
