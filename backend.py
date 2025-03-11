import werkzeug
from flask import Flask, request, jsonify, send_file, send_from_directory
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv
from datetime import datetime
import openai  # OpenAI 모듈 자체를 임포트
import logging

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app, resources={r"/*": {"origins": "*"}})  # 모든 출처에서의 요청 허용

# Upstage API 설정
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
UPSTAGE_API_BASE_URL = "https://api.upstage.ai/v1/solar"  # 올바른 base_url
UPSTAGE_EMBEDDING_MODEL = "embedding-query"  # 올바른 모델명

# openai 설정
openai.api_key = UPSTAGE_API_KEY
openai.api_base = UPSTAGE_API_BASE_URL

# 문장 데이터베이스 파일 경로
SENTENCES_DB = os.getenv("SENTENCES_DB_PATH", "sentences_db.json")

# 데이터베이스 디렉토리 확인
db_dir = os.path.dirname(SENTENCES_DB)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Upstage 임베딩 생성 함수 (이전 버전 openai 라이브러리 사용)
def get_upstage_embeddings(texts):
    # 단일 문자열과 문자열 리스트를 모두 처리할 수 있도록 함
    if isinstance(texts, str):
        texts = [texts]
    
    embeddings = []
    for text in texts:
        response = openai.Embedding.create(
            input=text,
            model=UPSTAGE_EMBEDDING_MODEL
        )
        embeddings.append(response["data"][0]["embedding"])
    
    return embeddings

@app.route("/", methods=["GET"])
def index():
    # index.html 파일 제공
    return send_file('index.html')

# 정적 파일 제공을 위한 추가 라우트
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route("/compute_similarity", methods=["POST"])
def compute_similarity():
    try:
        logger.info("Received compute_similarity request")
        data = request.json
        texts = data.get("texts")

        if not texts or len(texts) < 2:
            logger.warning("Invalid request: not enough texts")
            return jsonify({"error": "최소 두 개의 문장이 필요합니다"}), 400

        # Upstage 임베딩 생성
        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = get_upstage_embeddings(texts)
        
        # 임베딩을 numpy 배열로 변환
        vecs = [np.array(embedding) for embedding in embeddings]
        similarities = []

        for i in range(len(vecs)):
            for j in range(i + 1, len(vecs)):
                sim = cosine_similarity([vecs[i]], [vecs[j]])[0][0]
                similarities.append({"pair": f"{i+1} vs {j+1}", "similarity": round(sim, 4)})

        logger.info(f"Computed {len(similarities)} similarity pairs")
        return jsonify({"similarities": similarities})
    
    except Exception as e:
        logger.error(f"Error in compute_similarity: {str(e)}", exc_info=True)
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

@app.route("/debug", methods=["GET"])
def debug():
    # 환경 변수 확인 (API 키는 일부만 표시)
    api_key = os.getenv("UPSTAGE_API_KEY", "Not set")
    masked_key = "Not set" if api_key == "Not set" else api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"
    
    debug_info = {
        "api_key_set": api_key != "Not set",
        "api_key_preview": masked_key,
        "api_base_url": UPSTAGE_API_BASE_URL,
        "embedding_model": UPSTAGE_EMBEDDING_MODEL,
        "port": os.environ.get("PORT", "5003")
    }
    return jsonify(debug_info)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5003))
    app.run(host="0.0.0.0", port=port)
