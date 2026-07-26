# 딥러닝 연구 & Git/GitHub 개발 환경 치트시트

Dev Container 기반의 PyTorch/CUDA 연구 환경 설정부터 Git/GitHub 연동, 주요 명령어 및 에러 해결 가이드입니다.

---

## 1. 필수 VS Code 단축키

| 단축키 | 기능 설명 |
| :--- | :--- |
| `Ctrl` +  ` | **터미널 열기 / 닫기** |
| `F1` 또는 `Ctrl` + `Shift` + `P` | **명령 팔레트 열기** (`Reopen in Container` 검색) | 컨테이너 리빌드나 오픈등
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
   * 이때 커밋 메시지를 적지 않았다면 COMMIT_EDITMSG 창이 열림 적고싶은 내용 적고 저장후 창닫기.

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

# 개발 시스템 구조
[ 3층: Dev Container ]  <-- PyTorch 2.6, CUDA Nightly, 개발 라이브러리들
         │ (VS Code가 devcontainer.json을 읽고 여기에 직접 접속)
         ▼
[ 2층: Docker Engine ]  <-- Docker 데몬 (컨테이너 생성/관리)
         │ (WSL2 내부 자원 및 NVIDIA GPU 드라이버를 컨테이너로 통과시킴)
         ▼
[ 1층: WSL2 (Ubuntu) ] <-- 내 진짜 가상 OS (~/ai-research 폴더, SSH 키 위치)
         │ (Windows 커널 위에서 돌아가는 진짜 리눅스 지반)
         ▼
[ 0층: Windows 11 ]    <-- 그래픽카드 드라이버(NVIDIA Driver) 제공

한눈에 보는 실행 흐름 예시
VS Code에서 code ~/ai-research를 칩니다. -> VS Code가 WSL2 Ubuntu에 접속함

.devcontainer/devcontainer.json을 발견합니다. -> "아, 컨테이너 안으로 들어가라는 지시서구나!"

VS Code가 WSL2 내부의 Docker Engine에 명령을 내려 컨테이너를 실행시킵니다.

WSL2의 ~/ai-research 폴더를 컨테이너의 /workspaces/ai-research에 마운트합니다.

VS Code의 에디터와 터미널 작업 위치가 3층 컨테이너 내부로 이동합니다.


---

# 🚀 딥러닝 개발 환경 구축 가이드 (WSL2 + Dev Container + RTX 5070 Ti)

## 1. 기본 아키텍처 이해

본 환경은 호스트 PC를 깨끗하게 유지하기 위해 WSL2(Ubuntu)를 지반으로 삼고, 프로젝트마다 Docker(Dev Container)를 독립된 방으로 띄워서 작업하는 구조를 가집니다.

* **1층 (WSL2 Ubuntu):** 프로젝트 폴더와 소스코드 보관, 호스트 GPU 드라이버 제공
* **2층 (Docker Engine):** 컨테이너 관리 및 GPU 자원 할당
* **3층 (Dev Container):** PyTorch 등 실제 라이브러리가 설치되는 일회성 격리 공간 (VS Code로 직접 접속)

---

## 2. 프로젝트 초기 세팅 및 실행 순서

### Step 1. 프로젝트 폴더 생성 및 VS Code 실행

WSL 환경(Ubuntu)에서 터미널을 열고 새 프로젝트 폴더를 만든 뒤 VS Code를 실행합니다.

```bash
mkdir ~/ai-research
cd ~/ai-research
code .

```

### Step 2. Dev Container 설정 및 접속

1. VS Code에서 `F1` 키를 누르고 **`Dev Containers: Add Dev Container Configuration Files...`** 를 선택하여 Python/PyTorch 템플릿을 생성합니다.
2. 폴더 내에 `.devcontainer/devcontainer.json` 파일이 생성되면, 우측 하단 팝업이나 `F1` 키를 눌러 `Reopen in Container`를 실행합니다.
3. VS Code 창이 새로고침되며 좌측 하단에 `Dev Container` 마크가 뜨면 성공적으로 컨테이너 내부에 접속된 것입니다.

> ⚠️ **주의사항 (권한 꼬임 방지):**
> 컨테이너 안에서(`root` 계정) 만든 파일은 외부 WSL(`hjs` 계정)에서 수정하거나 삭제하려고 하면 `Permission denied` 에러가 발생합니다. **파일 생성, 이름 변경, Git 커밋, 파이썬 실행 등 모든 작업은 반드시 "컨테이너 내부에 접속한 상태(VS Code)"에서 진행해야 합니다.**

---

## 3. RTX 5070 Ti (Blackwell 아키텍처) PyTorch 호환성 해결

최신 RTX 50시리즈(아키텍처 `sm_120`)는 구형 PyTorch 버전에서 `CUDA error: no kernel image is available...` 에러를 발생시킵니다. 이를 해결하려면 **최신 Nightly(개발자 빌드) 버전**을 설치해야 합니다.

### Step 1. 기존 설치된 PyTorch 제거

컨테이너 내부 VS Code 터미널에서 아래 명령어를 실행합니다.

```bash
pip uninstall -y torch torchvision torchaudio

```

### Step 2. PyTorch Nightly 버전(CUDA 12.8 이상 호환) 설치

```bash
pip install --no-cache-dir --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

```

*(※ 설치 시 `cu128`로 지정해도 서버에서 50시리즈 최적화 빌드인 `cu130` 등으로 자동 연결되어 설치될 수 있으며, 이는 정상입니다.)*

### Step 3. GPU 연산 정상 작동 테스트

터미널에서 아래 명령어를 한 줄로 입력하여 에러 없이 결과가 출력되는지 확인합니다.

```bash
python -c "import torch; print('GPU:', torch.cuda.get_device_name(0)); print('Test:', torch.randn(2,2, device='cuda'))"

```

---

#### 4. (꿀팁) devcontainer.json 자동화 세팅

나중에 컨테이너를 삭제하고 리빌드(`Rebuild Container`) 하더라도, 방금 설정한 PyTorch Nightly 버전과 필수 라이브러리들이 **자동으로 재설치**되도록 `.devcontainer/devcontainer.json`의 맨 아래에 다음 구문을 추가해 둡니다.

```json
{
    "name": "PyTorch GPU Environment",
    "image": "pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel",
    "runArgs": [
        "--gpus", "all",
        "--ipc=host"
    ],
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "ms-toolsai.jupyter"
            ]
        }
    },
    // 리빌드 시 아래 명령어가 자동 실행되어 최적의 환경을 즉시 복구함
    "postCreateCommand": "pip uninstall -y torch torchvision torchaudio && pip install --no-cache-dir --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128 && pip install matplotlib wandb pandas scikit-learn"
}
##### 5. 해야할것들

1단계: PyTorch 기초 및 텐서 조작법 익히기 (현재 단계 바로 다음)
모델을 구현하기 전, 파이토치가 데이터를 어떻게 다루고 연산하는지 손에 익혀야 합니다.

학습 내용:

Tensor 생성, 차원 변환(reshape, permute, transpose), 브로드캐스팅(Broadcasting)

Autograd(자동 미분)의 동작 원리 이해

간단한 선형 회귀(Linear Regression) 모델을 torch.nn 없이 순수 텐서 연산으로 구현해보기

2단계: 신경망 기본 구조(MLP, CNN, RNN) 실습
03번 폴더명(03_MLP_CNN_RNN_etc.)과 연계하여 기초 신경망들을 직접 코딩하고 돌려봅니다.

학습 내용:

MLP (다층 퍼셉트론): MNIST 같은 손글씨 데이터셋을 이용해 가장 기본적인 분류 모델 학습시키기

CNN (합성곱 신경망): 이미지 특성을 추출하는 원리를 이해하고 이미지 분류 모델 구축하기

RNN / Transformer 기초: 시계열 데이터나 텍스트를 다루는 모델의 기본 구조 맛보기

3단계: 논문 구현 및 미니 프로젝트 (학부생 논문 준비의 초석)
단순 예제 코드를 넘어, 유명한 딥러닝 논문(예: ResNet, Transformer 등)의 핵심 구조를 코드로 직접 구현(Reproduction)해 봅니다.

목표:

깃허브(GitHub)에 내 코드를 깔끔하게 커밋하고 문서화(Markdown)하는 습관 들이기

작은 아이디어를 더하거나 데이터셋을 바꿔보며 실험(Experiment)을 설계하는 감각

##논문 적용시 주의
대부분의 논문은 우리가 쓴 것 같은 .devcontainer.json 파일 같은 걸 따로 친절하게 주지 않는다. (물론 아주 가끔 깃허브 공식 구현체에 도커 파일이 포함된 경우도 있긴함)

대부분의 논문 오픈소스(GitHub)에 들어가 보면 환경 설정 파일은 보통 아래와 같은 식으로 구성.

1. 논문들이 환경을 알려주는 방식 (보통 주는 파일들)
requirements.txt: 파이썬 패키지 목록과 버전이 적힌 텍스트 파일 (예: torch==2.1.0, transformers==4.30.0 등)

environment.yaml: 아나콘다(Conda)를 쓸 때 필요한 가상환경 설정 파일

README.md: "이 모델을 돌리려면 어떤 명령어들을 순서대로 쳐야 하는지" 설명서 역할 (여기에 보통 설치법이 적혀 있음)

2. 논문 속 환경과 내 환경(RTX 5070 Ti + 최신 PyTorch)이 다를 때 대처법
논문이 발표된 지 몇 년 지났거나, 구버전 PyTorch(예: PyTorch 1.x 또는 2.0 등)를 기준으로 쓰인 논문이라면 내 최신 환경에서 그대로 실행했을 때 에러가 날 수 있습니다. 이럴 때는 다음 2가지 전략 중 하나 사용.

① 최신 버전으로 마이그레이션하며 돌리기 (추천)
일단 논문의 requirements.txt에 적힌 패키지들을 내 Dev Container 안에 설치.

코드를 실행했을 때 Deprecated(지원 중단)된 함수나 문법 에러가 나면, 최신 PyTorch 문법에 맞게 코드를 직접 수정(Refactoring)하면서 공부.
어차피 논문을 구현하고 내 것으로 만드는 과정 자체가 코드를 뜯어보는 것

② 도커 이미지를 다르게 파서 완벽히 맞추기
만약 논문이 특정 구형 CUDA 버전(예: CUDA 11.8 등)을 강하게 타서 도저히 최신 버전으로 안 돌아간다면?

.devcontainer/devcontainer.json에서 "image": "nvidia/cuda:11.8.0-devel-ubuntu22.04" 이런 식으로 논문이 요구하는 베이스 이미지로만 살짝 바꿔서 프로젝트별로 방을 따로 파기

학부생 논문 구현 시 팁
나중에 본격적으로 논문 구현을 하실 때, 깃허브 코드를 가져와서 내 컨테이너에 세팅하는 표준적인 루틴.

새 프로젝트 폴더를 만들고 내 방식대로 .devcontainer 세팅을 켠다.

깃허브에서 논문 코드를 클론(git clone)한다.

README.md를 열어서 저자가 추천하는 설치 명령어(pip install -r requirements.txt 등)를 터미널에 입력해 본다.

버전 충돌이 나거나 내 그래픽카드(sm_120) 이슈가 생기면, 우리가 앞서 배운 지식을 바탕으로 패키지 버전을 유연하게 조절해가며 실행시킨다.