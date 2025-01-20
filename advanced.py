import os
import re
from PyPDF2 import PdfReader
import streamlit as st
import ollama
import pandas as pd
import matplotlib.pyplot as plt


#def draw_pyramid():

#    st.header("Bloom's Taxonomy Pyramid")
#    st.write("This pyramid represents the six levels of Bloom's Taxonomy, from lower-order thinking skills at the base to higher-order skills at the top.")

    # Bloom's Taxonomy levels
#    levels = [
#        "Remembering",
#        "Understanding",
#        "Applying",
#        "Analyzing",
#        "Evaluating",
#        "Creating"
#    ]
#    colors = ["#FF6F61", "#FFB400", "#F7EA00", "#94D82D", "#4CAF50", "#2196F3"]

    # Figure and axis
#    fig, ax = plt.subplots(figsize=(4, 6))  # Smaller and more compact
#    ax.axis("off")

    # Draw pyramid
#    base_width = 10
#    height = len(levels)
#    for i, (level, color) in enumerate(zip(levels, colors)):
#        # Calculate dimensions
#        width = base_width * (1 - i / height)
#        left = (base_width - width) / 2
#        bottom = i

        # Draw rectangle
#        ax.add_patch(plt.Rectangle((left, bottom), width, 1, color=color, ec="white", lw=1))
        
        # Add text
#        ax.text(left + width / 2, bottom + 0.5, level, ha="center", va="center", 
#                fontsize=6, color="white", fontweight="bold")

#    ax.set_xlim(0, base_width)
#    ax.set_ylim(0, height)
#    ax.set_aspect("equal")
    
#    return fig '''


st.markdown(
    """
    <style>
    /* Style the number input box */
    .stNumberInput input {
        width: 80px; /* Set a small width for the number input box */
        font-size: 16px; /* Optional: Adjust font size */
    }
    </style>
    """,
    unsafe_allow_html=True
)



# Custom CSS for 
st.markdown(
    """
    <style>
    /* Style for the Difficulty slider label */
    .difficulty-slider-label {
        font-size: 18px; /* Size for the 'Set Difficulty' text */
        font-weight: bold; /* Make it bold */
        text-align: left; /* Align the label to the left */
        margin-bottom: 10px; /* Add spacing below the label */
    }
    
    /* Style for the Number of Questions label */
    .questions-slider-label {
        font-size: 18px; /* Same size as 'Set Difficulty' */
        font-weight: bold; /* Make it bold */
        margin-bottom: 0px; /* Add different margin-bottom for Number of Questions */
    }

    .stSlider > div {
        width: 200px; /* Set a fixed width for the slider (same size as number input) */
        margin: 0; /* Align the slider to the left */
    }
    .stSlider label {
        font-size: 18px; /* Size for the options: easy, medium, hard */
        font-weight: bold; /* Make the options bold */
    }
    
    /* Style the number input wrapper and input box to match slider size */
    .stNumberInput {
        width: 200px; /* Set a fixed width for the number input box */
    }
    .stNumberInput input {
        width: 100%; /* Fill the wrapper width */
        font-size: 16px; /* Optional: Adjust font size */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Function to read content from a structured text file
def read_context(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {e}"
# Prompt for the model
PROMPT = (
    "You are an AI tasked with reorganizing and structuring the following text while preserving every detail, technical term, and nuance of the original. "
    "Ensure that the output retains all original information and presents it in a more organized and readable way. "
    "Do not skip or summarize any content; instead, reformat for clarity. Use detailed headings, subheadings, and lists, "
    "and where appropriate, retain long text blocks with the original technical terms, examples, and contextual elements. "
    "Focus on maintaining the integrity and completeness of the information while improving its presentation."
)







def preprocess_generated_text(text):
    """
    Preprocess the generated text to:
    - Remove unwanted characters, emojis, and specific patterns.
    - Eliminate empty lines (including between sections).
    - Remove phrases like 'True or False', 'True False', 'True/False' before or after each question in the $$Questions$$ section.
    - Preserve 'True or False' or 'True False' in the $$Correct Answers$$ section.
    """
    # Split text into $$Questions$$ and $$Correct Answers$$ sections
    sections = re.split(r'(\$\$Correct Answers\$\$)', text, flags=re.IGNORECASE)
    
    # If both sections exist, process them separately
    if len(sections) > 1:
        questions_section = sections[0]
        correct_answers_section = sections[1] + (sections[2] if len(sections) > 2 else "")
    else:
        questions_section = text
        correct_answers_section = ""

    # Clean the $$Questions$$ section
    questions_section = re.sub(r'[#*-]', '', questions_section)  # Remove '#' and '*'
    questions_section = questions_section.replace('✅', '')  # Remove '✅'

    # Remove occurrences of 'True or False', 'True False', and 'True/False' at the beginning or end of questions
    questions_section = re.sub(r'^\s*(True\s?(or\s?)?\s?False[\s:]*\s*)', '', questions_section, flags=re.IGNORECASE)  # Before question
    questions_section = re.sub(r'\s*(True\s?(or\s?)?\s?False[\s:]*\s*)\s*$', '', questions_section, flags=re.IGNORECASE)  # After question
    
    # Remove other unwanted characters and empty lines
    questions_section = '\n'.join([line.strip() for line in questions_section.splitlines() if line.strip()])  # Remove empty lines

    # Clean the $$Correct Answers$$ section (only remove unwanted characters, not True/False)
    correct_answers_section = re.sub(r'[#*]', '', correct_answers_section)
    correct_answers_section = correct_answers_section.replace('✅', '')
    correct_answers_section = '\n'.join([line.strip() for line in correct_answers_section.splitlines() if line.strip()])  # Remove empty lines

    # Combine cleaned sections back together
    cleaned_text = questions_section
    if correct_answers_section:
        cleaned_text += '\n' + correct_answers_section

    return cleaned_text









# Function to extract text from uploaded PDFs
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PdfReader(pdf_file)
        text = "".join(page.extract_text() for page in pdf_reader.pages)
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

# Function to save text to a file
def save_text_to_file(text, filename):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(text)
        return filename
    except Exception as e:
        st.error(f"Error saving text to file: {e}")
        return None

# Function to process text with the AI model
def process_text_with_model(input_file):
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            input_text = file.read()

        # Create full prompt
        messages = [{"role": "system", "content": input_text}]

        # Stream response from the AI model
        stream = ollama.chat(
           model="gemma2:2b",  # Adjust model if necessary
            #model="phi3:mini",
            #model="phi3:medium",
            messages=messages,
            stream=True
        )

        # Collect response chunks progressively
        response_chunks = []
        for chunk in stream:
            response_chunks.append(chunk["message"]["content"])

        # Combine all chunks into a single response
        response = "".join(response_chunks)

        # Clean response by removing unnecessary tags
        cleaned_response = re.sub(r"<\|.*?\|>", "", response)
        return cleaned_response
    except Exception as e:
        st.error(f"Error processing text with the model: {e}")
        return None

# Streamlit App
st.title("QuizMasterAI")


# Session states for buttons
if "training_complete" not in st.session_state:
    st.session_state.training_complete = False
if "page" not in st.session_state:
    st.session_state.page = "home"

    


def parse_questions_flexible(txt_content):
    """
    Parse questions and their correct answers from text content with options
    in formats like (A) or A for multiple choice and various formats for True/False.
    """
   

    questions = []
    correct_answers = {}
    current_question = None
    in_answer_section = False
    in_true_false_section = False
    in_mcq_section = False

    # Split text into lines
    lines = txt_content.split('\n')

    for line in lines:
        line = line.strip()

        # Detect the start of the answer section
        if "$$Correct Answers$$" in line:
            in_answer_section = True
            continue

        # Parse correct answers for multiple-choice or True/False questions
        if in_answer_section:
            # For True/False
            answer_match = re.match(r'(\d+)[\:\)\.\s]*\s*(True|False|T|F)', line, re.IGNORECASE)
            if answer_match:
                question_id, answer = answer_match.groups()
                correct_answers[question_id] = answer.strip().capitalize()
            # For Multiple Choice
            else:
                answer_match = re.match(r'(\d+)[\:\)\.\s]*\s*([A-Da-d])', line)
                if answer_match:
                    question_id, answer = answer_match.groups()
                    correct_answers[question_id] = answer.upper()
            continue

        # Detect the section for True/False or Multiple Choice
        if "$$True/False Questions$$" in line:
            in_true_false_section = True
            in_mcq_section = False
            continue
        if "$$MCQ Questions$$" in line:
            in_true_false_section = False
            in_mcq_section = True
            continue

        
        # Match questions with their numbers
        question_match = re.match(r'^(?P<question_id>\d+)[\.\)\s]*\s*(?:\((?P<question_bt>[^\)]+)\))?\s*(?P<question_text>.*?)$', line)

        if question_match:
            # Save the previous question before starting a new one
            if current_question:
                questions.append(current_question)

            question_id = question_match.group('question_id')
            question_text = question_match.group('question_text').strip()
            question_bt = question_match.group('question_bt')

            print(question_bt)

            # Assign question type based on the section
            if in_true_false_section:
                question_type = 'True/False'
            else:
                question_type = 'Multiple Choice'

            current_question = {
                'Question ID': question_id,
                'Question': question_text,
                'Type': question_type,  # Assign the correct type dynamically
                'BT level': question_bt,
                'Options': {},
                'Correct Answer': ''
            }
            continue

        # Match options for True/False questions
        true_false_match = re.match(r'^(True|False|T|F)\s*(.+)$', line, re.IGNORECASE)
        if true_false_match:
            answer_option, option_text = true_false_match.groups()

            if current_question and answer_option.lower() in ['true', 'false', 't', 'f']:
                current_question['Options'] = {
                    'T': 'True',
                    'F': 'False'
                }
                current_question['Type'] = 'True/False'
            continue

        # Match options in either (A) Option or A. Option formats for MCQs
        option_match = re.match(r'^(?:\(([A-Da-d])\)|([A-Da-d])[\.\)])\s*(.+)$', line)
        if option_match and current_question:
            option_letter = option_match.group(1) or option_match.group(2)
            option_text = option_match.group(3)
            current_question['Options'][option_letter.upper()] = option_text.strip()

    # Add the last question
    if current_question:
        questions.append(current_question)

    # Map correct answers to the questions
    for question in questions:
        question_id_str = str(question['Question ID'])
        correct_answer = correct_answers.get(question_id_str, '')
        question['Correct Answer'] = correct_answer

    return questions




def convert_questions(file_path, output_dir):
    """
    Convert questions from text file to CSV, include options (A, B, C, D),
    and ensure question type appears only once for each type.
    """
    

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_csv = os.path.join(output_dir, f"{base_name}_generated_questions.csv")

    try:
        with open(file_path, "r", encoding='utf-8') as file:
            txt_content = file.read()

        questions = parse_questions_flexible(txt_content)

        if questions:
            # Prepare data for CSV
            processed_data = []
            type_tracker = set()  # To track which types have already been added

            for question in questions:
                
                options = question['Options']
                processed_data.append({
                    'Question ID': question['Question ID'],
                    'Question': question['Question'],
                    'Option A': options.get('A', ''),
                    'Option B': options.get('B', ''),
                    'Option C': options.get('C', ''),
                    'Option D': options.get('D', ''),
                    'Correct Answer': question['Correct Answer'],
                    'Question Type': question['Type'],
                    'BT Level': question['BT level']
                })

            # Convert processed data to DataFrame
            df = pd.DataFrame(processed_data)

            # Save to CSV
            df.to_csv(output_csv, index=False)
            print(f"Processed questions saved to {output_csv}")
            print(f"Total questions processed: {len(questions)}")
        else:
            print("No questions to process.")

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")









        
# Upload PDF and Train Model
if st.session_state.page == "home":
    st.write("Upload a PDF file to train the AI for Quiz generation.")
    uploaded_pdf = st.file_uploader("Upload a PDF", type="pdf", label_visibility="visible")

    if uploaded_pdf:
        # Ensure directories exist
        base_dir = "upload"
        folders = ["file", "unstructured", "feed", "structured", "question", "generated_questions"]
        for folder in folders:
            os.makedirs(os.path.join(base_dir, folder), exist_ok=True)

        # Save the uploaded PDF file
        file_path = os.path.join(base_dir, "file", uploaded_pdf.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_pdf.getbuffer())

        if not st.session_state.training_complete:
            if st.button("Train the AI Model"):
                # Extract text from the PDF
                with st.spinner("Processing PDF..."):
                    extracted_text = extract_text_from_pdf(file_path)

                    if extracted_text:
                        # Save unstructured text
                        unstructured_path = os.path.join(base_dir, "unstructured", f"{os.path.splitext(uploaded_pdf.name)[0]}.txt")
                        save_text_to_file(extracted_text, unstructured_path)

                        # Create feed.txt
                        feed_content = f"{PROMPT}\n\n{extracted_text}"
                        feed_path = os.path.join(base_dir, "feed", f"{os.path.splitext(uploaded_pdf.name)[0]}.txt")
                        save_text_to_file(feed_content, feed_path)

                        # Process text with the AI model
                        structured_text = process_text_with_model(feed_path)

                        if structured_text:
                            # Save the structured response
                            structured_path = os.path.join(base_dir, "structured", f"{os.path.splitext(uploaded_pdf.name)[0]}.txt")
                            save_text_to_file(structured_text, structured_path)
                            st.session_state.training_complete = True
                            st.success("AI has been successfully trained. You can now generate questions.")
                        else:
                            st.error("The model failed to process the text.")
                    else:
                        st.warning("No text could be extracted from the PDF.")

    # Enable "Go to Question Generation" button after training
    if st.session_state.training_complete:
        if st.button("Go to Question Generation"):
            st.session_state.page = "questions"  # Set the page to "questions"
            st.rerun()  # Re-run to refresh the page view





# Question Generation
elif st.session_state.page == "questions":
    st.title("Generate Questions")
    
    # Selecting the structured text file
    structured_dir = "upload/structured"
    structured_files = [f for f in os.listdir(structured_dir) if f.endswith(".txt")]
    selected_file = st.selectbox("Select a structured text file", structured_files)

    if selected_file:
        # Read the selected structured text file
        file_path = os.path.join(structured_dir, selected_file)
        context = read_context(file_path)

        # User input for question generation
        st.write("### Customize Your Question Preferences")

        # Question generation inputs
        # Initialize session state for options
        if "ins_option" not in st.session_state:
            st.session_state.ins_option = 0

        col1, col2 = st.columns(2)

        # Specify option chosen
        with col1:
            if st.button("Standard", use_container_width=True):
                st.session_state.ins_option = 1

        with col2:
            if st.button("Advanced", use_container_width=True):
                st.session_state.ins_option = 2

        # Display slider with custom styles
        if st.session_state.ins_option == 1:
            st.markdown('<div class="difficulty-slider-label">Set Difficulty</div>', unsafe_allow_html=True)
            difficulty = st.select_slider(
                "",
                options=["easy", "medium", "hard"],
                value="medium",
                label_visibility="collapsed"
            )
        # Display textbox for customization
        elif st.session_state.ins_option == 2:
            
            #fig = draw_pyramid()
            #st.pyplot(fig)

            from PIL import Image

            # Load the image
            image = Image.open('bt level.png') 

            # Display the image
            st.image(image, caption='Blooms Taxonomy Levels')

            custom_bt_level = st.text_area(
                "Customize the Bloom's Taxonomy levels you want included. You may combine different levels.",
                placeholder="Enter Bloom's Taxonomy instructions here ..."
            )
            
            custom_comments = st.text_area(
                "Specify any additional comments for the questions.",
                placeholder="Enter additional comments here ..."
            )

        st.markdown('<div class="questions-slider-label">Number of Questions</div>', unsafe_allow_html=True)
        ques_no = st.number_input("", min_value=1, max_value=20, value=5)
        
        
        
        question_type = st.radio("Select question type", ["True/False", "Multiple-Choice"])

        # Combine input choices and the structured text into a new file
        if st.button("Generate Questions"):
            if context:
                # Generate the prompt
                if st.session_state.ins_option == 1:
                    
                    taxonomy_levels = {
                        "easy": "Remembering and Understanding",
                        "medium": "Applying and Analyzing",
                        "hard": "Evaluating and Creating"
                    }
                    prompt = (
                        f"Generate {ques_no} {question_type} questions "
                        f"at the  {taxonomy_levels[difficulty]} level of Bloom's Taxonomy. "
                        f"It should focus on {taxonomy_levels[difficulty].lower()} concepts relevant to the text. "
                        "Specify the Bloom's taxanomy level applied for every question. \n\n"
                    )

                elif st.session_state.ins_option == 2:

                    taxonomy_levels = custom_bt_level
                    prompt = (
                        f"Generate {ques_no} {question_type} questions based on the Bloom's Taxonomy levels specified in the instructions. "
                        f"Strictly focus on the specified instructions on which Bloom's Taxonomy levels to apply that is relevant to the text to generate the questions. "
                        "Specify the Bloom's taxonomy level applied for every question. \n\n"
                        f"The customized instructions : \n{taxonomy_levels} \n\n"
                        "IMPORTANT : Must apply the Bloom's Taxonomy levels to its corresponding questions as per the instructions. "
                        "STRICTLY DO NOT apply Bloom's Taxonomy levels that are not mentioned, ONLY apply the level specified for each question. "
                        "Example, question 1 : level 4 means apply level 4 : Analyzing on ONLY question 1. "
                        "If instruction says question 3 - 5 : level 1 and level 2, it means apply level 1 : remembering and "
                        "level 2 : understanding ONLY on question 3, question 4 and question 5. \n\n"
                    )

                    if custom_comments:
                        prompt += (
                            "Strictly take note of these comments when generating the questions.\n"
                            f"Additional Comments:\n{custom_comments}\n\n"
                        )
                    
                    prompt += (
                        "Description of Bloom's Taxonomy levels from the lower-order thinking skills to higher-order thinking skills :\n"
                        "Level 1 : Remembering\nLevel 2 : Understanding\nLevel 3 : Applying\nLevel 4 : Analyzing\nLevel 5 : Evaluating\nLevel 6 : Creating\n"
                        "Refer to the description above when instructions contain specific Bloom's Taxonomy Level numbers for specific questions.\n"
                        "For example, question 2 : level 4 means level 4 : analyzing must be applied to question 2 only\n\n"
                        "Ensure the questions follow these instructions exactly:\n"
                        "- Specify the Bloom's Taxonomy level for each question in parentheses.\n"
                        "- Match all instructions and comments given above.\n\n"
                    )

                # Add specific instructions based on question type
                if question_type == "Multiple-Choice":
                    prompt += "For multiple-choice questions, provide four options (A, B, C, and D), and ensure only one answer is correct, randomized across options. Title the header as $$MCQ Questions$$"
                elif question_type == "True/False":
                    prompt +=  (
                        "For true/false statement, strictly ONLY provide statement that can be answered with True or False. Title the header as $$True/False Questions$$ "
                        "Do NOT include 'according to text' if no related text is provided in the question itself. "
                        "Do NOT include 'True or False?' in the beginning or end of the statement. "
                        "Randomize between True and False as the correct answer.\n"
                        "IMPORTANT: Do NOT provide explanations or other options. Only include the statement text without the answer at the end.\n"
                        "In the $$Correct Answers$$ section, strictly list ONLY 'True' or 'False' as the answer for each statement.\n"
                )

                prompt += (
                    "Do NOT reveal the correct answers yet\n\n"
                   
                    "For specifying Bloom's taxanomy level, follow these instructions : \n"
                    "IMPORTANT : MUST specify Bloom's taxanomy level for each question. ")
                
                if st.session_state.ins_option == 1:
                    prompt += (f"Choose one or both from these Bloom's taxanomy levels : {taxonomy_levels[difficulty].lower()}, to replace inside the parentheses. ")
                elif st.session_state.ins_option == 2:
                    prompt += ("Identify the respective Bloom's Taxonomy levels for each question and replace inside the parentheses. "
                               "The Bloom's Taxonomy levels labelled for each question MUST be exactly how it is specified in the instructions. ")

                prompt += (
                    "Do NOT mention 'Bloom's taxanomy level' inside the parentheses, ONLY specify Bloom's taxanomy level name such as (Analyzing) or (Understanding). "
                    "Do NOT mention the level numbering such as (Level 1) or (Level 3) inside the parentheses, only mention the level's names such as (Analyzing) or (Understanding). "
                    "The parentheses MUST be placed after the question numbering and before question starts.\n\n"

                    "After generating, include a separate section titled '$$Correct Answers$$'. "
                    #"In this section, list only the numbers and their corresponding correct answers.\n\n"
                    "{Strictly follow this format :{ "
                    "$$Questions$$ "
                    "1. (Question1 Bloom's taxanomy level) Question1 ..... , 2. (Question2 Bloom's taxanomy level) Question2 ..... "
                    "$$Correct Answers$$ then new line " 
                    "1. must be one of =  A,B,C or D for MCQ  or True or false for True False statement ,  ,2.  ,3.  , ......\n"
                    "Do NOT output anything else.}"
                    f" Based on the following context ----> "
                )

                # Combine the prompt and structured text
                combined_content = prompt + context

                # Save the combined content to a new file
                generated_config_file = os.path.join("upload/question", f"{selected_file.replace('.txt', '')}_config.txt")
                save_text_to_file(combined_content, generated_config_file)

                st.success(f"Structured content saved successfully as {generated_config_file}!")

                

                # Process the file with the AI model and generate questions
                generated_text = process_text_with_model(generated_config_file)

                if generated_text:
                    # Preprocess the generated text
                    preprocessed_text = preprocess_generated_text(generated_text)

                    # Save the generated questions to the generated_questions folder
                    generated_questions_file = os.path.join("upload/generated_questions", f"{selected_file.replace('.txt', '')}_generated_questions.txt")
                    save_text_to_file(preprocessed_text, generated_questions_file)

                    st.success(f"Generated questions saved successfully as {generated_questions_file}!")

                    output_dir = "upload/csv"
                    convert_questions(generated_questions_file, output_dir)
                    st.success(f"Generated csv saved successfully as {output_dir}!")

                   
            else:
                st.warning("Please select a valid structured text file first.")
