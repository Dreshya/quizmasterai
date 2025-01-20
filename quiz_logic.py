import streamlit as st
import pandas as pd

def load_quiz_data(uploaded_file):
    st.session_state.data = pd.read_csv(uploaded_file)
    required_columns = {'Question ID', 'Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Correct Answer', 'Question Type'}
    if not required_columns.issubset(st.session_state.data.columns):
        st.error("The uploaded file doesn't match the required format. Please check the columns.")
    else:
        st.session_state.quiz_started = True
        st.session_state.current_question = 0
        st.session_state.answers = {}

def process_answer(current_index):
    question_row = st.session_state.data.iloc[current_index]

    # Display question in a styled container
    st.markdown(f"""
    <div style="border: 2px solid #4CAF50; padding: 20px; margin: 20px 0; border-radius: 10px; background-color: #f9f9f9;">
        <h3>Question {current_index + 1}/{len(st.session_state.data)}</h3>
        <p style="font-size: 18px;">{question_row['Question']}</p>
    </div>
    """, unsafe_allow_html=True)

    student_answer = None
    if question_row['Question Type'] == "Multiple Choice":
        options = {
            "A": question_row['Option A'],
            "B": question_row['Option B'],
            "C": question_row['Option C'],
            "D": question_row['Option D']
        }
        filtered_options = {k: v for k, v in options.items() if pd.notna(v) and v != ""}
        if filtered_options:
            student_answer = st.radio(
                "Select your answer:",
                options=list(filtered_options.keys()),
                format_func=lambda x: f"{x}: {filtered_options[x]}"
            )
    elif question_row['Question Type'] == "True/False":
        student_answer = st.radio("Select your answer:", options=["True", "False"])

    if st.button("Submit Answer"):
        st.session_state.answers[current_index] = student_answer
        correct_answer = str(question_row['Correct Answer']).strip()
        if student_answer == correct_answer:
            st.success("Correct! 🎉")
            st.session_state.correct_answers += 1
        else:
            st.error("Incorrect! ❌")
            st.session_state.wrong_answers += 1
        st.session_state.current_question += 1
        st.rerun()
