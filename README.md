# Flavor Map: 하이브리드 AI 주류 & 푸드 큐레이션 시스템

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Vulkan](https://img.shields.io/badge/Vulkan-C41E3A?style=for-the-badge&logo=vulkan&logoColor=white)

## 프로젝트 소개
**Flavor Map**은 사용자의 미각 선호도(스모키, 달콤함, 과일향, 바디감)를 유클리드 거리(Euclidean Distance) 알고리즘으로 분석하여 최적의 위스키와 안주를 매칭해 주는 지능형 큐레이션 시스템입니다. 

특히 클라우드 API에 의존하지 않고, **로컬 환경(내 컴퓨터)에서 C++ 기반의 Llama 3 모델을 직접 구동**하여 개인화된 소믈리에 테이스팅 노트를 실시간으로 생성하는 **하이브리드 MSA(Microservices Architecture)**를 구현했습니다.

## 시연 화면 (Demo)
> *사용자의 취향을 반영한 거리지수 시각화 및 실시간 번역된 AI 소믈리에 추천 화면*

## 핵심 기능 (Key Features)
1. **Taste Vector 매칭 엔진:** 1~5점 척도의 사용자 취향 데이터를 4차원 벡터로 변환하여 DB와의 거리지수를 계산, 최적의 페어링 도출.
2. **다크모드 데이터 시각화:** Plotly를 활용한 오버레이 형태의 방사형(Radar) 차트 제공.
3. **로컬 AI 소믈리에 (C++ ↔ Python 통신):** Vulkan GPU 가속을 활용하는 C++ 백엔드 엔진이 테이스팅 노트를 작성.
4. **실시간 번역 파이프라인 (UX 개선):** 로컬 AI 모델의 언어 출력 한계를 극복하기 위해, 백엔드 단에서 실시간 번역 파이프라인(`deep-translator`)을 거쳐 자연스러운 한국어 UI/UX 제공.

## 시스템 아키텍처 및 폴더 구조
본 프로젝트는 시스템의 안정성을 위해 프론트엔드(웹)와 백엔드(AI 서버) 폴더를 분리하여 운영합니다.

* **Frontend & Data Layer (Python):** `flavor-map-v2` 폴더
  * UI 렌더링, 유저 입력 처리 (Streamlit, Plotly) 및 실시간 번역 (`deep-translator`)
  * Pandas 활용 CSV 데이터베이스 연동 및 거리 연산
* **Backend Layer (C++):** `cpp-local-llm-server` 폴더
  * Llama 3 모델 추론 및 텍스트 생성 (Localhost Port: 8080)

## 트러블슈팅 (Troubleshooting)
### Issue: Quantized 로컬 모델의 다국어 출력 뇌정지(Tokenizer Error) 현상
* **문제 상황:** Llama 3 모델 경량화(Quantization) 과정에서 한국어 출력 토큰이 손상되어, 프롬프트에 한국어 답변을 강제할 경우 모델이 쉼표(`, , ,`)만 출력하며 뻗어버리는 현상 발생.
* **해결 및 아키텍처 개선:** 1. AI 프롬프트를 가장 안정적인 '순정 영어'로 강제하여 AI의 성능을 100% 이끌어냄.
  2. Streamlit 프론트엔드에 출력하기 직전, 파이썬 백엔드 레이어에서 구글 번역 파이프라인을 추가로 장착.
* **결과:** 모델을 재학습(Fine-tuning)하는 엄청난 리소스 낭비 없이, 가벼운 파이프라인 추가만으로 다국어 지원이 가능한 우아한 하이브리드 시스템 완성.

## 사전 준비 사항 (Prerequisites)
본 시스템을 로컬 환경에서 구동하기 위해서는 아래의 종속성 파일 및 프로그램들이 먼저 세팅되어 있어야 합니다.

1. **C++ 로컬 AI 서버 환경 구축 (`llama.cpp` 기반)**
   * 이 프로젝트는 백엔드로 `llama.cpp` 기반의 서버 구동기가 필요합니다. 
   * [llama.cpp 공식 깃허브](https://github.com/ggerganov/llama.cpp)에서 소스코드를 다운받아 직접 빌드(Build)하거나, Release 페이지에서 미리 컴파일된 서버 실행 파일(exe)을 다운로드하세요.
   * 준비된 서버 환경을 `C:\cpp-local-llm-server` 경로에 배치하여 본 프로젝트와 연동합니다. (실행 파일명이나 경로는 본인의 빌드 환경에 맞게 `app.py` 또는 실행 명령어에서 수정 가능합니다.)
2. **LLM 모델 파일 다운로드**
   * Hugging Face 등에서 양자화된 Llama 3 모델(`Meta-Llama-3-8B-Instruct.Q4_K_M.gguf`) 파일을 다운로드합니다.
   * 다운로드한 파일을 `C:\cpp-local-llm-server\models\` 폴더 안에 넣어줍니다.
3. **Ngrok (외부망 접속 툴) 설치**
   * 외부 기기(스마트폰 등) 연동을 원할 경우, [Ngrok 공식 홈페이지](https://ngrok.com/)에서 실행 파일을 다운로드하여 `flavor-map-v2` 폴더 안에 배치하거나 환경 변수에 등록해야 합니다.

## 실행 방법 (How to Run)

**1. C++ 백엔드 서버 실행 (Llama 3 로드)**
사전 준비가 완료되었다면, 별도의 AI 로컬 서버 폴더로 이동하여 백엔드를 가동합니다.
```bash
cd C:\cpp-local-llm-server
.\build\bin\Debug\llm_server.exe -m models\Meta-Llama-3-8B-Instruct.Q4_K_M.gguf --port 8080
```
**2. Python 프론트엔드 가동 (의존성 설치 및 실행)**
Flavor Map 프로젝트 폴더에서 실행합니다.

Contact
Author: 김태우

Email: kimha100402@gmail.com

GitHub: https://github.com/TWoo-it
```bash
pip install -r requirements.txt
streamlit run app.py
```
**3. 외부 네트워크망 접속 (선택사항)**
```bash
ngrok http 8501
```
