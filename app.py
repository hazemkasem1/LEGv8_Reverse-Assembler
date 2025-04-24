import streamlit as st
from legv8_disasm import decode

# ─── Page config & CSS ────────────────────────────────────────────────────────
st.set_page_config(page_title="LEGv8 Reverse-Assembler", layout="centered")
st.markdown(
    """
    <style>
    /* 1) White page background */
    [data-testid="stAppViewContainer"] { background-color: #FFFFFF; }

    /* 2) Center & style the title in royal-blue */
    h1 {
      text-align: center !important;
      color: #1E3A8A !important;
    }

    /* 3) Other text in royal-blue */
    h2, p, label, .stRadio label {
      color: #1E3A8A !important;
    }

    /* 4) Dark textarea styling */
    .stTextArea>div>textarea {
      background-color: #222222 !important;
      color: #FFFFFF !important;
      border: 2px solid #1E3A8A !important;
      border-radius: 4px !important;
      font-family: monospace !important;
    }

    /* 5) Decode button: blue background, white text */
    .stButton>button {
      background-color: #1E3A8A !important;
      color: #FFFFFF !important;
      border: none !important;
      border-radius: 4px !important;
      font-weight: bold !important;
      padding: 0.6rem 1.2rem !important;
      min-width: 100px !important;
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

# ─── Textarea label based on format ───────────────────────────────────────────
paste_label = (
    "Paste one or more 8-digit HEX machine codes (e.g. D1002C27), separated by spaces or new lines:"
    if fmt == "Hexadecimal"
    else
    "Paste one or more 32-bit BINARY codes (e.g. 000100010000…), separated by spaces or new lines:"
)

# ─── Single textarea for codes ────────────────────────────────────────────────
codes_input = st.text_area(paste_label, height=180)

# ─── Decode button & output ───────────────────────────────────────────────────
if st.button("Decode"):
    if not codes_input.strip():
        st.warning("Please enter at least one machine code.")
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
