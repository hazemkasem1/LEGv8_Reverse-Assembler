import streamlit as st
from streamlit.components.v1 import html
from legv8_disasm import decode

# ─── Page config & CSS ────────────────────────────────────────────────────────
st.set_page_config(page_title="LEGv8 Reverse-Assembler", layout="centered")
st.markdown(
    """
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
    """,
    unsafe_allow_html=True,
)

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
        for idx in range(8):
            st.session_state[f'hex_{idx}'] = c[idx] if idx < len(c) else ''
    else:
        b = ''.join(ch for ch in code if ch in '01')
        for idx in range(8):
            start, end = 4 * idx, 4 * (idx + 1)
            st.session_state[f'bin_{idx}'] = b[start:end]

# ─── Header & format selector ─────────────────────────────────────────────────
st.title("LEGv8 Reverse-Assembler")
st.markdown("Choose input format, fill the boxes or paste your code, then click **Decode**.")
fmt = st.radio("Input format:", ("Hexadecimal", "Binary"), key='fmt', horizontal=True)

# ─── Paste area with on_change ────────────────────────────────────────────────
paste_label = (
    "...or paste full hex code here:" if fmt == 'Hexadecimal'
    else "...or paste full binary code here:"
)
st.text_area(paste_label, key='paste', on_change=paste_callback, height=100)

# ─── OTP‐style boxes (MS‐group leftmost) ───────────────────────────────────────
st.markdown("#### Enter your code below")
cols = st.columns(8)
if fmt == 'Hexadecimal':
    for idx, col in enumerate(cols):
        col.text_input("", max_chars=1, key=f'hex_{idx}')
else:
    for idx, col in enumerate(cols):
        col.text_input("", max_chars=4, key=f'bin_{idx}')

# ─── Inject JS to auto‐advance focus ───────────────────────────────────────────
html(
    """
    <script>
    window.addEventListener('DOMContentLoaded', () => {
      const inputs = Array.from(document.querySelectorAll('.stTextInput input'));
      inputs.forEach((inp, idx) => {
        inp.addEventListener('input', () => {
          if (inp.value.length >= inp.maxLength) {
            const nxt = inputs[idx+1];
            if (nxt) nxt.focus();
          }
        });
      });
    });
    </script>
    """,
    height=0,
)

# ─── Build code from boxes ────────────────────────────────────────────────────
if fmt == 'Hexadecimal':
    code = "".join(st.session_state[f'hex_{i}'] for i in range(8))
else:
    code = "".join(st.session_state[f'bin_{i}'] for i in range(8))

# ─── Decode button & display ─────────────────────────────────────────────────
if st.button("Decode"):
    if not code:
        st.warning("Please enter or paste a code.")
    else:
        if fmt == 'Binary':
            try:
                code = format(int(code, 2), '08X')
            except ValueError:
                st.error("Invalid binary: must be up to 32 bits of 0s and 1s.")
                st.stop()
        try:
            result = decode(code)
            st.success(f"**{code}** → {result}")
        except Exception as e:
            st.error(f"Error decoding: {e}")
