import streamlit as st
from legv8_disasm import decode

# ─── Page config & minimal CSS ────────────────────────────────────────────────
st.set_page_config(page_title="LEGv8 Reverse-Assembler", layout="centered")
st.markdown(
    """
    <style>
    /* White background */
    [data-testid="stAppViewContainer"] {
      background-color: #FFFFFF;
    }
    /* Center & style the title */
    h1 {
      text-align: center !important;
      color: #1E3A8A !important;
    }
    /* Royal-blue for all other text */
    h2, p, label, .stRadio label {
      color: #1E3A8A !important;
    }
    /* Dark textarea */
    .stTextArea>div>textarea {
      background-color: #222222 !important;
      color: #FFFFFF !important;
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

# ─── Format selector ─────────────────────────────────────────────────────────
fmt = st.radio("Input format:", ("Hexadecimal", "Binary"), index=0, horizontal=True)

# ─── Textarea prompt ─────────────────────────────────────────────────────────
prompt = (
    "Paste one or more 8-digit HEX codes (e.g. D1002C27), separated by spaces or new lines:"
    if fmt == "Hexadecimal"
    else
    "Paste one or more 32-bit BINARY codes (e.g. 000100010000…), separated by spaces or new lines:"
)
codes_input = st.text_area(prompt, height=180)

# ─── Decode button & result ─────────────────────────────────────────────────
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
