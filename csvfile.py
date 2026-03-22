def convert_dataframe_to_csv(df):
    if df.empty:
        return ""

    return df.to_csv(index=False).encode("utf-8")