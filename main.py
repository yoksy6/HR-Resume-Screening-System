import streamlit as st
from parser import extract_text_from_pdf, extract_text_from_docx
from skills import extract_skills
from scoring import calculate_resume_score
from contact import extract_email, extract_phone
from auth import signup_user, login_user
from database import create_users_table
from analytics import create_candidate_dataframe, calculate_score_statistics, get_top_candidates
from ml_model import train_shortlist_model, predict_candidate_status
from dashboard import create_score_distribution_chart, create_prediction_chart, create_top_skills_chart
from csvfile import convert_dataframe_to_csv
from chatbot import get_chatbot_response

def initialize_app():
    create_users_table()
    return train_shortlist_model()

def initialize_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = ""
    if "candidate_df" not in st.session_state:
        st.session_state.candidate_df = None

def logout_user():
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.rerun()

def show_home_banner():
    st.image("images/banner.jpg", use_container_width=True)

def login_page():
    st.title("Resume Screening System")
    st.subheader("Login Page")

    username = st.text_input("Enter Username", key="login_username")
    password = st.text_input("Enter Password", type="password", key="login_password")

    if st.button("Login"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.rerun()
        else:
            st.error("Invalid Username or Password")

def signup_page():
    st.title("Resume Screening System")
    st.subheader("Signup Page")

    username = st.text_input("Create Username", key="signup_username")
    password = st.text_input("Create Password", type="password", key="signup_password")

    if st.button("Signup"):
        success, message = signup_user(username, password)
        if success:
            st.success(message)
        else:
            st.error(message)

def extract_resume_text(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    if file_name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    return uploaded_file.read().decode("utf-8")

def create_candidate_record(uploaded_file, required_skills, model):
    resume_text = extract_resume_text(uploaded_file)

    email = extract_email(resume_text)
    phone = extract_phone(resume_text)
    skills = extract_skills(resume_text)
    score, matched = calculate_resume_score(skills, required_skills)
    prediction, probability = predict_candidate_status(model, skills, matched, score)

    return {
        "File Name": uploaded_file.name,
        "Email": email,
        "Phone": phone,
        "Skills Found": ", ".join(skills) if skills else "No skills found",
        "Resume Score": round(score, 2),
        "Matched Skills": ", ".join(matched) if matched else "No matched skills",
        "ML Prediction": prediction,
        "Prediction Confidence": round(probability * 100, 2)
    }

def process_uploaded_resumes(uploaded_files, required_skills, model):
    candidate_data = []

    for uploaded_file in uploaded_files:
        candidate_record = create_candidate_record(uploaded_file, required_skills, model)
        candidate_data.append(candidate_record)

    return candidate_data

def show_candidate_table(df):
    st.subheader("Candidate Results Table")
    st.dataframe(df, use_container_width=True)

def show_csv_download(df):
    csv_data = convert_dataframe_to_csv(df)

    if csv_data:
        st.download_button(
            label="Download Candidate Report (CSV)",
            data=csv_data,
            file_name="candidate_report.csv",
            mime="text/csv"
        )

def show_score_summary(df):
    stats = calculate_score_statistics(df)

    st.subheader("Score Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Average Score", round(stats["average_score"], 2))

    with col2:
        st.metric("Highest Score", round(stats["highest_score"], 2))

    with col3:
        st.metric("Lowest Score", round(stats["lowest_score"], 2))

    with col4:
        st.metric("Total Candidates", stats["total_candidates"])

def show_top_candidates(df):
    st.subheader("Top Candidates")
    top_df = get_top_candidates(df, top_n=3)
    st.dataframe(top_df, use_container_width=True)

def show_dashboard(df):
    st.subheader("Dashboard")

    score_chart = create_score_distribution_chart(df)
    if score_chart:
        st.pyplot(score_chart)

    prediction_chart = create_prediction_chart(df)
    if prediction_chart:
        st.pyplot(prediction_chart)

    skills_chart = create_top_skills_chart(df)
    if skills_chart:
        st.pyplot(skills_chart)

def display_results(candidate_data):
    df = create_candidate_dataframe(candidate_data)
    st.session_state.candidate_df = df

    show_candidate_table(df)
    show_csv_download(df)
    show_score_summary(df)
    show_top_candidates(df)
    show_dashboard(df)

def chatbot_page():
    st.title("AI Chatbot")
    st.subheader("Ask Questions About Candidates")

    if st.session_state.candidate_df is None or st.session_state.candidate_df.empty:
        st.warning("Please upload and process resumes first.")
        return

    user_query = st.text_input("Ask something about candidates")

    if st.button("Ask AI"):
        response = get_chatbot_response(st.session_state.candidate_df, user_query)
        st.success(response)

def main_app(model):
    st.title("Resume Screening System")
    st.header("AI Powered Resume Screening")

    show_home_banner()

    st.write(f"Welcome, {st.session_state.current_user}")

    st.sidebar.title("Navigation")

    option = st.sidebar.selectbox(
        "Select Option",
        ["Upload Resume", "Screen Candidates", "View Results", "AI Chatbot"]
    )

    if st.sidebar.button("Logout"):
        logout_user()

    if option == "AI Chatbot":
        chatbot_page()
        return

    job_skills_input = st.text_input(
        "Enter Required Skills",
        "Python, SQL, Machine Learning, NLP"
    )

    required_skills = [skill.strip() for skill in job_skills_input.split(",") if skill.strip()]

    uploaded_files = st.file_uploader(
        "Upload Resumes",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

    if uploaded_files:
        candidate_data = process_uploaded_resumes(uploaded_files, required_skills, model)
        display_results(candidate_data)
    else:
        st.info("Please upload one or more resumes.")

def run_app():
    st.set_page_config(page_title="Resume Screening System", layout="wide")

    model = initialize_app()
    initialize_session_state()

    if st.session_state.logged_in:
        main_app(model)
    else:
        menu = st.sidebar.radio("Select Page", ["Login", "Signup"])

        if menu == "Login":
            login_page()
        else:
            signup_page()