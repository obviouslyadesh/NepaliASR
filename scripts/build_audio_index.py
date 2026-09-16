from pathlib import Path
import csv


# ============================================================
# CONFIGURATION
# ============================================================

# CHANGE THIS to the folder containing:
# asr_nepali_0, asr_nepali_1, ..., asr_nepali_15
DATA_ROOT = Path("/Users/adeshbohara/Desktop/NepaliASR/asr_nepali_data")

OUTPUT_FILE = Path("manifests/audio_index.csv")


# ============================================================
# FIND ALL AUDIO FILES
# ============================================================

def find_audio_files():

    audio_files = []

    # Look for folders such as:
    # asr_nepali_0
    # asr_nepali_1
    # ...
    # asr_nepali_15

    dataset_dirs = sorted(
        DATA_ROOT.glob("asr_nepali_*")
    )

    print(f"Dataset folders found: {len(dataset_dirs)}")
    print()

    for dataset_dir in dataset_dirs:

        print(f"Scanning: {dataset_dir.name}")

        # Search recursively for every FLAC file
        files = sorted(
            dataset_dir.rglob("*.flac")
        )

        print(
            f"  FLAC files found: {len(files)}"
        )

        audio_files.extend(files)

    return audio_files


# ============================================================
# BUILD AUDIO INDEX
# ============================================================

def build_index(audio_files):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        # CSV header
        writer.writerow([
            "file_id",
            "audio_path",
            "dataset",
            "shard"
        ])

        for audio_path in audio_files:

            # Example:
            # abc123.flac
            #
            # becomes:
            # abc123

            file_id = audio_path.stem

            # Find which asr_nepali_X folder
            # this file belongs to

            relative_path = audio_path.relative_to(
                DATA_ROOT
            )

            dataset = relative_path.parts[0]

            # Example:
            # asr_nepali_0/data/00/file.flac
            #
            # parts:
            # [0] asr_nepali_0
            # [1] data
            # [2] 00
            # [3] file.flac

            shard = relative_path.parts[2]

            writer.writerow([
                file_id,
                relative_path.as_posix(),
                dataset,
                shard
            ])


# ============================================================
# CHECK DUPLICATE FILE IDs
# ============================================================

def check_duplicates(audio_files):

    seen = {}
    duplicates = []

    for audio_path in audio_files:

        file_id = audio_path.stem

        if file_id in seen:

            duplicates.append({
                "file_id": file_id,
                "first": seen[file_id],
                "duplicate": audio_path
            })

        else:

            seen[file_id] = audio_path

    return duplicates


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("NEPALI ASR - AUDIO INDEXING")
    print("=" * 60)
    print()

    # Step 1: Find audio
    audio_files = find_audio_files()

    print()
    print("-" * 60)

    print(
        f"TOTAL FLAC FILES: {len(audio_files)}"
    )

    print("-" * 60)

    # Step 2: Check duplicate IDs
    duplicates = check_duplicates(
        audio_files
    )

    print(
        f"DUPLICATE FILE IDs: {len(duplicates)}"
    )

    # Show examples if duplicates exist
    if duplicates:

        print()
        print("First 10 duplicates:")

        for item in duplicates[:10]:

            print(
                f"{item['file_id']}:"
            )

            print(
                f"  First:     {item['first']}"
            )

            print(
                f"  Duplicate: {item['duplicate']}"
            )

    # Step 3: Create CSV
    build_index(audio_files)

    print()
    print(
        f"INDEX CREATED: {OUTPUT_FILE}"
    )

    print()
    print("Done!")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()