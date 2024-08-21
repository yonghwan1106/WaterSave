import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import os

# 페이지 설정
st.set_page_config(layout="wide")
st.title('워터세이브(WaterSave) 앱')

# 데이터베이스 파일 경로
DB_FILE = os.environ.get('DB_FILE', 'water_usage.db')

# 데이터베이스 초기화 함수
def init_db():
    try:
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
        st.success("데이터베이스가 성공적으로 초기화되었습니다.")
    except sqlite3.Error as e:
        st.error(f"데이터베이스 초기화 중 오류 발생: {e}")
        st.error(f"현재 작업 디렉토리: {os.getcwd()}")
        st.error(f"데이터베이스 파일 존재 여부: {os.path.exists(DB_FILE)}")
        st.stop()

# 앱 시작 시 데이터베이스 초기화
init_db()

# 데이터베이스 연결
try:
    conn = sqlite3.connect(DB_FILE)
    st.success("데이터베이스에 성공적으로 연결되었습니다.")
except sqlite3.Error as e:
    st.error(f"데이터베이스 연결 중 오류 발생: {e}")
    st.error(f"현재 작업 디렉토리: {os.getcwd()}")
    st.error(f"데이터베이스 파일 존재 여부: {os.path.exists(DB_FILE)}")
    st.stop()

# Font Awesome CSS 추가
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
<style>
    .icon-title {
        font-size: 24px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 1. 실시간 물 사용량 모니터링
st.markdown('<p class="icon-title"><i class="fas fa-tachometer-alt"></i> 실시간 물 사용량 모니터링</p>', unsafe_allow_html=True)


with col1:
    # 시간대별 사용량
    query = """
    SELECT strftime('%H', timestamp) as hour, AVG(usage) as avg_usage
    FROM water_usage
    WHERE timestamp >= datetime('now', '-1 day')
    GROUP BY hour
    ORDER BY hour
    """
    try:
        hourly_data = pd.read_sql_query(query, conn)
        fig = go.Figure(data=go.Bar(x=hourly_data['hour'], y=hourly_data['avg_usage']))
        fig.update_layout(title='시간대별 평균 물 사용량 (최근 24시간)', xaxis_title='시간', yaxis_title='사용량 (L)')
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"데이터 조회 중 오류 발생: {str(e)}")
        st.error(f"현재 작업 디렉토리: {os.getcwd()}")
        st.error(f"데이터베이스 파일 존재 여부: {os.path.exists(DB_FILE)}")

with col2:
    # 요일별 사용량
    query = """
    SELECT strftime('%w', timestamp) as day, AVG(usage) as avg_usage
    FROM water_usage
    WHERE timestamp >= datetime('now', '-7 days')
    GROUP BY day
    ORDER BY day
    """
    try:
        daily_data = pd.read_sql_query(query, conn)
        days = ['일', '월', '화', '수', '목', '금', '토']
        daily_data['day'] = daily_data['day'].apply(lambda x: days[int(x)])
        fig = go.Figure(data=go.Bar(x=daily_data['day'], y=daily_data['avg_usage']))
        fig.update_layout(title='요일별 평균 물 사용량 (최근 7일)', xaxis_title='요일', yaxis_title='사용량 (L)')
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"데이터 조회 중 오류 발생: {str(e)}")

# 2. AI 기반 개인 맞춤형 분석 및 추천
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

# 3. 게이미피케이션 요소
st.header('3. 게이미피케이션 요소')
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

# 데이터베이스 연결 종료
conn.close()