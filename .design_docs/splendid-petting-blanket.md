# Generative AI PM Resume Project - Progress & Implementation Plan

## Current Status Summary (Nov 28, 2025)

### ✅ COMPLETED (Infrastructure Ready)

**1. Role Configuration System**
- 6 roles defined with filtering rules: `data_development`, `full_stack`, `ai_development`, `product_manager`, `ai_product_designer`, `ai_engineer`
- Each role has `include_projects` and `exclude_projects` rules based on:
  - `data_domain` (e.g., "数据|BI")
  - `responsibility_focus` (e.g., "commercialization", "stakeholder_management")
  - `decision_accountability` (e.g., "commercial_strategy", "risk_governance")
  - `role_title` patterns
  - `ai_component_flag`
- Sorting: `relevance_then_time` (newer projects first, weighted by rule matches)

**2. LLM Polisher Enhancement**
- Persona-aware prompting fully implemented
- `_get_persona_hint()` extracts language-specific instructions
- Persona guidance injected into both Chinese and English prompts
- GitHub link preservation working correctly

**3. CLI Integration**
- `--role` parameter required and validated
- Calls `role_filter.filter_resume()` but filtering currently disabled

**4. Role Filter Infrastructure (Built but Inactive)**
- Helper methods exist: `_filter_and_sort_projects()`, `_filter_work_experience()`, rule matching logic
- **Current issue:** `filter_resume()` returns unfiltered data for all roles
- **Fix needed:** Wire up filtering logic to actually apply include/exclude rules

**5. YAML Data Synchronized**
- 3 flagship projects with rich metadata for filtering:
  - MySixth TarotAI: hybrid role, commercialization + stakeholder_management, AI component
  - NGSE: hybrid role, planning + architecture + compliance + commercialization, AI component
  - Remedium BI: architect role, architecture + compliance, NO AI component
- Both Chinese and English versions aligned
- All enums validated against `.design_docs/role_mapping_guidelines.md`

### 📋 REMAINING WORK (3 Phases)

#### Phase 1: Activate RoleFilter (1-2 hours)
**Objective:** Wire up the filtering logic to actually apply include/exclude rules

**Tasks:**
1. **Modify `resume_docs/role_filter.py`:**
   - Update `filter_resume()` method to call `_filter_and_sort_projects()` with role config
   - Apply include/exclude rules based on role
   - Sort projects by relevance score (rule matches) then by time
   - Return filtered `ResumeDocument` with filtered projects and work experience

2. **Test filtering logic:**
   - Verify each role sees correct project subset:
     - `data_development`: projects with data/BI focus or AI components
     - `ai_development`: projects with AI components only
     - `product_manager`: projects with commercialization/stakeholder_management focus
     - `full_stack`: projects with implementation/architecture focus
   - Verify sorting by relevance (more matching rules = higher priority)

3. **Validate YAML data:**
   - Run `yamllint latest_resumes/*.yaml` (capture output)
   - Python safe-load script (verify all YAML parses)
   - Confirm all project metadata fields match role filtering criteria

**Success Criteria:**
- `filter_resume()` applies include/exclude rules correctly
- Each role sees appropriate project subset
- Projects sorted by relevance score
- All YAML validation passes

#### Phase 2: Multi-Role Acceptance Testing (2-3 hours)
**Objective:** Verify role-based filtering and persona effects work correctly

**Test Matrix:**
```
Roles: data_development, ai_development, product_manager, full_stack
Locales: zh-CN, en-US
Polishing: with/without LLM (skip-polish + model gpt-4o or glm-4-flash)
```

**Test Procedure per Role:**
1. Generate Chinese resume (no polish): `--template modern --locale zh-CN --role {role} --include-contact --skip-polish`
2. Generate Chinese resume (with polish): `--template modern --locale zh-CN --role {role} --include-contact --model glm-4-flash`
3. Generate English resume (no polish): `--template modern --locale en-US --role {role} --include-contact --skip-polish`
4. Generate English resume (with polish): `--template modern --locale en-US --role {role} --include-contact --model gpt-4o`
5. Verify DOCX renders correctly (open in Word/Google Docs)
6. Spot-check filtering results:
   - `data_development`: should see MySixth + NGSE (data/AI focus)
   - `ai_development`: should see MySixth + NGSE (AI components only)
   - `product_manager`: should see MySixth + NGSE (commercialization/stakeholder focus)
   - `full_stack`: should see MySixth + NGSE (implementation/architecture focus)
7. Verify persona effects in LLM-polished output

**Deliverables:**
- Screenshot/excerpt samples showing role-specific project filtering
- Confirmation that DOCX rendering works for all combinations
- List of any issues encountered

**Success Criteria:**
- All 16 DOCX files generate without errors
- Role-based filtering works correctly (each role sees appropriate projects)
- Persona effects visible in LLM-polished output
- No rendering issues in DOCX

#### Phase 3: Documentation & PR Packaging (1 hour)
**Objective:** Document changes and prepare for merge

**Tasks:**
1. Update documentation:
   - `CLAUDE.md`: Explain role-based filtering mechanism and persona guidance
   - `resume_docs/ROLE_FILTERS.md`: Document filtering rules for each role

2. Create PR summary:
   - Intent: "Activate role-based filtering with persona-aware LLM prompting"
   - Impacted files: `role_filter.py`, `CLAUDE.md`, `ROLE_FILTERS.md`
   - Validation output: yamllint + safe-load results
   - Test results: acceptance test matrix summary

3. Include in PR body:
   - Filtering rules for each role
   - Sample DOCX excerpts showing role-specific project selection
   - Validation commands and output

4. Merge to main branch

**Success Criteria:**
- PR clearly documents filtering logic and persona mechanism
- All validation passes
- Acceptance tests documented
- Ready for merge

---

## Architecture Overview

**Data Flow:**
```
YAML (3 projects with rich metadata)
  ↓
Loader (locale-aware: zh-CN or en-US)
  ↓
RoleFilter (applies include/exclude rules, sorts by relevance)
  ↓
LLMPolisher (injects persona guidance into prompts)
  ↓
DOCX Renderer (generates themed document)
```

**Key Design Decisions:**
1. **Role-based filtering:** Different roles see different project subsets based on include/exclude rules
   - `data_development`: data/BI focus or AI components
   - `ai_development`: AI components only
   - `product_manager`: commercialization/stakeholder_management focus
   - `full_stack`: implementation/architecture focus

2. **Persona-aware LLM prompting:** Each role gets different perspective guidance in LLM prompts
   - Product Manager: emphasizes metrics, commercialization, stakeholder alignment
   - AI Engineer: emphasizes technical architecture, implementation details
   - Data Engineer: emphasizes data platform, infrastructure, scalability

3. **Sorting:** Projects sorted by relevance score (how many include rules match) then by time (newer first)

---

## Critical Files to Modify

| File | Purpose | Status | Changes |
|------|---------|--------|---------|
| `resume_docs/role_filter.py` | Role-based filtering | 📋 Phase 1 | Wire up `filter_resume()` to apply include/exclude rules |
| `resume_docs/role_config.py` | Role definitions + filtering rules | ✅ Complete | No changes needed |
| `resume_docs/llm_polisher.py` | Persona-aware LLM prompting | ✅ Complete | No changes needed |
| `resume_docs/cli.py` | CLI integration | ✅ Complete | No changes needed |
| `latest_resumes/projects_summary.yaml` | Chinese project data | ✅ Complete | No changes needed |
| `latest_resumes/projects_summary_en.yaml` | English project data | ✅ Complete | No changes needed |
| `CLAUDE.md` | Project documentation | 📋 Phase 3 | Add role-based filtering explanation |
| `resume_docs/ROLE_FILTERS.md` | Role filtering documentation | 📋 Phase 3 | Document filtering rules for each role |

---

## Implementation Sequence

1. **Phase 1 (1-2 hours):** Activate RoleFilter
   - Modify `role_filter.py` to wire up filtering logic
   - Test filtering for each role
   - Validate YAML data

2. **Phase 2 (2-3 hours):** Acceptance Testing
   - Generate 16 DOCX files (4 roles × 2 locales × 2 polishing modes)
   - Verify role-based filtering works
   - Verify persona effects visible in output

3. **Phase 3 (1 hour):** Documentation & PR
   - Update `CLAUDE.md` and `ROLE_FILTERS.md`
   - Create PR with validation + test results
   - Merge to main

**Total estimated time:** 4-6 hours
