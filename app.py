import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title('워터세이브(WaterSave) 앱')

# 1. 실시간 물 사용량 모니터링
st.header('실시간 물 사용량 모니터링')
data = pd.DataFrame(np.random.randn(20, 3), columns=['사용량', '평균', '목표'])
st.line_chart(data)

# 2. AI 기반 개인 맞춤형 분석 및 추천
st.header('AI 기반 개인 맞춤형 분석 및 추천')
st.write('당신의 물 사용량은 이웃 평균보다 10% 적습니다. 주방에서의 물 사용을 5% 더 줄이면 목표를 달성할 수 있습니다.')

# 3. 게이미피케이션 요소
st.header('물 절약 목표')
progress = st.progress(0)
progress.progress(65)
st.write('목표의 65%를 달성했습니다!')

# 4. 커뮤니티 기능
st.header('커뮤니티')
tip = st.text_input('물 절약 팁을 공유해주세요:')
if st.button('공유하기'):
    st.success('팁이 공유되었습니다. 감사합니다!')

# 5. 환경 영향 시각화
st.header('환경 영향')
col1, col2 = st.columns(2)
col1.metric('CO2 감축량', '50kg', '↑ 2kg')
col2.metric('절약한 물', '1000L', '↑ 100L')

# 6. 스마트홈 연동
st.header('스마트홈 연동')
if st.toggle('스마트 샤워기 절약 모드'):
    st.success('절약 모드가 활성화되었습니다.')