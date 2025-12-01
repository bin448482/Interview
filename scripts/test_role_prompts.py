"""测试脚本：为不同角色生成 prompt 用于 review"""

from pathlib import Path
from resume_docs.prompt_loader import PromptLoader

# 测试项目内容
TEST_PROJECT = """TarotAI 全渠道套件：Expo React Native 客户端 + FastAPI 后端 + Next.js 管理台 + AI 内容生成工具，叠加产品遥测、Cohort 仪表盘与提示治理，面向匿名用户提供四步塔罗体验与付费 AI 解读。"""

# 所有角色
ROLES = [
    "project_manager",
    "product_manager",
    "ai_development",
    "data_development",
    "full_stack",
    "ai_product_designer",
    "ai_engineer",
]

def main():
    loader = PromptLoader()
    output_file = Path("artifacts/role_prompts_review.txt")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# 不同角色的 Prompt 生成结果\n\n")
        f.write(f"测试项目: {TEST_PROJECT}\n\n")

        for role in ROLES:
            f.write(f"\n{'='*80}\n")
            f.write(f"角色: {role}\n")
            f.write(f"{'='*80}\n\n")

            # 生成中文 prompt
            prompt_zh = loader.build_role_aware_prompt(
                TEST_PROJECT,
                "Chinese",
                role,
                persona_hint=None
            )

            f.write(f"【中文 Prompt】\n{prompt_zh}\n")
            f.write(f"\n{'-'*80}\n")

            # 同时打印到控制台
            print(f"✓ 已生成 {role} 的 prompt")

    print(f"\n✓ 所有 prompt 已保存到: {output_file}")

if __name__ == "__main__":
    main()
