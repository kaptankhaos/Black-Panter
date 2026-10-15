import html as _h
import json
import math
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote

import requests
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw

try:
    from streamlit_js_eval import streamlit_js_eval
except Exception:  # paket yoksa uygulama yine de çalışır (kayıt devre dışı)
    streamlit_js_eval = None


def make_icon():
    im = Image.new("RGBA", (128, 128), (13, 18, 28, 255))
    d = ImageDraw.Draw(im)
    gold = (212, 175, 106, 255)
    d.rounded_rectangle([6, 6, 122, 122], radius=30, outline=gold, width=5)
    d.line([(28, 88), (52, 64), (68, 76), (100, 38)], fill=gold, width=9, joint="curve")
    d.ellipse([92, 30, 108, 46], fill=(241, 217, 160, 255))
    return im


st.set_page_config(page_title="Akıllı Portföy", page_icon=make_icon(), layout="centered")

# ───────────────────────── TASARIM ─────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap');
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent; }
.stApp {
  background:
    radial-gradient(900px 420px at 50% -120px, rgba(212,175,106,.16) 0%, transparent 70%),
    radial-gradient(700px 500px at 100% 100%, rgba(46,204,143,.06) 0%, transparent 60%),
    #07090f;
  background-attachment: fixed;
  color: #e9edf5;
  font-family: 'Manrope', -apple-system, sans-serif;
}
.block-container { padding: 1.2rem 1rem 4rem; max-width: 560px; }
.stApp p, .stApp label, .stApp li, .stApp span { font-family: 'Manrope', sans-serif; }
.stApp p, .stApp label { color: #e9edf5; }

/* Başlık */
.brand { display: flex; align-items: center; justify-content: center; gap: 12px; margin: 6px 0 2px; }
.brand .nm { font-family: 'Playfair Display', serif; font-weight: 800; font-size: 31px;
  background: linear-gradient(120deg, #f6e3b4, #d4af6a 55%, #b98b3e);
  -webkit-background-clip: text; background-clip: text; color: transparent;
  -webkit-text-fill-color: transparent; letter-spacing: .5px; }
.brand-sub { text-align: center; color: #8a93a6 !important; font-size: 11px;
  letter-spacing: 3px; text-transform: uppercase; margin-bottom: 14px; }

/* Sekmeler */
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: rgba(15,20,32,.85); padding: 5px;
  border-radius: 16px; border: 1px solid rgba(212,175,106,.18); }
.stTabs [data-baseweb="tab"] { flex: 1; height: 42px; border-radius: 12px; padding: 0 4px;
  background: transparent; justify-content: center; }
.stTabs [data-baseweb="tab"] p { font-size: 12px; font-weight: 700; color: #8a93a6 !important;
  white-space: nowrap; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #e7c887, #b98b3e) !important; }
.stTabs [aria-selected="true"] p { color: #1a1405 !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none !important; }

/* Kartlar */
.glass { background: linear-gradient(145deg, rgba(27,34,52,.88), rgba(13,17,27,.92));
  border: 1px solid rgba(212,175,106,.2); border-radius: 20px; padding: 18px;
  box-shadow: 0 10px 40px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.04); }
.sum { text-align: center; margin: 14px 0; }
.sum .lbl { color: #8a93a6 !important; font-size: 11px; letter-spacing: 2.5px; text-transform: uppercase; }
.sum .big { font-family: 'Playfair Display', serif; font-weight: 700; font-size: 38px; margin: 4px 0 2px;
  color: #f6e3b4 !important; }
.sum .pl { font-weight: 800; font-size: 16px; }
.sum .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 16px;
  padding-top: 14px; border-top: 1px solid rgba(212,175,106,.15); }
.sum .row div b { display: block; font-size: 15px; color: #e9edf5 !important; margin-top: 2px; }
.sum .row div span { color: #8a93a6 !important; font-size: 11px; letter-spacing: 1px; }
.up { color: #2ecc8f !important; } .dn { color: #ff5d6c !important; }
.hold { background: linear-gradient(145deg, rgba(24,30,46,.9), rgba(13,17,27,.95));
  border: 1px solid rgba(212,175,106,.16); border-left: 3px solid #d4af6a; border-radius: 16px;
  padding: 14px 16px; margin-top: 10px; }
.hold.g { border-left-color: #2ecc8f; } .hold.r { border-left-color: #ff5d6c; }
.h-top { display: flex; justify-content: space-between; align-items: flex-start; }
.h-tk { font-family: 'Playfair Display', serif; font-weight: 700; font-size: 22px; color: #f6e3b4 !important; }
.h-sub { color: #8a93a6 !important; font-size: 12px; margin-top: 2px; }
.h-r { text-align: right; }
.h-pl { font-weight: 800; font-size: 17px; } .h-pct { font-weight: 700; font-size: 13px; }
.h-bot { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-top: 12px;
  padding-top: 10px; border-top: 1px dashed rgba(255,255,255,.08); font-size: 11px; color: #8a93a6 !important; }
.h-bot b { display: block; color: #e9edf5 !important; font-size: 13px; margin-top: 2px; }
.empty { text-align: center; padding: 34px 16px; color: #8a93a6 !important; }
.empty .ic { font-size: 34px; }
.sec { font-family: 'Playfair Display', serif; font-weight: 700; font-size: 18px; margin: 20px 0 8px;
  color: #f6e3b4 !important; }
.hint { color: #8a93a6 !important; font-size: 12px; margin: 4px 0 10px; }
.res { text-align: center; }
.res .big { font-family: 'Playfair Display', serif; font-size: 34px; font-weight: 700; }
.tbl { max-height: 330px; overflow: auto; border-radius: 14px; border: 1px solid rgba(212,175,106,.18);
  background: rgba(10,13,21,.8); margin-top: 8px; }
.tbl table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; }
.tbl th { position: sticky; top: 0; background: #121828; color: #d4af6a !important; font-size: 10px;
  letter-spacing: 1.5px; padding: 9px 4px; text-transform: uppercase; }
.tbl td { padding: 9px 4px; border-top: 1px solid rgba(255,255,255,.05); color: #e9edf5; }
.news { display: block; text-decoration: none !important; background: rgba(15,20,32,.85);
  border: 1px solid rgba(212,175,106,.14); border-radius: 14px; padding: 12px 14px; margin-top: 8px; }
.news .t { color: #eef1f7 !important; font-weight: 700; font-size: 14px; line-height: 1.4; }
.news .m { color: #8a93a6 !important; font-size: 11px; margin-top: 6px; }
.news .m b { color: #d4af6a !important; }
.sel { text-align: center; margin: 8px 0; }
.sel .tk { font-family: 'Playfair Display', serif; font-size: 32px; font-weight: 800; color: #f6e3b4 !important; }
.loading { text-align: center; padding: 40px 10px; color: #d4af6a !important; letter-spacing: 2px; }
.note { text-align: center; font-size: 10px; color: #5d667a !important; margin-top: 22px; line-height: 1.6; }

/* Form elemanları */
div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="textarea"] {
  background: #0d1320 !important; border-radius: 12px !important;
  border: 1px solid rgba(212,175,106,.28) !important; }
input, textarea { color: #f3f5fa !important; -webkit-text-fill-color: #f3f5fa !important;
  background: transparent !important; font-family: 'Manrope', sans-serif !important; }
input::placeholder, textarea::placeholder { color: #5d667a !important; -webkit-text-fill-color: #5d667a !important; }
.stNumberInput button { background: #141b2c !important; color: #d4af6a !important; border: none !important; }
.stTextInput label p, .stNumberInput label p, .stTextArea label p, .stCheckbox label p,
div[role="radiogroup"] label p { color: #c9d0de !important; font-size: 13px !important; font-weight: 600; }
[data-testid="stForm"] { background: linear-gradient(145deg, rgba(27,34,52,.88), rgba(13,17,27,.92));
  border: 1px solid rgba(212,175,106,.25) !important; border-radius: 20px; padding: 14px; }
[data-testid="stExpander"] { border: 1px solid rgba(212,175,106,.18) !important; border-radius: 14px !important;
  background: rgba(15,20,32,.7) !important; margin-top: 4px; }
[data-testid="stExpander"] summary p { color: #d4af6a !important; font-weight: 700; font-size: 13px; }
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
  width: 100%; border-radius: 12px; border: 1px solid rgba(212,175,106,.4); background: #111726;
  color: #ecd9a8 !important; font-weight: 700; min-height: 44px; }
.stButton > button p, .stFormSubmitButton > button p, .stDownloadButton > button p { color: inherit !important; }
button[kind="primary"], button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primaryFormSubmit"] {
  background: linear-gradient(135deg, #f0d596, #c39440) !important; color: #1a1405 !important;
  border: none !important; box-shadow: 0 6px 22px rgba(212,175,106,.28); }
button[kind="primary"] p, button[data-testid="stBaseButton-primary"] p,
button[data-testid="stBaseButton-primaryFormSubmit"] p { color: #1a1405 !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ───────────────────────── YARDIMCILAR ─────────────────────────
TICKERS = sorted(set("""
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
""".split()))
POPULAR = ["THYAO", "GARAN", "ASELS", "EREGL", "BIMAS", "AKBNK", "KCHOL", "SASA",
           "TUPRS", "FROTO", "ISCTR", "SISE"]


def num(x, d=2):
    s = f"{x:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def tl(x, signed=False):
    sign = "-" if x < 0 else ("+" if signed else "")
    return f"{sign}₺{num(abs(x))}"


def pc(x):
    return f"{'+' if x >= 0 else '-'}{num(abs(x))}%"


def cls(x):
    return "up" if x >= 0 else "dn"


def tick(p):
    """BIST fiyat adımı (kademe)."""
    for lim, t in ((20, 0.01), (50, 0.02), (100, 0.05), (250, 0.10),
                   (500, 0.25), (1000, 0.50), (2500, 1.0)):
        if p < lim:
            return t
    return 2.5


def next_price(p, up, limit, use_tick):
    if up:
        n = p * (1 + limit / 100)
        if use_tick:
            t = tick(n)
            n = math.floor(n / t + 1e-9) * t
    else:
        n = p * (1 - limit / 100)
        if use_tick:
            t = tick(n)
            n = math.ceil(n / t - 1e-9) * t
    return max(round(n, 2), 0.01)


def simulate(price, days, up, limit, use_tick):
    out, p = [price], price
    for _ in range(days):
        p = next_price(p, up, limit, use_tick)
        out.append(p)
    return out


def days_to_target(price, target_pct, up, limit, use_tick):
    goal = price * (1 + target_pct / 100) if up else price * (1 - target_pct / 100)
    p = price
    for d in range(1, 301):
        p = next_price(p, up, limit, use_tick)
        if (up and p >= goal) or (not up and p <= goal):
            return d, p
    return None, p


def tv_embed(widget, cfg, height):
    inner = (
        '<div class="tradingview-widget-container" style="height:100%;width:100%">'
        '<div class="tradingview-widget-container__widget" style="height:100%;width:100%"></div>'
        f'<script type="text/javascript" '
        f'src="https://s3.tradingview.com/external-embedding/embed-widget-{widget}.js" async>'
        f'{json.dumps(cfg)}</script></div>'
    )
    page = ('<html><body style="margin:0;background:transparent;height:100vh">'
            f'{inner}</body></html>')
    components.html(page, height=height)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_news(query: str):
    url = ("https://news.google.com/rss/search?q=" + quote(query + " when:2d")
           + "&hl=tr&gl=TR&ceid=TR:TR")
    try:
        r = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
        root = ET.fromstring(r.content)
    except Exception:
        return []
    out = []
    for it in list(root.iter("item"))[:30]:
        title = (it.findtext("title") or "").strip()
        src = (it.findtext("source") or "").strip()
        if src and title.endswith(" - " + src):
            title = title[: -len(src) - 3]
        out.append({"t": title, "l": it.findtext("link") or "#", "s": src or "Haber",
                    "d": it.findtext("pubDate") or ""})
    return out


def ago(date_str):
    try:
        dt = parsedate_to_datetime(date_str)
        mins = int((datetime.now(timezone.utc) - dt).total_seconds() // 60)
        if mins < 60:
            return f"{max(mins, 1)} dk önce"
        if mins < 1440:
            return f"{mins // 60} sa önce"
        return f"{mins // 1440} gün önce"
    except Exception:
        return ""


# ───────────────────────── DURUM & KAYIT ─────────────────────────
st.session_state.setdefault("pf", None)
st.session_state.setdefault("ver", 0)
st.session_state.setdefault("show_add", False)
st.session_state.setdefault("sel", None)


def bump():
    st.session_state.ver += 1


def load_items():
    if st.session_state["pf"] is not None:
        return
    if streamlit_js_eval is None:
        st.session_state["pf"] = []
        return
    raw = streamlit_js_eval(js_expressions="localStorage.getItem('ap_items') || '[]'",
                            key="ls_get")
    if not isinstance(raw, str):
        st.markdown('<div class="loading">PORTFÖYÜNÜZ YÜKLENİYOR…</div>', unsafe_allow_html=True)
        if st.button("Boş portföyle başla"):
            st.session_state["pf"] = []
            st.rerun()
        st.stop()
    try:
        data = json.loads(raw)
        assert isinstance(data, list)
    except Exception:
        data = []
    st.session_state["pf"] = data


def delete_item(iid):
    st.session_state["pf"] = [i for i in st.session_state["pf"] if i["id"] != iid]
    bump()


def set_price(iid):
    v = st.session_state.get(f"g_{iid}")
    if v and v > 0:
        for i in st.session_state["pf"]:
            if i["id"] == iid:
                i["guncel"] = float(v)
        bump()


def refresh_prices():
    try:
        import yfinance as yf
    except Exception:
        st.session_state["msg"] = "Fiyat servisi bulunamadı."
        return
    got = 0
    for t in sorted({i["t"] for i in st.session_state["pf"]}):
        try:
            h = yf.Ticker(t + ".IS").history(period="5d")
            p = float(h["Close"].dropna().iloc[-1])
        except Exception:
            continue
        if p > 0:
            got += 1
            for i in st.session_state["pf"]:
                if i["t"] == t:
                    i["guncel"] = round(p, 2)
                    st.session_state[f"g_{i['id']}"] = round(p, 2)
    st.session_state["msg"] = f"{got} hissenin fiyatı güncellendi." if got else \
        "Fiyat alınamadı, elle girebilirsiniz."
    bump()


def toggle_add():
    st.session_state.show_add = not st.session_state.show_add


def pick(t):
    st.session_state.sel = t


def clear_pick():
    st.session_state.sel = None


# ───────────────────────── BAŞLIK ─────────────────────────
st.markdown("""
<div class="brand"><svg viewBox="0 0 64 64" width="52" height="52" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="gd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6e3b4"/><stop offset="1" stop-color="#b98b3e"/></linearGradient></defs><rect x="3" y="3" width="58" height="58" rx="16" fill="#0d121c" stroke="url(#gd)" stroke-width="2.5"/><polyline points="14,44 26,32 34,38 50,19" fill="none" stroke="url(#gd)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle cx="50" cy="19" r="4.5" fill="#f6e3b4"/><path d="M14 51 H50" stroke="#3a4256" stroke-width="2" stroke-linecap="round"/></svg><div class="nm">Akıllı Portföy</div></div>
<div class="brand-sub">Yatırımınızı akıllıca yönetin</div>
""", unsafe_allow_html=True)

load_items()
items = st.session_state["pf"] if isinstance(st.session_state["pf"], list) else []

tab1, tab2, tab3, tab4 = st.tabs(["💼 Portföyüm", "🧮 Hesap Kurdu", "🔎 Hisseler", "📰 Piyasalar"])

# ───────────────────────── 1) PORTFÖYÜM ─────────────────────────
with tab1:
    # Özet
    cost = sum(i["alis"] * i["lot"] for i in items)
    value = sum(i["guncel"] * i["lot"] for i in items)
    kz = value - cost
    kzp = (kz / cost * 100) if cost else 0.0
    st.markdown(f"""
    <div class="glass sum">
      <div class="lbl">Toplam Portföy Değeri</div>
      <div class="big">{tl(value)}</div>
      <div class="pl {cls(kz)}">{'▲' if kz >= 0 else '▼'} {tl(kz, True)} &nbsp;({pc(kzp)})</div>
      <div class="row"><div><span>TOPLAM MALİYET</span><b>{tl(cost)}</b></div>
      <div><span>HİSSE SAYISI</span><b>{len(items)}</b></div></div>
    </div>""", unsafe_allow_html=True)

    st.button("✕ Kapat" if st.session_state.show_add else "＋ Hisse Ekle",
              type="primary", on_click=toggle_add, key="btn_add")

    if st.session_state.show_add:
        with st.form("add_form", clear_on_submit=True):
            f_t = st.text_input("Hisse adı", placeholder="örn: THYAO")
            c1, c2 = st.columns(2)
            f_a = c1.number_input("Alış fiyatı (₺)", min_value=0.0, value=None, step=0.01,
                                  format="%.2f", placeholder="0,00")
            f_l = c2.number_input("Alınan lot", min_value=1, value=None, step=1,
                                  placeholder="0")
            f_g = st.number_input("Güncel hisse fiyatı (₺)", min_value=0.0, value=None,
                                  step=0.01, format="%.2f", placeholder="0,00")
            ok = st.form_submit_button("Portföye Ekle", type="primary")
        if ok:
            tk = (f_t or "").strip().upper().replace(".IS", "").replace("BIST:", "")
            if not tk or not f_a or not f_l or not f_g:
                st.warning("Lütfen dört alanı da doldurun.")
            else:
                items.append({"id": uuid.uuid4().hex[:8], "t": tk, "alis": float(f_a),
                              "lot": int(f_l), "guncel": float(f_g)})
                st.session_state.show_add = False
                bump()
                st.rerun()

    if st.session_state.get("msg"):
        st.info(st.session_state.pop("msg"))

    if not items:
        st.markdown("""<div class="glass empty" style="margin-top:12px"><div class="ic">💎</div>
        <p>Portföyünüz henüz boş.<br>İlk hissenizi eklemek için yukarıdaki düğmeye dokunun.</p></div>""",
                    unsafe_allow_html=True)
    else:
        st.button("🔄 Güncel fiyatları otomatik çek", on_click=refresh_prices, key="btn_ref")
        for i in items:
            c = i["alis"] * i["lot"]
            v = i["guncel"] * i["lot"]
            k = v - c
            kp = (k / c * 100) if c else 0.0
            side = "g" if k > 0 else ("r" if k < 0 else "")
            st.markdown(f"""
            <div class="hold {side}">
              <div class="h-top">
                <div><div class="h-tk">{_h.escape(i['t'])}</div>
                <div class="h-sub">{i['lot']} lot · alış {tl(i['alis'])}</div></div>
                <div class="h-r"><div class="h-pl {cls(k)}">{tl(k, True)}</div>
                <div class="h-pct {cls(k)}">{'▲' if k >= 0 else '▼'} {pc(kp)}</div></div>
              </div>
              <div class="h-bot"><div>Maliyet<b>{tl(c)}</b></div>
              <div>Güncel fiyat<b>{tl(i['guncel'])}</b></div>
              <div>Güncel değer<b>{tl(v)}</b></div></div>
            </div>""", unsafe_allow_html=True)
            with st.expander(f"Düzenle · {i['t']}"):
                st.number_input("Güncel fiyat (₺)", min_value=0.01, value=float(i["guncel"]),
                                step=0.01, format="%.2f", key=f"g_{i['id']}",
                                on_change=set_price, args=(i["id"],))
                st.button("🗑 Hisseyi sil", key=f"del_{i['id']}", on_click=delete_item,
                          args=(i["id"],))

    with st.expander("💾 Yedekle / Geri yükle"):
        st.download_button("Yedeği indir (JSON)",
                           data=json.dumps(items, ensure_ascii=False, indent=1),
                           file_name="akilli_portfoy.json", mime="application/json")
        imp = st.text_area("Yedek içeriğini buraya yapıştırın", height=90, key="imp_txt")
        if st.button("İçe aktar", key="btn_imp"):
            try:
                data = json.loads(imp)
                assert isinstance(data, list)
                clean = [{"id": uuid.uuid4().hex[:8], "t": str(d["t"]).upper(),
                          "alis": float(d["alis"]), "lot": int(d["lot"]),
                          "guncel": float(d["guncel"])} for d in data]
                st.session_state["pf"] = clean
                bump()
                st.rerun()
            except Exception:
                st.error("Yedek okunamadı.")

# ───────────────────────── 2) HESAP KURDU ─────────────────────────
with tab2:
    st.markdown('<div class="sec">Tavan / Taban Hesaplayıcı</div>'
                '<div class="hint">Bir hisse art arda kaç gün tavan ya da taban olursa fiyatı '
                'ne olur, hesaplayın.</div>', unsafe_allow_html=True)
    price = st.number_input("Hissenin güncel fiyatı (₺)", min_value=0.0, value=None,
                            step=0.01, format="%.2f", placeholder="örn: 25,40", key="c_price")
    c1, c2 = st.columns(2)
    days = c1.number_input("Kaç gün?", min_value=1, max_value=60, value=3, step=1, key="c_days")
    limit = c2.number_input("Günlük limit (%)", min_value=1.0, max_value=30.0, value=10.0,
                            step=0.5, key="c_lim")
    direction = st.radio("Yön", ["🟢 Tavan", "🔴 Taban"], horizontal=True, key="c_dir")
    use_tick = st.checkbox("BIST fiyat adımına göre yuvarla (daha gerçekçi)", value=True,
                           key="c_tick")
    lot = st.number_input("Lot sayım (isteğe bağlı)", min_value=0, value=0, step=1, key="c_lot")
    up = direction.startswith("🟢")

    if not price:
        st.markdown('<div class="glass empty"><div class="ic">🧮</div>'
                    '<p>Hesaplamak için hisse fiyatını girin.</p></div>', unsafe_allow_html=True)
    else:
        path = simulate(price, int(days), up, limit, use_tick)
        end = path[-1]
        diff = end - price
        tot = (end / price - 1) * 100
        extra = ""
        if lot:
            extra = (f'<div class="hint" style="margin-top:10px">{int(lot)} lot için değer: '
                     f'<b>{tl(end * lot)}</b> · kâr/zarar: '
                     f'<b class="{cls(diff)}">{tl(diff * lot, True)}</b></div>')
        st.markdown(f"""
        <div class="glass res" style="margin-top:12px">
          <div class="hint">{int(days)} gün {'tavan' if up else 'taban'} sonrası fiyat</div>
          <div class="big {cls(diff)}">{tl(end)}</div>
          <div class="h-pl {cls(diff)}">{tl(diff, True)} · {pc(tot)}</div>
          <div class="hint">Başlangıç: {tl(price)}</div>{extra}
        </div>""", unsafe_allow_html=True)
        rows = "".join(
            f'<tr><td>{d}</td><td>{tl(path[d])}</td>'
            f'<td class="{cls(path[d] - path[d - 1])}">{pc((path[d] / path[d - 1] - 1) * 100)}</td>'
            f'<td class="{cls(path[d] - price)}">{pc((path[d] / price - 1) * 100)}</td></tr>'
            for d in range(1, len(path)))
        st.markdown('<div class="tbl"><table><thead><tr><th>Gün</th><th>Fiyat</th><th>Günlük</th>'
                    f'<th>Toplam</th></tr></thead><tbody>{rows}</tbody></table></div>',
                    unsafe_allow_html=True)

        st.markdown('<div class="sec">Hedefe kaç gün?</div>'
                    '<div class="hint">Aynı yönde (tavan/taban) hedef değişime kaç günde '
                    'ulaşılır?</div>', unsafe_allow_html=True)
        hedef = st.number_input("Hedef değişim (%)", min_value=1.0, max_value=5000.0,
                                value=50.0, step=5.0, key="c_target")
        if not up and hedef >= 100:
            st.warning("Taban için hedef %100'den küçük olmalı.")
        else:
            d, p_end = days_to_target(price, hedef, up, limit, use_tick)
            if d is None:
                st.warning("Bu hedefe 300 günde ulaşılamıyor.")
            else:
                st.markdown(f"""
                <div class="glass res"><div class="hint">%{num(hedef, 0)} hedefi için</div>
                <div class="big">{d} gün {'tavan' if up else 'taban'}</div>
                <div class="h-pl {cls(p_end - price)}">Fiyat: {tl(p_end)} ({pc((p_end / price - 1) * 100)})</div>
                </div>""", unsafe_allow_html=True)
    st.markdown('<div class="note">Bu hesaplayıcı, her gün limit fiyatından kapanış olduğunu varsayar. '
                'Fiyat adımı yaklaşık değerdir; gerçek limitler borsa kurallarına göre değişebilir.</div>',
                unsafe_allow_html=True)

# ───────────────────────── 3) HİSSELER ─────────────────────────
with tab3:
    sel = st.session_state.sel
    if sel:
        st.button("← Aramaya dön", on_click=clear_pick, key="btn_back")
        sym = f"BIST:{sel}"
        st.markdown(f'<div class="sel"><div class="tk">{_h.escape(sel)}</div>'
                    f'<div class="hint">Borsa İstanbul · TradingView verileri</div></div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="sec">Anlık bilgi</div>', unsafe_allow_html=True)
        tv_embed("symbol-info", {"symbol": sym, "width": "100%", "locale": "tr",
                                 "colorTheme": "dark", "isTransparent": True}, 190)
        st.markdown('<div class="sec">Gün içi hareket</div>', unsafe_allow_html=True)
        tv_embed("mini-symbol-overview", {"symbol": sym, "width": "100%", "height": 260,
                                          "locale": "tr", "dateRange": "1D",
                                          "colorTheme": "dark", "isTransparent": True,
                                          "autosize": False, "largeChartUrl": ""}, 270)
        st.markdown('<div class="sec">Fiyat grafiği</div>'
                    '<div class="hint">Grafikte 1 dk\'dan aylığa kadar zaman aralığı seçebilirsiniz.</div>',
                    unsafe_allow_html=True)
        tv_embed("advanced-chart", {"autosize": True, "symbol": sym, "interval": "D",
                                    "timezone": "Europe/Istanbul", "theme": "dark", "style": "1",
                                    "locale": "tr", "allow_symbol_change": False,
                                    "hide_side_toolbar": True, "save_image": False,
                                    "backgroundColor": "rgba(7,9,15,1)",
                                    "support_host": "https://www.tradingview.com"}, 480)
        st.markdown('<div class="sec">Temel bilgiler</div>', unsafe_allow_html=True)
        tv_embed("symbol-profile", {"width": "100%", "height": 400, "colorTheme": "dark",
                                    "isTransparent": True, "symbol": sym, "locale": "tr"}, 410)
        st.markdown('<div class="sec">Finansal veriler</div>', unsafe_allow_html=True)
        tv_embed("financials", {"isTransparent": True, "largeChartUrl": "",
                                "displayMode": "adaptive", "width": "100%", "height": 650,
                                "colorTheme": "dark", "symbol": sym, "locale": "tr"}, 660)
        st.markdown('<div class="sec">Teknik analiz</div>', unsafe_allow_html=True)
        tv_embed("technical-analysis", {"interval": "1D", "width": "100%", "height": 430,
                                        "isTransparent": True, "symbol": sym,
                                        "showIntervalTabs": True, "locale": "tr",
                                        "colorTheme": "dark"}, 440)
        st.markdown('<div class="note">Grafik ve temel veriler TradingView tarafından sağlanır; '
                    'BIST verileri gecikmeli olabilir.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sec">Hisse Ara</div>'
                    '<div class="hint">Borsa İstanbul\'daki hisse kodunu yazın, '
                    'üzerine dokunun.</div>', unsafe_allow_html=True)
        q = st.text_input("Hisse kodu", placeholder="örn: THYAO, GARAN, ASELS",
                          label_visibility="collapsed", key="q").strip().upper()
        if q:
            res = [t for t in TICKERS if q in t]
            res.sort(key=lambda t: (not t.startswith(q), t))
            title = f"{len(res)} sonuç" if res else "Listede bulunamadı"
        else:
            res, title = POPULAR, "Popüler hisseler"
        st.markdown(f'<div class="hint">{title}</div>', unsafe_allow_html=True)
        res = res[:36]
        for r in range(0, len(res), 3):
            cols = st.columns(3)
            for col, t in zip(cols, res[r:r + 3]):
                col.button(t, key=f"pick_{t}", on_click=pick, args=(t,))
        if q and q.isalnum() and q not in res and 3 <= len(q) <= 6:
            st.button(f"BIST:{q} sembolünü doğrudan aç", key="pick_direct",
                      on_click=pick, args=(q,), type="primary")

# ───────────────────────── 4) PİYASALAR ─────────────────────────
with tab4:
    tv_embed("ticker-tape", {"symbols": [
        {"proName": "BIST:XU100", "title": "BIST 100"},
        {"proName": "FX_IDC:USDTRY", "title": "USD/TRY"},
        {"proName": "FX_IDC:EURTRY", "title": "EUR/TRY"},
        {"proName": "OANDA:XAUUSD", "title": "Altın (ons)"},
        {"proName": "TVC:UKOIL", "title": "Brent"},
        {"proName": "BITSTAMP:BTCUSD", "title": "Bitcoin"}],
        "showSymbolLogo": False, "isTransparent": True, "displayMode": "adaptive",
        "colorTheme": "dark", "locale": "tr"}, 80)
    topic = st.radio("Konu", ["Borsa", "Ekonomi", "Döviz & Altın"], horizontal=True,
                     label_visibility="collapsed", key="news_topic")
    queries = {"Borsa": "Borsa İstanbul BIST 100",
               "Ekonomi": "Türkiye ekonomi piyasalar",
               "Döviz & Altın": "dolar euro altın fiyatı"}
    news = fetch_news(queries[topic])
    if not news:
        st.markdown('<div class="glass empty"><div class="ic">📡</div>'
                    '<p>Haberler şu an alınamadı.</p></div>', unsafe_allow_html=True)
        st.button("Tekrar dene", on_click=st.cache_data.clear, key="btn_news")
    else:
        st.markdown('<div class="sec">Güncel haberler</div>', unsafe_allow_html=True)
        for n in news:
            st.markdown(
                f'<a class="news" href="{_h.escape(n["l"])}" target="_blank" rel="noopener">'
                f'<div class="t">{_h.escape(n["t"])}</div>'
                f'<div class="m"><b>{_h.escape(n["s"])}</b> · {ago(n["d"])}</div></a>',
                unsafe_allow_html=True)

st.markdown('<div class="note">Akıllı Portföy bilgilendirme amaçlıdır; yatırım tavsiyesi '
            'değildir. Veriler gecikmeli olabilir.</div>', unsafe_allow_html=True)

# ───────────────────────── KALICI KAYIT ─────────────────────────
if streamlit_js_eval is not None and st.session_state.ver > 0:
    payload = json.dumps(json.dumps(st.session_state["pf"], ensure_ascii=False))
    streamlit_js_eval(js_expressions=f"localStorage.setItem('ap_items', {payload})",
                      key=f"ls_set_{st.session_state.ver}")
