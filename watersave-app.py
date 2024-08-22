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
st.set_page_config(layout="wide")
st.title('워터세이브(WaterSave) 앱')

# 데이터베이스 파일 경로
DB_FILE = os.environ.get('DB_FILE', 'water_usage.db')

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

# 데이터베이스 초기화 함수
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # water_usage 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS water_usage
                 (timestamp TEXT, usage REAL)''')
    
    # user_info 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS user_info
                 (key TEXT PRIMARY KEY, value TEXT)''')
    
    # 초기 데이터 삽입 (테스트용)
    c.execute("INSERT OR IGNORE INTO user_info (key, value) VALUES (?, ?)", 
              ('daily_goal', '200'))
    c.execute("INSERT OR IGNORE INTO user_info (key, value) VALUES (?, ?)", 
              ('weekly_challenge', '설거지 물 사용량 20% 줄이기'))
    
    # 테스트용 water_usage 데이터 삽입
    current_time = datetime.now()
    for i in range(24 * 7):  # 일주일치 데이터
        timestamp = (current_time - timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S')
        usage = np.random.uniform(0.5, 3.0)
        c.execute("INSERT OR IGNORE INTO water_usage (timestamp, usage) VALUES (?, ?)", 
                  (timestamp, usage))
    
    conn.commit()
    conn.close()

# 앱 시작 시 데이터베이스 초기화
init_db()

# 데이터베이스 연결
conn = sqlite3.connect(DB_FILE)

# 1. 실시간 물 사용량 모니터링 (기존 코드 유지)
st.header('1. 실시간 물 사용량 모니터링')
# ... (기존 코드 유지)

# 2. AI 기반 개인 맞춤형 분석 및 추천 (Claude API 통합)
st.header('2. AI 기반 개인 맞춤형 분석 및 추천')
col1, col2 = st.columns(2)

with col1:
    st.subheader('개인 맞춤형 분석')
    query = """
    SELECT 
        AVG(CASE WHEN strftime('%w', timestamp) IN ('0', '6') THEN usage ELSE NULL END) as weekend_avg,
        AVG(CASE WHEN strftime('%w', timestamp) NOT IN ('0', '6') THEN usage ELSE NULL END) as weekday_avg
    FROM water_usage
    WHERE timestamp >= datetime('now', '-30 days')
    """
    try:
        usage_data = pd.read_sql_query(query, conn).iloc[0]
        st.write(f"- 주중 평균: {usage_data['weekday_avg']:.2f}L/시간")
        st.write(f"- 주말 평균: {usage_data['weekend_avg']:.2f}L/시간")
        st.write("- 샤워 사용량: 전체의 40% (추정)")
        st.write("- 세탁 사용량: 전체의 20% (추정)")
        
        prompt = f"""
        사용자의 물 사용 데이터:
        - 주중 평균: {usage_data['weekday_avg']:.2f}L/시간
        - 주말 평균: {usage_data['weekend_avg']:.2f}L/시간
        - 샤워 사용량: 전체의 40% (추정)
        - 세탁 사용량: 전체의 20% (추정)

        위 데이터를 바탕으로 사용자의 물 사용 패턴을 분석하고, 
        물 절약을 위한 3가지 맞춤형 조언을 제공해주세요.
        """
        analysis = call_claude_api(prompt)
        st.write("AI 분석 결과:", analysis)
    except Exception as e:
        st.error(f"데이터 분석 중 오류 발생: {str(e)}")

with col2:
    st.subheader('지능형 물 절약 어시스턴트')
    user_question = st.text_input("물 절약에 대해 질문해주세요:")
    if st.button("답변 받기"):
        prompt = f"""
        사용자 질문: {user_question}
        사용자의 최근 30일 평균 물 사용량: {(usage_data['weekday_avg'] + usage_data['weekend_avg']) / 2:.2f}L/일

        위 정보를 바탕으로 사용자에게 맞춤형 물 절약 조언을 제공해주세요.
        """
        response = call_claude_api(prompt)
        st.write("AI 답변:", response)

# 3. 게이미피케이션 요소 (맞춤형 절약 챌린지 추가)
st.header('3. 게이미피케이션 요소')
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader('일일 목표')
    # ... (기존 코드 유지)

with col2:
    st.subheader('주간 챌린지')
    # ... (기존 코드 유지)

with col3:
    st.subheader('맞춤형 절약 챌린지')
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

# 4. 커뮤니티 기능 (기존 코드 유지)
st.header('4. 커뮤니티 기능')
# ... (기존 코드 유지)

# 5. 환경 영향 시각화 (환경 영향 시뮬레이션 추가)
st.header('5. 환경 영향 시각화')
col1, col2 = st.columns(2)

with col1:
    st.subheader('CO2 감축량')
    # ... (기존 코드 유지)

with col2:
    st.subheader('환경 영향 시뮬레이션')
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

# 6. 스마트홈 연동 (지능형 문제 해결 추가)
st.header('6. 스마트홈 연동')
col1, col2 = st.columns(2)

with col1:
    st.subheader('IoT 기기 연동')
    # ... (기존 코드 유지)

with col2:
    st.subheader('지능형 문제 해결')
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
            st.success('누수가 감지되지 않았습니다.')
    st.write('마지막 검사: 2023-08-21 14:30')

# 7. 다국어 지원 및 문화적 맥락화
st.header('7. 다국어 지원 및 문화적 맥락화')
selected_language = st.selectbox("언어 선택", ["한국어", "English", "日本語", "中文"])
selected_region = st.selectbox("지역 선택", ["서울", "부산", "대구", "인천", "광주"])

prompt = f"""
{selected_region} 지역의 물 사용 문화와 규제에 대한 간략한 정보를 {selected_language}로 제공해주세요.
"""
response = call_claude_api(prompt)
st.write(response)

# 8. 지능형 보고서 생성
st.header('8. 지능형 보고서 생성')
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