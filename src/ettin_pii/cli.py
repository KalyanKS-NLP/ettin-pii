"""
Command Line Interface for ettin-pii.
"""
import sys
import argparse
from .detector import PIIDetector
from .models import BatchDetectionResult


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ettin-pii",
        description="Fast PII Detection and Redaction CLI powered by the Ettin Nemotron PII model family",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: detect
    detect_parser = subparsers.add_parser("detect", help="Scan text or file for PII entities")
    detect_parser.add_argument("input", help="Raw text string or path to a text file")
    detect_parser.add_argument(
        "--model",
        choices=["nano", "tiny", "small"],
        default="small",
        help="PII model size: nano (17M), tiny (32M), or small (68M, default)",
    )
    detect_parser.add_argument("--threshold", type=float, default=0.5, help="Confidence threshold (0.0-1.0)")
    detect_parser.add_argument(
        "--batch",
        "-b",
        action="store_true",
        help="Process input line-by-line as a batch of independent records",
    )
    detect_parser.add_argument("--output", "-o", help="Optional JSON output filepath")

    # Subcommand: redact
    redact_parser = subparsers.add_parser("redact", help="Sanitize text or file")
    redact_parser.add_argument("input", help="Raw text string or path to a text file")
    redact_parser.add_argument(
        "--model",
        choices=["nano", "tiny", "small"],
        default="small",
        help="PII model size: nano (17M), tiny (32M), or small (68M, default)",
    )
    redact_parser.add_argument("--threshold", type=float, default=0.5, help="Confidence threshold (0.0-1.0)")
    redact_parser.add_argument(
        "--batch",
        "-b",
        action="store_true",
        help="Process input line-by-line as a batch of independent records",
    )
    redact_parser.add_argument(
        "--strategy",
        choices=["replace", "mask", "fake"],
        default="replace",
        help="Redaction strategy to apply",
    )
    redact_parser.add_argument("--mask-char", default="*", help="Masking character (default: *)")
    redact_parser.add_argument(
        "--mask-mode",
        choices=["full", "alternate", "first_only"],
        default="full",
        help="Masking style when strategy='mask' (default: full)",
    )
    redact_parser.add_argument("--output", "-o", help="Optional output filepath for sanitized text")

    # Subcommand: stats
    stats_parser = subparsers.add_parser("stats", help="Show summary PII statistics and density")
    stats_parser.add_argument("input", help="Raw text string or path to a text file")
    stats_parser.add_argument(
        "--model",
        choices=["nano", "tiny", "small"],
        default="small",
        help="PII model size: nano (17M), tiny (32M), or small (68M, default)",
    )
    stats_parser.add_argument("--threshold", type=float, default=0.5, help="Confidence threshold (0.0-1.0)")
    stats_parser.add_argument(
        "--batch",
        "-b",
        action="store_true",
        help="Process input line-by-line as a batch of independent records",
    )
    stats_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Include detailed list of extracted entities with scores and offsets",
    )

    args = parser.parse_args()

    is_batch = getattr(args, "batch", False)

    # Read input from file if existing path, else treat as raw string
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            if is_batch:
                content = [line.strip() for line in f if line.strip()]
            else:
                content = f.read()
    except (FileNotFoundError, OSError):
        if is_batch:
            content = [line.strip() for line in args.input.splitlines() if line.strip()]
        else:
            content = args.input

    detector = PIIDetector(
        model=args.model,
        confidence_threshold=getattr(args, "threshold", 0.5),
    )
    result = detector.detect(content)

    if args.command == "detect":
        if isinstance(result, BatchDetectionResult):
            if args.output:
                result.to_json(args.output)
                print(f"Batch entities exported to {args.output}")
            else:
                print(f"\nProcessed {len(result)} records (Total PII: {result.total_entities}):")
                for i, r in enumerate(result):
                    if r.has_pii:
                        print(f" [Record #{i+1}] '{r.text}'")
                        for ent in r.entities:
                            print(f"   - [{ent.label}] '{ent.text}' (Score: {ent.score:.2%}, Offsets: {ent.start}-{ent.end})")
        else:
            if args.output:
                result.to_json(args.output)
                print(f"Entities exported to {args.output}")
            else:
                print(f"\nFound {result.num_entities} PII entities:")
                for ent in result.entities:
                    print(f" - [{ent.label}] '{ent.text}' (Score: {ent.score:.2%}, Offsets: {ent.start}-{ent.end})")

    elif args.command == "redact":
        sanitized = result.redact(
            strategy=args.strategy,
            mask_char=args.mask_char,
            mask_mode=args.mask_mode,
        )
        if isinstance(result, BatchDetectionResult):
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write("\n".join(sanitized) + "\n")
                print(f"Sanitized {len(sanitized)} records saved to {args.output}")
            else:
                for line in sanitized:
                    print(line)
        else:
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(sanitized)
                print(f"Sanitized text saved to {args.output}")
            else:
                print(sanitized)

    elif args.command == "stats":
        if isinstance(result, BatchDetectionResult):
            stats = result.statistics
            total = stats["total_texts"]
            with_pii = stats["texts_with_pii"]
            pct_pii = (with_pii / total * 100) if total > 0 else 0.0
            clean = total - with_pii
            pct_clean = 100.0 - pct_pii

            print("\n--- Batch PII Statistics Report ---")
            print(f"Total Texts Analyzed : {total}")
            print(f"Texts with PII       : {with_pii} ({pct_pii:.2f}%)")
            print(f"Clean Texts          : {clean} ({pct_clean:.2f}%)")
            print(f"Total Entities Found : {stats['total_entities']}")
            print(f"Unique Entity Types  : {stats['unique_entity_types']}")
            print("\nBreakdown by Label across Batch:")
            for label, count in stats["entity_counts"].items():
                print(f"  - {label}: {count}")

            if getattr(args, "verbose", False) and stats["total_entities"] > 0:
                print("\nExtracted Entities by Record:")
                for i, r in enumerate(result):
                    if r.has_pii:
                        print(f"  [Record #{i+1}] {r.text}")
                        for ent in r.entities:
                            print(f"    - [{ent.label}] '{ent.text}' (Score: {ent.score:.2%}, Offsets: {ent.start}-{ent.end})")
        else:
            stats = result.statistics
            print("\n--- PII Statistics Report ---")
            print(f"Total Entities : {stats['total_entities']}")
            print(f"Unique Types   : {stats['unique_entity_types']}")
            print(f"Text Density   : {stats['density']:.2%}")
            print(f"Avg Confidence : {stats['average_confidence']:.2%}")
            print("Breakdown by Label:")
            for label, count in stats["entity_counts"].items():
                print(f"  - {label}: {count}")

            if getattr(args, "verbose", False) and result.entities:
                print("\nExtracted Entities:")
                for ent in result.entities:
                    print(f"  - [{ent.label}] '{ent.text}' (Score: {ent.score:.2%}, Offsets: {ent.start}-{ent.end})")


if __name__ == "__main__":
    main()
