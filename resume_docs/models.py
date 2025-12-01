"""Dataclasses describing resume content."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional


@dataclass
class Certification:
    name: str
    url: Optional[str] = None


@dataclass
class EducationEntry:
    description: str


@dataclass
class PersonalInfo:
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    hukou: Optional[str] = None
    gender: Optional[str] = None
    github: Optional[str] = None
    education: List[EducationEntry] = field(default_factory=list)
    certifications: List[Certification] = field(default_factory=list)


@dataclass
class SkillCategory:
    category: str
    items: List[str] = field(default_factory=list)


@dataclass
class SkillsSummary:
    categories: List[SkillCategory] = field(default_factory=list)


@dataclass
class Timeframe:
    label: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None


@dataclass
class ManagementScope:
    team_size: Optional[int] = None
    budget_level: Optional[str] = None
    stakeholder_tiers: List[str] = field(default_factory=list)


@dataclass
class ImpactMetrics:
    business_metrics: List[str] = field(default_factory=list)
    technical_metrics: List[str] = field(default_factory=list)
    operational_metrics: List[str] = field(default_factory=list)

    def grouped(self) -> List[tuple[str, List[str]]]:
        return [
            ("Business", self.business_metrics),
            ("Technical", self.technical_metrics),
            ("Operational", self.operational_metrics),
        ]


@dataclass
class Project:
    project_name: str
    company_or_context: Optional[str] = None
    timeframe: Timeframe = field(default_factory=Timeframe)
    role_title: Optional[str] = None
    role_perspective: Optional[str] = None
    llm_primary_role: Optional[str] = None
    llm_secondary_roles: List[str] = field(default_factory=list)
    management_scope: ManagementScope = field(default_factory=ManagementScope)
    decision_accountability: List[str] = field(default_factory=list)
    responsibility_focus: List[str] = field(default_factory=list)
    impact_metrics: ImpactMetrics = field(default_factory=ImpactMetrics)
    governance_artifacts: List[str] = field(default_factory=list)
    project_overview: Optional[str] = None
    data_domain: Optional[str] = None
    ai_component_flag: Optional[bool] = None
    challenges_or_objectives: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    architecture_or_solution: List[str] = field(default_factory=list)
    process_or_methodology: List[str] = field(default_factory=list)
    deliverables_or_features: List[str] = field(default_factory=list)
    metrics_or_impact: List[str] = field(default_factory=list)
    tech_stack: List[str] = field(default_factory=list)
    tools_platforms: List[str] = field(default_factory=list)
    team_info: Dict[str, object] = field(default_factory=dict)
    notes: Optional[str] = None


@dataclass
class WorkExperienceEntry:
    company: str
    duration: Optional[str] = None
    title: Optional[str] = None


@dataclass
class RoleResponsibility:
    role: str
    responsibilities: List[str] = field(default_factory=list)


@dataclass
class WorkSummary:
    experiences: List[WorkExperienceEntry] = field(default_factory=list)
    role_responsibilities: List[RoleResponsibility] = field(default_factory=list)


@dataclass
class ResumeDocument:
    personal_info: PersonalInfo
    skills: SkillsSummary
    projects: List[Project]
    work: WorkSummary

    def to_dict(self) -> dict:
        return asdict(self)
