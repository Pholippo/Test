import streamlit as st
from PIL import Image
import base64
import io
import re
from openai import OpenAI

from streamlit_lottie import st_lottie
import requests

# HIER MUSS ES STEHEN:
client = OpenAI(api_key="sk-...")   # <- Diese Zeile musst du so anpassen:
import os
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# --- HACKER-THEME: Dark Mode + Matrix Green + Monospace
st.set_page_config(page_title="Kreuzwort-KI", layout="wide", page_icon="💻")
st.markdown("""
<style>
/* Hackt das Design der Info-Box: */
.stAlert, .stAlert > div {

    color: #39FF14 !important;

}

}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #111 !important;
    color: #39FF14 !important;
    font-family: 'Fira Mono', 'Consolas', monospace !important;
}
h1, h2, h3, h4, h5, h6 {
    color: #39FF14 !important;
    letter-spacing: 2px;
    text-shadow: 0 0 8px #39ff1480, 0 0 20px #39ff1422;
}
.st-cm, .st-cd, .stCodeBlock, .stCode {
    background: #161616 !important;
    color: #39FF14 !important;
    border-radius: 8px;
    font-family: 'Fira Mono', 'Consolas', monospace !important;
    font-size: 1.1em;
    border: 1.5px solid #39FF1488;
    box-shadow: 0 0 8px #39ff1422;
}
.stButton>button {
    background: linear-gradient(90deg, #222 40%, #39FF14 200%) !important;
    color: #111 !important;
    border-radius: 14px;
    font-family: 'Fira Mono', 'Consolas', monospace !important;
    font-weight: bold;
    letter-spacing: 2px;
    border: 2px solid #39FF14;
    box-shadow: 0 0 18px #39ff1433;
    transition: all .2s;
}
.stButton>button:hover {
    background: #39FF14 !important;
    color: #000 !important;
    transform: scale(1.05) rotate(-1deg);
    border: 2.5px solid #fff;
    box-shadow: 0 0 24px #39ff14cc;
}
textarea, .stTextInput>div>div>input {
    background: #131 !important;
    color: #39FF14 !important;
    border-radius: 6px;
    border: 1.5px solid #39FF14 !important;
    font-family: 'Fira Mono', 'Consolas', monospace !important;
    font-size: 1em;
    box-shadow: 0 0 8px #39ff1422;
}
.stMarkdownContainer, .st-cm, .st-cd, .stCodeBlock, .stCode, .st-bb, .st-bs {
    animation: fadein 1.1s cubic-bezier(.57,2,.41,-0.33);
}
@keyframes fadein {
    from { opacity: 0; filter: blur(6px); transform: scale(.99) translateY(18px);}
    to { opacity: 1; filter: blur(0); transform: scale(1) translateY(0);}
}
/* Terminal Box Style */
.terminal-box {
    background: #161616;
    border: 2px solid #39FF14;
    border-radius: 11px;
    color: #39FF14;
    font-family: 'Fira Mono', monospace;
    font-size: 1.05em;
    padding: 18px 18px 12px 18px;
    margin-bottom: 16px;
    box-shadow: 0 0 16px #39ff1444;
    transition: box-shadow .2s;
}
.terminal-box:hover {
    box-shadow: 0 0 32px #39ff1499;
}
</style>
""", unsafe_allow_html=True)

# --- NEUE Überschrift ---
st.markdown('<h1>Kreuzwort-KI</h1>', unsafe_allow_html=True)
st.caption("Lade ein Kreuzworträtsel-Bild hoch und erhalte Lösungsvorschläge.")

# --- Lottie-Animation Matrix/Hacker Theme
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_hacker = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_QKRDTQ.json")  # Matrix Rain

uploaded_file = st.file_uploader("Bild hochladen", type=["jpg", "jpeg", "png"])

def bild_als_base64(image):
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def extrahiere_antworten(text):
    muster = re.compile(r"^\s*\d+\s*=\s*.+", re.MULTILINE)
    antworten = muster.findall(text)
    return "\n".join(antworten) if antworten else "(Keine kompakten Antworten gefunden)"

# Terminal-Antwort als grüne Matrix-Box
def terminal_message(text):
    st.markdown(f'<div class="terminal-box">{text}</div>', unsafe_allow_html=True)

def analyse_bild(base64_img):
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Was steht auf diesem Kreuzworträtselbild? Gib Fragen + Lösungen an. "
                            "Vergiss die Pfeile nicht. Gib Lösungen unbedingt nochmal im Format: 1 = Lösung, 2 = Lösung, ... "
                            "(ohne weiteren Text)."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
                    }
                ]
            }
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content

if "new_answer" not in st.session_state:
    st.session_state.new_answer = None
if "correction_sent" not in st.session_state:
    st.session_state.correction_sent = False

if uploaded_file:
    img = Image.open(uploaded_file)
    col1, col2, col3 = st.columns([2, 3, 3])

    with col1:
        st.image(img, caption="Dein Bild", use_container_width=True)

    with st.spinner("💾 KI-Terminal scannt Bild..."):
        base64_img = bild_als_base64(img)
        antwort = analyse_bild(base64_img)
    nur_antworten = extrahiere_antworten(antwort)

    with col2:
        st.subheader("Kompakte KI-Antworten")
        st.code(nur_antworten, language="")

    with col3:
        st.subheader("Terminal Output / Chat")
        terminal_message(antwort)

        if st.session_state.get("correction_sent"):
            st.markdown("#### Neue Antwort")
            terminal_message(st.session_state.new_answer)
            st.session_state.correction_sent = False

        st.markdown("---")
        st.markdown("#### Neue Frage / Korrektur")
        user_feedback = st.text_area("Terminaleingabe (z.B. Korrektur):")
        if st.button("Senden ›"):
            with st.spinner("› KI-Terminal sendet..."):
                response = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "Du bist ein Kreuzworträtsel-Experte."},
                        {"role": "user", "content": "Hier ist die ursprüngliche Analyse:\n" + antwort},
                        {"role": "user", "content": user_feedback}
                    ],
                    max_tokens=1000
                )
                st.session_state.new_answer = response.choices[0].message.content
                st.session_state.correction_sent = True
            st.rerun()
else:
    st.info("Lade eine Datei hoch!")

# Footer
st.markdown(
    '<div style="text-align:center; opacity:0.8; font-size:0.98em; color:#39FF14;">Erstellt von <b>Philipp</b> &lt;/&gt;</div>',
    unsafe_allow_html=True,
)
