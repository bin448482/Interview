"""职位过滤模块 - 根据职位过滤和排序简历内容"""

import re
from typing import List
from dataclasses import replace

from resume_docs.models import ResumeDocument, Project
from resume_docs.role_config import ROLE_FILTERS


class RoleFilter:
    def __init__(self):
        self.role_config = ROLE_FILTERS

    def filter_resume(self, resume: ResumeDocument, role: str) -> ResumeDocument:
        """根据职位过滤简历内容，应用项目级和字段级过滤"""
        if role not in self.role_config:
            available = ", ".join(self.role_config.keys())
            raise ValueError(f"Unknown role: {role}. Available: {available}")

        # 项目级过滤和排序
        filtered_projects = self._filter_and_sort_projects(resume.projects, role)

        # 字段级过滤
        visibility = self._get_field_visibility(role)
        filtered_projects = self._filter_projects(filtered_projects, visibility)

        return ResumeDocument(
            personal_info=resume.personal_info,
            skills=resume.skills,
            projects=filtered_projects,
            work=resume.work,
        )

    def _filter_and_sort_projects(self, projects: List[Project], role: str) -> List[Project]:
        """根据角色的 include/exclude 规则过滤和排序项目"""
        config = self.role_config.get(role, {})
        include_rules = config.get("include_projects", [])
        exclude_rules = config.get("exclude_projects", [])

        # 计算每个项目的相关性分数
        scored_projects = []
        for project in projects:
            # 检查是否应该排除
            if self._matches_any_rule(project, exclude_rules):
                continue

            # 计算相关性分数（匹配的 include 规则数）
            relevance_score = sum(
                1 for rule in include_rules if self._matches_rule(project, rule)
            )

            scored_projects.append((project, relevance_score))

        # 按相关性分数降序、时间降序排序
        scored_projects.sort(
            key=lambda x: (
                -x[1],  # 相关性分数降序
                -(self._get_project_timestamp(x[0])),  # 时间降序
            )
        )

        return [p for p, _ in scored_projects]

    def _matches_any_rule(self, project: Project, rules: List[dict]) -> bool:
        """检查项目是否匹配任何规则"""
        return any(self._matches_rule(project, rule) for rule in rules)

    def _matches_rule(self, project: Project, rule: dict) -> bool:
        """检查项目是否匹配单个规则"""
        field = rule.get("field")
        value = getattr(project, field, None)

        if "pattern" in rule:
            pattern = rule["pattern"]
            if isinstance(value, str):
                return bool(re.search(pattern, value))
            return False

        if "contains" in rule:
            contains_list = rule["contains"]
            if isinstance(value, list):
                return any(item in value for item in contains_list)
            return False

        if "exact" in rule:
            return value == rule["exact"]

        if "value" in rule:
            return value == rule["value"]

        return False

    def _get_project_timestamp(self, project: Project) -> float:
        """获取项目的时间戳用于排序"""
        if project.timeframe and project.timeframe.start:
            try:
                # 将 "2025-10" 格式转换为浮点数用于排序
                parts = project.timeframe.start.split("-")
                return float(parts[0]) * 100 + float(parts[1])
            except (ValueError, IndexError, AttributeError):
                return 0.0
        return 0.0

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
