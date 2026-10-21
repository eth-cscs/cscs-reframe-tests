import argparse
from pathlib import Path
from typing import Tuple
from .models import ReFrameReporterConfig
from .orchestrator import ReportOrchestrator


def parse_args() -> Tuple[ReFrameReporterConfig, argparse.Namespace]:
    """Parse command line arguments and return configuration and namespace."""
    parser = argparse.ArgumentParser(description="ReFrame Test Reporter CLI")
    parser.add_argument("--uenv-recipes-dir", type=str, help="Directory containing UEnv recipes")
    parser.add_argument("-C", "--checks", action='append', default=[], help="Path to ReFrame config file or directory of checks")
    parser.add_argument("-c", "--config_dir", type=str, help="Directory containing test configs (passed via extra args)")
    parser.add_argument("-R", "--recursive", action="store_true", help="Recursive mode")
    parser.add_argument("-f", "--filename", default=None, help="Output filename. If not provided, defaults to 'eligible_tests.md'. If provided, the filename is used as-is without automatic suffix modification.")
    parser.add_argument("-o", "--output_dir", type=str, help="Output directory for the report")
    parser.add_argument("--uenv-image-inventory", type=str, help="Path to UHM image inventory JSON")
    parser.add_argument("--matrix-mode", type=str, help="Comma-separated matrix entries: label:system:mode,label2:system2:mode")
    parser.add_argument("--matrix-tag", type=str, help="Comma-separated matrix entries: label:system:tag,label2:system2:tag2")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    parser.add_argument("extra", nargs=argparse.REMAINDER, help="Extra args passed to ReFrame after '--'")

    args = parser.parse_args()

    # Build config from parsed arguments
    config = ReFrameReporterConfig(
        config_files=[Path(c) for c in args.checks],
        recursive=args.recursive,
        uenv_recipes_dir=Path(args.uenv_recipes_dir) if args.uenv_recipes_dir else None,
        uenv_image_inventory=Path(args.uenv_image_inventory) if args.uenv_image_inventory else None,
        output_dir=Path(args.output_dir) if args.output_dir else Path.cwd()
    )

    # Handle filename: None means not provided, so use default
    if args.filename is None:
        args.filename = "eligible_tests.md"
    
    # If filename is custom (not the default), mark it as explicit
    explicit_filename = args.filename != "eligible_tests.md"

    # Update config with filename and explicit_filename
    config.output_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
    config.filename = args.filename
    config.explicit_filename = explicit_filename

    # Track processed state
    processed = argparse.Namespace()
    processed.config = config
    processed.explicit_filename = explicit_filename
    processed.filename = args.filename

    # Reconstruct extra args from the namespace
    extra_args = []
    for check in args.checks:
        extra_args.extend(["-C", str(Path(check).resolve())])
    if args.config_dir:
        extra_args.extend(["-c", str(Path(args.config_dir).resolve())])

    # Update processed with extra_args
    processed.extra_args = extra_args

    return processed, args


def main():
    try:
        parsed, args = parse_args()
        
        # Pass explicit_filename to orchestrator
        orchestrator = ReportOrchestrator(
            parsed.config,
            explicit_filename=parsed.explicit_filename
        )

        if args.matrix_mode and args.matrix_tag:
            raise ValueError("--matrix-mode and --matrix-tag are mutually exclusive")

        def validate_target(t: str):
            parts = t.split(':')
            if len(parts) != 3:
                raise ValueError(f"Target '{t}' is not in the required 3-part format (label:system:mode/tag)")
            return parts

        if args.matrix_mode:
            targets = [entry.strip() for entry in args.matrix_mode.split(',') if entry.strip()]
            for t in targets: validate_target(t)
            output_file = orchestrator.run_matrix_mode(targets, parsed.extra_args)
        elif args.matrix_tag:
            targets = [entry.strip() for entry in args.matrix_tag.split(',') if entry.strip()]
            for t in targets: validate_target(t)
            output_file = orchestrator.run_matrix_tag_mode(targets, parsed.extra_args)
        else:
            raise ValueError("Either --matrix-mode or --matrix-tag must be specified")

        print(f"\n[SUCCESS] Report generation complete.")
        print(f"[INFO] Output file: {output_file}")

    except Exception as e:
        print(f"Execution Error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
