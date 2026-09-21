import streamlit as st
import sys

## create input box for user to enter a prompt
st.title("Welcome to FormIA")
from pkg.watermarking.pkg.utils import new_generate_text
with st.container():
    input_text = st.chat_input("Ask me to generate some text...")
    print(f"User input: {input_text}")
    seed =  st.number_input("Seed", min_value=0, value=42, step=1)
    watermarking = st.checkbox("Enable watermarking", value=True)
    model = st.selectbox("Choose a model", ["qwen3.5"], index=0)
    if input_text:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": input_text}
        ]
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
        
            text, average_1_bias_score, t_statistic, p_value = new_generate_text(
                model, 
                messages, 
                watermarking=watermarking, 
                n_duels=8, 
                placeholder=message_placeholder, 
                seed=seed
            )
            ## say if the text is watermarked or not based on the p-value
            if p_value < 0.05:
                st.success("The text is likely watermarked (p-value < 0.05).")
            else:
                st.warning("The text is likely not watermarked (p-value >= 0.05).")
            ## display the statisitcs and p-value in a table
            with st.container():
                st.write("### Watermarking Statistics")
                st.write(f"Average 1 Bias Score: {sum(average_1_bias_score) / len(average_1_bias_score) if average_1_bias_score else 0}")
                st.write(f"T-statistic: {t_statistic}")
                st.write(f"P-value: {p_value}")
    

    