import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import asyncio
import json
from deep_translator import GoogleTranslator


# 페이지 설정
st.set_page_config(layout="wide")
st.title('워터세이브(WaterSave) 앱')

# API 키 입력
api_key = st.sidebar.text_input("Claude API 키를 입력하세요:", type="password")
if api_key:
    client = Anthropic(api_key=api_key)
else:
    st.sidebar.warning("API 키를 입력해주세요.")
    client = None

# 데이터베이스 파일 경로
DB_FILE = os.environ.get('DB_FILE', 'water_usage.db')

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

# Claude API를 사용한 지능형 어시스턴트 함수
def claude_assistant(prompt):
    if not client:
        return "API 키를 입력해주세요."
    
    try:
        response = client.completions.create(
            model="claude-2",
            max_tokens_to_sample=150,
            prompt=f"{HUMAN_PROMPT} {prompt}{AI_PROMPT}",
        )
        return response.completion
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"

# 메인 대시보드
def main_dashboard():
    st.header('실시간 물 사용량 모니터링')
    col1, col2 = st.columns(2)

    with col1:
        # 시간대별 사용량
        query = """
        SELECT strftime('%H', timestamp) as hour, AVG(usage) as avg_usage
        FROM water_usage
        WHERE timestamp >= datetime('now', '-1 day')
        GROUP BY hour
        ORDER BY hour
        """
        hourly_data = pd.read_sql_query(query, conn)
        fig = go.Figure(data=go.Bar(x=hourly_data['hour'], y=hourly_data['avg_usage']))
        fig.update_layout(title='시간대별 평균 물 사용량 (최근 24시간)', xaxis_title='시간', yaxis_title='사용량 (L)')
        st.plotly_chart(fig)

    with col2:
        # 요일별 사용량
        query = """
        SELECT strftime('%w', timestamp) as day, AVG(usage) as avg_usage
        FROM water_usage
        WHERE timestamp >= datetime('now', '-7 days')
        GROUP BY day
        ORDER BY day
        """
        daily_data = pd.read_sql_query(query, conn)
        days = ['일', '월', '화', '수', '목', '금', '토']
        daily_data['day'] = daily_data['day'].apply(lambda x: days[int(x)])
        fig = go.Figure(data=go.Bar(x=daily_data['day'], y=daily_data['avg_usage']))
        fig.update_layout(title='요일별 평균 물 사용량 (최근 7일)', xaxis_title='요일', yaxis_title='사용량 (L)')
        st.plotly_chart(fig)

# 지능형 물 절약 어시스턴트
def intelligent_assistant():
    st.header('지능형 물 절약 어시스턴트')
    user_question = st.text_input("물 절약에 대해 질문해 주세요:")
    if user_question:
        # 사용자의 물 사용 데이터를 가져옴
        query = """
        SELECT AVG(usage) as avg_usage
        FROM water_usage
        WHERE timestamp >= datetime('now', '-30 days')
        """
        avg_usage = pd.read_sql_query(query, conn).iloc[0]['avg_usage']
        
        prompt = f"사용자의 평균 물 사용량은 {avg_usage:.2f}L/시간입니다. 다음 질문에 답해주세요: {user_question}"
        response = claude_assistant(prompt)
        st.write(response)

# 고급 데이터 분석 및 예측
def advanced_analysis():
    st.header('고급 데이터 분석 및 예측')
    
    # 미래 물 사용량 예측
    future_usage = np.random.uniform(150, 250)
    st.write(f"다음 달 예상 물 사용량: {future_usage:.2f}L")
    
    # 이상 징후 감지
    anomaly = np.random.choice([True, False], p=[0.2, 0.8])
    if anomaly:
        st.warning("지난 주 대비 물 사용량이 30% 증가했습니다. 누수 가능성을 확인해보세요.")

# 맞춤형 절약 챌린지
def personalized_challenge():
    st.header('맞춤형 절약 챌린지')
    challenge = "이번 주는 세탁기 사용을 10% 줄이는 챌린지에 도전해보세요!"
    st.write(challenge)
    if st.button('챌린지 수락'):
        st.success('챌린지가 시작되었습니다. 행운을 빕니다!')

# 지능형 문제 해결
def intelligent_problem_solving():
    st.header('지능형 문제 해결')
    problem = st.selectbox('문제를 선택하세요:', ['누수 감지', '수도 요금 증가'])
    if problem == '누수 감지':
        st.write("가능한 원인: 파이프 균열, 수도꼭지 마모")
        st.write("해결 방법: 전문 배관공 상담, 수도꼭지 교체")
    elif problem == '수도 요금 증가':
        st.write("가능한 원인: 숨겨진 누수, 사용량 증가")
        st.write("대처 방안: 누수 점검, 물 절약 습관 개선")

# 환경 영향 시뮬레이션
def environmental_impact():
    st.header('환경 영향 시뮬레이션')
    saved_water = st.number_input('절약한 물의 양 (L)', value=1000)
    trees_saved = saved_water // 100
    st.write(f'당신의 노력으로 {trees_saved}그루의 나무를 살렸습니다! 🌳' * min(trees_saved, 10))
    
    # 장기 효과 예측
    years = st.slider('몇 년 후의 효과를 보고 싶으신가요?', 1, 10, 5)
    long_term_effect = saved_water * 12 * years
    st.write(f"{years}년 후에는 총 {long_term_effect:,}L의 물을 절약할 수 있습니다!")

# 5. 환경 영향 시각화
def environmental_visual():
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

# 다국어 지원 및 문화적 맥락화
def multilingual_support():
    st.header('다국어 지원 및 문화적 맥락화')
    languages = {'한국어': 'ko', '영어': 'en', '일본어': 'ja', '중국어': 'zh-CN'}
    selected_lang = st.selectbox('언어를 선택하세요:', list(languages.keys()))
    
    tip = "물을 절약하는 가장 좋은 방법은 짧은 샤워를 하는 것입니다."
    translator = GoogleTranslator(source='ko', target=languages[selected_lang])
    translated_tip = translator.translate(tip)
    st.write(translated_tip)

# 지능형 보고서 생성
def generate_report():
    st.header('지능형 보고서 생성')
    report_type = st.radio('보고서 유형', ['월간', '연간'])
    if st.button('보고서 생성'):
        st.write(f"{report_type} 물 사용 분석 보고서")
        st.write("1. 총 사용량: 5,000L")
        st.write("2. 절약량: 500L (전월 대비 10% 감소)")
        st.write("3. 가장 많이 사용한 요일: 토요일")
        st.write("4. 추천 절약 방법: 빗물 저장 시스템 설치")

# AI 기반 개인 맞춤형 분석 및 추천
def ai_analysis_and_recommendation():
    st.header('AI 기반 개인 맞춤형 분석 및 추천')
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
        except Exception as e:
            st.error(f"데이터 분석 중 오류 발생: {str(e)}")

    with col2:
        st.subheader('AI 추천')
        try:
            weekday_high = usage_data['weekday_avg'] > usage_data['weekend_avg']
            st.write(f"1. {'주중' if weekday_high else '주말'}에 물 사용량이 더 많습니다. {'업무 중 ' if weekday_high else '여가 활동 중 '}물 절약에 신경 써주세요.")
            st.write("2. 샤워 시간을 1분 줄이면 하루 10L 절약 가능합니다.")
            st.write("3. 빗물 저장 시스템 설치로 월 100L 절약 가능합니다.")
        except Exception as e:
            st.error(f"추천 생성 중 오류 발생: {str(e)}")

# 게이미피케이션 요소
def gamification_elements():
    st.header('게이미피케이션 요소')
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader('일일 목표')
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_info WHERE key='daily_goal'")
            daily_goal = float(cursor.fetchone()[0])
            
            query = """
            SELECT SUM(usage) as total_usage
            FROM water_usage
            WHERE timestamp >= datetime('now', 'start of day')
            """
            today_usage = pd.read_sql_query(query, conn).iloc[0]['total_usage']
            
            progress = min(100, (today_usage / daily_goal) * 100)
            st.progress(progress)
            st.write(f'목표의 {progress:.1f}%를 사용했습니다. (목표: {daily_goal}L)')
        except Exception as e:
            st.error(f"일일 목표 계산 중 오류 발생: {str(e)}")

    with col2:
        st.subheader('주간 챌린지')
        try:
            cursor.execute("SELECT value FROM user_info WHERE key='weekly_challenge'")
            challenge = cursor.fetchone()[0]
            st.write(f'이번 주 챌린지: {challenge}')
            st.write('현재 순위: 지역 내 상위 10%')
        except Exception as e:
            st.error(f"주간 챌린지 정보 조회 중 오류 발생: {str(e)}")

    with col3:
        st.subheader('절약량 시각화')
        try:
            query = """
            SELECT SUM(usage) as total_usage
            FROM water_usage
            WHERE timestamp >= datetime('now', '-30 days')
            """
            last_month_usage = pd.read_sql_query(query, conn).iloc[0]['total_usage']
            average_monthly_usage = 6000  # 가정: 평균 월간 사용량
            saved_water = max(0, average_monthly_usage - last_month_usage)
            trees_saved = int(saved_water / 100)
            st.write(f'지난 달 대비 {saved_water:.0f}L의 물을 절약했습니다!')
            st.write(f'당신의 노력으로 {trees_saved}그루의 나무를 살렸습니다! 🌳' * min(trees_saved, 10))
        except Exception as e:
            st.error(f"절약량 계산 중 오류 발생: {str(e)}")

# 커뮤니티 기능
def community_features():
    st.header('커뮤니티 기능')
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

# 스마트홈 연동
def smart_home_integration():
    st.header('스마트홈 연동')
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


# 메인 앱
def main():
    st.sidebar.title('메뉴')
    menu = st.sidebar.radio('선택하세요:', 
        ['대시보드', 'AI 분석 및 추천', '게이미피케이션', 
         '커뮤니티', '스마트홈 연동','지능형 어시스턴트', '고급 분석', '맞춤형 챌린지', 
         '문제 해결', '환경 영향 시뮬레이션', '환경 영향 시각화','다국어 지원', '보고서 생성'])
    
        
    
    if menu == '대시보드':
        main_dashboard()
    elif menu == '지능형 어시스턴트':
        intelligent_assistant()
    elif menu == 'AI 분석 및 추천':
        ai_analysis_and_recommendation()
    elif menu == '게이미피케이션':
        gamification_elements()
    elif menu == '커뮤니티':
        community_features()
    elif menu == '환경 영향 시뮬레이션':
        environmental_impact()
    elif menu == '환경 영향 시각화':
        environmental_visual()
    elif menu == '다국어 지원':
        multilingual_support()
    elif menu == '스마트홈 연동':
        smart_home_integration()
    elif menu == '보고서 생성':
        generate_report()
    elif menu == '고급 분석':
        advanced_analysis()
    elif menu == '맞춤형 챌린지':
        personalized_challenge()
    elif menu == '문제 해결':
        intelligent_problem_solving()
   

if __name__ == "__main__":
    main()

# 데이터베이스 연결 종료
conn.close()