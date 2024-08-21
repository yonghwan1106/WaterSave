import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title('워터세이브(WaterSave) 앱')

# 1. 실시간 물 사용량 모니터링
st.header('1. 실시간 물 사용량 모니터링')
col1, col2 = st.columns(2)

with col1:
    # 시간대별 사용량
    hourly_data = pd.DataFrame({
        'hour': range(24),
        'usage': np.random.randint(10, 100, 24)
    })
    fig = go.Figure(data=go.Bar(x=hourly_data['hour'], y=hourly_data['usage']))
    fig.update_layout(title='시간대별 물 사용량', xaxis_title='시간', yaxis_title='사용량 (L)')
    st.plotly_chart(fig)

with col2:
    # 요일별 사용량
    daily_data = pd.DataFrame({
        'day': ['월', '화', '수', '목', '금', '토', '일'],
        'usage': np.random.randint(500, 1000, 7)
    })
    fig = go.Figure(data=go.Bar(x=daily_data['day'], y=daily_data['usage']))
    fig.update_layout(title='요일별 물 사용량', xaxis_title='요일', yaxis_title='사용량 (L)')
    st.plotly_chart(fig)

# 2. AI 기반 개인 맞춤형 분석 및 추천
st.header('2. AI 기반 개인 맞춤형 분석 및 추천')
col1, col2 = st.columns(2)

with col1:
    st.subheader('개인 맞춤형 분석')
    st.write('당신의 물 사용 패턴:')
    st.write('- 주중 평균: 200L/일')
    st.write('- 주말 평균: 250L/일')
    st.write('- 샤워 사용량: 전체의 40%')
    st.write('- 세탁 사용량: 전체의 20%')

with col2:
    st.subheader('AI 추천')
    st.write('1. 샤워 시간을 1분 줄이면 하루 10L 절약 가능')
    st.write('2. 세탁기 사용 시 절약 모드 활용으로 20% 절감 가능')
    st.write('3. 빗물 저장 시스템 설치로 월 100L 절약 가능')

# 3. 게이미피케이션 요소
st.header('3. 게이미피케이션 요소')
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader('일일 목표')
    daily_goal = st.slider('일일 물 절약 목표 설정', 0, 100, 50)
    st.progress(daily_goal)
    st.write(f'목표의 {daily_goal}%를 달성했습니다!')

with col2:
    st.subheader('주간 챌린지')
    st.write('이번 주 챌린지: 설거지 물 사용량 20% 줄이기')
    st.write('현재 순위: 지역 내 상위 10%')

with col3:
    st.subheader('절약량 시각화')
    saved_water = st.number_input('절약한 물의 양 (L)', value=1000)
    trees_saved = saved_water // 100
    st.write(f'당신의 노력으로 {trees_saved}그루의 나무를 살렸습니다! 🌳' * trees_saved)

# 4. 커뮤니티 기능
st.header('4. 커뮤니티 기능')
col1, col2 = st.columns(2)

with col1:
    st.subheader('물 절약 팁 공유')
    tip = st.text_area('물 절약 팁을 공유해주세요:')
    if st.button('공유하기'):
        st.success('팁이 공유되었습니다. 감사합니다!')

with col2:
    st.subheader('지역 물 절약 현황')
    regions = ['서울', '부산', '대구', '인천', '광주']
    savings = np.random.randint(1000, 10000, len(regions))
    fig = go.Figure(data=[go.Bar(x=regions, y=savings)])
    fig.update_layout(title='지역별 월간 물 절약량', xaxis_title='지역', yaxis_title='절약량 (L)')
    st.plotly_chart(fig)

# 5. 환경 영향 시각화
st.header('5. 환경 영향 시각화')
col1, col2 = st.columns(2)

with col1:
    st.subheader('CO2 감축량')
    co2_reduced = st.number_input('물 절약으로 인한 CO2 감축량 (kg)', value=50)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = co2_reduced,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "CO2 감축량 (kg)"}))
    st.plotly_chart(fig)

with col2:
    st.subheader('지역 수자원 영향')
    water_saved = st.number_input('절약한 물의 양 (L)', value=1000)
    st.write(f'당신의 노력으로 {water_saved}L의 물을 절약했습니다.')
    st.write(f'이는 {water_saved // 2}명의 하루 물 사용량과 같습니다.')

# 6. 스마트홈 연동
st.header('6. 스마트홈 연동')
col1, col2 = st.columns(2)

with col1:
    st.subheader('IoT 기기 연동')
    st.write('연결된 기기:')
    st.checkbox('스마트 샤워기', value=True)
    st.checkbox('스마트 세탁기', value=True)
    st.checkbox('스마트 식기세척기', value=False)

with col2:
    st.subheader('누수 감지 시스템')
    if st.button('누수 검사 실행'):
        st.success('누수가 감지되지 않았습니다.')
    st.write('마지막 검사: 2023-08-21 14:30')