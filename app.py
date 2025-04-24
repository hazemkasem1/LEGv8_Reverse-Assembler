st.markdown(
    """
    <style>
    /* 1) White page background */
    [data-testid="stAppViewContainer"] {
      background-color: #FFFFFF;
    }
    /* 2) Center & style the title */
    h1 {
      text-align: center !important;
      color: #1E3A8A !important;
    }
    /* 3) Royal-blue for all other text */
    h2, p, label, .stRadio label {
      color: #1E3A8A !important;
    }
    /* 4) Dark code box */
    .stTextArea>div>textarea {
      background-color: #222222 !important;
      color: #FFFFFF !important;
      border: 2px solid #1E3A8A !important;
      border-radius: 4px !important;
      font-family: monospace !important;
    }

    /* 5) Fancy Decode button */
    .stButton button {
      background: linear-gradient(135deg, #1E3A8A 0%, #3F51B5 100%) !important;
      color: #FFFFFF !important;
      border: none !important;
      border-radius: 8px !important;
      padding: 0.6rem 1.4rem !important;
      font-size: 1.1rem !important;
      font-weight: 600 !important;
      box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
      transition: all 0.2s ease-in-out !important;
    }
    .stButton button:hover {
      box-shadow: 0 6px 12px rgba(0,0,0,0.3) !important;
      transform: translateY(-2px) !important;
    }
    .stButton button:active {
      box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
      transform: translateY(0) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
