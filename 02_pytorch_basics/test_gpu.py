import torch

def main():
    print(f"PyTorch Version: {torch.__version__}")

    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"GPU is available! Using: {torch.cuda.get_device_name(0)}")

        # 간단한 텐서 연산 테스트
        x = torch.randn(10000, 10000, device=device)
        y = torch.randn(10000, 10000, device=device)
        z = torch.matmul(x, y)
        print("Matrix multiplication on GPU successful!")
    else:
        print("CUDA is not available. Check your Docker/WSL settings.")

if __name__ == "__main__":
    main()