"""职位过滤模块 - 根据职位过滤和排序简历内容"""

from typing import List
from dataclasses import replace

from resume_docs.models import ResumeDocument, Project
from resume_docs.role_config import ROLE_FILTERS


class RoleFilter:
    def __init__(self):
        self.role_config = ROLE_FILTERS

    def filter_resume(self, resume: ResumeDocument, role: str) -> ResumeDocument:
        """根据职位过滤简历内容，应用字段级可见性"""
        if role not in self.role_config:
            available = ", ".join(self.role_config.keys())
            raise ValueError(f"Unknown role: {role}. Available: {available}")

        visibility = self._get_field_visibility(role)
        filtered_projects = self._filter_projects(resume.projects, visibility)

        return ResumeDocument(
            personal_info=resume.personal_info,
            skills=resume.skills,
            projects=filtered_projects,
            work=resume.work,
        )

    def _get_field_visibility(self, role: str) -> dict:
        """获取角色的字段可见性配置"""
        config = self.role_config.get(role, {})
        return config.get("field_visibility", {})

    def _filter_projects(self, projects: List[Project], visibility: dict) -> List[Project]:
        """对所有项目应用字段过滤"""
        return [self._filter_project_fields(p, visibility) for p in projects]

    def _filter_project_fields(self, project: Project, visibility: dict) -> Project:
        """创建仅包含可见字段的新 Project 实例"""
        filtered_data = {}

        for field_name in project.__dataclass_fields__:
            if visibility.get(field_name, True):
                filtered_data[field_name] = getattr(project, field_name)
            else:
                # 根据字段类型设置默认值
                field_type = project.__dataclass_fields__[field_name].type
                if field_name in ("governance_artifacts", "challenges_or_objectives",
                                 "responsibilities", "architecture_or_solution",
                                 "process_or_methodology", "deliverables_or_features",
                                 "metrics_or_impact", "tech_stack", "tools_platforms",
                                 "decision_accountability", "responsibility_focus"):
                    filtered_data[field_name] = []
                else:
                    filtered_data[field_name] = None

        return replace(project, **filtered_data)
