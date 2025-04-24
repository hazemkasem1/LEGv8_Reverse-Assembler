import streamlit as st
from legv8_disasm import decode

# ─── Page config & CSS ────────────────────────────────────────────────────────
st.set_page_config(page_title="LEGv8 Reverse-Assembler", layout="centered")
st.markdown(
    """
    <style>
    /* 1) Page background */
    [data-testid="stAppViewContainer"] { background-color: #E0F7FA; }
    /* 2) Headings & text in royal-blue */
    h1, h2, p, label, .stRadio label { color: #1E3A8A !important; }
    /* 3) Textarea styling */
    .stTextArea>div>textarea {
      background-color: #222222 !important;
      color: #E0F7FA !important;
      border: 2px solid #1E3A8A !important;
      border-radius: 4px;
      font-family: monospace;
    }
    /* 4) Decode button */
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

# ─── Single textarea for codes ────────────────────────────────────────────────
label = (
    "…or paste full hex code here (32-bit words, separated by spaces or new lines):"
    if fmt == "Hexadecimal"
    else
    "…or paste full binary code here (32-bit words, separated by spaces or new lines):"
)
codes_input = st.text_area(label, height=180)

# ─── Decode button & results ─────────────────────────────────────────────────
if st.button("Decode"):
    if not codes_input.strip():
        st.warning("Please enter at least one machine code.")
    else:
        for token in codes_input.split():
            tok = token.strip()
            # Auto-detect / convert
            if fmt == "Binary":
                if not all(c in "01" for c in tok):
                    st.error(f"Invalid binary: {tok}")
                    continue
                tok = format(int(tok, 2), "08X")
            else:  # Hex
                tok = tok.removeprefix("0x").upper().zfill(8)
                # Validate
                try:
                    int(tok, 16)
                except ValueError:
                    st.error(f"Invalid hex: {token}")
                    continue

            # Decode & display
            try:
                asm = decode(tok)
                st.write(f"**{tok}** → {asm}")
            except Exception as e:
                st.error(f"Error decoding {tok}: {e}")
