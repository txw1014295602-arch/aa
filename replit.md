# Parameter Checker System

## Overview
This is a Python-based parameter checking system (参数核查系统) that validates network configuration parameters using Excel files as a knowledge base. The system supports complex validation rules with nested checking capabilities and multi-value parameter validation.

## Current State
- **Language**: Python 3.11
- **Dependencies**: pandas, openpyxl, xlsxwriter
- **Deployment**: Configured for VM deployment using uv
- **Status**: Fully functional and ready for use

## Project Architecture
- **parameter_checker.py**: Single comprehensive file containing the complete parameter checking system
- **参数知识库.xlsx**: Knowledge base Excel file with dual-sheet structure:
  - **参数信息 sheet**: MO名称, MO描述, 场景类型, 参数名称, 参数ID, 参数类型, 参数含义, 值描述
  - **验证规则 sheet**: 校验ID, 校验类型, MO名称, 条件表达式, 期望值表达式, 错误描述, 继续校验ID

## Key Features
1. **Dual-table design**: Parameter information and validation rules are completely separated
2. **Nested validation chains**: Supports complex validation flows like MISS_001→ERROR_001→ERROR_002
3. **Complex condition support**: Handles expressions like `(param1=value1 and param2=value2) or (param3>value3)`
4. **Enhanced multi-value parameters**: 
   - Supports beam switch combinations like `beam1:开&beam2:关&beam3:开`
   - Switch-level error reporting with individual switch descriptions
   - Only validates specified switches from expected expression
   - Error descriptions only for wrong switches from value description
5. **Alternating validation**: Supports infinite nesting of missing config ↔ incorrect config checks
6. **Smart condition filtering**: Filters data rows matching conditions before validation

## Recent Changes
- Fixed duplicate loop issue in ParameterChecker.py (2025-09-08)
- Set up Python environment with required dependencies
- Configured workflow for console output
- Set up VM deployment configuration
- Added comprehensive .gitignore for Python project

## Workflow Configuration
- **Name**: Parameter Checker
- **Command**: `uv run python parameter_checker.py`
- **Output**: Console (shows validation logs and results)
- **Status**: Running successfully

## Deployment Configuration
- **Target**: VM (maintains state, suitable for long-running validation jobs)
- **Run Command**: `["uv", "run", "python", "parameter_checker.py"]`

## Sample Output
The system generates detailed logs showing:
- Loading of MO configurations and validation rules
- Execution of nested validation chains
- Detection and reporting of configuration errors
- Generation of Excel knowledge base files