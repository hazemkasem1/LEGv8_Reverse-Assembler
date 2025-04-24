import streamlit as st
from legv8_disasm import decode  # your decoder from before

# ─── Page & theme setup ───────────────────────────────────────────────────────
st.set_page_config(page_title="LEGv8 Reverse-Assembler", layout="centered")
st.markdown("""
<style>
/* background */
[data-testid="stAppViewContainer"] {
  background-color: #E0F7FA;
}
/* headers */
h1, h2, h3 { color: #1E88E5; }
/* inputs */
.stTextInput>div>div>input {
  border: 2px solid #42A5F5 !important;
  background-color: #E3F2FD !important;
}
/* decode button */
.stButton>button {
  background-color: #1E88E5 !important;
  color: white !important;
  border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

st.title("LEGv8 Reverse-Assembler")
st.markdown("A little front-end polish: choose your input format, fill boxes or paste, then Decode.")

# ─── Input format selector ─────────────────────────────────────────────────────
fmt = st.radio(
    "Input format:",
    ("Hexadecimal", "Binary"),
    index=0,
    horizontal=True
)

# ─── OTP-style boxes + paste area ──────────────────────────────────────────────
st.markdown("#### Enter your code below")
if fmt == "Hexadecimal":
    cols = st.columns(8)
    hex_digits = []
    for i, col in enumerate(cols):
        d = col.text_input(f"{i}", max_chars=1, key=f"hex_{i}")
        hex_digits.append(d or "")
    box_val = "".join(hex_digits)

    raw = st.text_area("…or paste full hex code here:", box_val)
    code = raw.strip() or box_val

else:  # Binary
    cols = st.columns(8)
    bit_groups = []
    for i, col in enumerate(cols):
        g = col.text_input(f"{i*4}-{i*4+3}", max_chars=4, key=f"bin_{i}")
        bit_groups.append(g or "")
    box_val = "".join(bit_groups)

    raw = st.text_area("…or paste full binary code here:", box_val)
    code = raw.strip() or box_val

# ─── Decode button & logic ─────────────────────────────────────────────────────
if st.button("Decode"):
    if not code:
        st.warning("Please enter a code in the boxes or paste it above.")
    else:
        # If binary, convert to hex first
        if fmt == "Binary":
            cleaned = code.replace(" ", "")
            try:
                code = format(int(cleaned, 2), "08X")
            except ValueError:
                st.error("Invalid binary string—must be 32 bits of 0s and 1s.")
                st.stop()

        # Now run the decoder
        try:
            result = decode(code)
            st.success(f"**{code.upper()}** → {result}")
        except Exception as e:
            st.error(f"Error decoding: {e}")
