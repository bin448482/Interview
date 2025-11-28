"""职位过滤模块 - 根据职位过滤和排序简历内容"""

import re
from typing import List
from datetime import datetime

from resume_docs.models import ResumeDocument, Project, WorkSummary
from resume_docs.role_config import ROLE_FILTERS


class RoleFilter:
    def __init__(self):
        self.role_config = ROLE_FILTERS

    def filter_resume(self, resume: ResumeDocument, role: str) -> ResumeDocument:
        """根据职位过滤简历内容"""
        if role not in self.role_config:
            available = ", ".join(self.role_config.keys())
            raise ValueError(f"Unknown role: {role}. Available: {available}")

        config = self.role_config[role]
        filtered_projects = self._filter_and_sort_projects(resume.projects, config)
        filtered_work = self._filter_work_experience(resume.work, config)

        return ResumeDocument(
            personal_info=resume.personal_info,
            skills=resume.skills,
            projects=filtered_projects,
            work=filtered_work,
        )

    def _filter_and_sort_projects(self, projects: List[Project], config: dict) -> List[Project]:
        """按规则过滤项目，然后按相关度 + 时间排序"""
        # 1. 应用 exclude_projects 规则
        filtered = [p for p in projects if not self._match_exclude_rule(p, config.get("exclude_projects", []))]

        # 2. 应用 include_projects 规则
        filtered = [p for p in filtered if self._match_include_rule(p, config.get("include_projects", []))]

        # 3. 按时间倒序排列（新项目优先）
        filtered.sort(key=lambda p: self._get_project_date(p), reverse=True)

        return filtered

    def _filter_work_experience(self, work: WorkSummary, config: dict) -> WorkSummary:
        """按职位相关性过滤工作经历"""
        include_rules = config.get("include_work_roles", [])
        if not include_rules:
            return work

        filtered_experiences = [
            exp for exp in work.experiences
            if any(self._match_field_rule(exp, rule) for rule in include_rules)
        ]

        return WorkSummary(
            experiences=filtered_experiences,
            role_responsibilities=work.role_responsibilities,
        )

    def _match_exclude_rule(self, project: Project, exclude_rules: List[dict]) -> bool:
        """检查项目是否匹配任何排除规则"""
        return any(self._match_field_rule(project, rule) for rule in exclude_rules)

    def _match_include_rule(self, project: Project, include_rules: List[dict]) -> bool:
        """检查项目是否匹配任何包含规则"""
        if not include_rules:
            return True
        return any(self._match_field_rule(project, rule) for rule in include_rules)

    def _match_field_rule(self, obj, rule: dict) -> bool:
        """检查对象字段是否匹配规则"""
        field = rule.get("field")
        value = getattr(obj, field, None)

        if value is None:
            return False

        if "exact" in rule:
            return value == rule["exact"]

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

        if "value" in rule:
            return value == rule["value"]

        return False

    def _calculate_relevance_score(self, project: Project, config: dict) -> float:
        """计算项目相关度评分"""
        score = 0.0
        include_rules = config.get("include_projects", [])

        for rule in include_rules:
            if self._match_field_rule(project, rule):
                score += 1.0

        return score

    def _get_project_date(self, project: Project) -> tuple:
        """提取项目结束日期用于排序（新项目优先）"""
        if not project.timeframe:
            return (0, 0)

        # 优先使用 end 日期，如果没有则使用 start 日期
        date_str = project.timeframe.end or project.timeframe.start
        if not date_str:
            return (0, 0)

        try:
            if isinstance(date_str, str):
                parts = date_str.split("-")
                return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
            return (0, 0)
        except (ValueError, IndexError, AttributeError):
            return (0, 0)
