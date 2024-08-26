import torch
print(f"PyTorch version: {torch.__version__}")
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"Device Name: {torch.cuda.get_device_name(0)}")
