import streamlit as st
from streamlit.components.v1 import html
from legv8_disasm import decode

# ─── Page config & CSS ────────────────────────────────────────────────────────
st.set_page_config(page_title="LEGv8 Reverse-Assembler", layout="centered")
st.markdown("""
<style>
/* Background */
[data-testid="stAppViewContainer"] { background-color: #E0F7FA; }
/* Global text */
h1, h2, h3, p, label, .stRadio label { color: #1E3A8A !important; }
/* OTP boxes */
.stTextInput>div>div>input {
  background-color: #BBDEFB !important;
  border: 2px solid #1E3A8A !important;
  color: #1E3A8A !important;
  font-weight: bold;
  text-align: center;
}
/* Paste area */
.stTextArea>div>textarea {
  background-color: #E3F2FD !important;
  border: 2px solid #1E3A8A !important;
  color: #1E3A8A !important;
  font-family: monospace;
}
/* Decode button */
.stButton>button {
  background-color: #1E3A8A !important;
  color: white !important;
  border-radius: 8px;
  font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ─── Session‐state defaults ───────────────────────────────────────────────────
if 'fmt' not in st.session_state:
    st.session_state['fmt'] = 'Hexadecimal'
if 'paste' not in st.session_state:
    st.session_state['paste'] = ''
for i in range(8):
    st.session_state.setdefault(f'hex_{i}', '')
    st.session_state.setdefault(f'bin_{i}', '')

# ─── Paste callback: auto‐fill the boxes ───────────────────────────────────────
def paste_callback():
    code = st.session_state['paste'].strip()
    fmt = st.session_state['fmt']
    if fmt == 'Hexadecimal':
        c = code.upper()
        for i in range(8):
            st.session_state[f'hex_{i}'] = c[i] if i < len(c) else ''
    else:
        b = ''.join(ch for ch in code if ch in '01')
        # b[0:4]="bits 31–28" → box 0, etc.
        for i in range(8):
            st.session_state[f'bin_{i}'] = b[4*i:4*(i+1)]

# ─── Header & format selector ─────────────────────────────────────────────────
st.title("LEGv8 Reverse-Assembler")
st.markdown("Choose input format, fill the boxes or paste your code, then click **Decode**.")
fmt = st.radio("Input format:", ("Hexadecimal","Binary"), key='fmt', horizontal=True)

# ─── Paste area with on_change → paste_callback ──────────────────────────────
paste_label = "...or paste full hex code here:" if fmt=='Hexadecimal' else "...or paste full binary code here:"
st.text_area(paste_label, key='paste', on_change=paste_callback, height=100)

# ─── OTP‐style boxes (MS‐group leftmost) ───────────────────────────────────────
st.markdown("
