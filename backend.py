import werkzeug
from flask import Flask, request, jsonify, send_file
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI  # 새로운 OpenAI 클라이언트 임포트

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)
CORS(app)  # 프론트엔드와 연동을 위해 CORS 활성화

# Upstage API 설정
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
UPSTAGE_API_BASE_URL = "https://api.upstage.ai/v1/solar"  # 올바른 base_url
UPSTAGE_EMBEDDING_MODEL = "embedding-query"  # 올바른 모델명

# 문장 데이터베이스 파일 경로
SENTENCES_DB = "sentences_db.json"

# 문장 데이터베이스 로드
def load_sentences_db():
    if os.path.exists(SENTENCES_DB):
        with open(SENTENCES_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"sentences": []}

# 문장 데이터베이스 저장
def save_sentences_db(db):
    with open(SENTENCES_DB, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# Upstage 임베딩 생성 함수 (OpenAI 1.0.0 API 사용)
def get_upstage_embeddings(texts):
    # OpenAI 클라이언트 초기화
    client = OpenAI(
        api_key=UPSTAGE_API_KEY,
        base_url=UPSTAGE_API_BASE_URL
    )
    
    # 단일 문자열과 문자열 리스트를 모두 처리할 수 있도록 함
    if isinstance(texts, str):
        texts = [texts]
    
    embeddings = []
    for text in texts:
        response = client.embeddings.create(
            input=text,
            model=UPSTAGE_EMBEDDING_MODEL
        )
        embeddings.append(response.data[0].embedding)
    
    return embeddings

@app.route("/", methods=["GET"])
def index():
    # index.html 파일 제공
    return send_file('index.html')

@app.route("/compute_similarity", methods=["POST"])
def compute_similarity():
    try:
        data = request.json
        texts = data.get("texts")

        if not texts or len(texts) < 2:
            return jsonify({"error": "최소 두 개의 문장이 필요합니다"}), 400

        # Upstage 임베딩 생성
        embeddings = get_upstage_embeddings(texts)
        
        # 임베딩을 numpy 배열로 변환
        vecs = [np.array(embedding) for embedding in embeddings]
        similarities = []

        for i in range(len(vecs)):
            for j in range(i + 1, len(vecs)):
                sim = cosine_similarity([vecs[i]], [vecs[j]])[0][0]
                similarities.append({"pair": f"{i+1} vs {j+1}", "similarity": round(sim, 4)})

        return jsonify({"similarities": similarities})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/save_sentence", methods=["POST"])
def save_sentence():
    try:
        data = request.json
        sentence = data.get("sentence")

        if not sentence:
            return jsonify({"error": "문장이 필요합니다"}), 400

        # 현재 시각 정보 가져오기
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 임베딩 생성
        embedding = get_upstage_embeddings(sentence)[0]

        # DB에 문장과 임베딩 저장
        db = load_sentences_db()
        db["sentences"].append({
            "text": sentence,
            "embedding": embedding,
            "timestamp": timestamp  # 시각 정보 추가
        })
        save_sentences_db(db)

        return jsonify({"success": True, "message": "문장이 저장되었습니다"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/search_similar", methods=["POST"])
def search_similar():
    try:
        data = request.json
        query = data.get("query")

        if not query:
            return jsonify({"error": "검색어가 필요합니다"}), 400

        # DB 로드
        db = load_sentences_db()
        if not db["sentences"]:
            return jsonify({"error": "저장된 문장이 없습니다"}), 404

        # 검색어 임베딩 생성
        query_embedding = get_upstage_embeddings(query)[0]
        query_embedding_np = np.array(query_embedding)

        # 각 저장된 문장과의 유사도 계산
        results = []
        for item in db["sentences"]:
            stored_embedding = np.array(item["embedding"])
            similarity = cosine_similarity([query_embedding_np], [stored_embedding])[0][0]
            results.append({
                "text": item["text"],
                "similarity": round(similarity, 4),
                "timestamp": item.get("timestamp", "")  # 시각 정보 추가 (기존 데이터 호환성 유지)
            })

        # 유사도 높은 순으로 정렬
        results.sort(key=lambda x: x["similarity"], reverse=True)

        return jsonify({"results": results})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_all_sentences", methods=["GET"])
def get_all_sentences():
    try:
        db = load_sentences_db()
        sentences = []
        for item in db["sentences"]:
            sentences.append({
                "text": item["text"],
                "timestamp": item.get("timestamp", "")  # 시각 정보 추가 (기존 데이터 호환성 유지)
            })
        return jsonify({"sentences": sentences})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/reset_sentences", methods=["POST"])
def reset_sentences():
    try:
        # 빈 문장 데이터베이스 생성
        db = {"sentences": []}
        save_sentences_db(db)
        
        return jsonify({"success": True, "message": "모든 문장이 삭제되었습니다"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5003))
    app.run(host="0.0.0.0", port=port)
