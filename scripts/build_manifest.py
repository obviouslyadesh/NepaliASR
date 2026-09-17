from pathlib import Path
import csv


# ============================================================
# CONFIGURATION
# ============================================================

DATA_ROOT = Path("asr_nepali_data")

AUDIO_INDEX = Path(
    "manifests/audio_index.csv"
)

OUTPUT_FILE = Path(
    "manifests/all.csv"
)


# ============================================================
# LOAD AUDIO INDEX
# ============================================================

def load_audio_index():

    audio_index = {}

    with AUDIO_INDEX.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            file_id = row["file_id"]

            audio_index[file_id] = {
                "audio_path": row["audio_path"],
                "dataset": row["dataset"],
                "shard": row["shard"]
            }

    return audio_index


# ============================================================
# FIND METADATA FILES
# ============================================================

def find_metadata_files():

    metadata_files = sorted(
        DATA_ROOT.glob(
            "asr_nepali_*/utt_spk_text.tsv"
        )
    )

    return metadata_files


# ============================================================
# PARSE TSV FILES
# ============================================================

def parse_metadata(metadata_files):

    records = []

    malformed_rows = []

    for metadata_file in metadata_files:

        dataset = metadata_file.parent.name

        print(
            f"Reading metadata: {dataset}"
        )

        with metadata_file.open(
            "r",
            encoding="utf-8"
        ) as f:

            reader = csv.reader(
                f,
                delimiter="\t"
            )

            for line_number, row in enumerate(
                reader,
                start=1
            ):

                if len(row) != 3:

                    malformed_rows.append({
                        "file": str(metadata_file),
                        "line": line_number,
                        "columns": len(row)
                    })

                    continue

                file_id = row[0].strip()
                speaker_id = row[1].strip()
                transcript = row[2].strip()

                records.append({
                    "file_id": file_id,
                    "speaker_id": speaker_id,
                    "transcript": transcript,
                    "dataset": dataset
                })

    return records, malformed_rows


# ============================================================
# DUPLICATE CHECK
# ============================================================

def find_duplicate_metadata_ids(records):

    seen = set()
    duplicates = set()

    for record in records:

        file_id = record["file_id"]

        if file_id in seen:

            duplicates.add(file_id)

        else:

            seen.add(file_id)

    return duplicates


# ============================================================
# MATCH METADATA WITH AUDIO
# ============================================================

def create_manifest(
    records,
    audio_index
):

    matched = []
    missing_audio = []

    for record in records:

        file_id = record["file_id"]

        audio_info = audio_index.get(
            file_id
        )

        if audio_info is None:

            missing_audio.append(
                record
            )

            continue

        matched.append({
            "utterance_id": file_id,
            "speaker_id": record["speaker_id"],
            "audio_path": audio_info["audio_path"],
            "transcript": record["transcript"]
        })

    return matched, missing_audio


# ============================================================
# WRITE MASTER MANIFEST
# ============================================================

def write_manifest(records):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "utterance_id",
                "speaker_id",
                "audio_path",
                "transcript"
            ]
        )

        writer.writeheader()

        writer.writerows(records)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("NEPALI ASR - BUILD MASTER MANIFEST")
    print("=" * 60)
    print()

    # 1. Load audio index
    audio_index = load_audio_index()

    print(
        f"Audio index records: {len(audio_index)}"
    )

    print()

    # 2. Find TSV files
    metadata_files = find_metadata_files()

    print(
        f"Metadata files found: {len(metadata_files)}"
    )

    print()

    # 3. Parse metadata
    records, malformed_rows = parse_metadata(
        metadata_files
    )

    print()

    print(
        f"Metadata records: {len(records)}"
    )

    print(
        f"Malformed rows: {len(malformed_rows)}"
    )

    # 4. Duplicate check
    duplicate_ids = find_duplicate_metadata_ids(
        records
    )

    print(
        f"Duplicate metadata IDs: "
        f"{len(duplicate_ids)}"
    )

    # 5. Match audio
    matched, missing_audio = create_manifest(
        records,
        audio_index
    )

    print()

    print(
        f"Matched records: {len(matched)}"
    )

    print(
        f"Missing audio: {len(missing_audio)}"
    )

    # 6. Write final manifest
    write_manifest(matched)

    print()

    print(
        f"Manifest created: {OUTPUT_FILE}"
    )

    print()
    from pathlib import Path
    import csv


# ============================================================
# CONFIGURATION
# ============================================================

DATA_ROOT = Path("asr_nepali_data")

# One canonical metadata file
METADATA_FILE = DATA_ROOT / "metadata" / "utt_spk_text.tsv"

AUDIO_INDEX = Path(
    "manifests/audio_index.csv"
)

OUTPUT_FILE = Path(
    "manifests/all.csv"
)


# ============================================================
# LOAD AUDIO INDEX
# ============================================================

def load_audio_index():

    audio_index = {}

    with AUDIO_INDEX.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            file_id = row["file_id"]

            if file_id in audio_index:

                raise ValueError(
                    f"Duplicate file_id in audio index: {file_id}"
                )

            audio_index[file_id] = {
                "audio_path": row["audio_path"],
                "dataset": row["dataset"],
                "shard": row["shard"]
            }

    return audio_index


# ============================================================
# PARSE SINGLE TSV METADATA FILE
# ============================================================

def parse_metadata():

    records = []
    malformed_rows = []

    print(
        f"Reading metadata: {METADATA_FILE}"
    )

    with METADATA_FILE.open(
        "r",
        encoding="utf-8"
    ) as f:

        reader = csv.reader(
            f,
            delimiter="\t"
        )

        for line_number, row in enumerate(
            reader,
            start=1
        ):

            # --------------------------------------------
            # Validate number of columns
            # --------------------------------------------

            if len(row) != 3:

                malformed_rows.append({
                    "file": str(METADATA_FILE),
                    "line": line_number,
                    "columns": len(row)
                })

                continue

            # --------------------------------------------
            # Extract fields
            # --------------------------------------------

            file_id = row[0].strip()
            speaker_id = row[1].strip()
            transcript = row[2].strip()

            # --------------------------------------------
            # Basic validation
            # --------------------------------------------

            if not file_id:

                malformed_rows.append({
                    "file": str(METADATA_FILE),
                    "line": line_number,
                    "columns": len(row),
                    "reason": "empty file_id"
                })

                continue

            records.append({
                "file_id": file_id,
                "speaker_id": speaker_id,
                "transcript": transcript
            })

    return records, malformed_rows


# ============================================================
# DUPLICATE CHECK
# ============================================================

def find_duplicate_metadata_ids(records):

    seen = set()
    duplicates = set()

    for record in records:

        file_id = record["file_id"]

        if file_id in seen:

            duplicates.add(file_id)

        else:

            seen.add(file_id)

    return duplicates


# ============================================================
# MATCH METADATA WITH AUDIO
# ============================================================

def create_manifest(
    records,
    audio_index
):

    matched = []
    missing_audio = []

    for record in records:

        file_id = record["file_id"]

        audio_info = audio_index.get(
            file_id
        )

        if audio_info is None:

            missing_audio.append(
                record
            )

            continue

        matched.append({
            "utterance_id": file_id,
            "speaker_id": record["speaker_id"],
            "audio_path": audio_info["audio_path"],
            "transcript": record["transcript"]
        })

    return matched, missing_audio


# ============================================================
# WRITE MASTER MANIFEST
# ============================================================

def write_manifest(records):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "utterance_id",
                "speaker_id",
                "audio_path",
                "transcript"
            ]
        )

        writer.writeheader()

        writer.writerows(records)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("NEPALI ASR - BUILD MASTER MANIFEST")
    print("=" * 60)
    print()

    # ========================================================
    # 0. Validate required files
    # ========================================================

    if not METADATA_FILE.exists():

        raise FileNotFoundError(
            f"Metadata file not found:\n{METADATA_FILE}"
        )

    if not AUDIO_INDEX.exists():

        raise FileNotFoundError(
            f"Audio index not found:\n{AUDIO_INDEX}"
        )

    # ========================================================
    # 1. Load audio index
    # ========================================================

    audio_index = load_audio_index()

    print(
        f"Audio index records: {len(audio_index):,}"
    )

    print()

    # ========================================================
    # 2. Parse ONE metadata file
    # ========================================================

    records, malformed_rows = parse_metadata()

    print()

    print(
        f"Metadata records: {len(records):,}"
    )

    print(
        f"Malformed rows: {len(malformed_rows):,}"
    )

    # ========================================================
    # 3. Check duplicate metadata IDs
    # ========================================================

    duplicate_ids = find_duplicate_metadata_ids(
        records
    )

    print(
        f"Duplicate metadata IDs: "
        f"{len(duplicate_ids):,}"
    )

    # ========================================================
    # 4. Match metadata with audio
    # ========================================================

    matched, missing_audio = create_manifest(
        records,
        audio_index
    )

    print()

    print(
        f"Matched records: {len(matched):,}"
    )

    print(
        f"Missing audio: {len(missing_audio):,}"
    )

    # ========================================================
    # 5. Write master manifest
    # ========================================================

    write_manifest(matched)

    print()

    print(
        f"Manifest created: {OUTPUT_FILE}"
    )

    # ========================================================
    # 6. Final validation
    # ========================================================

    print()
    print("-" * 60)
    print("FINAL VALIDATION")
    print("-" * 60)

    print(
        f"Audio index:        {len(audio_index):,}"
    )

    print(
        f"Metadata:           {len(records):,}"
    )

    print(
        f"Matched:            {len(matched):,}"
    )

    print(
        f"Missing audio:      {len(missing_audio):,}"
    )

    print(
        f"Duplicate IDs:      {len(duplicate_ids):,}"
    )

    print(
        f"Malformed rows:     {len(malformed_rows):,}"
    )

    # ========================================================
    # Expected result
    # ========================================================

    if (
        len(missing_audio) == 0
        and len(duplicate_ids) == 0
        and len(malformed_rows) == 0
        and len(matched) == len(records)
    ):

        print()
        print("✓ MANIFEST VALID")
        print("✓ All metadata matched with audio")

    else:

        print()
        print("⚠ MANIFEST REQUIRES REVIEW")

    print()
    print("Done!")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
    print("Done!")


if __name__ == "__main__":
    main()