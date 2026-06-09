import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import requests
from deep_translator import GoogleTranslator # 새로 장착한 마법의 번역기 부품!

# 1. 페이지 기본 설정
st.set_page_config(page_title="Flavor Map (Hybrid AI Version)", layout="wide")
st.title("Flavor Map: 지능형 주류 & 푸드 큐레이션 시스템")
st.write("하이브리드 MSA 아키텍처: 로컬 C++ 엔진(Llama3 v2)과 파이썬 번역 파이프라인이 융합된 완성형 시스템입니다.")

# 데이터 로드
try:
    df_whiskey = pd.read_csv("whiskey_db.csv")
    df_food = pd.read_csv("food_db.csv")
except FileNotFoundError:
    st.error("데이터 파일(CSV)이 폴더에 없습니다! 파일을 먼저 넣어주세요.")
    st.stop()
    
categories = ['smoky', 'sweet', 'fruity', 'body']

# 2. 사이드바: 제어 패널 및 백엔드 연결 설정
st.sidebar.title("제어 패널")

ai_server_url = st.sidebar.text_input(
    "AI 백엔드 서버 주소:", 
    value="http://localhost:8080", 
    help="기본값은 내 컴퓨터(localhost)입니다. 외부 시연 시 Ngrok 주소를 붙여넣으세요!"
)

mode = st.sidebar.radio(
    "분석 모드를 선택하세요:", 
    ["기존 위스키 기반 추천", "내 입맛 맞춤 커스텀 추천", "오늘의 안주 맞춤 추천 (New)"]
)

# 3. 모드별 유저 취향 벡터(Taste Vector) 생성
user_choice = None
if mode == "기존 위스키 기반 추천":
    user_choice = st.sidebar.selectbox("좋아하는 위스키를 골라보세요:", df_whiskey['name'].tolist())
    target_data = df_whiskey[df_whiskey['name'] == user_choice].iloc[0]
    user_profile = [target_data['smoky'], target_data['sweet'], target_data['fruity'], target_data['body']]
    label_name = user_choice
    context_text = f"The user normally likes {user_choice} whisky."

elif mode == "내 입맛 맞춤 커스텀 추천":
    st.sidebar.subheader("당신의 선호도를 조절해보세요 (1~5점)")
    u_smoky = st.sidebar.slider("스모키함 (피트 향)", 1, 5, 3)
    u_sweet = st.sidebar.slider("달콤함 (바닐라/카라멜)", 1, 5, 3)
    u_fruity = st.sidebar.slider("과일향 (상큼함/시트러스)", 1, 5, 3)
    u_body = st.sidebar.slider("바디감 (무게감)", 1, 5, 3)
    user_profile = [u_smoky, u_sweet, u_fruity, u_body]
    label_name = "내 커스텀 취향"
    context_text = f"The user wants a whisky with smoky {u_smoky}, sweet {u_sweet}, fruity {u_fruity}, and body {u_body} levels."

else:
    food_choice = st.sidebar.selectbox("오늘 함께 먹을 안주를 골라보세요:", df_food['food_name'].tolist())
    target_food = df_food[df_food['food_name'] == food_choice].iloc[0]
    user_profile = [target_food['ideal_smoky'], target_food['ideal_sweet'], target_food['ideal_fruity'], target_food['ideal_body']]
    label_name = f"{food_choice}의 이상적 매칭"
    context_text = f"The user is planning to eat {food_choice} as a side dish."

# 4. [추천 알고리즘] 유클리드 거리 연산
df_whiskey['distance'] = (
    (df_whiskey['smoky'] - user_profile[0])**2 +
    (df_whiskey['sweet'] - user_profile[1])**2 +
    (df_whiskey['fruity'] - user_profile[2])**2 +
    (df_whiskey['body'] - user_profile[3])**2
)**0.5

recommendations = df_whiskey[df_whiskey['name'] != user_choice].sort_values(by='distance') if (mode == "기존 위스키 기반 추천" and user_choice) else df_whiskey.sort_values(by='distance')
recommended_whiskey = recommendations.iloc[0]

# 5. 메인 대시보드 화면 구성
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("취향 대조 분석 맵 (Flavor Overlay)")
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=user_profile, theta=categories, fill='toself', name=label_name, line_color='#1f77b4'))
    fig.add_trace(go.Scatterpolar(
        r=[recommended_whiskey['smoky'], recommended_whiskey['sweet'], recommended_whiskey['fruity'], recommended_whiskey['body']],
        theta=categories, fill='toself', name=f"추천: {recommended_whiskey['name']}", line_color='#ff7f0e'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True, height=500)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("매칭 엔진 분석 결과")
    st.metric(label="최적 매칭 모델", value=recommended_whiskey['name'])
    st.metric(label="맛 거리지수 (Taste Distance)", value=f"{recommendations.iloc[0]['distance']:.3f}")
    
    st.divider()
    st.markdown("### C++ 로컬 AI 소믈리에의 페어링 가이드 (실시간 번역)")
    
    
    prompt = f"You are a whiskey sommelier. We recommend {recommended_whiskey['name']} to the user. Explain why this whiskey is a great choice in 3 elegant sentences. You MUST answer ONLY in English."
    
    if st.button("AI 소믈리에 의견 듣기"):
        with st.spinner("당신만을 위한 고품격 테이스팅 노트를 실시간으로 분석 중입니다..."):
            try:
                # 1. C++ 서버로 질문 송신
                response = requests.get(f"{ai_server_url}/chat", params={"msg": prompt}, timeout=120)
                
                if response.status_code == 200:
                    english_response = response.text.strip()
                    #st.info(f"AI 영어 원본 텍스트: {english_response}")
                    
                    # 2. AI가 정상적으로 영어를 뱉었을 때만 번역기 가동
                    if len(english_response) > 10:
                        translated_response = GoogleTranslator(source='en', target='ko').translate(english_response)
                        st.success(f"**소믈리에의 한글 번역 노트:**\n\n{translated_response}")
                    else:
                        st.warning("AI가 생각에 잠겼습니다. 뇌를 다시 깨우기 위해 버튼을 한 번 더 눌러주세요!")
                else:
                    st.error(f"서버가 응답했지만 오류가 발생했습니다. (상태 코드: {response.status_code})")
                    
            except requests.exceptions.ConnectionError:
                st.error(f"AI 서버({ai_server_url})에 연결할 수 없습니다!")
            except Exception as e:
                st.error(f"알 수 없는 오류가 발생했습니다: {e}")