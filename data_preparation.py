# python data_preparation.py
import re

def clean_gutenberg_text(file_path, start_marker, end_marker):
    """
    구텐베르크 txt 파일에서 메타데이터를 제거하고 본문만 추출하는 함수
    """
    try:
        # 1. 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            full_text = f.read()
    except FileNotFoundError:
        print(f"err ::: 파일을 찾을 수 없습니다: {file_path}")
        return None
    
    # 2. start_marker 기준으로 자르기
    start_match = re.search(start_marker, full_text, re.IGNORECASE)
    
    if start_match:
        text_after_start = full_text[start_match.end():]
    else:
        print("err ::: 본문 시작 마커를 찾을 수 없습니다.")
        return full_text

    # 3. end_marker 기준으로 자르기
    end_match = re.search(end_marker, text_after_start, re.IGNORECASE)
    
    if end_match:
        cleaned_text = text_after_start[:end_match.start()].strip()
    else:
        print("경고 ::: end_marker를 찾을 수 없습니다. 파일 전체를 사용합니다.")
        cleaned_text = text_after_start.strip()
        
    # 4. 불필요한 공백 제거
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
    
    return cleaned_text

def main():
    """
    clean 함수 호출 및 파일 저장하는 메인 실행 함수
    """
    book_name = "sherlock"

    INPUT_FILE = f"C:/Reading_Mate/data/01_original/{book_name}/{book_name}_ori.txt"
    OUTPUT_FILE = f"C:/Reading_Mate/data/02_cleaned/{book_name}/en/{book_name}_cleaned.txt"

    START_MARKER = "START OF THE PROJECT GUTENBERG EBOOK"
    END_MARKER = "END OF THE PROJECT GUTENBERG EBOOK"

    print(f"[{book_name}] 정제 시작...")

    # 코드 실행
    cleaned_content = clean_gutenberg_text(INPUT_FILE, START_MARKER, END_MARKER)

    if cleaned_content:
        # 5. 정제된 텍스트 저장
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        print("저장 성공")


if __name__ == "__main__":
    main()