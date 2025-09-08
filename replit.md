# Parameter Checker System

## Overview

This is a Python-based parameter validation system designed for network configuration management. The system validates network parameters (particularly airspace/radio configurations) against a knowledge base stored in Excel files. It features a ParameterChecker class that can handle both single-value and multi-value parameters (like switch groups), with intelligent error aggregation that generates one error per parameter per row while consolidating multiple switch errors.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Components

**ParameterChecker Class**
- Main validation engine that processes parameters against knowledge base rules
- Supports both single-value and multi-value parameter validation
- Implements error aggregation to avoid duplicate error reporting
- Handles numeric type conversion issues that commonly occur with Excel data

**Knowledge Base System**
- Excel-based parameter knowledge storage using "参数知识库.xlsx"
- Default sheet "空域配置" (Airspace Configuration) for network parameters
- Schema includes: MO名称, 参数名称, 参数ID, 期望值, 参数含义, 条件表达式, 参数类型
- Forced string type conversion during Excel reading to prevent float conversion issues

**Data Processing Pipeline**
- Pandas-based Excel file processing with custom converters
- Type-safe parameter loading with validation of required columns
- Error collection and logging system with structured error reporting

### Design Patterns

**Singleton Knowledge Base**
- Parameter knowledge loaded once during initialization
- Cached in memory for efficient repeated validations
- Column validation ensures data integrity before processing

**Error Aggregation Strategy**
- Single error per parameter per row approach
- Multi-switch errors consolidated into unified error objects
- Prevents error spam while maintaining detailed diagnostics

### Data Flow

1. Excel knowledge base loaded and validated at startup
2. Parameter data processed through validation rules
3. Errors collected and aggregated per parameter
4. Results logged with structured formatting

## External Dependencies

**Core Python Libraries**
- `pandas`: Excel file processing and data manipulation
- `logging`: Structured logging and error tracking
- `typing`: Type hints for code clarity and validation

**File Dependencies**
- Excel files (.xlsx format) for parameter knowledge base storage
- Log files for runtime error tracking and debugging

**Data Sources**
- Parameter knowledge base Excel files with network configuration rules
- Input parameter data for validation (format determined by implementation)