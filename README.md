# 문장 유사도 도구 (Sentence Similarity Tool)

이 프로젝트는 한국어 문장 간의 의미적 유사도를 계산하고 분석하는 웹 애플리케이션입니다. Upstage의 임베딩 API를 활용하여 텍스트를 벡터로 변환하고, 코사인 유사도를 통해 문장 간의 의미적 유사성을 측정합니다.

## 주요 기능

1. **유사도 계산**: 여러 문장 간의 의미적 유사도를 계산하고 시각화
2. **문장 저장**: 자주 사용하는 문장을 데이터베이스에 저장
3. **유사도 검색**: 저장된 문장 중에서 입력 문장과 의미적으로 유사한 문장 검색

## 기술 스택

- **프론트엔드**: HTML, CSS, JavaScript (순수 바닐라 JS)
- **백엔드**: Flask (Python)
- **임베딩 API**: Upstage Solar API
- **유사도 계산**: 코사인 유사도 (scikit-learn)
- **데이터 저장**: JSON 파일 기반 로컬 스토리지

## 설치 및 실행 방법

### 필수 요구사항

- Python 3.7 이상
- Upstage API 키

### 로컬 환경에서 실행하기

1. 저장소 클론
   ```bash
   git clone https://github.com/your-username/sentence-similarity-tool.git
   cd sentence-similarity-tool
   ```

2. 가상 환경 설정 (선택 사항)
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```

4. 환경 변수 설정
   - `.env` 파일을 생성하고 다음 내용 추가:
   ```
   UPSTAGE_API_KEY=your_api_key_here
   ```

5. 애플리케이션 실행
   ```bash
   python backend.py
   ```

6. 웹 브라우저에서 접속
   - http://localhost:5003 으로 접속

## 배포 방법 (Render)

1. GitHub 저장소에 코드 푸시
2. Render.com에서 새 웹 서비스 생성
3. GitHub 저장소 연결
4. 환경 변수 설정 (`UPSTAGE_API_KEY`)
5. 배포 시작

## 사용 방법

### 유사도 계산

1. "유사도 계산" 탭 선택
2. 텍스트 영역에 비교할 문장들을 입력 (한 줄에 하나씩)
3. "유사도 계산" 버튼 클릭
4. 결과 확인: 각 문장 쌍의 유사도 점수와 시각화된 바 차트

### 문장 저장

1. "문장 저장" 탭 선택
2. 저장할 문장 입력
3. "문장 저장" 버튼 클릭
4. 저장된 문장 목록에서 확인

### 유사도 검색

1. "유사도 검색" 탭 선택
2. 검색할 문장 입력
3. "유사 문장 검색" 버튼 클릭
4. 저장된 문장 중 유사도가 높은 순으로 결과 확인

## 작동 원리

1. **텍스트 임베딩**: Upstage의 임베딩 API를 사용하여 각 문장을 고차원 벡터로 변환
2. **코사인 유사도**: 변환된 벡터 간의 코사인 유사도를 계산
3. **결과 시각화**: 계산된 유사도 점수를 색상 바로 시각화

## 라이선스

MIT License

## 기여 방법

1. 이 저장소를 포크합니다.
2. 새 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`).
3. 변경 사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`).
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`).
5. Pull Request를 생성합니다.

## 연락처

프로젝트 관리자: [이메일 주소]

---

이 프로젝트는 Upstage의 임베딩 API를 활용합니다. 자세한 내용은 [Upstage 공식 문서](https://upstage.ai)를 참조하세요. 