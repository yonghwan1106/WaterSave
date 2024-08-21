import sqlite3
import random
import time
from datetime import datetime, timedelta

# 데이터베이스 연결
conn = sqlite3.connect('water_usage.db')
c = conn.cursor()

# 테이블 생성
c.execute('''CREATE TABLE IF NOT EXISTS water_usage
             (timestamp TEXT, usage REAL)''')

# 사용자 정보 테이블 생성
c.execute('''CREATE TABLE IF NOT EXISTS user_info
             (key TEXT PRIMARY KEY, value TEXT)''')

# 초기 사용자 정보 설정
c.execute("INSERT OR REPLACE INTO user_info (key, value) VALUES (?, ?)", 
          ('daily_goal', '200'))
c.execute("INSERT OR REPLACE INTO user_info (key, value) VALUES (?, ?)", 
          ('weekly_challenge', '설거지 물 사용량 20% 줄이기'))
conn.commit()

def generate_data():
    # 현재 시간
    now = datetime.now()
    
    # 시간에 따른 기본 사용량 (0시~5시: 낮음, 6시~9시: 높음, 10시~15시: 중간, 16시~23시: 높음)
    hour = now.hour
    if 0 <= hour < 6:
        base_usage = random.uniform(0.1, 0.5)
    elif 6 <= hour < 10 or 16 <= hour < 24:
        base_usage = random.uniform(1, 3)
    else:
        base_usage = random.uniform(0.5, 1.5)
    
    # 요일에 따른 변동 (주말에는 사용량이 더 많음)
    if now.weekday() >= 5:  # 5: 토요일, 6: 일요일
        base_usage *= 1.2
    
    # 랜덤 노이즈 추가
    usage = base_usage + random.uniform(-0.1, 0.1)
    
    # 음수 방지
    usage = max(0, usage)
    
    return now.strftime('%Y-%m-%d %H:%M:%S'), round(usage, 2)

# 실시간 데이터 생성 및 저장
while True:
    timestamp, usage = generate_data()
    c.execute("INSERT INTO water_usage VALUES (?, ?)", (timestamp, usage))
    conn.commit()
    print(f"Inserted: {timestamp}, {usage}")
    time.sleep(60)  # 1분마다 데이터 생성