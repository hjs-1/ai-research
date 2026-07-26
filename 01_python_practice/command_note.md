# 딥러닝 연구 & Git/GitHub 개발 환경 치트시트

Dev Container 기반의 PyTorch/CUDA 연구 환경 설정부터 Git/GitHub 연동, 주요 명령어 및 에러 해결 가이드입니다.

---

## 1. 필수 VS Code 단축키

| 단축키 | 기능 설명 |
| :--- | :--- |
| `Ctrl` +  ` | **터미널 열기 / 닫기** |
| `F1` 또는 `Ctrl` + `Shift` + `P` | **명령 팔레트 열기** (`Reopen in Container` 검색) |
| `Ctrl` + `Shift` + `G` | **소스 제어(Git 가지 아이콘) 탭으로 이동** |
| `Ctrl` + `S` | **현재 파일 저장** (탭 옆 흰색 점 `●` 유무로 저장 상태 확인) |
| `Shift` + `Enter` | **Jupyter Notebook(`.ipynb`)에서 셀 실행 후 다음 셀 이동** |

---

## 2. 매일 쓰는 딥러닝 연구 루틴

1. **프로젝트 실행:** VS Code 열기 $\rightarrow$ `File` $\rightarrow$ `Open Recent` $\rightarrow$ `ai-research [Dev Container]` 선택.
2. **코드 및 실험 작성:** Jupyter Notebook(`.ipynb`) 또는 파이썬 스크립트(`.py`) 작업 진행.
3. **결과 저장 (Git/GitHub):**
   * VS Code 소스 제어 탭에서 **Message 작성** 후 `Commit & Push` 버튼 클릭.
   * 또는 터미널에서 `git add .` $\rightarrow$ `git commit -m "설명"` $\rightarrow$ `git push` 실행.

---

## 3. PyTorch & GPU 검증 명령어

컨테이너 내부 터미널에서 GPU와 PyTorch 연동 상태를 확인합니다.

```bash
# 1. GPU 하드웨어 상태 및 드라이버/전력/온도 확인
nvidia-smi

# 2. PyTorch CUDA GPU 인식 여부 확인
python -c "import torch; print('CUDA 사용 가능:', torch.cuda.is_available()); print('GPU 모델:', torch.cuda.get_device_name(0))"

# 딥러닝 연구 & Git/GitHub 개발 환경 치트시트

Dev Container 기반의 PyTorch/CUDA 연구 환경 설정부터 Git/GitHub 연동, 주요 명령어 및 에러 해결 가이드입니다.

---

# VS Code 터미널 기반 Git & GitHub 관련

VS Code 내부 터미널(`Ctrl` + `` ` ``)에서 실행하는 Git 명령어의 기본 워크플로우부터 브랜치 관리, 실수 복구(Undo), VS Code 연동 참고 노트

---

## 1. Git 기본 워크플로우 (상태 확인 ~ 업로드)
개발 작업 시 가장 자주 사용하는 기본 5단계 흐름

```bash
# 1. 현재 파일들의 상태 확인 (수정된 파일, 트래킹 안 되는 파일 등)
git status

# 2. 특정 파일 또는 전체 파일 스테이징 (업로드 대상 등록)
git add .                    # 변경된 모든 파일 등록
git add src/main.py          # 특정 파일만 등록

# 3. 스테이징 상태 취소 (잘못 add했을 때)
git restore --staged <파일경로>

# 4. 저장점(Commit) 만들기
git commit -m "feat: add model training script"

# 5. 원격 저장소(GitHub)로 업로드
git push origin main         # origin 원격 저장소의 main 브랜치로 푸시
