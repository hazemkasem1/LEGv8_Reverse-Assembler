import streamlit as st
from legv8_disasm import decode

# ─── Page configuration & custom CSS ──────────────────────────────────────────
st.set_page_config(page_title="LEGv8 Reverse-Assembler", layout="centered")
st.markdown("""
<style>
/* 1) Page background */
[data-testid="stAppViewContainer"] {
  background-color: #E0F7FA;
}

/* 2) Global text color */
h1, h2, h3, h4, p, label, .stRadio > div > label {
  color: #1E3A8A !important;
}

/* 3) OTP-style input boxes */
.stTextInput>div>div>input {
  background-color: #BBDEFB !important;
  border: 2px solid #1E3A8A !important;
  color: #1E3A8A !important;
  font-weight: bold;
  text-align: center;
}

/* 4) Paste area */
.stTextArea>div>textarea {
  background-color: #E3F2FD !important;
  border: 2px solid #1E3A8A !important;
  color: #1E3A8A !important;
  font-family: monospace;
}

/* 5) Decode button */
.stButton>button {
  background-color: #1E3A8A !important;
  color: white !important;
  border-radius: 8px;
  font-weight: bold;
}

/* 6) Radio labels */
.stRadio>div>label>div[data-testid="stMarkdownContainer"] {
  color: #1E3A8A !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Header & description ────────────────────────────────────────────────────
st.title("LEGv8 Reverse-Assembler")
st.markdown("Choose input format, fill the boxes or paste your code, then click **Decode**.")

# ─── Input format selector ─────────────────────────────────────────────────────
fmt = st.radio("Input format:", ("Hexadecimal", "Binary"), index=0, horizontal=True)

# ─── OTP-style boxes + paste area ──────────────────────────────────────────────
st.markdown("#### Enter your code below")
if fmt == "Hexadecimal":
    cols = st.columns(8)
    hex_digits = []
    for i, col in enumerate(cols):
        d = col.text_input(str(i), max_chars=1, key=f"hex_{i}")
        hex_digits.append(d or "")
    box_val = "".join(hex_digits)
    raw = st.text_area("…or paste full hex code here:", box_val)
    code = raw.strip() or box_val

else:
    cols = st.columns(8)
    bit_groups = []
    for i, col in enumerate(cols):
        g = col.text_input(f"{i*4}-{i*4+3}", max_chars=4, key=f"bin_{i}")
        bit_groups.append(g or "")
    box_val = "".join(bit_groups)
    raw = st.text_area("…or paste full binary code here:", box_val)
    code = raw.strip() or box_val

# ─── Decode button & result ───────────────────────────────────────────────────
if st.button("Decode"):
    if not code:
        st.warning("Please enter or paste a code.")
    else:
        if fmt == "Binary":
            cleaned = code.replace(" ", "").replace("\n", "")
            try:
                code = format(int(cleaned, 2), "08X")
            except ValueError:
                st.error("Invalid binary string — must be up to 32 bits of 0s and 1s.")
                st.stop()
        try:
            result = decode(code)
            st.success(f"**{code.upper()}** → {result}")
        except Exception as e:
            st.error(f"Error decoding: {e}")
