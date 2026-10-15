import pandas as pd
import streamlit as st
import yfinance as yf

from PIL import Image, ImageDraw


def make_icon():
    im = Image.new("RGBA", (128, 128), (7, 8, 18, 255))
    d = ImageDraw.Draw(im)
    cy, mg = (0, 240, 255, 255), (255, 43, 214, 255)
    for x, y in [(24, 54), (48, 30), (80, 30), (104, 54)]:
        d.ellipse([x - 11, y - 14, x + 11, y + 14], outline=cy, width=4)
    d.ellipse([30, 64, 98, 120], outline=mg, width=4)
    d.ellipse([46, 82, 82, 104], fill=(252, 238, 9, 255))
    d.ellipse([60, 80, 68, 106], fill=(5, 6, 13, 255))
    return im


st.set_page_config(page_title="Black Panter", page_icon=make_icon(), layout="centered")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Share+Tech+Mono&display=swap');
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.stApp {
  background:
    linear-gradient(rgba(0,240,255,.05) 1px, transparent 1px) 0 0 / 34px 34px,
    linear-gradient(90deg, rgba(255,43,214,.05) 1px, transparent 1px) 0 0 / 34px 34px,
    radial-gradient(ellipse at 50% -10%, #1b0b3a 0%, #070812 55%, #03030a 100%);
  background-attachment: fixed;
}
.block-container { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 560px; }
.stApp, .stApp p, .stApp span, .stApp label, .stApp div {
  color: #d6f6ff; font-family: 'Share Tech Mono', monospace;
}
.hero { text-align: center; margin-bottom: 18px; }
.hero .logo { display: flex; justify-content: center; margin-bottom: 4px;
  filter: drop-shadow(0 0 14px rgba(255,43,214,.45)); }
.hero .name { font-family: 'Orbitron', sans-serif; font-weight: 900; font-size: 34px;
  letter-spacing: 6px; color: #00f0ff !important;
  text-shadow: 0 0 8px #00f0ff, 0 0 22px #00f0ff88, 3px 0 #ff2bd6aa, -3px 0 #fcee0955; }
.hero .tag { font-size: 12px; letter-spacing: 3px; color: #ff2bd6 !important;
  text-transform: uppercase; margin-top: 4px; }
.line { height: 2px; margin: 12px auto 0; width: 80%;
  background: linear-gradient(90deg, transparent, #00f0ff, #ff2bd6, #00f0ff, transparent);
  box-shadow: 0 0 10px #00f0ff; }
.sec { font-family: 'Orbitron', sans-serif; font-size: 13px; letter-spacing: 3px;
  text-align: center; margin: 22px 0 10px; color: #fcee09 !important;
  text-shadow: 0 0 8px #fcee0966; }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.stat, .pick { text-align: center; background: rgba(8,12,30,.78);
  border: 1px solid rgba(0,240,255,.45); border-radius: 6px; padding: 10px 6px;
  box-shadow: 0 0 14px rgba(0,240,255,.15), inset 0 0 14px rgba(0,240,255,.06); }
.stat .v { font-family: 'Orbitron', sans-serif; font-size: 22px; font-weight: 700; }
.stat .k, .pick .p { font-size: 11px; color: #7fa7b5 !important; letter-spacing: 1px; }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.pick.bad { border-color: rgba(255,46,99,.5);
  box-shadow: 0 0 14px rgba(255,46,99,.15), inset 0 0 14px rgba(255,46,99,.06); }
.pick .t { font-family: 'Orbitron', sans-serif; font-weight: 700; font-size: 15px;
  letter-spacing: 1px; }
.pick .g { font-family: 'Orbitron', sans-serif; font-weight: 700; font-size: 15px; margin-top: 2px; }
.tbl-wrap { max-height: 560px; overflow: auto; border-radius: 6px;
  background: rgba(6,9,24,.85); border: 1px solid rgba(255,43,214,.5);
  box-shadow: 0 0 18px rgba(255,43,214,.2); }
table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; }
th { position: sticky; top: 0; background: #0c0a24; z-index: 2; padding: 10px 6px;
  font-size: 10px; letter-spacing: 2px; color: #00f0ff !important;
  border-bottom: 1px solid #00f0ff; text-transform: uppercase; }
td { padding: 9px 6px; border-top: 1px solid rgba(0,240,255,.12); white-space: nowrap; }
tr:hover td { background: rgba(0,240,255,.07); }
.tk { font-family: 'Orbitron', sans-serif; font-weight: 700; letter-spacing: 1px;
  color: #ffffff !important; }
.up { color: #00ff9c !important; text-shadow: 0 0 6px #00ff9c66; }
.dn { color: #ff2e63 !important; text-shadow: 0 0 6px #ff2e6366; }
.note { font-size: 10px; color: #5f7f8c !important; margin-top: 14px;
  text-align: center; letter-spacing: 1px; }
.stTextInput input { background: #080c1e !important; color: #00f0ff !important;
  border: 1px solid rgba(0,240,255,.5) !important; border-radius: 6px !important; }
.stTextInput label p, div[role="radiogroup"] label p { color: #d6f6ff !important; }
div[role="radiogroup"] { justify-content: center; }
.stButton button { background: #080c1e; color: #00f0ff; border: 1px solid #00f0ff; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

TICKERS = """
A1CAP ACSEL ADEL ADESE AEFES AFYON AGESA AGHOL AGROT AGYO AHGAZ AKBNK AKCNS AKENR AKFGY
AKFYE AKGRT AKMGY AKSA AKSEN AKSGY AKSUE AKYHO ALARK ALBRK ALCAR ALCTL ALFAS ALGYO ALKA
ALKIM ALKLC ALMAD ALTNY ALVES ANELE ANGEN ANHYT ANSGR ARASE ARCLK ARDYZ ARENA ARMGD ARSAN
ARTMS ARZUM ASELS ASGYO ASTOR ASUZU ATAGY ATAKP ATATP ATEKS ATLAS ATSYH AVGYO AVHOL AVOD
AVPGY AVTUR AYCES AYDEM AYEN AYES AYGAZ AZTEK
BAGFS BAKAB BALAT BANVT BARMA BASCM BASGZ BAYRK BEGYO BERA BEYAZ BFREN BIENY BIGCH BIMAS
BINHO BIOEN BIZIM BJKAS BLCYT BMSCH BMSTL BNTAS BOBET BORLS BORSK BOSSA BRISA BRKSN BRKVY
BRLSM BRMEN BRSAN BRYAT BSOKE BTCIM BUCIM BURCE BURVA BVSAN BYDNR
CANTE CASA CATES CCOLA CELHA CEMAS CEMTS CEOEM CGCAM CIMSA CLEBI CMBTN CMENT CONSE COSMO
CRDFA CRFSA CUSAN CVKMD CWENE
DAGHL DAGI DAPGM DARDL DENGE DERHL DERIM DESA DESPC DEVA DGATE DGGYO DGNMO DIRIT DITAS
DMRGD DMSAS DNISI DOAS DOBUR DOCO DOFER DOGUB DOHOL DOKTA DURDO DYOBY DZGYO
EBEBK ECILC ECZYT EDATA EDIP EFORC EGEEN EGEPO EGGUB EGPRO EGSER EKGYO EKIZ EKOS EKSUN
ELITE EMKEL EMNIS ENJSA ENKAI ENSRI EPLAS ERBOS ERCB EREGL ERSU ESCAR ESCOM ESEN ETILR
ETYAT EUHOL EUKYO EUPWR EUREN EUYO EYGYO
FADE FENER FLAP FMIZP FONET FORMT FORTE FRIGO FROTO FZLGY
GARAN GARFA GEDIK GEDZA GENIL GENTS GEREL GESAN GIPTA GLBMD GLCVY GLRYH GLYHO GMTAS GOKNR
GOLTS GOODY GOZDE GRNYO GRSEL GRTRK GSDDE GSDHO GSRAY GUBRF GWIND GZNMI
HALKB HATEK HATSN HDFGS HEDEF HEKTS HKTM HLGYO HTTBT HUBVC HUNER HURGZ
ICBCT ICUGS IDGYO IEYHO IHAAS IHEVA IHGZT IHLAS IHLGM IHYAY IMASM INDES INFO INGRM INTEM
INVEO INVES IPEKE ISATR ISBIR ISBTR ISCTR ISDMR ISFIN ISGSY ISGYO ISKPL ISKUR ISMEN ISSEN
ISYAT IZENR IZFAS IZINV IZMDC
JANTS
KAPLM KARSN KARTN KARYE KATMR KAYSE KBORU KCAER KCHOL KENT KERVN KERVT KFEIN KGYO KIMMR
KLGYO KLKIM KLMSN KLNMA KLRHO KLSER KLSYN KMPUR KNFRT KOCMT KONKA KONTR KONYA KOPOL KORDS
KOTON KRDMA KRDMB KRDMD KRGYO KRONT KRPLS KRSTL KRTEK KRVGD KSTUR KTLEV KTSKR KUTPO KUVVA
KUYAS KZBGY KZGYO
LIDER LIDFA LILAK LINK LKMNH LMKDC LOGO LRSHO LUKSK
MAALT MACKO MAGEN MAKIM MAKTK MANAS MARBL MARKA MARTI MAVI MEDTR MEGAP MEGMT MEKAG MEPET
MERCN MERIT MERKO METRO METUR MGROS MHRGY MIATK MMCAS MNDRS MNDTR MOBTL MPARK MRGYO MRSHL
MSGYO MTRKS MTRYO MZHLD
NATEN NETAS NIBAS NTGAZ NTHOL NUGYO NUHCM
OBAMS OBASE ODAS ODINE OFSYM ONCSM ORCAY ORGE ORMA OSMEN OSTIM OTKAR OTTO OYAKC OYAYO OYLUM
OYYAT OZGYO OZKGY OZRDN OZSUB OZYSR
PAGYO PAMEL PAPIL PARSN PASEU PCILT PEGYO PEKGY PENGD PENTA PETKM PETUN PGSUS PINSU PKART
PKENT PLTUR PNLSN PNSUT POLHO POLTK PRDGS PRKAB PRKME PRZMA PSDTC PSGYO
QUAGR
RALYH RAYSG REEDR RNPOL RODRG ROYAL RTALB RUBNS RYGYO RYSAS
SAFKR SAHOL SAMAT SANEL SANFM SANKO SARKY SASA SAYAS SDTTR SEGYO SEKFK SEKUR SELEC SELGD
SELVA SEYKM SILVR SISE SKBNK SKTAS SKYLP SKYMD SMART SMRTG SMRVA SNGYO SNICA SNKRN SNPAM
SODSN SOKE SOKM SONME SRVGY SUMAS SUNTK SURGY SUWEN
TABGD TARKM TATEN TATGD TAVHL TBORG TCELL TDGYO TEKTU TERA TETMT TEZOL TGSAS THYAO TIRE
TKFEN TKNSA TLMAN TMPOL TMSN TNZTP TOASO TRCAS TRGYO TRILC TSGYO TSKB TSPOR TTKOM TTRAK
TUCLK TUKAS TUPRS TURGG TURSG
UFUK ULAS ULKER ULUFA ULUSE ULUUN UMPAS UNLU USAK UZERB
VAKBN VAKFN VAKKO VANGD VBTYZ VERTU VERUS VESBE VESTL VKFYO VKGYO VKING VRGYO
YAPRK YATAS YAYLA YEOTK YESIL YGGYO YGYO YIGIT YKBNK YKSLN YONGA YUNSA YYAPI YYLGD
ZEDUR ZOREN ZRGYO
""".split()


@st.cache_data(ttl=1800, show_spinner="Borsa İstanbul taranıyor... (ilk açılış ~1 dk sürebilir)")
def load(extra: tuple):
    syms = sorted(set(TICKERS + list(extra)))
    syms = [s + ".IS" for s in syms]
    cs, vs = [], []
    for i in range(0, len(syms), 100):
        chunk = syms[i:i + 100]
        try:
            df = yf.download(chunk, period="1y", auto_adjust=True,
                             progress=False, threads=True)
            c, v = df["Close"], df["Volume"]
            if isinstance(c, pd.Series):
                c, v = c.to_frame(chunk[0]), v.to_frame(chunk[0])
            cs.append(c)
            vs.append(v)
        except Exception:
            continue
    if not cs:
        return pd.DataFrame(), pd.DataFrame()
    close, vol = pd.concat(cs, axis=1), pd.concat(vs, axis=1)
    close = close.loc[:, ~close.columns.duplicated()]
    vol = vol.loc[:, ~vol.columns.duplicated()]
    close = close.dropna(axis=1, thresh=100)
    end = close.index[-1]
    alive = [c for c in close.columns
             if close[c].last_valid_index() is not None
             and close[c].last_valid_index() >= end - pd.Timedelta(days=10)]
    close = close[alive].ffill()
    vol = vol[alive]
    close.columns = [c.replace(".IS", "") for c in close.columns]
    vol.columns = close.columns
    return close, vol


def cls(v):
    return "up" if v >= 0 else "dn"


st.markdown("""
<div class="hero">
  <div class="logo"><svg viewBox="0 0 200 200" width="130" height="130" xmlns="http://www.w3.org/2000/svg"><defs><filter id="gl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter><radialGradient id="ir" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#fcee09"/><stop offset="70%" stop-color="#00ff9c"/><stop offset="100%" stop-color="#007a5a"/></radialGradient></defs><g filter="url(#gl)" stroke-width="3.5" fill="#0a0c22"><ellipse cx="42" cy="86" rx="14" ry="20" transform="rotate(-22 42 86)" stroke="#00f0ff"/><ellipse cx="78" cy="50" rx="15" ry="21" transform="rotate(-8 78 50)" stroke="#00f0ff"/><ellipse cx="122" cy="50" rx="15" ry="21" transform="rotate(8 122 50)" stroke="#00f0ff"/><ellipse cx="158" cy="86" rx="14" ry="20" transform="rotate(22 158 86)" stroke="#00f0ff"/><path d="M100 92 C138 92 162 124 162 150 C162 176 136 188 100 188 C64 188 38 176 38 150 C38 124 62 92 100 92 Z" stroke="#ff2bd6"/></g><path d="M60 142 Q100 106 140 142 Q100 178 60 142 Z" fill="#05060d" stroke="#00f0ff" stroke-width="2.5" filter="url(#gl)"/><circle cx="100" cy="142" r="17" fill="url(#ir)"/><ellipse cx="100" cy="142" rx="4.5" ry="16" fill="#05060d"/><circle cx="94" cy="135" r="3" fill="#ffffff" opacity=".85"/></svg></div>
  <div class="name">BLACK PANTER</div>
  <div class="tag">// Borsa İstanbul · Tüm Hisseler //</div>
  <div class="line"></div>
</div>""", unsafe_allow_html=True)

extra_raw = st.text_input("Hisse ekle (eksik varsa kodunu yazın, virgülle ayırın)",
                          placeholder="örn: TRHOL, ABCDE")
extra = tuple(x.strip().upper() for x in extra_raw.replace(" ", ",").split(",") if x.strip())

close, vol = load(extra)
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
volratio = (vol.rolling(10).mean().iloc[-1] / vol.rolling(60).mean().iloc[-1])
volratio = volratio.replace([float("inf"), -float("inf")], float("nan"))
near_high = last / close.rolling(200, min_periods=60).max().iloc[-1]
rk = lambda s: s.rank(pct=True)
data["skor"] = (rk(data.m3) + rk(data.m1)
                + 0.5 * rk(volratio).fillna(0.5) + rk(near_high).fillna(0.5))
data = data.dropna(subset=["fiyat", "gun", "m1", "m3", "skor"])

up_n, dn_n = int((data.gun > 0).sum()), int((data.gun < 0).sum())
st.markdown(f"""
<div class="stats">
  <div class="stat"><div class="v up">{up_n}</div><div class="k">YÜKSELEN</div></div>
  <div class="stat"><div class="v" style="color:#00f0ff">{len(data)}</div><div class="k">HİSSE</div></div>
  <div class="stat"><div class="v dn">{dn_n}</div><div class="k">DÜŞEN</div></div>
</div>""", unsafe_allow_html=True)


def cards(df, bad=False):
    return "".join(
        f'<div class="pick{" bad" if bad else ""}"><div class="t">{tk}</div>'
        f'<div class="p">₺{r.fiyat:,.2f}</div>'
        f'<div class="g {cls(r.m3)}">{r.m3:+.1f}%</div><div class="p">3 AY</div></div>'
        for tk, r in df.iterrows())


ranked = data.sort_values("skor", ascending=False)
st.markdown('<div class="sec">▲ EN GÜÇLÜ MOMENTUM</div>', unsafe_allow_html=True)
st.markdown(f'<div class="grid3">{cards(ranked.head(3))}</div>', unsafe_allow_html=True)
st.markdown('<div class="sec">▼ EN ZAYIF MOMENTUM</div>', unsafe_allow_html=True)
st.markdown(f'<div class="grid3">{cards(ranked.tail(3).iloc[::-1], True)}</div>',
            unsafe_allow_html=True)

st.markdown('<div class="sec">◆ FİYAT TABLOSU</div>', unsafe_allow_html=True)
q = st.text_input("Hisse ara", placeholder="örn: THYAO")
sort = st.radio("Sırala", ["Skor", "Günlük", "1 Ay", "3 Ay", "A-Z"],
                horizontal=True, label_visibility="collapsed")
cols = {"Skor": "skor", "Günlük": "gun", "1 Ay": "m1", "3 Ay": "m3"}
view = data.sort_index() if sort == "A-Z" else data.sort_values(cols[sort], ascending=False)
if q:
    view = view[view.index.str.contains(q.strip().upper())]

rows = "".join(
    f'<tr><td class="tk">{tk}</td><td>₺{r.fiyat:,.2f}</td>'
    f'<td class="{cls(r.gun)}">{r.gun:+.2f}%</td>'
    f'<td class="{cls(r.m1)}">{r.m1:+.1f}%</td>'
    f'<td class="{cls(r.m3)}">{r.m3:+.1f}%</td></tr>'
    for tk, r in view.iterrows())
st.markdown(
    '<div class="tbl-wrap"><table><thead><tr><th>HİSSE</th><th>FİYAT</th>'
    '<th>GÜN</th><th>1 AY</th><th>3 AY</th></tr></thead>'
    f'<tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="note">{len(view)} hisse · Son veri: {close.index[-1].strftime("%d.%m.%Y")} '
    '· Veriler gecikmeli olabilir · Yatırım tavsiyesi değildir</div>',
    unsafe_allow_html=True)
