# Role-Based Field Filtering Redesign for resume_docs/role_filter.py

## Overview
Redesign `role_filter.py` to implement role-aware field-level filtering. Different roles will see different subsets of Project fields based on their perspective, while maintaining the same project list. The filtering rules are dynamically inferred from `role_config.py` include/exclude rules.

## Current State
- `role_filter.py` currently disables all filtering and returns complete ResumeDocument for all roles
- `role_config.py` defines `include_projects`, `exclude_projects`, and `persona` for each role
- Project model has 20+ fields including governance_artifacts, decision_accountability, responsibility_focus, etc.

## Design Approach

### 1. Field Visibility Mapping Strategy
- **Source of truth**: `role_config.py` include/exclude rules determine which fields are relevant to each role
- **Logic**: If a role's include rules reference fields like `decision_accountability` or `governance_artifacts`, those fields should be visible; others hidden
- **Implementation**: Add `field_visibility` dict to each role config that maps field names to visibility (True/False)

### 2. Field Visibility Definition in role_config.py
For each role, add a `field_visibility` section that explicitly lists which Project fields should be visible:

```python
"field_visibility": {
    "governance_artifacts": True,
    "decision_accountability": True,
    "responsibility_focus": True,
    "impact_metrics": True,
    "management_scope": True,
    "role_perspective": True,
    # ... other fields
}
```

**Rationale**:
- Explicit definition is clearer than trying to infer from rules
- Easy to maintain and review
- Supports future role additions without code changes

### 3. role_filter.py Implementation
Modify `RoleFilter.filter_resume()` to:
1. Validate role exists in ROLE_FILTERS
2. Get field_visibility config for the role
3. For each project in resume.projects:
   - Create a new Project instance with only visible fields
   - Set hidden fields to None or empty defaults
4. Return modified ResumeDocument with filtered projects

**Key methods**:
- `_get_field_visibility(role: str) -> dict`: Extract field_visibility from role config
- `_filter_project_fields(project: Project, visibility: dict) -> Project`: Create new Project with only visible fields
- `_filter_projects(projects: List[Project], visibility: dict) -> List[Project]`: Apply filtering to all projects

### 4. Handling Field Defaults
When a field is hidden:
- String fields → None
- List fields → empty list []
- Object fields (ManagementScope, ImpactMetrics, Timeframe) → empty instance or None
- Boolean fields → None

### 5. Integration Points
- **docx_renderer.py**: Already handles None/empty fields gracefully (skips rendering)
- **llm_polisher.py**: Will only see visible fields, naturally adapts to role perspective
- **CLI**: No changes needed; filtering happens transparently in role_filter.py

## Implementation Steps

1. **Update role_config.py**
   - Add `field_visibility` dict to each existing role (data_development, full_stack, ai_development, product_manager, ai_product_designer, ai_engineer)
   - Define which fields are relevant to each role's perspective

2. **Refactor role_filter.py**
   - Implement `_get_field_visibility()` method
   - Implement `_filter_project_fields()` method to create filtered Project instances
   - Update `filter_resume()` to apply field filtering
   - Remove or keep disabled filtering methods for future use

3. **Validation**
   - Ensure all Project fields are accounted for in field_visibility configs
   - Test that filtered projects render correctly in DOCX
   - Verify LLM polishing works with filtered fields

## Files to Modify
1. `resume_docs/role_config.py` - Add field_visibility to each role
2. `resume_docs/role_filter.py` - Implement field-level filtering logic

## Expected Outcomes
- Each role sees only fields relevant to its perspective
- Project list remains the same (no project-level filtering)
- Renderer and polisher automatically adapt to visible fields
- Cleaner, more focused resume output per role
