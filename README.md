# teamR 프로젝트
## 설치 방법
1. miniconda 설치
- https://docs.anaconda.com/miniconda/
2. 라이브러리 환경 자동 설치 
- conda env export > environment.yml
3. ollama 설치
- https://ollama.com/download
4. opensearch 설치(옵션) docker


## 실행방법
```bash
streamlit run main.py
```


## 핵심 라이브러리
- langchain
- ollama
- llama3.1 8B
- opensearch
- streamlit


## 영화 안내 챗봇 프로젝트 
### 개요
- 최신 개봉 영화 최근 영화의 추천(최근 데이터를 기반으로)
- 원하는 영화를 어떠 OTT에서 볼수 있을지 확인
- 네이버 영화 크롤링 데이터셋
- 넷플릭스 영화 데이터 셋



### 파일구조
```
.
├── README.md
├── crawling
│   ├── __pycache__
│   │   └── movie_scraper.cpython-310.pyc
│   ├── movie_scraper.py
│   └── origin_scraper.py
├── dataset
├── docker-compose.yaml
├── environment.yml
├── lib
├── main.py
└── pages
    ├── chat.py
    └── crawling.py

6 directories, 9 files


```








