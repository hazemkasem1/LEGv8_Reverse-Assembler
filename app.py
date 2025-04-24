import streamlit as st
from legv8_disasm import decode

# ─── Page config & CSS ────────────────────────────────────────────────────────
st.set_page_config(page_title="LEGv8 Reverse-Assembler", layout="centered")
st.markdown(
    """
    <style>
    /* Baby-blue background */
    [data-testid="stAppViewContainer"] { background-color: #E0F7FA; }

    /* Center & color the title */
    h1 { text-align: center !important; color: #1E3A8A !important; }

    /* Other text in royal-blue */
    h2, p, label, .stRadio label { color: #1E3A8A !important; }

    /* Dark code box */
    .stTextArea>div>textarea {
      background-color: #222222 !important;
      color: #E0F7FA !important;
      border: 2px solid #1E3A8A !important;
      border-radius: 4px !important;
      font-family: monospace !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Header & instructions ────────────────────────────────────────────────────
st.title("LEGv8 Reverse-Assembler")
st.markdown("Choose input format, paste your code below, then click **Decode**.")

# ─── Format selector & textarea ───────────────────────────────────────────────
fmt = st.radio("Input format:", ("Hexadecimal", "Binary"), index=0, horizontal=True)

paste_label = (
    "Paste one or more 8-digit HEX codes (e.g. D1002C27), separated by spaces/new lines:"
    if fmt == "Hexadecimal"
    else
    "Paste one or more 32-bit BINARY codes (e.g. 000100010000…), separated by spaces/new lines:"
)
codes_input = st.text_area(paste_label, height=180)

# ─── Decode button & output ───────────────────────────────────────────────────
if st.button("Decode"):  
    if not codes_input.strip():
        st.warning("Please enter at least one code.")
    else:
        for token in codes_input.split():
            tok = token.strip()
            # Convert binary → hex if needed
            if fmt == "Binary":
                if not all(c in "01" for c in tok):
                    st.error(f"Invalid binary: {tok}")
                    continue
                tok = format(int(tok, 2), "08X")
            else:  # Hex mode
                tok = tok.removeprefix("0x").upper().zfill(8)
                try:
                    int(tok, 16)
                except ValueError:
                    st.error(f"Invalid hex: {token}")
                    continue

            # Decode and display
            try:
                asm = decode(tok)
                st.write(f"**{tok}** → {asm}")
            except Exception as e:
                st.error(f"Error decoding {tok}: {e}")
