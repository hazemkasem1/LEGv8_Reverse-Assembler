import streamlit as st
from legv8_disasm import decode

# ─── Page config & CSS ────────────────────────────────────────────────────────
st.set_page_config(page_title="LEGv8 Reverse-Assembler", layout="centered")
st.markdown(
    """
    <style>
    /* Page background */
    [data-testid="stAppViewContainer"] { background-color: #E0F7FA; }
    /* Headings & text */
    h1, h2, p, label, .stRadio label { color: #1E3A8A !important; }
    /* Textarea styling */
    .stTextArea>div>textarea {
      background-color: #222222 !important;
      color: #E0F7FA !important;
      border: 2px solid #1E3A8A !important;
      border-radius: 4px;
      font-family: monospace;
    }
    /* Decode button */
    .stButton>button {
      background-color: #1E3A8A !important;
      color: white !important;
      border-radius: 4px;
      font-weight: bold;
      margin-top: 0.5em;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ─── Header & instructions ────────────────────────────────────────────────────
st.title("LEGv8 Reverse-Assembler")
st.markdown("Choose input format, paste your code below, then click **Decode**.")

# ─── Input format radio ───────────────────────────────────────────────────────
fmt = st.radio(
    "Input format:",
    ("Hexadecimal", "Binary"),
    index=0,
    horizontal=True
)

# ─── Updated textarea label ──────────────────────────────────────────────────
paste_label = (
    "Paste one or more 8-digit HEX machine codes (e.g. D1002C27), separated by spaces or new lines:"
    if fmt == "Hexadecimal"
    else
    "Paste one or more 32-bit BINARY codes (e.g. 000100010000…), separated by spaces or new lines:"
)

# ─── Single textarea for codes ────────────────────────────────────────────────
codes_input = st.text_area(paste_label, height=180)

# ─── Decode button & results ─────────────────────────────────────────────────
if st.button("Decode"):
    if not codes_input.strip():
        st.warning("Please enter at least one machine code.")
    else:
        for token in codes_input.split():
            tok = token.strip()
            if fmt == "Binary":
                if not all(c in "01" for c in tok):
                    st.error(f"Invalid binary: {tok}")
                    continue
                tok = format(int(tok, 2), "08X")
            else:  # Hex
                tok = tok.removeprefix("0x").upper().zfill(8)
                try:
                    int(tok, 16)
                except ValueError:
                    st.error(f"Invalid hex: {token}")
                    continue

            try:
                asm = decode(tok)
                st.write(f"**{tok}** → {asm}")
            except Exception as e:
                st.error(f"Error decoding {tok}: {e}")
