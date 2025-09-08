# Parameter Checker System

## Overview
This is a Python-based parameter checking system (参数核查系统) that validates network configuration parameters using Excel files as a knowledge base. The system supports complex validation rules with nested checking capabilities and multi-value parameter validation.

## Current State
- **Language**: Python 3.11
- **Dependencies**: pandas, openpyxl, xlsxwriter
- **Deployment**: Configured for VM deployment using uv
- **Status**: Fully functional and ready for use

## Project Architecture
- **main.py**: Entry point that initializes the system and runs validation tests
- **ParameterChecker.py**: Core validation engine with dual-table design support
- **参数知识库.xlsx**: Knowledge base Excel file containing parameter configurations and validation rules

## Key Features
1. **Dual-table design**: Parameter information and validation rules are completely separated
2. **Nested validation chains**: Supports complex validation flows like MISS_001→ERROR_001→ERROR_002
3. **Complex condition support**: Handles expressions like `(param1=value1 and param2=value2) or (param3>value3)`
4. **Multi-value parameters**: Supports beam switch combinations like `beam1:开&beam2:关&beam3:开`
5. **Alternating validation**: Supports infinite nesting of missing config ↔ incorrect config checks

## Recent Changes
- Fixed duplicate loop issue in ParameterChecker.py (2025-09-08)
- Set up Python environment with required dependencies
- Configured workflow for console output
- Set up VM deployment configuration
- Added comprehensive .gitignore for Python project

## Workflow Configuration
- **Name**: Parameter Checker
- **Command**: `uv run python main.py`
- **Output**: Console (shows validation logs and results)
- **Status**: Running successfully

## Deployment Configuration
- **Target**: VM (maintains state, suitable for long-running validation jobs)
- **Run Command**: `["uv", "run", "python", "main.py"]`

## Sample Output
The system generates detailed logs showing:
- Loading of MO configurations and validation rules
- Execution of nested validation chains
- Detection and reporting of configuration errors
- Generation of Excel knowledge base files