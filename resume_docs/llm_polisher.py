"""LLM-based content polishing for resume projects."""
from __future__ import annotations

from typing import Dict, List, Optional

from .langchain_clients import get_llm_client
from .models import Project, ImpactMetrics
from .prompt_loader import PromptLoader


class LLMPolisher:
    """Polishes project descriptions using LLM."""

    def polish_projects(
        self,
        projects: List[Project],
        model_name: str,
        locale: str,
        persona: Optional[Dict] = None,
        role: Optional[str] = None,
    ) -> List[Project]:
        """Polish project descriptions using LLM.

        Args:
            projects: List of projects to polish
            model_name: Name of the LLM model to use
            locale: Locale for language-aware polishing (e.g., 'zh-CN', 'en-US')
            persona: Optional persona configuration
            role: Optional role name for role-aware prompt generation

        Returns:
            List of projects with polished descriptions

        Raises:
            ValueError: If LLM invocation fails
        """
        client = get_llm_client(model_name)
        polished_projects = []

        for project in projects:
            polished_project = self._polish_single_project(
                project, client, locale, persona, role
            )
            polished_projects.append(polished_project)

        return polished_projects

    def _polish_single_project(
        self,
        project: Project,
        client,
        locale: str,
        persona: Optional[Dict] = None,
        role: Optional[str] = None,
    ) -> Project:
        """Polish a single project's description.

        Args:
            project: Project to polish
            client: LLM client to use
            locale: Locale for language-aware polishing
            persona: Optional persona configuration
            role: Optional role name for role-aware prompt

        Returns:
            Project with polished description
        """
        if not project.project_overview:
            return project

        language = self._get_language_from_locale(locale)
        persona_hint = self._get_persona_hint(persona, language)

        # 使用 role-aware prompt 如果提供了 role，否则使用旧的 prompt
        if role:
            prompt_loader = PromptLoader()
            prompt = prompt_loader.build_role_aware_prompt(
                project.project_overview, language, role, persona_hint
            )
        else:
            prompt = self._build_polish_prompt(
                project.project_overview, language, persona_hint
            )

        try:
            polished_text = client.invoke(prompt)
        except Exception as e:
            raise ValueError(
                f"Failed to polish project '{project.project_name}': {e}"
            )

        # Create a copy of the project with polished description
        polished_project = self._copy_project(project)
        polished_text = polished_text.strip()

        # Preserve GitHub link if present in original
        if "github.com" in project.project_overview and "github.com" not in polished_text:
            polished_text += f"\nGitHub: {self._extract_github_link(project.project_overview)}"

        polished_project.project_overview = polished_text

        # Clear raw data fields to avoid duplication in output
        polished_project.challenges_or_objectives = []
        polished_project.responsibilities = []
        polished_project.architecture_or_solution = []
        polished_project.process_or_methodology = []
        polished_project.deliverables_or_features = []
        polished_project.metrics_or_impact = []
        polished_project.impact_metrics = ImpactMetrics()

        return polished_project

    def _build_polish_prompt(
        self, text: str, language: str, persona_hint: Optional[str] = None
    ) -> str:
        """Build a prompt for polishing project description.

        Args:
            text: Original project description
            language: Target language
            persona_hint: Optional perspective guidance for the LLM

        Returns:
            Prompt for LLM
        """
        persona_line = ""
        if persona_hint:
            if language == "Chinese":
                persona_line = f"\n角色视角提示（必须体现在措辞、指标与优先级中）：{persona_hint}\n"
            else:
                persona_line = f"\nPerspective cue (must shape tone, metrics, and emphasis): {persona_hint}\n"

        if language == "Chinese":
            return f"""你是一名资深技术招聘官与简历优化专家，擅长根据候选人提供的项目内容，重写为结构清晰、量化明确、对招聘方友好的项目经验。

请根据以下项目内容，生成一段可以直接放入简历的【项目经验】内容。

要求：
1. 按照以下结构输出：
   - 项目名称 | 所属公司/个人 | 起止时间
   - 角色 Role
   - 技术栈 Tech Stack
   - 项目背景（严格控制在400-800字以内，综合以下信息组织）：
     * 项目的核心目标与用户群体
     * 主要挑战与技术难点
     * 采用的架构方案与技术选型
     * 交付的核心产品与功能
   - 主要职责（4~6 条，每条以动词开头）
   - 成果产出（1~4 条；原文有数据则忠实引用，缺少数据时可基于行业通用区间补写保守指标，例如：Day1留存约20%~30%、Day30留存约5%~12%、DAU/MAU约20%~30%。务必使用"约""保持在"等措辞，严禁超出这些区间或给出明显夸张的用户规模。）

2. 项目背景部分应该：
   - 从用户需求出发，说明为什么要做这个项目
   - 阐述面临的主要技术挑战
   - 介绍采用的解决方案与架构设计
   - 突出交付的核心价值与影响
   - 字数严格控制在400-800字以内，不要超过800字

3. 风格要求：
   - 简洁、专业、重点突出
   - 避免列表式堆砌，用段落形式组织
   - 尽量使用动词开头
   - 原文缺少数据时，可以引用上述行业区间生成保守指标，并注明这是区间表现；严禁出现夸张数字（例如：超大用户量、远高于行业均值的增长率）。

4. 重要：只输出上述6个部分的内容，不要包含任何其他信息（如Business、Technical、Challenges、Responsibilities、Solution、Deliverables、Impact等原始数据）；可以在成果部分使用前述行业区间，但不要超出这些范围，更不要虚构庞大里程碑、收入或用户规模。
{persona_line if persona_line else ''}

原始项目内容：
{text}

请直接返回结构化的项目经验内容，不要添加任何前缀或解释。"""
        else:
            return f"""You are a senior technical recruiter and resume optimization expert skilled at rewriting candidate project descriptions into well-structured, quantified, and recruiter-friendly project experience.

Based on the following project content, generate a project experience section that can be directly included in a resume.

Requirements:
1. Structure your output as follows:
   - Project Name | Company/Organization | Duration
   - Role
   - Tech Stack
   - Project Background (strictly limit to 200-400 words, synthesizing the following):
     * Core objectives and target users
     * Key challenges and technical complexities
     * Architecture and technology choices
     * Core deliverables and features
   - Key Responsibilities (4-6 bullet points, each starting with an action verb)
   - Achievements & Outcomes (1-4 bullet points; cite source data when available. If none exists, you may infer conservative benchmarks such as Day-1 retention of 20-30%, Day-30 retention of 5-12%, or DAU/MAU ratios of 20-30%. Use "around"/"kept at" phrasing and stay strictly within these ranges.)

2. Project Background should:
   - Start with user needs and explain why this project matters
   - Articulate the main technical challenges faced
   - Describe the solutions and architectural design adopted
   - Highlight the core value and impact delivered
   - Strictly limit word count to 200-400 words, do not exceed 400 words

3. Style requirements:
   - Concise, professional, highlight key points
   - Avoid list-style enumeration; use paragraph format
   - Start each responsibility with an action verb
   - When inferring metrics, rely only on the benchmark ranges above, clearly mark them as approximate, and never exceed those limits with inflated user counts or growth claims.

4. Important: Output ONLY the 6 sections above. Do NOT include any other information such as Business, Technical, Challenges, Responsibilities, Solution, Deliverables, Impact, or any raw data from the source. The only acceptable synthetic metrics are those within the stated benchmark bands; do not introduce additional milestones, revenue, user counts, or percentages beyond them.
{persona_line if persona_line else ''}

Original project content:
{text}

Please return only the structured project experience content without any prefix or explanation."""

    def _get_language_from_locale(self, locale: str) -> str:
        """Get language name from locale code.

        Args:
            locale: Locale code (e.g., 'zh-CN', 'en-US')

        Returns:
            Language name
        """
        if locale.startswith("zh"):
            return "Chinese"
        elif locale.startswith("en"):
            return "English"
        else:
            return "English"

    def _get_persona_hint(
        self, persona: Optional[Dict], language: str
    ) -> Optional[str]:
        """Derive persona hint text based on selected role and language."""

        if not persona:
            return None

        instructions = persona.get("instructions", {})
        lang_key = "zh" if language == "Chinese" else "en"
        return instructions.get(lang_key) or instructions.get("default")

    def _extract_github_link(self, text: str) -> str:
        """Extract GitHub link from text.

        Args:
            text: Text containing GitHub link

        Returns:
            GitHub URL or empty string if not found
        """
        import re

        match = re.search(r"https://github\.com/[\w\-]+/[\w\-]+", text)
        return match.group(0) if match else ""

    def _copy_project(self, project: Project) -> Project:
        """Create a copy of a project.

        Args:
            project: Project to copy

        Returns:
            Copy of the project
        """
        from dataclasses import replace

        return replace(project)
