// ===== 설정 =====
const FASTAPI_BASE_URL = 'http://127.0.0.1:8003';

// PDF.js 워커 설정
if (typeof pdfjsLib !== 'undefined') {
    pdfjsLib.GlobalWorkerOptions.workerSrc = 
        'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
}

// ===== 전역 변수 =====
let currentBook = null;  // 현재 책 데이터
let currentPage = 1;     // 현재 페이지
let totalPages = 1;      // 전체 페이지
let bookType = null;     // 'txt' 또는 'pdf'
let selectedText = '';   // 선택된 텍스트
let lastSessionId = null; // 마지막 세션 ID
let pageCache = {};

// ===== DOM 요소 =====
const loadTxtBtn = document.getElementById('load-txt-btn');
const loadPdfBtn = document.getElementById('load-pdf-btn');
const loadBookBtn = document.getElementById('load-book-btn');
const fileInput = document.getElementById('file-input');
const bookTitle = document.getElementById('book-title');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const pageInfo = document.getElementById('page-info');
const pageSlider = document.getElementById('page-slider');
const bookViewer = document.getElementById('book-viewer');
const selectionMenu = document.getElementById('selection-menu');
const createImageBtn = document.getElementById('create-image-btn');
const copyTextBtn = document.getElementById('copy-text-btn');
const selectedTextDisplay = document.getElementById('selected-text');
const userInput = document.getElementById('user-input');
const generateBtn = document.getElementById('generate-btn');
const regenerateBtn = document.getElementById('regenerate-btn');
const statusArea = document.getElementById('status-area');
const statusText = document.getElementById('status-text');
const resultArea = document.getElementById('result-area');
const resultImage = document.getElementById('result-image');
const qualityScore = document.getElementById('quality-score');
const generationTime = document.getElementById('generation-time');
const downloadBtn = document.getElementById('download-btn');
const debugInfo = document.getElementById('debug-info');
const tabBtns = document.querySelectorAll('.tab-btn');
const savedProgressSpan = document.getElementById('saved-progress');
const totalProgressSpan = document.getElementById('total-progress');
const qaSendBtn = document.getElementById('qa-send-btn');
const qaInput = document.getElementById('qa-input');
const qaMessages = document.getElementById('qa-messages');
const bookSelectModal = document.getElementById('book-select-modal');
const closeModalBtn = document.querySelector('.close');
const bookListDiv = document.getElementById('book-list');
const characterSelect = document.getElementById('character-select');
const characterInput = document.getElementById('character-input');
const characterSendBtn = document.getElementById('character-send-btn');
const characterMessages = document.getElementById('character-messages');

// ===== 1. 파일 로드 =====

// TXT 파일 로드 버튼
loadTxtBtn.addEventListener('click', () => {
    fileInput.accept = '.txt';
    fileInput.click();
});

// PDF 파일 로드 버튼
loadPdfBtn.addEventListener('click', () => {
    fileInput.accept = '.pdf';
    fileInput.click();
});

// 파일 선택 이벤트
fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    console.log('📁 파일 선택:', file.name);
    
    const extension = file.name.split('.').pop().toLowerCase();
    
    if (extension === 'txt') {
        await loadTextFile(file);
    } else if (extension === 'pdf') {
        await loadPdfFile(file);
    } else {
        alert('TXT 또는 PDF 파일만 지원합니다.');
    }
    
    // 입력 초기화
    fileInput.value = '';
});

// ===== TXT 파일 로드 =====
async function loadTextFile(file) {
    console.log('📄 TXT 파일 로딩 중...');
    
    try {
        const text = await file.text();
        
        // 줄바꿈으로 분할 (빈 줄 제거)
        const lines = text.split('\n').filter(line => line.trim());
        
        // 페이지 단위로 분할 (15줄씩)
        const linesPerPage = 15;
        const pages = [];
        
        for (let i = 0; i < lines.length; i += linesPerPage) {
            pages.push(lines.slice(i, i + linesPerPage).join('\n\n'));
        }
        
        currentBook = {
            type: 'txt',
            pages: pages,
            name: file.name
        };
        
        bookType = 'txt';
        totalPages = pages.length;
        currentPage = 1;
        
        // UI 업데이트
        bookTitle.textContent = file.name;
        updatePageControls();
        renderTextPage(currentPage);
        
        console.log(`✅ TXT 로드 완료: ${totalPages} 페이지`);
        
    } catch (error) {
        console.error('❌ TXT 로드 실패:', error);
        alert('TXT 파일을 읽을 수 없습니다.');
    }
}

// ===== PDF 파일 로드 (텍스트 추출) =====
async function loadPdfFile(file) {
    console.log('📕 PDF 파일 로딩 중...');
    
    try {
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
        
        bookTitle.textContent = `${file.name} - 텍스트 추출 중...`;
        
        // 모든 페이지에서 텍스트 추출
        const allText = [];
        
        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
            const page = await pdf.getPage(pageNum);
            const textContent = await page.getTextContent();
            
            // 텍스트 아이템들을 문자열로 결합
            const pageText = textContent.items
                .map(item => item.str)
                .join(' ')
                .trim();
            
            if (pageText) {
                allText.push(pageText);
            }
            
            // 진행상황 표시
            if (pageNum % 5 === 0) {
                bookTitle.textContent = `${file.name} - ${pageNum}/${pdf.numPages} 페이지 추출 중...`;
            }
        }
        
        // 전체 텍스트를 줄 단위로 재분할 (가독성 향상)
        const fullText = allText.join('\n\n');
        const lines = fullText.split('\n').filter(line => line.trim());
        
        // 페이지 단위로 분할 (15줄씩)
        const linesPerPage = 15;
        const pages = [];
        
        for (let i = 0; i < lines.length; i += linesPerPage) {
            pages.push(lines.slice(i, i + linesPerPage).join('\n\n'));
        }
        
        currentBook = {
            type: 'pdf-text',
            pages: pages,
            name: file.name
        };
        
        bookType = 'txt';  // TXT처럼 취급
        totalPages = pages.length;
        currentPage = 1;
        
        // UI 업데이트
        bookTitle.textContent = `${file.name} (텍스트 모드)`;
        updatePageControls();
        renderTextPage(currentPage);
        
        console.log(`✅ PDF 텍스트 추출 완료: ${totalPages} 페이지`);
        
    } catch (error) {
        console.error('❌ PDF 로드 실패:', error);
        alert('PDF 파일을 읽을 수 없습니다.');
        bookTitle.textContent = '파일을 열어주세요';
    }
}

// ===== 2. 페이지 렌더링 =====

// TXT 페이지 렌더링
// function renderTextPage(pageNum) {
//     console.log("renderTextPage ::: ", currentBook);
//     if (!currentBook || (currentBook.type !== 'txt' && currentBook.type !== 'pdf-text')) return;
    
//     const content = currentBook.pages[pageNum - 1];
    
//     // HTML로 변환 (줄바꿈 유지)
//     const paragraphs = content.split('\n\n')
//         .map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`)
//         .join('');
    
//     bookViewer.innerHTML = paragraphs;
    
//     console.log(`📄 페이지 ${pageNum} 렌더링 완료`);
// }

// ===== TXT 페이지 렌더링 =====
async function renderTextPage(pageNum) {
    console.log("renderTextPage ::: ", currentBook);
    
    // 로컬 파일 (txt, pdf-text)인 경우
    if (currentBook && (currentBook.type === 'txt' || currentBook.type === 'pdf-text')) {
        const content = currentBook.pages[pageNum - 1];
        
        // HTML로 변환 (줄바꿈 유지)
        const paragraphs = content.split('\n\n')
            .map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`)
            .join('');
        
        bookViewer.innerHTML = paragraphs;
        
        console.log(`📄 페이지 ${pageNum} 렌더링 완료`);
        return;
    }
    
    // 서버에서 가져온 chunk인 경우
    if (currentBook && bookType === 'chunk') {
        // 캐시 확인
        if (pageCache[pageNum]) {
            bookViewer.innerHTML = pageCache[pageNum];
            console.log(`📄 페이지 ${pageNum} (캐시) 렌더링 완료`);
            return;
        }

        try {
            const res = await fetch(`${FASTAPI_BASE_URL}/book/${currentBook.id}/chunk/${pageNum}`);
            if (!res.ok) throw new Error('청크를 가져올 수 없습니다.');
            const data = await res.json();

            // HTML 변환
            const paragraphs = data.chunk.text.split('\n\n')
                .map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`)
                .join('');

            bookViewer.innerHTML = paragraphs;
            pageCache[pageNum] = paragraphs; // 캐시에 저장
            console.log(`📄 페이지 ${pageNum} 렌더링 완료`);
        } catch (err) {
            console.error(err);
            alert('페이지를 가져오지 못했습니다.');
        }
    }
}


// async function renderTextPage(pageNum) {
//     if (!currentBook || (currentBook.type !== 'txt' && currentBook.type !== 'pdf-text')) return;

//     // 캐시 확인
//     if (pageCache[pageNum]) {
//         bookViewer.innerHTML = pageCache[pageNum];
//         console.log(`📄 페이지 ${pageNum} (캐시) 렌더링 완료`);
//         return;
//     }

//     try {
//         const res = await fetch(`/book/${currentBook.id}/chunk/${pageNum}`);
//         if (!res.ok) throw new Error('청크를 가져올 수 없습니다.');
//         const data = await res.json(); // 서버에서 { chunk: "내용" } 반환 가정

//         // HTML 변환
//         const paragraphs = data.chunk.split('\n\n')
//             .map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`)
//             .join('');

//         bookViewer.innerHTML = paragraphs;
//         pageCache[pageNum] = paragraphs; // 캐시에 저장
//         console.log(`📄 페이지 ${pageNum} 렌더링 완료`);
//     } catch (err) {
//         console.error(err);
//         alert('페이지를 가져오지 못했습니다.');
//         currentPage--; // 실패 시 페이지 되돌리기
//     }
// }

// ===== 3. 페이지 네비게이션 =====

function updatePageControls() {
    pageInfo.textContent = `${currentPage} / ${totalPages}`;
    pageSlider.max = totalPages;
    pageSlider.value = currentPage;
    
    prevBtn.disabled = currentPage <= 1;
    nextBtn.disabled = currentPage >= totalPages;
    pageSlider.disabled = false;
}

prevBtn.addEventListener('click', async() => {
    if (currentPage > 1) {
        currentPage--;

        // 로컬 파일 vs 서버 청크 분기
        if (bookType === 'txt' || bookType === 'pdf-text') {
            await renderTextPage(currentPage);
        } else {
            await renderChunkPage(currentPage);
        }
        updatePageControls();
        updateProgressDisplay();

        // 진도 저장
        if (currentBook && currentBook.id) {
            await saveProgress('default_user', currentBook.id, currentPage);
        }

        // 캐릭터 탭이 활성화되어 있으면 캐릭터 목록 업데이트
        const activeTab = document.querySelector('.tab-btn.active');
        if (activeTab && activeTab.dataset.mode === 'character') {
            await loadAvailableCharacters();
        }
    }
});

nextBtn.addEventListener('click', async() => {
    if (currentPage < totalPages) {
        currentPage++;

        // 로컬 파일 vs 서버 청크 분기
        if (bookType === 'txt' || bookType === 'pdf-text') {
            await renderTextPage(currentPage);
        } else {
            await renderChunkPage(currentPage);
        }

        updatePageControls();
        updateProgressDisplay();

        // 진도 저장
        if (currentBook && currentBook.id) {
            await saveProgress('default_user', currentBook.id, currentPage);
        }

        // 캐릭터 탭이 활성화되어 있으면 캐릭터 목록 업데이트
        const activeTab = document.querySelector('.tab-btn.active');
        if (activeTab && activeTab.dataset.mode === 'character') {
            await loadAvailableCharacters();
        }
    }
});

pageSlider.addEventListener('input', async() => {
    const newPage = Number(pageSlider.value);
    if (newPage !== currentPage) {
        currentPage = newPage;

        // 로컬 파일 vs 서버 청크 분기
        if (bookType === 'txt' || bookType === 'pdf-text') {
            await renderTextPage(currentPage);
        } else {
            await renderChunkPage(currentPage);
        }

        updatePageControls();
        updateProgressDisplay();

        // 진도 저장
        if (currentBook && currentBook.id) {
            await saveProgress('default_user', currentBook.id, currentPage);
        }

        // 캐릭터 탭이 활성화되어 있으면 캐릭터 목록 업데이트
        const activeTab = document.querySelector('.tab-btn.active');
        if (activeTab && activeTab.dataset.mode === 'character') {
            await loadAvailableCharacters();
        }
    }
});

// 키보드 단축키
document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'TEXTAREA') return;
    
    if (e.key === 'ArrowLeft') {
        prevBtn.click();
    } else if (e.key === 'ArrowRight') {
        nextBtn.click();
    }
});

// ===== 4. 텍스트 선택 및 팝업 =====

bookViewer.addEventListener('mouseup', (e) => {
    const selection = window.getSelection();
    const text = selection.toString().trim();
    
    if (text && text.length > 0) {
        selectedText = text;
        console.log('📝 선택된 텍스트:', text);
        
        // UI 업데이트
        selectedTextDisplay.textContent = text;
        userInput.value = text;
        generateBtn.disabled = false;
        
        // 팝업 표시
        // showSelectionMenu(e);
    }
    // } else {
    //     hideSelectionMenu();
    // }
});

function showSelectionMenu(event) {
    const selection = window.getSelection();
    
    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        
        // 팝업 위치 계산
        let menuX = rect.left + (rect.width / 2) - 80;
        let menuY = rect.top + window.scrollY - 70;
        
        // 경계 체크
        if (menuX < 10) menuX = 10;
        if (menuX > window.innerWidth - 170) {
            menuX = window.innerWidth - 170;
        }
        if (menuY < 10) menuY = rect.bottom + window.scrollY + 10;
        
        selectionMenu.style.display = 'block';
        selectionMenu.style.left = menuX + 'px';
        selectionMenu.style.top = menuY + 'px';
    }
}

function hideSelectionMenu() {
    selectionMenu.style.display = 'none';
}

// 외부 클릭 시 팝업 숨기기
document.addEventListener('click', (e) => {
    if (!selectionMenu.contains(e.target) && !bookViewer.contains(e.target)) {
        hideSelectionMenu();
    }
});

// ===== 5. 팝업 메뉴 버튼 =====

createImageBtn.addEventListener('click', () => {
    const text = userInput.value.trim();
    if (text) {
        generateImage(text);
        hideSelectionMenu();
    }
});

copyTextBtn.addEventListener('click', () => {
    const text = userInput.value.trim();
    if (text) {
        navigator.clipboard.writeText(text).then(() => {
            alert('✅ 텍스트가 복사되었습니다!');
            hideSelectionMenu();
        }).catch(err => {
            console.error('복사 실패:', err);
            alert('복사에 실패했습니다.');
        });
    }
});

// ===== 6. 빠른 예시 버튼 =====

document.querySelectorAll('.example-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const text = btn.dataset.text;
        userInput.value = text;
        selectedTextDisplay.textContent = text;
        generateBtn.disabled = false;
    });
});

// ===== 7. 이미지 생성 API =====

async function generateImage(userText) {
    console.log('🎨 이미지 생성 요청:', userText);
    
    generateBtn.disabled = true;
    statusArea.style.display = 'block';
    resultArea.style.display = 'none';
    statusText.textContent = '⏳ 프롬프트 생성 및 이미지 렌더링 중...';
    
    try {
        const response = await fetch(`${FASTAPI_BASE_URL}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_input: userText,
                book_id: 'the_wizard_of_oz',
                steps: 20,
                cfg_scale: 1.0,
                width: 1024,
                height: 1024,
                lora_strength: 0.8
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'API 오류');
        }
        
        const result = await response.json();
        console.log('✅ 생성 완료:', result);
        
        lastSessionId = result.session_id;
        displayResult(result);
        
    } catch (error) {
        console.error('❌ 생성 실패:', error);
        alert(`이미지 생성 실패: ${error.message}`);
    } finally {
        statusArea.style.display = 'none';
        generateBtn.disabled = false;
    }
}

async function displayResult(result) {
    const imageUrl = `${FASTAPI_BASE_URL}${result.image_url}`;
    
    resultImage.src = imageUrl;
    qualityScore.textContent = result.quality_score.toFixed(2);
    generationTime.textContent = result.generation_time.toFixed(1);
    
    try {
        const debugResponse = await fetch(`${FASTAPI_BASE_URL}/session/${result.session_id}`);
        const debugData = await debugResponse.json();
        debugInfo.textContent = JSON.stringify(debugData.debug_info, null, 2);
    } catch {
        debugInfo.textContent = '디버그 정보를 가져올 수 없습니다.';
    }
    
    downloadBtn.onclick = () => {
        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = 'generated_image.png';
        link.click();
    };
    
    resultArea.style.display = 'block';
    regenerateBtn.style.display = 'block';
}

async function regenerateImage() {
    if (!lastSessionId) {
        alert('먼저 이미지를 생성해주세요!');
        return;
    }
    
    regenerateBtn.disabled = true;
    statusArea.style.display = 'block';
    resultArea.style.display = 'none';
    statusText.textContent = '🔄 재생성 중...';
    
    try {
        const response = await fetch(
            `${FASTAPI_BASE_URL}/regenerate?session_id=${lastSessionId}`,
            { method: 'POST' }
        );
        
        if (!response.ok) throw new Error('재생성 실패');
        
        const result = await response.json();
        lastSessionId = result.session_id;
        displayResult(result);
        
    } catch (error) {
        alert(`재생성 실패: ${error.message}`);
    } finally {
        statusArea.style.display = 'none';
        regenerateBtn.disabled = false;
    }
}

generateBtn.addEventListener('click', () => {
    const text = userInput.value.trim();
    if (!text) {
        alert('텍스트를 입력하거나 선택해주세요!');
        return;
    }
    generateImage(text);
});

regenerateBtn.addEventListener('click', regenerateImage);

// ===== 8. 서버 상태 확인 =====

async function checkServerHealth() {
    try {
        const response = await fetch(`${FASTAPI_BASE_URL}/connection_check`);
        const health = await response.json();
        console.log('✅ FastAPI 서버 연결됨:', health);
        return true;
    } catch (error) {
        console.error('❌ FastAPI 서버 미연결:', error);
        alert('⚠️ FastAPI 서버가 실행되고 있지 않습니다.\nmain.py를 먼저 실행해주세요!');
        return false;
    }
}

// ===== 9. 탭 전환 기능 =====

// 탭 버튼 클릭 이벤트
tabBtns.forEach(btn => {
    btn.addEventListener('click', async() => {
        const mode = btn.dataset.mode;
        
        // 모든 탭 비활성화
        tabBtns.forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.chat-mode-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // 선택한 탭 활성화
        btn.classList.add('active');
        document.getElementById(`${mode}-mode`).classList.add('active');
        
        console.log(`✅ 탭 전환: ${mode}`);

        // 캐릭터 탭으로 전환 시 캐릭터 목록 로드
        if (mode === 'character') {
            await loadAvailableCharacters();
        }
    });
});

// ===== 10. 진도 관리 =====

// 진도 표시 업데이트
function updateProgressDisplay() {
    savedProgressSpan.textContent = currentPage;
    totalProgressSpan.textContent = totalPages;
}

// 진도 저장 (서버에 저장)
async function saveProgress(userId = 'default_user', bookId, chunkIndex) {
    try {
        const response = await fetch(`${FASTAPI_BASE_URL}/progress/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                book_id: bookId,
                position: chunkIndex
            })
        });
        
        if (response.ok) {
            console.log(`✅ 진도 저장: ${chunkIndex}페이지`);
            updateProgressDisplay();
        } else {
            console.warn('⚠️ 진도 저장 실패');
        }
    } catch (error) {
        console.error('❌ 진도 저장 오류:', error);
    }
}

// 진도 불러오기 (서버에서 불러오기)
async function loadProgress(userId = 'default_user', bookId) {
    try {
        const response = await fetch(
            `${FASTAPI_BASE_URL}/progress/get?user_id=${userId}&book_id=${bookId}`
        );
        
        if (response.ok) {
            const data = await response.json();
            const savedPage = data.position || 1;
            console.log(`✅ 저장된 진도: ${savedPage}페이지`);
            return savedPage;
        }
    } catch (error) {
        console.error('❌ 진도 불러오기 오류:', error);
    }
    return 1; // 실패 시 1페이지부터
}

// ===== 11. 초기화 =====

window.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 앱 초기화');
    await checkServerHealth();
    updateProgressDisplay();
    console.log('✅ 초기화 완료 - 파일을 열어주세요');
});


// 추가 (파일 로드 대신 서버에서 책 가져오기)
async function loadBookFromServer(bookId, bookTitleText) {
    console.log(`📚 서버에서 책 로드 중: ${bookId}`);
    
    try {
        const chunksRes = await fetch(`${FASTAPI_BASE_URL}/book/${bookId}/chunks`);
        const chunksData = await chunksRes.json();
        totalPages = chunksData.total_chunks;

        // 추가: 저장된 진도 불러오기
        const savedPage = await loadProgress('default_user', bookId);
        currentPage = savedPage;
        
        bookType = 'chunk';
        currentBook = { id: bookId };
        
        bookTitle.textContent = bookTitleText;
        updatePageControls();
        await renderChunkPage(currentPage);
        
        // 추가: 진도 표시 업데이트
        updateProgressDisplay();
        
        console.log(`책 로드 완료: ${totalPages} 청크, ${currentPage}페이지부터 시작`);
        // currentPage = 1;
        // bookType = 'chunk';
        // currentBook = { id: bookId };
        
        // bookTitle.textContent = `${bookId} (서버 모드)`;
        // updatePageControls();
        // await renderChunkPage(currentPage);
        
        // console.log(`✅ 책 로드 완료: ${totalPages} 청크`);
    } catch (error) {
        console.error('❌ 책 로드 실패:', error);
        alert('책을 불러올 수 없습니다.');
    }
}

// ===== 청크 렌더링 =====
async function renderChunkPage(pageNum) {
    // if (!currentBook || bookType !== 'chunk') return;
    // const res = await fetch(`${FASTAPI_BASE_URL}/book/${currentBook.id}/chunk/${pageNum}`);
    // const data = await res.json();
    
    // const html = `<div class="chunk-page">
    //     <h3>📖 Page ${data.page}</h3>
    //     <p>${data.text}</p>
    // </div>`;
    
    // bookViewer.innerHTML = html;
    // console.log(`📄 청크 ${pageNum} 렌더링 완료`);
    if (!currentBook || (bookType !== 'chunk')) return;

    // 캐시 확인
    if (pageCache[pageNum]) {
        bookViewer.innerHTML = pageCache[pageNum];
        console.log(`📄 페이지 ${pageNum} (캐시) 렌더링 완료`);
        return;
    }

    try {
        const res = await fetch(`${FASTAPI_BASE_URL}/book/${currentBook.id}/chunk/${pageNum}`);
        if (!res.ok) throw new Error('청크를 가져올 수 없습니다.');
        const data = await res.json(); // 서버에서 { chunk: "내용" } 반환 가정

        // HTML 변환
        // const paragraphs = data.text.split('\n\n')
        //     .map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`)
        //     .join('');
        const paragraphs = `<div class="chunk-page">
            <h3>📖 Page ${data.page}</h3>
            <p>${data.chunk.text}</p>
        </div>`;

        bookViewer.innerHTML = paragraphs;
        pageCache[pageNum] = paragraphs; // 캐시에 저장
        console.log(`📄 페이지 ${pageNum} 렌더링 완료`);
    } catch (err) {
        console.error(err);
        alert('페이지를 가져오지 못했습니다.');
        currentPage--; // 실패 시 페이지 되돌리기
    }
}

// ===== 12. Q&A 기능 =====

// Q&A 메시지 추가 함수
function addQAMessage(role, content) {
    // placeholder 제거 (처음 메시지일 때)
    const placeholder = qaMessages.querySelector('.chat-placeholder');
    if (placeholder) {
        placeholder.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    
    if (role === 'loading') {
        messageDiv.id = 'loading-message';
    }
    
    messageDiv.textContent = content;
    qaMessages.appendChild(messageDiv);
    
    // 스크롤 아래로
    qaMessages.scrollTop = qaMessages.scrollHeight;
    
    return messageDiv;
}

// 로딩 메시지 제거
function removeLoadingMessage() {
    const loadingMsg = document.getElementById('loading-message');
    if (loadingMsg) {
        loadingMsg.remove();
    }
}

// Q&A API 호출
async function askQuestion(question) {
    try {
        const response = await fetch(`${FASTAPI_BASE_URL}/qa/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: question,
                selected_text: selectedText || null,
                book_id: currentBook?.id || 'unknown',
                user_id: 'default_user'
            })
        });
        
        if (!response.ok) {
            throw new Error('답변을 가져올 수 없습니다.');
        }
        
        const data = await response.json();
        return data.answer;
        
    } catch (error) {
        console.error('Q&A 오류:', error);
        throw error;
    }
}

// Q&A 전송 버튼 이벤트
qaSendBtn.addEventListener('click', async () => {
    const question = qaInput.value.trim();
    
    if (!question) {
        alert('질문을 입력해주세요.');
        return;
    }

    // 서버에 저장된 책인지 확인 (Option 2: 서버 책만 Q&A 가능)
    if (!currentBook || !currentBook.id || bookType !== 'chunk') {
        addQAMessage('assistant', '⚠️ Q&A 기능은 서버에 저장된 책에서만 사용할 수 있습니다. "책 보기" 버튼으로 책을 선택해주세요.');
        qaInput.value = ''; // 입력창 초기화
        return;
    }
    
    // 1. 사용자 메시지 표시
    addQAMessage('user', question);
    
    // 2. 입력창 초기화
    qaInput.value = '';
    
    // 3. 로딩 표시
    addQAMessage('loading', '답변 생성 중...');
    
    try {
        // 4. API 호출
        const answer = await askQuestion(question);
        
        // 5. 로딩 제거 & 답변 표시
        removeLoadingMessage();
        addQAMessage('assistant', answer);
        
    } catch (error) {
        removeLoadingMessage();
        addQAMessage('assistant', '죄송합니다. 답변을 생성하는 중 오류가 발생했습니다.');
    }
});

// Enter 키 지원 (Shift+Enter는 줄바꿈)
qaInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        qaSendBtn.click();
    }
});

// ===== 책 목록 모달 =====

// "책 보기" 버튼 클릭
loadBookBtn.addEventListener('click', async () => {
    bookSelectModal.style.display = 'block';
    bookListDiv.innerHTML = '<p>로딩 중...</p>';
    
    try {
        const response = await fetch(`${FASTAPI_BASE_URL}/books/list`);
        const books = await response.json();
        
        if (books.length === 0) {
            bookListDiv.innerHTML = '<p>서버에 저장된 책이 없습니다.</p>';
            return;
        }
        
        bookListDiv.innerHTML = '';
        books.forEach(book => {
            const bookItem = document.createElement('div');
            bookItem.className = 'book-item';
            bookItem.innerHTML = `
                <h3>${book.title_ko}</h3>
                <p>저자: ${book.author} | 장르: ${book.genre || '미분류'}</p>
            `;
            bookItem.addEventListener('click', () => {
                selectBook(book.book_id, book.title_ko);
            });
            bookListDiv.appendChild(bookItem);
        });
        
    } catch (error) {
        console.error('책 목록 로드 실패:', error);
        bookListDiv.innerHTML = '<p>책 목록을 불러올 수 없습니다.</p>';
    }
});

// 모달 닫기
closeModalBtn.addEventListener('click', () => {
    bookSelectModal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === bookSelectModal) {
        bookSelectModal.style.display = 'none';
    }
});

// 책 선택
async function selectBook(bookId, bookTitle) {
    bookSelectModal.style.display = 'none';
    await loadBookFromServer(bookId, bookTitle);
}

// ===== 캐릭터 대화 기능 =====

// 캐릭터 목록 로드
async function loadAvailableCharacters() {
    // 로딩 상태 표시
    characterSelect.innerHTML = '<option value="">로딩 중...</option>';

    try {
        const response = await fetch(
            `${FASTAPI_BASE_URL}/character/available?book_id=1&current_page=${currentPage}`
        );
        
        if (!response.ok) throw new Error('캐릭터 목록 조회 실패');
        
        const data = await response.json();
        
        // 드롭다운 업데이트
        characterSelect.innerHTML = '<option value="">캐릭터 선택...</option>';
        
        data.characters.forEach(char => {
            const option = document.createElement('option');
            option.value = char.name;
            option.textContent = `${char.name} - ${char.role}`;
            characterSelect.appendChild(option);
        });
        
        console.log('✅ 캐릭터 목록 로드 완료:', data.characters.length + '명');
        
    } catch (error) {
        console.error('❌ 캐릭터 목록 로드 실패:', error);
    }
}

// 캐릭터와 대화 전송
async function sendCharacterMessage() {
    const characterName = characterSelect.value;
    const message = characterInput.value.trim();
    
    if (!characterName) {
        alert('대화할 캐릭터를 선택하세요.');
        return;
    }
    
    if (!message) {
        alert('메시지를 입력하세요.');
        return;
    }
    
    // 사용자 메시지 표시
    addCharacterMessage(message, 'user');
    characterInput.value = '';
    
    // 로딩 메시지
    const loadingMsg = addCharacterMessage('응답 생성 중...', 'loading');
    
    try {
        const response = await fetch(`${FASTAPI_BASE_URL}/character/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: 'default_user',
                book_id: 1,
                character_name: characterName,
                user_message: message,
                current_page: currentPage
            })
        });
        
        if (!response.ok) throw new Error('대화 전송 실패');
        
        const data = await response.json();
        
        // 로딩 메시지 제거
        loadingMsg.remove();
        
        // 캐릭터 응답 표시
        addCharacterMessage(data.response, 'assistant', characterName);
        
    } catch (error) {
        console.error('❌ 캐릭터 대화 오류:', error);
        loadingMsg.textContent = '오류가 발생했습니다.';
        loadingMsg.className = 'chat-message error';
    }
}

// 메시지 DOM에 추가
function addCharacterMessage(text, type, characterName = '') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`;
    
    if (type === 'assistant' && characterName) {
        messageDiv.innerHTML = `<strong>${characterName}:</strong><br>${text}`;
    } else {
        messageDiv.textContent = text;
    }
    
    characterMessages.appendChild(messageDiv);
    characterMessages.scrollTop = characterMessages.scrollHeight;
    
    return messageDiv;
}

// 캐릭터 선택 시 히스토리 로드
characterSelect.addEventListener('change', async () => {
    const characterName = characterSelect.value;
    
    if (!characterName) return;
    
    // 메시지 영역 초기화
    characterMessages.innerHTML = '';
    
    // 히스토리 로드
    await loadCharacterHistory(characterName);
});

// 캐릭터 대화 히스토리 로드
async function loadCharacterHistory(characterName) {
    try {
        const response = await fetch(
            `${FASTAPI_BASE_URL}/character/history?user_id=default_user&book_id=1&character_name=${encodeURIComponent(characterName)}`
        );
        
        if (!response.ok) throw new Error('히스토리 로드 실패');
        
        const data = await response.json();
        
        if (data.history.length === 0) {
            // 히스토리 없으면 안내 메시지
            characterMessages.innerHTML = `
                <div class="chat-placeholder">
                    <p>💬 ${characterName}와(과) 대화를 시작하세요!</p>
                </div>
            `;
            return;
        }
        
        // 히스토리 표시
        data.history.forEach(msg => {
            addCharacterMessage(msg.content, msg.role, msg.role === 'assistant' ? characterName : '');
        });
        
    } catch (error) {
        console.error('❌ 히스토리 로드 실패:', error);
    }
}

// 이벤트 리스너
characterSendBtn.addEventListener('click', sendCharacterMessage);

characterInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendCharacterMessage();
    }
});

// 대화 초기화 버튼
document.getElementById('clear-history-btn')?.addEventListener('click', async () => {
    const characterName = characterSelect.value;
    
    if (!characterName) {
        alert('캐릭터를 선택하세요.');
        return;
    }
    
    if (!confirm(`${characterName}와(과)의 대화 기록을 삭제할까요?`)) return;
    
    try {
        const response = await fetch(
            `${FASTAPI_BASE_URL}/character/history?user_id=default_user&book_id=1&character_name=${encodeURIComponent(characterName)}`,
            { method: 'DELETE' }
        );
        
        if (response.ok) {
            characterMessages.innerHTML = `
                <div class="chat-placeholder">
                    <p>💬 ${characterName}와(과) 대화를 시작하세요!</p>
                </div>
            `;
            console.log('✅ 대화 기록 삭제 완료');
        }
    } catch (error) {
        console.error('❌ 삭제 실패:', error);
    }
});
