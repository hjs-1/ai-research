import os
import time
import json
import ollama
import threading
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# =====================================================================
# [1. 환경 설정]
# INPUT_FOLDER: 센서 데이터(JSON)가 생성되는 폴더
# OUTPUT_FOLDER: AI 분석 결과(TXT)가 저장될 폴더
# =====================================================================
INPUT_FOLDER = r"C:\Users\HJS\Desktop\sensor_data\input"
OUTPUT_FOLDER = r"C:\Users\HJS\Desktop\sensor_data\output"

# =====================================================================
# [2. 작업 대기열(Queue) 생성]
# 파일이 동시에 여러 개 들어올 경우, 시스템(Watchdog)이 멈추지 않도록
# 감지된 파일 경로만 이 큐(Queue)에 임시로 차곡차곡 쌓아둠.
# =====================================================================
task_queue = Queue()

# =====================================================================
# [3. 파일 감시자 (Producer: 생산자)]
# 지정된 폴더(INPUT_FOLDER)에 변화가 생길 때마다 호출되는 클래스.
# =====================================================================
class SensorDataHandler(FileSystemEventHandler):
    def on_created(self, event):
        # 1. 디렉토리(폴더) 생성은 무시하고, 확장자가 '.json'인 파일만 처리.
        # 2. 파일 생성 이벤트가 발생하면 무거운 AI 분석을 여기서 직접 하지 않음.
        # 3. 대신 큐(task_queue)에 파일 경로만 쏙 밀어넣고 즉시 함수를 종료하여 병목을 방지.
        if not event.is_directory and event.src_path.endswith('.json'):
            print(f"[감지] 큐에 추가됨: {event.src_path}")
            task_queue.put(event.src_path)

# =====================================================================
# [4. 안전한 파일 읽기 도우미 함수]
# 파일이 생성되자마자(on_created 이벤트 직후) 읽으려고 하면,
# 센서가 아직 내용을 다 쓰지 않아 JSON 에러.
# 이를 방지하기 위해 최대 retries(5번) 만큼 재시도하며 안전하게 읽어오기.
# =====================================================================
def safe_read_json(filepath, retries=5, delay=1):
    """파일이 완전히 쓰일 때까지 기다렸다가 안전하게 읽어오는 함수"""
    for _ in range(retries):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (json.JSONDecodeError, PermissionError):
            # 파일이 다른 프로그램에 의해 잠겨있거나(PermissionError) 
            # 덜 써졌다면(JSONDecodeError) 지정된 시간(delay)만큼 잠시 대기합니다.
            time.sleep(delay)  
    return None # 5번 모두 실패하면 None을 반환하여 무한 루프를 방지합니다.

# =====================================================================
# [5. AI 분석 작업자 (Consumer: 소비자)]
# 메인 프로그램과 별도의 스레드(백그라운드)에서 쉼 없이 돌아가는 함수.
# 큐에 파일이 들어오면 하나씩 꺼내서 차례대로 Ollama 모델에 넘기기
# =====================================================================
def process_worker():
    """큐에서 작업을 꺼내어 순차적으로 AI 분석을 수행하는 백그라운드 스레드"""
    while True:
        # 1. 큐에서 파일 경로를 하나 오픈. (큐가 비어있으면 새 파일이 올 때까지 여기서 대기)
        filepath = task_queue.get() 
        if filepath is None: 
            break
            
        try:
            print(f"\n[분석 시작] {filepath}")
            
            # 2. 안전하게 센서 데이터 읽기 시도
            data = safe_read_json(filepath)
            if not data:
                print(f"[오류] 파일을 읽을 수 없습니다: {filepath}")
                task_queue.task_done() # 실패해도 큐에게 "이 작업은 끝났어"라고 꼭 알려줘야함
                continue

            # 3. JSON에서 필요한 값 추출 (값이 누락되었을 경우 '알 수 없음'으로 처리)
            temp = data.get("temperature", "알 수 없음")
            humidity = data.get("humidity", "알 수 없음")
            co2 = data.get("co2", "알 수 없음")

            # 4. AI에게 전달할 자연어(User Prompt) 구성
            user_prompt = f"현재 수집된 센서 데이터입니다: 온도 {temp}도, 습도 {humidity}%, 이산화탄소 {co2}ppm. 분석을 부탁합니다."

            # 5. Ollama 로컬 AI 추론 시작
            # (미리 만들어둔 'sensorai' 모델에 시스템 프롬프트가 각인되어 있다고 가정)
            response = ollama.chat(model='sensorai', messages=[
                {'role': 'user', 'content': user_prompt}
            ])
            
            # AI의 답변 텍스트만 추출
            result_text = response['message']['content']

            # 6. 분석 결과를 텍스트 파일로 저장
            filename = os.path.basename(filepath)
            result_filepath = os.path.join(OUTPUT_FOLDER, f"result_{filename}.txt")
            
            with open(result_filepath, 'w', encoding='utf-8') as result_file:
                result_file.write(result_text)
            
            print(f"[완료] 결과 저장됨: {result_filepath}")

        except Exception as e:
            # 예기치 않은 오류가 발생해도 전체 스레드가 죽지 않도록 예외 처리
            print(f"[오류 발생] 데이터 처리 중 문제: {e}")
        finally:
            # 성공하든 실패하든, 큐에게 "이 작업 1개 처리 완료했어"라고 반드시 보고
            task_queue.task_done() 

# =====================================================================
# [6. 메인 실행부]
# 폴더를 만들고, 작업자 스레드를 깨우고, 감시자를 실행하는 총괄 역할.
# =====================================================================
def main():
    # 1. 입력/출력 폴더가 없으면 자동으로 생성
    os.makedirs(INPUT_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # 2. 작업자(Worker) 스레드 가동
    # daemon=True: 사용자가 프로그램을 끄면 이 백그라운드 스레드도 함께 얌전히 종료되도록 설정
    worker_thread = threading.Thread(target=process_worker, daemon=True)
    worker_thread.start()

    # 3. 폴더 감시자(Observer) 설정
    event_handler = SensorDataHandler()
    observer = Observer()
    # recursive=False: 하위 폴더까지는 감시하지 않고 딱 지정한 INPUT_FOLDER 직속 파일만 감시
    observer.schedule(event_handler, INPUT_FOLDER, recursive=False)
    
    print(f"[{INPUT_FOLDER}] 폴더 감시 및 큐 시스템 가동 (종료: Ctrl+C)")
    
    # 4. 감시 시작
    observer.start()
    
    try:
        # 메인 스레드는 1초마다 쉬면서 무한 루프를 돌며 프로그램이 꺼지지 않게 유지
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # 사용자가 터미널에서 Ctrl+C를 누르면 안전하게 종료 절차를 진행
        print("\n시스템을 종료합니다...")
        observer.stop()
    
    # 감시자 프로세스가 완전히 종료될 때까지 기다렸다가 프로그램을 깔끔하게 종료
    observer.join()

if __name__ == "__main__":
    main()