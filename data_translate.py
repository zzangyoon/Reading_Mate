import os
import json
import time
from openai import OpenAI  # 예시로 OpenAI 사용
# client = OpenAI(api_key="YOUR_API_KEY")

# ----------------------------------------------------
# 1. 설정 및 데이터 경로 정의
# ----------------------------------------------------
BOOK_FOLDER = 'little_women'
CLEANED_DIR = os.path.join('data', '02_cleaned', BOOK_FOLDER)
PROCESSED_DIR = os.path.join('data', '03_processed')
# book_meta.json 파일에서 정보 로드 (book_id, title 등)
META_FILE_PATH = os.path.join('data', 'book_meta.json') 

INPUT_EN_PATH = os.path.join(CLEANED_DIR, 'en.txt')
OUTPUT_JSON_PATH = os.path.join(PROCESSED_DIR, 'chunked_data_little_women.json') 

# ----------------------------------------------------
# 2. 헬퍼 함수
# ----------------------------------------------------

def load_book_metadata(meta_path, book_folder):
    """book_meta.json에서 특정 책의 메타데이터를 로드합니다."""
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta_data = json.load(f)
        for book in meta_data:
            if book.get('raw_folder') == book_folder:
                return book
    raise FileNotFoundError(f"'{book_folder}'에 해당하는 책 메타데이터를 찾을 수 없습니다.")

def simple_chunking(text: str) -> list:
    """텍스트를 문단(두 개 이상의 줄바꿈) 기준으로 분할합니다."""
    # 문단 분할: 두 개 이상의 연속된 줄바꿈('\n\n')을 기준으로 나눔
    chunks = text.split('\n\n')
    # 빈 문자열이나 공백만 있는 청크를 제거하고, 양쪽 공백 제거
    return [chunk.strip() for chunk in chunks if chunk.strip()]

def translate_chunk(client, text_en: str, model: str = "gpt-4o"):
    """LLM API를 사용하여 영어 텍스트를 한국어로 번역합니다."""
    # 실제 LLM API 호출 로직을 여기에 구현해야 합니다.
    
    # [주의] 이 부분은 LLM API 사용료와 직결되므로 반드시 실제 API 클라이언트를 사용해야 합니다.
    # 안전하고 정확한 번역을 위해 JSON 모드나 응답 포맷 지정을 고려해야 합니다.
    
    try:
        # 🌟 실제 API 호출 예시 (OpenAI) 🌟
        # response = client.chat.completions.create(
        #     model=model,
        #     messages=[
        #         {"role": "system", "content": "You are a professional Korean translator. Translate the following English text into natural, formal Korean."},
        #         {"role": "user", "content": text_en}
        #     ],
        #     temperature=0.3
        # )
        # return response.choices[0].message.content.strip()
        
        # 임시 (Dummy) 번역: 실제 LLM API 키가 없을 때 테스트용
        return f"[번역됨] {text_en[:50]}..." # 예시로 앞 50자만 사용

    except Exception as e:
        print(f"번역 중 오류 발생: {e}")
        return "번역 오류"

# ----------------------------------------------------
# 3. 메인 실행 로직
# ----------------------------------------------------

def main():
    # 폴더 생성 확인
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    try:
        # 1. 메타데이터 로드
        book_meta = load_book_metadata(META_FILE_PATH, BOOK_FOLDER)
        book_id = book_meta['book_id']

        # 2. 영어 정제 텍스트 로드
        with open(INPUT_EN_PATH, 'r', encoding='utf-8') as f:
            full_text_en = f.read()
            
        # 3. 청크 분할
        english_chunks = simple_chunking(full_text_en)
        print(f"총 {len(english_chunks)}개의 청크로 분할되었습니다.")

        # 4. 청크 처리 및 번역
        processed_chunks = []
        # LLM 클라이언트 초기화 (실제 사용 시 주석 해제)
        # client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        for i, chunk_en in enumerate(english_chunks):
            print(f"-> 청크 {i+1}/{len(english_chunks)} 번역 중...")
            
            # 🌟 [중요] 실제 번역 함수 호출 🌟
            # chunk_ko = translate_chunk(client, chunk_en) 
            chunk_ko = translate_chunk(None, chunk_en) # Dummy 호출
            
            processed_chunks.append({
                "chunk_index": i,
                # 이 단계에서 챕터 이름을 자동으로 추출하는 복잡한 로직이 필요할 수 있으나,
                # 일단은 수동 또는 간단한 정규표현식으로 처리 가정
                "chapter_name": f"Chapter {i//10 + 1}", # 예시 챕터명 할당
                "content_en": chunk_en,
                "content_ko": chunk_ko,
                "corresponding_chunk_id": None # DB 적재 시 채워질 임시 값
            })
            time.sleep(0.5) # API 호출 제한 방지 및 진행 상황 확인을 위한 딜레이

        # 5. 최종 JSON 구조 생성
        final_data_structure = [{
            "book_id": book_id,
            "gutenberg_id": book_meta['gutenberg_id'],
            "title_ko": book_meta['title_ko'],
            "title_en": book_meta['title_en'],
            "author": book_meta['author'],
            "chunks": processed_chunks
        }]
        
        # 6. JSON 파일 저장
        with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(final_data_structure, f, ensure_ascii=False, indent=4)
            
        print(f"\n성공: 최종 JSON 파일이 '{OUTPUT_JSON_PATH}'에 저장되었습니다.")
        
    except Exception as e:
        print(f"메인 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    # 실제 LLM API 키를 환경 변수에 설정해야 합니다.
    # dotenv 등을 사용하여 로드하는 것을 권장합니다.
    main()