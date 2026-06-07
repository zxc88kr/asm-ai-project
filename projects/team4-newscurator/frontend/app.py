import os

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


st.set_page_config(
    page_title="Team 04 AI Service",
    page_icon="AI",
    layout="centered",
)

st.title("Team 04 AI Service")
st.caption("제17기 부산센터 AI 기술 교육 프로젝트")

message = st.text_area("질문 또는 작업 요청", placeholder="AI 서비스에 요청할 내용을 입력하세요.")

if st.button("전송", type="primary", disabled=not message.strip()):
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": message},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        st.error(f"백엔드 요청에 실패했습니다: {exc}")
    else:
        st.subheader("응답")
        st.write(data["answer"])
        st.subheader("다음 작업")
        for item in data["next_steps"]:
            st.write(f"- {item}")

