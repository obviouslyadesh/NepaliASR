from pathlib import Path
import csv
import statistics
import soundfile as sf


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Day 2 manifest
MANIFEST_PATH = PROJECT_ROOT / "manifests" / "all.csv"

# Day 3 output
REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_PATH = REPORT_DIR / "audio_validation.csv"

# Expected audio properties
EXPECTED_SAMPLE_RATE = 16000
EXPECTED_CHANNELS = 1

# Sanity-check duratigiton limits
MIN_DURATION = 0.1
MAX_DURATION = 30.0


# ============================================================
# SETUP
# ============================================================

REPORT_DIR.mkdir(parents=True, exist_ok=True)

if not MANIFEST_PATH.exists():
    raise FileNotFoundError(
        f"\nManifest not found:\n{MANIFEST_PATH}\n"
    )


# ============================================================
# COUNTERS
# ============================================================

total_records = 0
files_checked = 0

missing_files = 0
unreadable_files = 0
invalid_sample_rate = 0
invalid_channels = 0
invalid_duration = 0

valid_files = 0

durations = []

report_rows = []


# ============================================================
# START
# ============================================================

print("=" * 60)
print("NEPALI ASR - AUDIO VALIDATION")
print("=" * 60)

print(f"\nProject root:          {PROJECT_ROOT}")
print(f"Manifest:              {MANIFEST_PATH}")
print(f"Expected sample rate:  {EXPECTED_SAMPLE_RATE} Hz")
print(f"Expected channels:     {EXPECTED_CHANNELS}")
print(
    f"Duration range:        "
    f"{MIN_DURATION}s - {MAX_DURATION}s"
)
print()


# ============================================================
# READ MANIFEST
# ============================================================

with open(
    MANIFEST_PATH,
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(f)

    if reader.fieldnames is None:
        raise ValueError("Manifest has no header row.")

    print("Manifest columns:")
    print(", ".join(reader.fieldnames))
    print()

    # We need the audio_path column.
    if "audio_path" not in reader.fieldnames:
        raise ValueError(
            "\nCould not find 'audio_path' column in all.csv.\n"
            f"Found columns: {reader.fieldnames}\n"
        )

    for row in reader:

        total_records += 1

        # ----------------------------------------------------
        # READ FIELDS
        # ----------------------------------------------------

        utterance_id = row.get("utterance_id", "")
        speaker_id = row.get("speaker_id", "")
        audio_path_string = row.get("audio_path", "")
        
        # ----------------------------------------------------
        # CHECK EMPTY AUDIO PATH
        # ----------------------------------------------------

        if not audio_path_string.strip():

            missing_files += 1

            report_rows.append({
                "utterance_id": utterance_id,
                "speaker_id": speaker_id,
                "audio_path": "",
                "sample_rate": "",
                "channels": "",
                "frames": "",
                "duration_seconds": "",
                "status": "missing",
                "error": "Empty audio_path",
            })

            continue

        audio_path = Path(audio_path_string)

        # ----------------------------------------------------
        # RESOLVE RELATIVE PATH
        # ----------------------------------------------------
        


        if not audio_path.is_absolute():
            audio_path = PROJECT_ROOT /"asr_nepali_data" / audio_path

        # ----------------------------------------------------
        # CHECK FILE EXISTS
        # ----------------------------------------------------

        if not audio_path.exists():

            missing_files += 1

            report_rows.append({
                "utterance_id": utterance_id,
                "speaker_id": speaker_id,
                "audio_path": str(audio_path),
                "sample_rate": "",
                "channels": "",
                "frames": "",
                "duration_seconds": "",
                "status": "missing",
                "error": "File does not exist",
            })

            continue

        files_checked += 1

        # ----------------------------------------------------
        # READ AUDIO INFORMATION
        # ----------------------------------------------------

        try:

            info = sf.info(str(audio_path))

            sample_rate = info.samplerate
            channels = info.channels
            frames = info.frames
            duration = info.duration

        except Exception as e:

            unreadable_files += 1

            report_rows.append({
                "utterance_id": utterance_id,
                "speaker_id": speaker_id,
                "audio_path": str(audio_path),
                "sample_rate": "",
                "channels": "",
                "frames": "",
                "duration_seconds": "",
                "status": "unreadable",
                "error": str(e),
            })

            continue

        # ----------------------------------------------------
        # SAMPLE RATE CHECK
        # ----------------------------------------------------

        sample_rate_valid = (
            sample_rate == EXPECTED_SAMPLE_RATE
        )

        if not sample_rate_valid:
            invalid_sample_rate += 1

        # ----------------------------------------------------
        # CHANNEL CHECK
        # ----------------------------------------------------

        channels_valid = (
            channels == EXPECTED_CHANNELS
        )

        if not channels_valid:
            invalid_channels += 1

        # ----------------------------------------------------
        # DURATION CHECK
        # ----------------------------------------------------

        duration_valid = (
            MIN_DURATION <= duration <= MAX_DURATION
        )

        if not duration_valid:
            invalid_duration += 1

        durations.append(duration)

        # ----------------------------------------------------
        # DETERMINE OVERALL STATUS
        # ----------------------------------------------------

        if (
            sample_rate_valid
            and channels_valid
            and duration_valid
        ):

            status = "valid"
            error = ""
            valid_files += 1

        else:

            status = "invalid"

            errors = []

            if not sample_rate_valid:
                errors.append(
                    f"sample_rate={sample_rate}"
                )

            if not channels_valid:
                errors.append(
                    f"channels={channels}"
                )

            if not duration_valid:
                errors.append(
                    f"duration={duration:.3f}s"
                )

            error = "; ".join(errors)

        # ----------------------------------------------------
        # STORE RESULT
        # ----------------------------------------------------

        report_rows.append({
            "utterance_id": utterance_id,
            "speaker_id": speaker_id,
            "audio_path": str(audio_path),
            "sample_rate": sample_rate,
            "channels": channels,
            "frames": frames,
            "duration_seconds": round(duration, 6),
            "status": status,
            "error": error,
        })

        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        if total_records % 5000 == 0:

            print(
                f"Checked {total_records:,} records..."
            )


# ============================================================
# WRITE VALIDATION REPORT
# ============================================================

fieldnames = [
    "utterance_id",
    "speaker_id",
    "audio_path",
    "sample_rate",
    "channels",
    "frames",
    "duration_seconds",
    "status",
    "error",
]

with open(
    REPORT_PATH,
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(report_rows)


# ============================================================
# DURATION STATISTICS
# ============================================================

if durations:

    total_duration = sum(durations)

    mean_duration = statistics.mean(durations)

    median_duration = statistics.median(durations)

    minimum_duration = min(durations)

    maximum_duration = max(durations)

else:

    total_duration = 0
    mean_duration = 0
    median_duration = 0
    minimum_duration = 0
    maximum_duration = 0


total_hours = total_duration / 3600


# ============================================================
# FINAL REPORT
# ============================================================

print()
print("=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)

print()
print(f"Manifest records:       {total_records:,}")
print(f"Files checked:          {files_checked:,}")

print()
print(f"Missing files:          {missing_files:,}")
print(f"Unreadable files:      {unreadable_files:,}")
print(f"Invalid sample rate:    {invalid_sample_rate:,}")
print(f"Invalid channels:       {invalid_channels:,}")
print(f"Invalid duration:       {invalid_duration:,}")

print()
print(f"Valid audio:            {valid_files:,}")

print()
print("-" * 60)
print("DURATION STATISTICS")
print("-" * 60)

print()
print(f"Total duration:         {total_hours:,.2f} hours")
print(f"Mean duration:          {mean_duration:.3f} seconds")
print(f"Median duration:        {median_duration:.3f} seconds")
print(f"Minimum duration:       {minimum_duration:.3f} seconds")
print(f"Maximum duration:       {maximum_duration:.3f} seconds")

print()
print("-" * 60)
print("REPORT")
print("-" * 60)

print()
print(REPORT_PATH)

print()
print("=" * 60)


# ============================================================
# FINAL STATUS
# ============================================================

if (
    missing_files == 0
    and unreadable_files == 0
    and invalid_sample_rate == 0
    and invalid_channels == 0
    and invalid_duration == 0
):

    print("✓ AUDIO VALIDATION PASSED")
    print("✓ All manifest audio files are valid")

else:

    print("⚠ AUDIO VALIDATION FOUND ISSUES")
    print("Review the validation report:")
    print(REPORT_PATH)

print("=" * 60)