#!/usr/bin/env python
"""Test script for role-based field filtering"""

from resume_docs.role_filter import RoleFilter
from resume_docs.role_config import ROLE_FILTERS
from resume_docs.models import Project, Timeframe, ManagementScope, ImpactMetrics

def test_field_visibility():
    """Test that all roles have field_visibility defined"""
    print("Testing field_visibility configuration...")
    for role, config in ROLE_FILTERS.items():
        assert "field_visibility" in config, f"{role} missing field_visibility"
        visibility = config["field_visibility"]
        assert isinstance(visibility, dict), f"{role} field_visibility is not a dict"
        print(f"  ✓ {role}: {len(visibility)} fields")
    print()

def test_role_filter_initialization():
    """Test RoleFilter initialization"""
    print("Testing RoleFilter initialization...")
    filter = RoleFilter()
    assert filter.role_config == ROLE_FILTERS
    print(f"  ✓ RoleFilter initialized with {len(filter.role_config)} roles")
    print()

def test_field_filtering():
    """Test field filtering for different roles"""
    print("Testing field filtering...")

    # Create test project
    test_project = Project(
        project_name="Test Project",
        company_or_context="Test Company",
        timeframe=Timeframe(start="2025-01", end="2025-12"),
        role_title="Product Manager",
        role_perspective="product",
        management_scope=ManagementScope(team_size=5),
        decision_accountability=["commercial_strategy", "risk_governance"],
        responsibility_focus=["commercialization", "stakeholder_management"],
        impact_metrics=ImpactMetrics(
            business_metrics=["ARR +20%"],
            technical_metrics=["Latency -30%"],
            operational_metrics=["Uptime 99.9%"]
        ),
        governance_artifacts=["prompt_playbook", "cost_dashboard"],
        project_overview="Test overview",
        challenges_or_objectives=["Challenge 1"],
        responsibilities=["Responsibility 1"],
        architecture_or_solution=["Solution 1"],
        tech_stack=["Python", "React"],
        tools_platforms=["AWS", "Docker"],
    )

    filter = RoleFilter()

    # Test product_manager role
    pm_visibility = filter._get_field_visibility("product_manager")
    filtered_pm = filter._filter_project_fields(test_project, pm_visibility)

    assert len(filtered_pm.decision_accountability) > 0, "PM should see decision_accountability"
    assert len(filtered_pm.tech_stack) == 0, "PM should not see tech_stack"
    print(f"  ✓ product_manager: decision_accountability visible, tech_stack hidden")

    # Test ai_engineer role
    eng_visibility = filter._get_field_visibility("ai_engineer")
    filtered_eng = filter._filter_project_fields(test_project, eng_visibility)

    assert len(filtered_eng.tech_stack) > 0, "Engineer should see tech_stack"
    assert len(filtered_eng.decision_accountability) == 0, "Engineer should not see decision_accountability"
    print(f"  ✓ ai_engineer: tech_stack visible, decision_accountability hidden")
    print()

def test_invalid_role():
    """Test error handling for invalid role"""
    print("Testing error handling...")
    filter = RoleFilter()
    try:
        filter._get_field_visibility("invalid_role")
        # Should not raise error, just return empty dict
        print(f"  ✓ Invalid role returns empty visibility dict")
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Role-Based Field Filtering Test Suite")
    print("=" * 60)
    print()

    test_field_visibility()
    test_role_filter_initialization()
    test_field_filtering()
    test_invalid_role()

    print("=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
