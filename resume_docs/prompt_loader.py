"""加载和构建角色感知的 LLM Prompt"""

import yaml
from pathlib import Path
from typing import Dict, Optional


class PromptLoader:
    """加载 YAML 配置并构建角色感知的 prompt"""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "latest_resumes" / "prompt_config.yaml"
        self.config_path = config_path
        self._config = None

    @property
    def config(self) -> Dict:
        """延迟加载配置"""
        if self._config is None:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f)
        return self._config

    def build_role_aware_prompt(
        self, text: str, language: str, role: str, persona_hint: Optional[str] = None
    ) -> str:
        """构建角色感知的 prompt

        Args:
            text: 原始项目描述
            language: 语言（"Chinese" 或 "English"）
            role: 角色名称
            persona_hint: 可选的 persona 提示

        Returns:
            完整的 LLM prompt
        """
        lang_key = "zh" if language == "Chinese" else "en"
        base = self.config["base_templates"][lang_key]
        role_config = self.config["roles"].get(role, {})

        # 获取角色特定的输出结构
        output_structure = role_config.get("output_structure", {}).get(lang_key, [])
        task_focus = role_config.get("task_focus", {}).get(lang_key, "")
        background_guidance = role_config.get("background_guidance", {}).get(lang_key, "")

        # 构建结构说明
        structure_items = "\n   ".join(f"- {item}" for item in output_structure)

        # 拼接防幻觉约束：全局 guard + 角色级 guard（如有）
        base_guard = base.get("hallucination_guard", "")
        role_guard_cfg = role_config.get("hallucination_guard", {})
        if isinstance(role_guard_cfg, dict):
            role_guard = role_guard_cfg.get(lang_key, "")
        else:
            role_guard = role_guard_cfg or ""
        hallucination_guard = "\n".join(
            part for part in (base_guard, role_guard) if part
        )

        # 构建 persona 提示行
        persona_line = ""
        if persona_hint:
            if language == "Chinese":
                persona_line = f"\n角色视角提示（必须体现在措辞、指标与优先级中）：{persona_hint}\n"
            else:
                persona_line = f"\nPerspective cue (must shape tone, metrics, and emphasis): {persona_hint}\n"

        if language == "Chinese":
            return f"""你是一名{base['system_role']}，擅长根据候选人提供的项目内容，重写为结构清晰、量化明确、对招聘方友好的项目经验。

请根据以下项目内容，生成一段可以直接放入简历的【项目经验】内容。

{base['requirements_intro']}
1. {base['structure_label']}
   {structure_items}

2. 项目背景部分应该：
   - 从用户需求出发，说明为什么要做这个项目
   - 阐述面临的主要挑战
   - 介绍采用的解决方案与架构设计
   - 突出交付的核心价值与影响
   - 字数{base['background_constraint']}，不要超过限制

3. {base['style_intro']}
   - 简洁、专业、重点突出
   - 避免列表式堆砌，用段落形式组织
   - 尽量使用动词开头
   - 原文缺少数据时，可以引用行业区间生成保守指标；严禁出现夸张数字

4. {base['important_note']}只输出上述结构中的内容，不要包含任何其他信息；可以在成果部分使用行业区间，但不要超出这些范围。

{base['metrics_guidance']}
{hallucination_guard}

任务焦点：{task_focus}

{background_guidance}{persona_line}
原始项目内容：
{text}

请直接返回结构化的项目经验内容，不要添加任何前缀或解释。"""
        else:
            return f"""You are a {base['system_role']} skilled at rewriting candidate project descriptions into well-structured, quantified, and recruiter-friendly project experience.

Based on the following project content, generate a project experience section that can be directly included in a resume.

{base['requirements_intro']}
1. {base['structure_label']}
   {structure_items}

2. Project background should:
   - Start with user needs and explain why this project matters
   - Articulate the main challenges faced
   - Describe the solutions and architectural design adopted
   - Highlight the core value and impact delivered
   - {base['background_constraint']}, do not exceed the limit

3. {base['style_intro']}
   - Concise, professional, highlight key points
   - Avoid list-style enumeration; use paragraph format
   - Start each responsibility with an action verb
   - When inferring metrics, rely only on benchmark ranges, clearly mark them as approximate, and never exceed those limits

4. {base['important_note']} Output ONLY the structure above. Do NOT include any other information. The only acceptable synthetic metrics are those within the stated benchmark bands.

{base['metrics_guidance']}
{hallucination_guard}

Task focus: {task_focus}

{background_guidance}{persona_line}
Original project content:
{text}

Please return only the structured project experience content without any prefix or explanation."""
