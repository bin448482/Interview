# Scripts 目录规范

所有辅助脚本都应放在此目录下。

## 脚本命名规范

- 使用 `snake_case` 命名
- 前缀表示脚本类型：
  - `test_*.py` - 测试脚本
  - `generate_*.py` - 生成脚本
  - `validate_*.py` - 验证脚本
  - `migrate_*.py` - 迁移脚本

## 脚本结构

每个脚本应包含：

```python
"""脚本功能说明"""

# 导入
# 常量定义
# 主函数
# 使用示例

if __name__ == "__main__":
    main()
```

## 脚本文档

在脚本顶部添加 docstring，说明：
- 功能
- 使用方式
- 输出位置
- 依赖

## 当前脚本

| 脚本 | 功能 | 使用 |
|------|------|------|
| `generate_prompts.py` | 生成不同角色的 prompt | `python scripts/generate_prompts.py` |
| `test_role_prompts.py` | 测试 prompt 生成（虚拟环境版） | `.venv\Scripts\python scripts/test_role_prompts.py` |
| `translate_projects.py` | 翻译项目数据 | `python scripts/translate_projects.py` |
