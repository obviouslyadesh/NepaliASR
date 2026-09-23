import torch
import torchaudio


print("========== PYTORCH VALIDATION ==========")

# Check PyTorch
print("PyTorch version:", torch.__version__)

# Check torchaudio
print("Torchaudio version:", torchaudio.__version__)


# ------------------------------------------------------------
# Basic tensor test
# ------------------------------------------------------------

x = torch.tensor([1.0, 2.0, 3.0])
y = x * 2

print("\nTensor test:")
print("Input: ", x)
print("Output:", y)


# ------------------------------------------------------------
# FFT test
# ------------------------------------------------------------

test_signal = torch.randn(400)

fft_result = torch.fft.rfft(test_signal)

print("\nFFT test:")
print("Input shape:", test_signal.shape)
print("FFT shape:", fft_result.shape)


# ------------------------------------------------------------
# Hann window test
# ------------------------------------------------------------

window = torch.hann_window(400)

print("\nHann window test:")
print("Window shape:", window.shape)


# ------------------------------------------------------------
# Final result
# ------------------------------------------------------------

print("\n========== RESULT ==========")

if (
    torch.__version__.startswith("2.11")
    and torchaudio.__version__.startswith("2.11")
    and fft_result.shape[0] == 201
    and window.shape[0] == 400
):
    print("✓ PYTORCH VALIDATION PASSED")
else:
    print("⚠ CHECK PYTORCH INSTALLATION")