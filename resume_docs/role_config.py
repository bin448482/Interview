"""职位过滤配置 - 定义不同职位的项目和工作经历过滤规则"""

ROLE_FILTERS = {
    "data_development": {
        "name": "数据开发",
        "include_projects": [
            {"field": "data_domain", "pattern": ".*数据.*|.*BI.*"},
            {"field": "ai_component_flag", "value": True},
        ],
        "exclude_projects": [
            {"field": "project_name", "exact": "Move To HP Cloud"},
            {"field": "data_domain", "pattern": ".*基础设施.*"},
        ],
        "sort_by": "relevance_then_time",
    },
    "full_stack": {
        "name": "全栈开发",
        "include_projects": [
            {"field": "responsibility_focus", "contains": ["implementation", "architecture"]},
        ],
        "exclude_projects": [
            {"field": "data_domain", "pattern": ".*爬虫.*"},
        ],
        "sort_by": "relevance_then_time",
    },
    "ai_development": {
        "name": "AI应用开发",
        "include_projects": [
            {"field": "ai_component_flag", "value": True},
        ],
        "exclude_projects": [],
        "sort_by": "relevance_then_time",
    },
    "product_manager": {
        "name": "Generative AI 产品经理",
        "include_projects": [
            {"field": "responsibility_focus", "contains": ["commercialization", "stakeholder_management"]},
            {"field": "decision_accountability", "contains": ["commercial_strategy", "risk_governance"]},
            {"field": "role_title", "pattern": ".*产品.*|.*Product.*"},
        ],
        "exclude_projects": [
            {"field": "role_title", "pattern": ".*(测试|运维).*"},
        ],
        "sort_by": "relevance_then_time",
    },
}
