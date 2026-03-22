def get_chatbot_response(df, user_query):
    if df.empty:
        return "No candidate data is available."

    query = user_query.lower().strip()

    if "highest score" in query or "top candidate" in query:
        top_candidate = df.sort_values(by="Resume Score", ascending=False).iloc[0]
        return (
            f"Top candidate is {top_candidate['File Name']} with score "
            f"{top_candidate['Resume Score']}%."
        )

    if "average score" in query:
        avg_score = round(df["Resume Score"].mean(), 2)
        return f"Average resume score is {avg_score}%."

    if "shortlisted" in query:
        shortlisted_df = df[df["ML Prediction"] == "Shortlisted"]
        if shortlisted_df.empty:
            return "No shortlisted candidates found."
        names = shortlisted_df["File Name"].tolist()
        return "Shortlisted candidates are: " + ", ".join(names)

    if "not shortlisted" in query:
        rejected_df = df[df["ML Prediction"] == "Not Shortlisted"]
        if rejected_df.empty:
            return "No not shortlisted candidates found."
        names = rejected_df["File Name"].tolist()
        return "Not shortlisted candidates are: " + ", ".join(names)

    if "python" in query:
        matched_df = df[df["Skills Found"].str.contains("Python", case=False, na=False)]
        if matched_df.empty:
            return "No candidates found with Python skill."
        names = matched_df["File Name"].tolist()
        return "Candidates with Python skill are: " + ", ".join(names)

    if "sql" in query:
        matched_df = df[df["Skills Found"].str.contains("SQL", case=False, na=False)]
        if matched_df.empty:
            return "No candidates found with SQL skill."
        names = matched_df["File Name"].tolist()
        return "Candidates with SQL skill are: " + ", ".join(names)

    if "machine learning" in query:
        matched_df = df[df["Skills Found"].str.contains("Machine Learning", case=False, na=False)]
        if matched_df.empty:
            return "No candidates found with Machine Learning skill."
        names = matched_df["File Name"].tolist()
        return "Candidates with Machine Learning skill are: " + ", ".join(names)

    if "nlp" in query:
        matched_df = df[df["Skills Found"].str.contains("NLP", case=False, na=False)]
        if matched_df.empty:
            return "No candidates found with NLP skill."
        names = matched_df["File Name"].tolist()
        return "Candidates with NLP skill are: " + ", ".join(names)