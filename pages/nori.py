from lib.opensearch import opensearch_utils 
import streamlit as st
import os

OPENSEARCH_URL = os.getenv("MY_OPENSERACH_URL")
USERNAME = os.getenv("MY_USERNAME")
PASSWORD = os.getenv("MY_PASSWORD")

# OpenSearch 클라이언트 생성

# opensearch 서버 주소, 아이디, 비밀번호 입력
client = opensearch_utils.create_local_opensearch_client(OPENSEARCH_URL, (USERNAME, PASSWORD))

# 인덱스 생성
index_name = "nori_test_index"
index_body = {
    "settings": {
        "analysis": {
            "analyzer": {
                "nori_analyzer": {
                    "type": "custom",
                    "tokenizer": "nori_tokenizer"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "text": {
                "type": "text",
                "analyzer": "nori_analyzer"
            }
        }
    }
}

# 인덱스 생성 요청
try:
    if client.indices.exists(index=index_name):
        client.indices.delete(index=index_name)
    client.indices.create(index=index_name, body=index_body)
    st.write(f"Index '{index_name}' created successfully.")
except Exception as e:
    st.write(f"Failed to create index: {e}")

# 문서 추가
document = {
    "text": "이것은 한국어 텍스트입니다."
}

st.title("형태 분석")
st.write(document)

try:
    client.index(index=index_name, body=document, id=1, refresh=True)
    st.write("Document added successfully.")
except Exception as e:
    st.write(f"Failed to add document: {e}")

# 분석 결과 확인
try:
    response = client.indices.analyze(
        index=index_name,
        body={
            "analyzer": "nori_analyzer",
            "text": document["text"]
        }
    )
    st.write("Analysis result:")
    for token in response["tokens"]:
        st.write(f"Token: {token['token']}, Start Offset: {token['start_offset']}, End Offset: {token['end_offset']}, Position: {token['position']}")
except Exception as e:
    st.write(f"Failed to analyze text: {e}")

# 인덱스 삭제
try:
    client.indices.delete(index=index_name)
    st.write(f"Index '{index_name}' deleted successfully.")
except Exception as e:
    st.write(f"Failed to delete index: {e}")