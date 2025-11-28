"""Load resume YAML data into in-memory dataclasses."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml

from . import constants, models

PERSONAL_INFO_FILE = "personal_info_summary.yaml"
SKILLS_FILE = "skills_summary.yaml"
PROJECTS_FILE = "projects_summary.yaml"
WORK_FILE = "work_experience_summary.yaml"


def _read_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_resume_data(base_dir: Path | None = None, locale: str = "zh-CN") -> models.ResumeDocument:
    base_path = Path(base_dir or constants.LATEST_RESUMES_DIR)
    suffix = "_en" if locale == "en-US" else ""
    personal_file = f"personal_info_summary{suffix}.yaml"
    skills_file = f"skills_summary{suffix}.yaml"
    projects_file = f"projects_summary{suffix}.yaml"
    work_file = f"work_experience_summary{suffix}.yaml"
    personal = _parse_personal(_read_yaml(base_path / personal_file))
    skills = _parse_skills(_read_yaml(base_path / skills_file))
    projects = _parse_projects(_read_yaml(base_path / projects_file))
    work = _parse_work(_read_yaml(base_path / work_file))
    return models.ResumeDocument(
        personal_info=personal,
        skills=skills,
        projects=projects,
        work=work,
    )


def _parse_personal(data: Dict[str, Any]) -> models.PersonalInfo:
    education_entries = [models.EducationEntry(description=e["description"]) for e in data.get("education", [])]
    certs = [models.Certification(name=item["name"], url=item.get("url")) for item in data.get("certifications", [])]
    return models.PersonalInfo(
        name=data.get("name", ""),
        phone=data.get("phone"),
        email=data.get("email"),
        address=data.get("address"),
        hukou=data.get("hukou"),
        gender=data.get("gender"),
        github=data.get("github"),
        education=education_entries,
        certifications=certs,
    )


def _parse_skills(data: Dict[str, Any]) -> models.SkillsSummary:
    categories = [
        models.SkillCategory(category=item.get("category", ""), items=list(item.get("items", [])))
        for item in data.get("skills", [])
    ]
    return models.SkillsSummary(categories=categories)


def _parse_projects(data: Dict[str, Any]) -> List[models.Project]:
    projects: List[models.Project] = []
    for raw in data.get("projects", []):
        _validate_project_enums(raw)
        timeframe = models.Timeframe(**raw.get("timeframe", {}) or {})
        management_scope = models.ManagementScope(**(raw.get("management_scope", {}) or {}))
        impact_metrics = models.ImpactMetrics(**(raw.get("impact_metrics", {}) or {}))
        project = models.Project(
            project_name=raw.get("project_name", ""),
            company_or_context=raw.get("company_or_context"),
            timeframe=timeframe,
            role_title=raw.get("role_title"),
            role_perspective=raw.get("role_perspective"),
            management_scope=management_scope,
            decision_accountability=list(raw.get("decision_accountability", []) or []),
            responsibility_focus=list(raw.get("responsibility_focus", []) or []),
            impact_metrics=impact_metrics,
            governance_artifacts=list(raw.get("governance_artifacts", []) or []),
            project_overview=raw.get("project_overview"),
            data_domain=raw.get("data_domain"),
            ai_component_flag=raw.get("ai_component_flag"),
            challenges_or_objectives=list(raw.get("challenges_or_objectives", []) or []),
            responsibilities=list(raw.get("responsibilities", []) or []),
            architecture_or_solution=list(raw.get("architecture_or_solution", []) or []),
            process_or_methodology=list(raw.get("process_or_methodology", []) or []),
            deliverables_or_features=list(raw.get("deliverables_or_features", []) or []),
            metrics_or_impact=list(raw.get("metrics_or_impact", []) or []),
            tech_stack=list(raw.get("tech_stack", []) or []),
            tools_platforms=list(raw.get("tools_platforms", []) or []),
            team_info=dict(raw.get("team_info", {}) or {}),
            notes=raw.get("notes"),
        )
        projects.append(project)
    return projects


def _parse_work(data: Dict[str, Any]) -> models.WorkSummary:
    experiences = [
        models.WorkExperienceEntry(
            company=item.get("company", ""),
            duration=item.get("duration"),
            title=item.get("title"),
        )
        for item in data.get("experiences", [])
    ]
    role_responsibilities = [
        models.RoleResponsibility(role=item.get("role", ""), responsibilities=list(item.get("responsibilities", []) or []))
        for item in data.get("role_responsibilities", [])
    ]
    return models.WorkSummary(experiences=experiences, role_responsibilities=role_responsibilities)


def _validate_project_enums(raw: Dict[str, Any]) -> None:
    role = raw.get("role_perspective")
    if role and role not in constants.ROLE_PERSPECTIVE_ALLOWED:
        raise ValueError(f"Invalid role_perspective '{role}' in project {raw.get('project_name')}")
    management_scope = raw.get("management_scope", {}) or {}
    budget_level = management_scope.get("budget_level")
    if budget_level and budget_level not in constants.BUDGET_LEVEL_ALLOWED:
        raise ValueError(f"Invalid budget_level '{budget_level}' in project {raw.get('project_name')}")
    for choice in raw.get("decision_accountability", []) or []:
        if choice not in constants.DECISION_ACCOUNTABILITY_ALLOWED:
            raise ValueError(f"Invalid decision_accountability '{choice}' in project {raw.get('project_name')}")
    for tag in raw.get("responsibility_focus", []) or []:
        if tag not in constants.RESPONSIBILITY_FOCUS_ALLOWED:
            raise ValueError(f"Invalid responsibility_focus '{tag}' in project {raw.get('project_name')}")
