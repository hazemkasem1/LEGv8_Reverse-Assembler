import streamlit as st
from legv8_disasm import decode

st.title("LEGv8 Reverse-Assembler")
codes = st.text_area("Enter hex codes, separated by spaces or new lines:")
if st.button("Decode"):
    for hx in codes.split():
        st.write(f"**{hx.upper()}** → {decode(hx)}")
