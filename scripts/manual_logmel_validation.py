import torch
import torchaudio


# ============================================================
# 1. Load one real Nepali FLAC file
# ============================================================

audio_path = (
    "asr_nepali_data/asr_nepali_3/data/4a/4aa1fdca33.flac"
)

waveform, sample_rate = torchaudio.load(audio_path)

# Convert [1, samples] -> [samples]
waveform = waveform.squeeze(0)

print("========== AUDIO ==========")
print("Waveform shape:", waveform.shape)
print("Sample rate:", sample_rate)

duration = waveform.shape[0] / sample_rate
print("Duration:", duration, "seconds")


# ============================================================
# 2. Parameters
# ============================================================

win_length = 400       # 25 ms
hop_length = 160       # 10 ms
n_fft = 400
n_mels = 80
f_min = 0.0
f_max = 8000.0


# ============================================================
# 3. MANUAL PIPELINE
# ============================================================

print("\n========== MANUAL PIPELINE ==========")


# ------------------------------------------------------------
# A. Framing
# ------------------------------------------------------------

frames = waveform.unfold(
    dimension=0,
    size=win_length,
    step=hop_length,
)

print("Frames shape:", frames.shape)


# ------------------------------------------------------------
# B. Hann window
# ------------------------------------------------------------

window = torch.hann_window(win_length)

windowed_frames = frames * window

print("Windowed frames shape:", windowed_frames.shape)


# ------------------------------------------------------------
# C. FFT
# ------------------------------------------------------------

spectrum = torch.fft.rfft(
    windowed_frames,
    n=n_fft,
    dim=-1,
)

print("Spectrum shape:", spectrum.shape)


# ------------------------------------------------------------
# D. Power spectrum
# ------------------------------------------------------------

power = spectrum.abs().pow(2)

print("Power spectrum shape:", power.shape)


# ------------------------------------------------------------
# E. Mel filterbank
# ------------------------------------------------------------

def hz_to_mel(hz):
    return 2595.0 * torch.log10(
        1.0 + hz / 700.0
    )


def mel_to_hz(mel):
    return 700.0 * (
        10.0 ** (mel / 2595.0) - 1.0
    )


mel_min = hz_to_mel(torch.tensor(f_min))
mel_max = hz_to_mel(torch.tensor(f_max))

mel_points = torch.linspace(
    mel_min,
    mel_max,
    n_mels + 2,
)

hz_points = mel_to_hz(mel_points)

freqs = torch.linspace(
    0.0,
    sample_rate / 2,
    n_fft // 2 + 1,
)

filterbank = torch.zeros(
    n_mels,
    n_fft // 2 + 1,
)

for m in range(1, n_mels + 1):

    left = hz_points[m - 1]
    center = hz_points[m]
    right = hz_points[m + 1]

    left_slope = (
        freqs - left
    ) / (center - left)

    right_slope = (
        right - freqs
    ) / (right - center)

    filterbank[m - 1] = torch.maximum(
        torch.zeros_like(freqs),
        torch.minimum(
            left_slope,
            right_slope,
        ),
    )


print("Mel filterbank shape:", filterbank.shape)


# ------------------------------------------------------------
# F. Apply Mel filterbank
# ------------------------------------------------------------

# [time, frequency] @ [frequency, mel]
# [418, 201] @ [201, 80]
# = [418, 80]

manual_mel = power @ filterbank.T

print("Manual Mel shape:", manual_mel.shape)


# ------------------------------------------------------------
# G. Log
# ------------------------------------------------------------

manual_log_mel = torch.log(
    manual_mel + 1e-10
)

print(
    "Manual Log-Mel shape:",
    manual_log_mel.shape,
)


# ============================================================
# 4. TORCHAUDIO REFERENCE
# ============================================================

print("\n========== TORCHAUDIO REFERENCE ==========")

mel_transform = torchaudio.transforms.MelSpectrogram(
    sample_rate=sample_rate,
    n_fft=n_fft,
    win_length=win_length,
    hop_length=hop_length,
    f_min=f_min,
    f_max=f_max,
    n_mels=n_mels,
    window_fn=torch.hann_window,
    power=2.0,
    center=False,
)

torchaudio_mel = mel_transform(
    waveform.unsqueeze(0)
)

torchaudio_log_mel = torch.log(
    torchaudio_mel + 1e-10
)


# Torchaudio:
# [1, 80, 418]
#
# Remove channel:
# [80, 418]
#
# Transpose:
# [418, 80]

torchaudio_log_mel = (
    torchaudio_log_mel
    .squeeze(0)
    .transpose(0, 1)
)

print(
    "Torchaudio Log-Mel shape:",
    torchaudio_log_mel.shape,
)


# ============================================================
# 5. COMPARE
# ============================================================

print("\n========== COMPARISON ==========")

print("Manual shape:", manual_log_mel.shape)
print("Torchaudio shape:", torchaudio_log_mel.shape)


difference = (
    manual_log_mel - torchaudio_log_mel
).abs()

max_diff = difference.max().item()
mean_diff = difference.mean().item()

print(
    "Maximum absolute difference:",
    max_diff,
)

print(
    "Mean absolute difference:",
    mean_diff,
)


# ============================================================
# 6. First 10 values
# ============================================================

print("\nFirst 10 values of first frame:")

print("\nManual:")
print(manual_log_mel[0, :10])

print("\nTorchaudio:")
print(torchaudio_log_mel[0, :10])

print("\nDifference:")
print(difference[0, :10])


# ============================================================
# 7. Final result
# ============================================================

print("\n========== FINAL RESULT ==========")

if max_diff < 1e-4:
    print("✓ VALIDATION PASSED")
    print("Manual implementation matches torchaudio.")

elif max_diff < 1e-2:
    print("✓ VERY CLOSE")
    print("Small numerical/convention differences exist.")

else:
    print("⚠ DIFFERENCE IS LARGER THAN EXPECTED")
    print("Inspect the Mel filterbank/conventions.")