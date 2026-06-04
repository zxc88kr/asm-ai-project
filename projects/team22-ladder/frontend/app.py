import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Ladder", layout="centered")
st.title("Ladder")

if st.button("서버 상태 확인"):
    try:
        res = requests.get(f"{API_URL}/health", timeout=3)
        if res.ok:
            st.success("서버 연결 성공!")
        else:
            st.error(f"오류: {res.status_code}")
    except Exception as e:
        st.error(f"연결 실패: {e}")
