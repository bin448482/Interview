#!/usr/bin/env python3
"""Translate projects_summary.yaml from Chinese to English using Zhipu GLM."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from resume_docs.runtime_config import load_runtime_config

load_runtime_config()

from resume_docs import loader, constants
from resume_docs.langchain_clients import get_llm_client


def translate_field(client, text: str) -> str:
    """Translate a single text field from Chinese to English."""
    if not text or not isinstance(text, str):
        return text

    prompt = f"""Translate the following Chinese text to English. Keep the translation concise and professional.
Only output the translated text, nothing else.

Chinese text:
{text}"""

    return client.invoke(prompt).strip()


def translate_value(client, value):
    """Recursively translate all text values in a data structure."""
    if isinstance(value, str):
        return translate_field(client, value)
    elif isinstance(value, list):
        return [translate_value(client, item) for item in value]
    elif isinstance(value, dict):
        return {k: translate_value(client, v) for k, v in value.items()}
    else:
        return value


def translate_project(client, project_data: dict) -> dict:
    """Translate all text fields in a project."""
    # Fields to preserve without translation (metadata, enums, etc.)
    preserve_fields = {
        "role_perspective", "decision_accountability",
        "responsibility_focus", "governance_artifacts", "ai_component_flag",
        "start", "end", "team_size", "budget_level", "stakeholder_tiers"
    }

    translated = {}
    for key, value in project_data.items():
        if key in preserve_fields:
            translated[key] = value
        elif key == "management_scope":
            # Preserve management_scope structure but translate nothing (all values are enums/numbers)
            translated[key] = value
        elif key == "timeframe":
            # Translate timeframe.label but preserve start/end
            timeframe = value.copy() if value else {}
            if "label" in timeframe and timeframe["label"]:
                timeframe["label"] = translate_field(client, timeframe["label"])
            translated[key] = timeframe
        else:
            translated[key] = translate_value(client, value)

    return translated


def translate_projects(model_name: str = "glm-4.6") -> None:
    """Translate all projects in projects_summary.yaml."""
    # Load YAML
    projects_file = constants.LATEST_RESUMES_DIR / "projects_summary.yaml"
    with open(projects_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Initialize LLM client
    client = get_llm_client(model_name)

    # Translate projects
    translated_projects = []
    for project in data.get("projects", []):
        print(f"Translating: {project.get('project_name', 'Unknown')}")
        translated_project = translate_project(client, project)
        translated_projects.append(translated_project)

    # Prepare output
    output_data = {
        "schema_version": data.get("schema_version", "1.1"),
        "generated_at": datetime.now().isoformat(),
        "source_file": data.get("source_file", ""),
        "projects": translated_projects,
    }

    # Write output
    output_file = constants.LATEST_RESUMES_DIR / "projects_summary_en.yaml"
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(output_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"\n✓ Translation complete. Output: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Translate projects_summary.yaml to English")
    parser.add_argument("--model", default="glm-4-flash", help="LLM model to use (default: glm-4-flash)")
    args = parser.parse_args()

    try:
        translate_projects(args.model)
    except Exception as e:
        print(f"✗ Translation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
