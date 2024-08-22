import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import os
import requests
import json

# 페이지 설정
st.set_page_config(layout="wide", page_title="WaterSave App")

# CSS 스타일 추가
st.markdown("""
<style>
    .main-title {
        font-size: 3em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2em;
    }
    .section-title {
        font-size: 2em;
        font-weight: bold;
        margin-top: 1em;
        margin-bottom: 0.5em;
    }
    .subsection-title {
        font-size: 1.5em;
        font-weight: bold;
        margin-top: 0.5em;
        margin-bottom: 0.5em;
    }
</style>
""", unsafe_allow_html=True)

# 메인 타이틀
st.markdown('<p class="main-title">워터세이브(WaterSave) 앱</p>', unsafe_allow_html=True)

# 데이터베이스 설정 및 초기화 (이전 코드와 동일)
DB_FILE = os.environ.get('DB_FILE', 'water_usage.db')

def init_db():
    # 데이터베이스 초기화 코드 (이전과 동일)
    pass

init_db()
conn = sqlite3.connect(DB_FILE)

# Claude API 호출 함수
def call_claude_api(prompt):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "API 키가 설정되지 않았습니다."
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    data = {
        "model": "claude-2.1",
        "prompt": prompt,
        "max_tokens_to_sample": 300
    }
    
    response = requests.post("https://api.anthropic.com/v1/complete", headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()['completion']
    else:
        return f"API 호출 오류: {response.status_code}"

# 1. 지능형 물 절약 어시스턴트
st.markdown('<p class="section-title">1. 지능형 물 절약 어시스턴트</p>', unsafe_allow_html=True)
user_question = st.text_input("물 절약에 대해 질문해주세요:")
if st.button("답변 받기"):
    # 사용자의 물 사용 데이터를 가져오는 쿼리
    query = """
    SELECT AVG(usage) as avg_usage
    FROM water_usage
    WHERE timestamp >= datetime('now', '-30 days')
    """
    avg_usage = pd.read_sql_query(query, conn).iloc[0]['avg_usage']
    
    prompt = f"""
    사용자 질문: {user_question}
    사용자의 최근 30일 평균 물 사용량: {avg_usage:.2f}L/일
    
    위 정보를 바탕으로 사용자에게 맞춤형 물 절약 조언을 제공해주세요.
    """
    response = call_claude_api(prompt)
    st.write(response)

# 2. 고급 데이터 분석 및 예측
st.markdown('<p class="section-title">2. 고급 데이터 분석 및 예측</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="subsection-title">물 사용량 예측</p>', unsafe_allow_html=True)
    # 간단한 선형 회귀를 사용한 예측 (실제로는 더 복잡한 모델을 사용해야 함)
    query = """
    SELECT date(timestamp) as date, SUM(usage) as daily_usage
    FROM water_usage
    WHERE timestamp >= datetime('now', '-30 days')
    GROUP BY date(timestamp)
    ORDER BY date(timestamp)
    """
    usage_data = pd.read_sql_query(query, conn)
    usage_data['date'] = pd.to_datetime(usage_data['date'])
    usage_data['day'] = range(len(usage_data))
    
    X = usage_data['day'].values.reshape(-1, 1)
    y = usage_data['daily_usage'].values
    
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(X, y)
    
    future_days = 7
    future_X = np.array(range(len(usage_data), len(usage_data) + future_days)).reshape(-1, 1)
    future_y = model.predict(future_X)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=usage_data['date'], y=usage_data['daily_usage'], mode='lines', name='실제 사용량'))
    fig.add_trace(go.Scatter(x=pd.date_range(start=usage_data['date'].iloc[-1] + pd.Timedelta(days=1), periods=future_days), 
                             y=future_y, mode='lines', name='예측 사용량'))
    fig.update_layout(title='물 사용량 예측', xaxis_title='날짜', yaxis_title='일일 사용량 (L)')
    st.plotly_chart(fig)

with col2:
    st.markdown('<p class="subsection-title">이상 징후 감지</p>', unsafe_allow_html=True)
    # 간단한 이상 징후 감지 (평균에서 2표준편차 이상 벗어난 경우)
    mean = usage_data['daily_usage'].mean()
    std = usage_data['daily_usage'].std()
    threshold = mean + 2 * std
    
    anomalies = usage_data[usage_data['daily_usage'] > threshold]
    
    if not anomalies.empty:
        st.write("다음 날짜에 이상적으로 높은 물 사용량이 감지되었습니다:")
        for _, row in anomalies.iterrows():
            st.write(f"- {row['date'].strftime('%Y-%m-%d')}: {row['daily_usage']:.2f}L")
        
        prompt = f"""
        사용자의 평균 물 사용량: {mean:.2f}L/일
        이상 징후가 감지된 날짜와 사용량: {', '.join([f"{row['date'].strftime('%Y-%m-%d')}: {row['daily_usage']:.2f}L" for _, row in anomalies.iterrows()])}
        
        위 정보를 바탕으로 이상 징후의 가능한 원인과 해결 방안을 제시해주세요.
        """
        response = call_claude_api(prompt)
        st.write("분석 결과:", response)
    else:
        st.write("최근 30일간 이상적인 물 사용량은 감지되지 않았습니다.")

# 3. 맞춤형 절약 챌린지 생성
st.markdown('<p class="section-title">3. 맞춤형 절약 챌린지</p>', unsafe_allow_html=True)
if st.button("새로운 챌린지 생성"):
    query = """
    SELECT AVG(usage) as avg_usage
    FROM water_usage
    WHERE timestamp >= datetime('now', '-7 days')
    """
    recent_avg = pd.read_sql_query(query, conn).iloc[0]['avg_usage']
    
    prompt = f"""
    사용자의 최근 7일 평균 물 사용량: {recent_avg:.2f}L/일
    
    위 정보를 바탕으로 사용자에게 맞춤형 물 절약 챌린지를 제안해주세요. 
    챌린지는 구체적이고 달성 가능해야 하며, 사용자의 현재 사용량을 고려해야 합니다.
    """
    response = call_claude_api(prompt)
    st.write("새로운 챌린지:", response)

# 4. 지능형 문제 해결 (누수 감지 부분만 구현)
st.markdown('<p class="section-title">4. 지능형 문제 해결</p>', unsafe_allow_html=True)
if st.button("누수 검사 실행"):
    # 실제로는 IoT 센서 데이터를 사용해야 함
    is_leakage = np.random.choice([True, False], p=[0.1, 0.9])
    
    if is_leakage:
        prompt = """
        누수가 감지되었습니다. 가능한 원인과 해결 방법을 제안해주세요.
        """
        response = call_claude_api(prompt)
        st.write("누수 감지 결과:", response)
    else:
        st.write("누수가 감지되지 않았습니다.")

# 5. 환경 영향 시뮬레이션
st.markdown('<p class="section-title">5. 환경 영향 시뮬레이션</p>', unsafe_allow_html=True)
query = """
SELECT SUM(usage) as total_usage
FROM water_usage
WHERE timestamp >= datetime('now', '-30 days')
"""
monthly_usage = pd.read_sql_query(query, conn).iloc[0]['total_usage']

prompt = f"""
사용자의 최근 30일 총 물 사용량: {monthly_usage:.2f}L

위 정보를 바탕으로 사용자의 물 사용이 지역 생태계에 미치는 영향과, 
만약 10% 물을 절약했을 때의 긍정적인 환경 영향을 시뮬레이션해주세요.
"""
response = call_claude_api(prompt)
st.write(response)

# 6. 다국어 지원 및 문화적 맥락화 (간단한 예시)
st.markdown('<p class="section-title">6. 지역별 물 사용 정보</p>', unsafe_allow_html=True)
selected_region = st.selectbox("지역 선택", ["서울", "부산", "대구", "인천", "광주"])

prompt = f"""
{selected_region} 지역의 물 사용 문화와 규제에 대한 간략한 정보를 제공해주세요.
"""
response = call_claude_api(prompt)
st.write(response)

# 7. 지능형 보고서 생성
st.markdown('<p class="section-title">7. 월간 물 사용 보고서</p>', unsafe_allow_html=True)
if st.button("월간 보고서 생성"):
    query = """
    SELECT date(timestamp) as date, SUM(usage) as daily_usage
    FROM water_usage
    WHERE timestamp >= datetime('now', '-30 days')
    GROUP BY date(timestamp)
    ORDER BY date(timestamp)
    """
    monthly_data = pd.read_sql_query(query, conn)
    total_usage = monthly_data['daily_usage'].sum()
    avg_usage = monthly_data['daily_usage'].mean()
    max_usage = monthly_data['daily_usage'].max()
    min_usage = monthly_data['daily_usage'].min()
    
    prompt = f"""
    최근 30일 물 사용 데이터:
    - 총 사용량: {total_usage:.2f}L
    - 일평균 사용량: {avg_usage:.2f}L
    - 최대 사용량: {max_usage:.2f}L
    - 최소 사용량: {min_usage:.2f}L

    위 정보를 바탕으로 사용자의 물 사용 패턴을 분석하고, 
    물 절약 노력과 성과를 강조하는 맞춤형 월간 보고서를 생성해주세요.
    """
    response = call_claude_api(prompt)
    st.write(response)

# 데이터베이스 연결 종료
conn.close()