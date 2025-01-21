import streamlit as st

taxonomy_levels = {
    "easy": ["Remembering", "Understanding"],
    "medium": ["Applying", "Analyzing"],
    "hard": ["Evaluating", "Creating"]
}

def get_difficulty_from_bt_level(bt_level):
    bt_level = bt_level.strip().capitalize()  # Clean and standardize BT Level
    for level, descriptions in taxonomy_levels.items():
        if bt_level in descriptions:
            return level
    return "easy"  # Default if not matched

def display_summary(total_questions):
    st.markdown("""
    <div>
        <h2 style="color: #4CAF50;">Summary</h2>
    </div>
    """, unsafe_allow_html=True)

    score = (st.session_state.correct_answers / total_questions) * 100
    st.title(f"{score:.2f}%")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Total Questions:** {total_questions}")
    with col2:
        st.write(f"**Total Correct Answers:** {st.session_state.correct_answers}")
    with col3:
        st.write(f"**Total Wrong Answers:** {st.session_state.wrong_answers}")

    taxonomy_level_analysis_normalized(total_questions)

def taxonomy_level_analysis_normalized(total_questions):
    # Initialize statistics for each Bloom's Taxonomy level
    bt_levels = {
        "Remembering": 0,
        "Understanding": 0,
        "Applying": 0,
        "Analyzing": 0,
        "Evaluating": 0,
        "Creating": 0
    }
    bt_totals = {level: 0 for level in bt_levels}

    # Iterate through each question and collect stats
    for question_id, student_answer in st.session_state.answers.items():
        question_row = st.session_state.data.iloc[question_id]
        bt_level = question_row.get("BT Level", "Remembering").strip().capitalize()
        correct_answer = str(question_row['Correct Answer']).strip()

        if bt_level in bt_levels:
            bt_totals[bt_level] += 1
            if student_answer == correct_answer:
                bt_levels[bt_level] += 1

    # Calculate total attempted questions across all levels
    total_attempted = sum(bt_totals.values())

    # Display percentages for levels with questions
    if total_attempted > 0:
        st.write("### Performance by Bloom's Taxonomy Levels:")
        st.caption("Shows the percentage of correct answers by its respective Bloom's Taxonomy Levels")
        for level, correct_count in bt_levels.items():
            total_count = bt_totals[level]
            if total_count > 0:  # Skip levels with no questions
                normalized_percentage = (correct_count / total_attempted) * 100
                st.write(f"**{level}:** {correct_count}/{total_count} ({normalized_percentage:.2f}%)")
                st.progress(normalized_percentage / 100)
    else:
        st.write("No questions were attempted.")




def review_answers():
    st.write("### Review Your Answers:")
    for question_id, student_answer in st.session_state.answers.items():
        question_row = st.session_state.data.iloc[question_id]
        question_text = question_row['Question']
        correct_answer = str(question_row['Correct Answer']).strip()

        bg_color = "#d4edda" if student_answer == correct_answer else "#f8d7da"

        st.markdown(f"""
        <div style="background-color: {bg_color}; padding: 15px; margin-bottom: 15px; border-radius: 8px;">
            <strong>{question_text}</strong><br><br>
            Your Answer: {student_answer}<br>
            Correct Answer: {correct_answer}
        </div>
        """, unsafe_allow_html=True)
