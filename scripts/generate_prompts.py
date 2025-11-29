"""生成不同角色的 prompt - 无需虚拟环境"""

import yaml
from pathlib import Path

TEST_PROJECT = """TarotAI 全渠道套件：Expo React Native 客户端 + FastAPI 后端 + Next.js 管理台 + AI 内容生成工具，叠加产品遥测、Cohort 仪表盘与提示治理，面向匿名用户提供四步塔罗体验与付费 AI 解读。"""

ROLES = [
    "product_manager",
    "ai_development",
    "data_development",
    "full_stack",
    "ai_product_designer",
    "ai_engineer",
]

def build_prompt(config, text, language, role):
    """构建 prompt"""
    lang_key = "zh" if language == "Chinese" else "en"
    base = config["base_templates"][lang_key]
    role_config = config["roles"].get(role, {})

    output_structure = role_config.get("output_structure", {}).get(lang_key, [])
    task_focus = role_config.get("task_focus", {}).get(lang_key, "")
    background_guidance = role_config.get("background_guidance", {}).get(lang_key, "")

    structure_items = "\n   ".join(f"- {item}" for item in output_structure)

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

任务焦点：{task_focus}

{background_guidance}

原始项目内容：
{text}

请直接返回结构化的项目经验内容，不要添加任何前缀或解释。"""

def main():
    # 加载配置
    with open("latest_resumes/prompt_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    output_file = Path("artifacts/role_prompts_review.txt")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# 不同角色的 Prompt 生成结果\n\n")
        f.write(f"测试项目: {TEST_PROJECT}\n\n")

        for role in ROLES:
            f.write(f"\n{'='*80}\n")
            f.write(f"角色: {role}\n")
            f.write(f"{'='*80}\n\n")

            prompt = build_prompt(config, TEST_PROJECT, "Chinese", role)
            f.write(f"【中文 Prompt】\n{prompt}\n")
            f.write(f"\n{'-'*80}\n")

            print(f"✓ 已生成 {role} 的 prompt")

    print(f"\n✓ 所有 prompt 已保存到: {output_file}")

if __name__ == "__main__":
    main()
