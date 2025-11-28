"""Command line interface for resume document generation."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from . import config as config_module
from . import constants
from . import docx_renderer, loader
from .llm_polisher import LLMPolisher
from .role_filter import RoleFilter
from .role_config import ROLE_FILTERS

# Load environment variables from .env file
load_dotenv()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate DOCX resumes with LLM-polished content from YAML data.")
    parser.add_argument("--template", default=constants.DEFAULT_THEME, help="Template key (modern|minimal)")
    parser.add_argument("--locale", default=constants.DEFAULT_LOCALE, help="Locale key, e.g. zh-CN")
    parser.add_argument("--include-contact", action="store_true", help="Include phone/address in DOCX header")
    parser.add_argument("--role", help=f"Target role for filtering. Available: {', '.join(ROLE_FILTERS.keys())}")
    parser.add_argument("--model", help="LLM model for polishing (e.g., gpt-4o, glm-4, ollama)")
    parser.add_argument("--output-dir", default=str(constants.DEFAULT_OUTPUT_DIR), help="Root output directory")
    parser.add_argument("--skip-polish", action="store_true", help="Skip LLM polishing (use original content)")
    parser.add_argument("--config", help="Optional YAML config override", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Parse YAML only without writing files")
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = config_module.create_config(cli_args={
        "template": args.template,
        "locale": args.locale,
        "include_contact": args.include_contact,
        "output_dir": args.output_dir,
        "dry_run": args.dry_run,
    }, config_file=Path(args.config) if args.config else None)

    resume_data = loader.load_resume_data(locale=args.locale)

    # Role filtering (required)
    if not args.role:
        available_roles = ", ".join(ROLE_FILTERS.keys())
        print(f"Error: --role is required. Available roles: {available_roles}")
        return 1

    role_filter = RoleFilter()
    resume_data = role_filter.filter_resume(resume_data, args.role)

    if cfg.dry_run:
        print("Dry run complete. Parsed resume data successfully.")
        return 0

    # LLM polishing (optional)
    if not args.skip_polish and args.model:
        polisher = LLMPolisher()
        try:
            resume_data.projects = polisher.polish_projects(
                resume_data.projects, args.model, cfg.locale
            )
            print(f"Projects polished using {args.model}")
        except ValueError as e:
            print(f"Error during polishing: {e}")
            return 1

    output_root = cfg.output_dir_path / cfg.locale / cfg.template

    # DOCX generation
    docx_path = output_root / "resume.docx"
    try:
        docx_renderer.render_docx(resume_data, docx_path, cfg.template, cfg.locale, cfg.include_contact)
        print(f"DOCX saved to {docx_path}")
    except docx_renderer.MissingDependencyError as exc:
        print(f"DOCX generation skipped: {exc}")
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
