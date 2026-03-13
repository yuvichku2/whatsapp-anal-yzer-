import streamlit as st
import pandas as pd
import re
import plotly.express as px

st.set_page_config(page_title="מנתח הווטסאפ שלי", layout="wide")
st.title("📊 ניתוח הודעות ווטסאפ - גרסה מתוקנת")

def parse_whatsapp(file_contents):
    data = []
    # תבנית גמישה שמתאימה גם לאייפון וגם לאנדרואיד
    pattern = r'^\[?(\d{1,2}[./]\d{1,2}[./]\d{2,4}),?\s(\d{1,2}:\d{2}(?::\d{2})?)\]?\s(?:-\s)?([^:]+):\s(.*)'
    
    for line in file_contents.split('\n'):
        match = re.match(pattern, line)
        if match:
            date_str, time, author, message = match.groups()
            author = author.strip()
            data.append([date_str, author])
            
    df = pd.DataFrame(data, columns=['Date', 'Author'])
    # הפיכת התאריך לאובייקט זמן - מתמודד עם פורמטים שונים
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    return df

uploaded_file = st.file_uploader("תעלו את קובץ ה-txt של הצ'אט", type="txt")

if uploaded_file:
    stringio = uploaded_file.getvalue().decode("utf-8")
    df = parse_whatsapp(stringio)
    
    if not df.empty:
        st.sidebar.header("סינון נתונים")
        min_date = df['Date'].min().to_pydatetime()
        max_date = df['Date'].max().to_pydatetime()
        
        start_date, end_date = st.sidebar.slider(
            "בחר טווח תאריכים:",
            min_value=min_date, max_value=max_date, value=(min_date, max_date)
        )
        
        filtered_df = df[(df['Date'] >= pd.Timestamp(start_date)) & (df['Date'] <= pd.Timestamp(end_date))]
        author_counts = filtered_df['Author'].value_counts().reset_index()
        author_counts.columns = ['חבר קבוצה', 'כמות הודעות']
        
        fig = px.pie(author_counts, values='כמות הודעות', names='חבר קבוצה', 
                     title="מי החופר של הקבוצה?", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(author_counts)
    else:
        st.error("לא הצלחתי לקרוא נתונים מהקובץ. וודא שהעלית קובץ ייצוא תקין של ווטסאפ.")
else:
    st.info("ממתין להעלאת קובץ ה-txt...")