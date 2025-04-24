import streamlit as st
from legv8_disasm import decode

# ─── Page config & minimal CSS ────────────────────────────────────────────────
st.set_page_config(page_title="LEGv8 Reverse-Assembler", layout="centered")
st.markdown(
    """
    <style>
    /* Background */
    [data-testid="stAppViewContainer"] { background-color: #E0F7FA; }
    /* Headings & text */
    h1, h2, p, label { color: #1E3A8A !important; }
    /* Decode button */
    .stButton>button {
      background-color: #1E3A8A !important;
      color: white !important;
      border-radius: 4px;
      font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Header & instructions ────────────────────────────────────────────────────
st.title("LEGv8 Reverse-Assembler")
st.markdown(
    "Insert one or more 32-bit machine codes below (hex or binary), separated by spaces or new lines, then click **Decode**."
)

# ─── Single textarea for all codes ────────────────────────────────────────────
codes_input = st.text_area(
    "Machine codes:",
    placeholder="e.g. D1002C27 FE000000 … or 110100010000… etc",
    height=150,
)

# ─── Decode button ────────────────────────────────────────────────────────────
if st.button("Decode"):
    if not codes_input.strip():
        st.warning("Please enter at least one machine code.")
    else:
        # Split on whitespace, handle each token
        for token in codes_input.split():
            tok = token.strip()
            # Detect binary vs hex
            if all(c in "01" for c in tok):
                # pad to 32-bit if needed
                try:
                    tok = format(int(tok, 2), "08X")
                except ValueError:
                    st.error(f"Invalid binary string: {token}")
                    continue
            else:
                tok = tok.removeprefix("0x").upper().zfill(8)
            # Decode and display
            try:
                asm = decode(tok)
                st.write(f"**{tok}** → {asm}")
            except Exception as e:
                st.error(f"Error decoding {tok}: {e}")
