import streamlit as st
from legv8_disasm import decode_inst  # or `decode` if you aliased it

# ─── Page config & CSS ────────────────────────────────────────────────────────
st.set_page_config(page_title="LEGv8 Reverse-Assembler", layout="centered")
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { background-color: #FFFFFF; }
    h1 { text-align: center !important; color: #1E3A8A !important; }
    h2, p, label, .stRadio label { color: #1E3A8A !important; }
    .stTextArea>div>textarea {
      background-color: #222222 !important;
      color: #FFFFFF !important;
      border: 2px solid #1E3A8A !important;
      border-radius: 4px !important;
      font-family: monospace !important;
    }
    /* Decode button: white background with dark blue text */
    div.stButton > button {
      background-color: #FFFFFF !important;
      color: #1E3A8A !important;
      font-weight: 600 !important;
      font-size: 16px !important;
      border: 2px solid #1E3A8A !important;
      border-radius: 8px !important;
      padding: 10px 24px !important;
      min-width: 140px !important;
      margin-top: 10px !important;
    }
    div.stButton > button:hover {
      background-color: #F3F4F6 !important;
      opacity: 0.95 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Header & instructions ────────────────────────────────────────────────────
st.title("LEGv8 Reverse-Assembler")
st.markdown("Choose input format, paste your code below, then click **Decode**.")

# ─── Input format selector ────────────────────────────────────────────────────
fmt = st.radio("Input format:", ("Hexadecimal", "Binary"), index=0, horizontal=True)

# ─── Textarea prompt based on format ──────────────────────────────────────────
paste_label = (
    "Paste one or more 8-digit HEX codes (e.g. D1002C27), separated by spaces or new lines:"
    if fmt == "Hexadecimal"
    else
    "Paste one or more 32-bit BINARY codes (e.g. 000100010000…), separated by spaces or new lines:"
)
codes_input = st.text_area(paste_label, height=180)

# ─── Decode button & warnings restored ────────────────────────────────────────
if st.button("Decode"):
    # 1) Empty‐input warning
    if not codes_input.strip():
        st.warning("Please enter at least one machine code.")
    else:
        # 2) Tokenize and decode each
        for token in codes_input.split():
            tok = token.strip()
            # a) Binary → hex
            if fmt == "Binary":
                if not all(c in "01" for c in tok):
                    st.warning(f"Invalid binary string: {tok}")
                    continue
                tok = format(int(tok, 2), "08X")
            # b) Normalize hex
            else:
                tok = tok.removeprefix("0x").upper().zfill(8)
                try:
                    int(tok, 16)
                except ValueError:
                    st.warning(f"Invalid hex code: {token}")
                    continue

            # 3) Decode and catch errors
            try:
                asm = decode_inst(tok)
                st.success(f"**{tok}** → {asm}")
            except Exception as e:
                st.error(f"Error decoding {tok}: {e}")
