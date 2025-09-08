#!/usr/bin/env python3
"""
参数核查系统 - 重新设计版本
支持双分表结构、复杂条件表达式、嵌套验证规则
Parameter Checker System - Redesigned Version
Supports dual-table structure, complex condition expressions, nested validation rules
"""

import pandas as pd
import logging
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('parameter_checker.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class ParameterChecker:
    """
    参数核查器类 - 支持双分表结构和复杂嵌套验证
    """

    def __init__(self, knowledge_file="参数知识库.xlsx"):
        """初始化参数核查器"""
        self.knowledge_file = knowledge_file
        self.parameter_info: Dict[str, Dict[str, Any]] = {}  # 参数信息表
        self.validation_rules: Dict[str, Dict[str, Any]] = {}  # 验证规则表
        
        # 加载知识库
        self.load_knowledge_base(knowledge_file)

    def load_knowledge_base(self, file_path: str) -> bool:
        """加载双分表知识库"""
        try:
            # 加载参数信息表
            param_success = self.load_parameter_info(file_path, "参数信息")
            # 加载验证规则表
            rule_success = self.load_validation_rules(file_path, "验证规则")
            
            if param_success and rule_success:
                logger.info(f"知识库加载成功: {len(self.parameter_info)}个参数, {len(self.validation_rules)}个验证规则")
                return True
            else:
                logger.warning("知识库加载部分失败")
                return False
                
        except FileNotFoundError:
            logger.info(f"文件 {file_path} 不存在，正在生成示例文件...")
            # 生成示例文件
            self.create_sample_excel()
            # 重新加载
            try:
                param_success = self.load_parameter_info(file_path, "参数信息")
                rule_success = self.load_validation_rules(file_path, "验证规则")
                if param_success and rule_success:
                    logger.info(f"示例知识库加载成功: {len(self.parameter_info)}个参数, {len(self.validation_rules)}个验证规则")
                    return True
            except Exception as e:
                logger.error(f"重新加载知识库失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"加载知识库失败: {str(e)}")
            return False

    def load_parameter_info(self, file_path: str, sheet_name: str) -> bool:
        """加载参数信息表"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
            
            # 验证必要列
            required_columns = ['MO名称', 'MO描述', '场景类型', '参数名称', '参数ID', '参数类型', '参数含义', '值描述']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.error(f"参数信息表缺少必要列: {missing_columns}")
                return False

            self.parameter_info = {}
            
            # 按MO名称和参数名称分组
            for (mo_name, param_name), group in df.groupby(['MO名称', '参数名称'], dropna=False):
                # 使用第一行的信息
                row = group.iloc[0]
                
                # 初始化MO信息
                if mo_name not in self.parameter_info:
                    self.parameter_info[mo_name] = {
                        'mo_description': str(row.get('MO描述', '')).strip(),
                        'scenario': str(row.get('场景类型', '')).strip(),
                        'parameters': {}
                    }
                
                # 添加参数信息
                param_type = str(row.get('参数类型', 'single')).strip()
                self.parameter_info[mo_name]['parameters'][param_name] = {
                    'parameter_id': str(row.get('参数ID', '')).strip(),
                    'parameter_type': param_type,
                    'parameter_description': str(row.get('参数含义', '')).strip(),
                    'value_description': str(row.get('值描述', '')).strip()
                }
            
            logger.info(f"参数信息表加载成功: {len(self.parameter_info)} 个MO")
            return True
            
        except FileNotFoundError:
            raise  # 重新抛出FileNotFoundError让上层处理
        except Exception as e:
            logger.error(f"加载参数信息表失败: {str(e)}")
            return False

    def load_validation_rules(self, file_path: str, sheet_name: str) -> bool:
        """加载验证规则表"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
            
            # 验证必要列
            required_columns = ['校验ID', '校验类型', 'MO名称', '条件表达式', '期望值表达式', '错误描述', '继续校验ID']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.error(f"验证规则表缺少必要列: {missing_columns}")
                return False

            self.validation_rules = {}
            
            for _, row in df.iterrows():
                rule_id = str(row.get('校验ID', '')).strip()
                if not rule_id or rule_id == 'nan':
                    continue
                    
                self.validation_rules[rule_id] = {
                    'rule_id': rule_id,
                    'check_type': str(row.get('校验类型', '')).strip(),
                    'mo_name': str(row.get('MO名称', '')).strip(),
                    'condition_expression': str(row.get('条件表达式', '')).strip(),
                    'expected_expression': str(row.get('期望值表达式', '')).strip(),
                    'error_description': str(row.get('错误描述', '')).strip(),
                    'next_check_id': str(row.get('继续校验ID', '')).strip() if str(row.get('继续校验ID', '')).strip() != 'nan' else None
                }
            
            logger.info(f"验证规则表加载成功: {len(self.validation_rules)} 个规则")
            return True
            
        except FileNotFoundError:
            raise  # 重新抛出FileNotFoundError让上层处理
        except Exception as e:
            logger.error(f"加载验证规则表失败: {str(e)}")
            return False

    def parse_condition_expression(self, expression: str, data_row: Dict[str, Any]) -> bool:
        """
        解析复杂条件表达式
        支持格式: (参数名1=值1and参数名2=值2)or(参数名3>值3and参数名2!=值2)
        """
        if not expression or expression == 'nan':
            return True
            
        try:
            # 替换中文逻辑运算符
            expression = expression.replace('and', ' and ').replace('or', ' or ')
            expression = expression.replace('且', ' and ').replace('或', ' or ')
            
            # 解析单个条件
            def evaluate_single_condition(cond: str) -> bool:
                cond = cond.strip()
                
                # 支持的运算符
                operators = ['>=', '<=', '!=', '=', '>', '<']
                
                for op in operators:
                    if op in cond:
                        parts = cond.split(op, 1)
                        if len(parts) == 2:
                            param_name = parts[0].strip()
                            expected_value = parts[1].strip()
                            
                            # 获取实际值
                            actual_value = str(data_row.get(param_name, '')).strip()
                            
                            # 执行比较
                            return self._compare_values(actual_value, op, expected_value)
                
                logger.warning(f"无法解析条件: {cond}")
                return False
            
            # 处理括号和逻辑运算符
            # 简化处理：先替换括号内的条件
            def evaluate_expression(expr: str) -> bool:
                # 处理括号
                while '(' in expr:
                    # 找到最内层括号
                    start = expr.rfind('(')
                    end = expr.find(')', start)
                    if end == -1:
                        break
                    
                    # 评估括号内的表达式
                    inner_expr = expr[start+1:end]
                    result = self._evaluate_simple_expression(inner_expr, evaluate_single_condition)
                    
                    # 替换括号
                    expr = expr[:start] + str(result) + expr[end+1:]
                
                # 评估剩余表达式
                return self._evaluate_simple_expression(expr, evaluate_single_condition)
            
            return evaluate_expression(expression)
            
        except Exception as e:
            logger.error(f"解析条件表达式失败: {expression}, 错误: {str(e)}")
            return False

    def _evaluate_simple_expression(self, expr: str, eval_func) -> bool:
        """评估简单表达式（不含括号）"""
        expr = expr.strip()
        
        # 处理 or 运算符
        if ' or ' in expr:
            parts = expr.split(' or ')
            return any(self._evaluate_simple_expression(part.strip(), eval_func) for part in parts)
        
        # 处理 and 运算符
        if ' and ' in expr:
            parts = expr.split(' and ')
            return all(self._evaluate_simple_expression(part.strip(), eval_func) for part in parts)
        
        # 处理布尔值
        if expr.lower() == 'true':
            return True
        elif expr.lower() == 'false':
            return False
        
        # 单个条件
        return eval_func(expr)

    def _compare_values(self, actual: str, operator: str, expected: str) -> bool:
        """比较两个值"""
        try:
            # 尝试数值比较
            try:
                actual_num = float(actual)
                expected_num = float(expected)
                
                if operator == '=':
                    return actual_num == expected_num
                elif operator == '!=':
                    return actual_num != expected_num
                elif operator == '>':
                    return actual_num > expected_num
                elif operator == '<':
                    return actual_num < expected_num
                elif operator == '>=':
                    return actual_num >= expected_num
                elif operator == '<=':
                    return actual_num <= expected_num
            except ValueError:
                # 字符串比较
                if operator == '=':
                    return actual == expected
                elif operator == '!=':
                    return actual != expected
                else:
                    # 字符串不支持大小比较
                    logger.warning(f"字符串不支持运算符 {operator}: {actual} {operator} {expected}")
                    return False
                    
        except Exception as e:
            logger.error(f"值比较失败: {actual} {operator} {expected}, 错误: {str(e)}")
            return False
        
        return False

    def parse_expected_expression(self, expression: str) -> List[Dict[str, Any]]:
        """
        解析期望值表达式
        支持格式: 参数名1=值1,参数名2=值2 或 参数名1=k1:开&k2:关&k3:开
        """
        expected_params = []
        
        if not expression or expression == 'nan':
            return expected_params
        
        # 按逗号分割多个参数
        param_expressions = [expr.strip() for expr in expression.split(',') if expr.strip()]
        
        for param_expr in param_expressions:
            if '=' in param_expr:
                param_name, param_value = param_expr.split('=', 1)
                param_name = param_name.strip()
                param_value = param_value.strip()
                
                # 检查是否是多值参数（包含开关组合）
                if '&' in param_value and ':' in param_value:
                    # 多值参数
                    switches = {}
                    for switch_expr in param_value.split('&'):
                        if ':' in switch_expr:
                            switch_name, switch_state = switch_expr.split(':', 1)
                            switches[switch_name.strip()] = switch_state.strip()
                    
                    expected_params.append({
                        'param_name': param_name,
                        'param_type': 'multiple',
                        'expected_switches': switches,
                        'expected_value': param_value
                    })
                else:
                    # 单值参数
                    expected_params.append({
                        'param_name': param_name,
                        'param_type': 'single',
                        'expected_value': param_value
                    })
        
        return expected_params

    def execute_validation_rule(self, rule_id: str, data_groups: Dict[str, pd.DataFrame], sector_id: str) -> List[Dict[str, Any]]:
        """执行单个验证规则"""
        if rule_id not in self.validation_rules:
            logger.warning(f"验证规则 {rule_id} 不存在")
            return []
        
        rule = self.validation_rules[rule_id]
        errors = []
        
        logger.info(f"执行验证规则: {rule_id} ({rule['check_type']})")
        
        # 根据校验类型执行不同的验证
        if rule['check_type'] == '漏配':
            errors.extend(self._check_missing_config(rule, data_groups, sector_id))
        elif rule['check_type'] == '错配':
            errors.extend(self._check_incorrect_config(rule, data_groups, sector_id))
        else:
            logger.warning(f"未知的校验类型: {rule['check_type']}")
        
        # 如果当前规则通过且有继续校验，执行继续校验
        if not errors and rule['next_check_id']:
            logger.info(f"规则 {rule_id} 通过，继续执行: {rule['next_check_id']}")
            errors.extend(self.execute_validation_rule(rule['next_check_id'], data_groups, sector_id))
        elif errors:
            logger.info(f"规则 {rule_id} 检查失败，不继续后续验证")
        
        return errors

    def _check_missing_config(self, rule: Dict[str, Any], data_groups: Dict[str, pd.DataFrame], sector_id: str) -> List[Dict[str, Any]]:
        """检查漏配"""
        mo_name = rule['mo_name']
        condition_expr = rule['condition_expression']
        expected_expr = rule['expected_expression']
        
        errors = []
        
        if mo_name not in data_groups:
            errors.append({
                'sector_id': sector_id,
                'rule_id': rule['rule_id'],
                'mo_name': mo_name,
                'check_type': '漏配',
                'error_type': '数据不存在',
                'message': f'{mo_name}数据不存在',
                'error_description': rule['error_description']
            })
            return errors
        
        mo_data = data_groups[mo_name]
        expected_params = self.parse_expected_expression(expected_expr)
        
        if not expected_params:
            logger.warning(f"规则 {rule['rule_id']} 没有有效的期望值表达式")
            return errors
        
        # 检查是否存在符合条件的记录
        found_matching_record = False
        
        for _, row in mo_data.iterrows():
            row_dict = row.to_dict()
            row_dict = {k: str(v).strip() for k, v in row_dict.items()}
            
            # 检查条件表达式
            if not self.parse_condition_expression(condition_expr, row_dict):
                continue
            
            # 检查期望值
            all_params_match = True
            for expected_param in expected_params:
                param_name = expected_param['param_name']
                
                if param_name not in row_dict:
                    all_params_match = False
                    break
                
                if expected_param['param_type'] == 'multiple':
                    # 多值参数检查
                    actual_value = row_dict[param_name]
                    if not self._check_multi_value_match(actual_value, expected_param['expected_switches']):
                        all_params_match = False
                        break
                else:
                    # 单值参数检查
                    if row_dict[param_name] != expected_param['expected_value']:
                        all_params_match = False
                        break
            
            if all_params_match:
                found_matching_record = True
                break
        
        if not found_matching_record:
            param_names = [p['param_name'] for p in expected_params]
            errors.append({
                'sector_id': sector_id,
                'rule_id': rule['rule_id'],
                'mo_name': mo_name,
                'param_names': param_names,
                'check_type': '漏配',
                'error_type': '漏配',
                'message': f'未找到符合条件的配置记录',
                'condition': condition_expr,
                'expected_expression': expected_expr,
                'error_description': rule['error_description']
            })
        
        return errors

    def _check_incorrect_config(self, rule: Dict[str, Any], data_groups: Dict[str, pd.DataFrame], sector_id: str) -> List[Dict[str, Any]]:
        """检查错配"""
        mo_name = rule['mo_name']
        condition_expr = rule['condition_expression']
        expected_expr = rule['expected_expression']
        
        errors = []
        
        if mo_name not in data_groups:
            return errors  # 数据不存在时不报错配错误
        
        mo_data = data_groups[mo_name]
        expected_params = self.parse_expected_expression(expected_expr)
        
        if not expected_params:
            logger.warning(f"规则 {rule['rule_id']} 没有有效的期望值表达式")
            return errors
        
        # 检查每条记录
        for idx, row in mo_data.iterrows():
            row_dict = row.to_dict()
            row_dict = {k: str(v).strip() for k, v in row_dict.items()}
            
            # 检查条件表达式
            if not self.parse_condition_expression(condition_expr, row_dict):
                continue
            
            # 检查期望值
            for expected_param in expected_params:
                param_name = expected_param['param_name']
                
                if param_name not in row_dict:
                    continue
                
                if expected_param['param_type'] == 'multiple':
                    # 多值参数检查
                    actual_value = row_dict[param_name]
                    if not self._check_multi_value_match(actual_value, expected_param['expected_switches']):
                        errors.append({
                            'sector_id': sector_id,
                            'rule_id': rule['rule_id'],
                            'mo_name': mo_name,
                            'param_name': param_name,
                            'check_type': '错配',
                            'error_type': '错配',
                            'message': f'{param_name}配置错误',
                            'current_value': actual_value,
                            'expected_value': expected_param['expected_value'],
                            'condition': condition_expr,
                            'error_description': rule['error_description'],
                            'row_index': idx
                        })
                else:
                    # 单值参数检查
                    if row_dict[param_name] != expected_param['expected_value']:
                        errors.append({
                            'sector_id': sector_id,
                            'rule_id': rule['rule_id'],
                            'mo_name': mo_name,
                            'param_name': param_name,
                            'check_type': '错配',
                            'error_type': '错配',
                            'message': f'{param_name}配置错误',
                            'current_value': row_dict[param_name],
                            'expected_value': expected_param['expected_value'],
                            'condition': condition_expr,
                            'error_description': rule['error_description'],
                            'row_index': idx
                        })
        
        return errors

    def _check_multi_value_match(self, actual_value: str, expected_switches: Dict[str, str]) -> bool:
        """检查多值参数是否匹配"""
        if not actual_value or not expected_switches:
            return False
        
        # 解析实际值中的开关状态
        actual_switches = {}
        for switch_expr in actual_value.split('&'):
            if ':' in switch_expr:
                switch_name, switch_state = switch_expr.split(':', 1)
                actual_switches[switch_name.strip()] = switch_state.strip()
        
        # 检查每个期望的开关状态
        for switch_name, expected_state in expected_switches.items():
            if switch_name not in actual_switches:
                return False
            if actual_switches[switch_name] != expected_state:
                return False
        
        return True

    def validate_sector_data(self, data_groups: Dict[str, pd.DataFrame], sector_id: str) -> List[Dict[str, Any]]:
        """验证扇区数据"""
        all_errors = []
        
        # 找到所有入口验证规则（没有被其他规则引用的规则）
        referenced_rules = set()
        for rule in self.validation_rules.values():
            if rule['next_check_id']:
                referenced_rules.add(rule['next_check_id'])
        
        entry_rules = [rule_id for rule_id in self.validation_rules.keys() 
                      if rule_id not in referenced_rules]
        
        logger.info(f"发现 {len(entry_rules)} 个入口验证规则: {entry_rules}")
        
        # 执行每个入口规则
        for rule_id in entry_rules:
            errors = self.execute_validation_rule(rule_id, data_groups, sector_id)
            all_errors.extend(errors)
        
        return all_errors

    def create_sample_excel(self) -> None:
        """创建示例Excel文件"""
        logger.info("正在生成示例参数知识库...")
        
        wb = Workbook()
        
        # 删除默认工作表
        wb.remove(wb.active)
        
        # 创建参数信息表
        self._create_parameter_info_sheet(wb)
        
        # 创建验证规则表
        self._create_validation_rules_sheet(wb)
        
        # 保存文件
        wb.save(self.knowledge_file)
        logger.info(f"示例参数知识库已生成: {self.knowledge_file}")

    def _create_parameter_info_sheet(self, wb: Workbook) -> None:
        """创建参数信息表"""
        ws = wb.create_sheet("参数信息")
        
        # 设置表头
        headers = ['MO名称', 'MO描述', '场景类型', '参数名称', '参数ID', '参数类型', '参数含义', '值描述']
        ws.append(headers)
        
        # 设置表头样式
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
        
        # 添加示例数据
        sample_data = [
            # NRCELL参数
            ["NRCELL", "5G小区对象", "5G基础配置", "跟踪区码", "tac", "single", "标识小区所属的跟踪区", ""],
            ["NRCELL", "5G小区对象", "5G基础配置", "小区状态", "cellState", "single", "小区的激活状态", ""],
            
            # NRDUCELL参数
            ["NRDUCELL", "5G DU小区对象", "5G物理层配置", "小区半径(米)", "cellRadius", "single", "小区覆盖半径", ""],
            ["NRDUCELL", "5G DU小区对象", "5G物理层配置", "最大传输功率", "maxTxPower", "single", "小区最大发射功率", ""],
            
            # NRDUCELLBEAM参数（多值参数）
            ["NRDUCELLBEAM", "5G波束配置对象", "5G波束管理", "波束开关组合", "beamSwitchComb", "multiple", "波束开关状态组合", "beam1:第一波束开关,beam2:第二波束开关,beam3:第三波束开关"],
            
            # NRCELLFREQRELATION参数
            ["NRCELLFREQRELATION", "小区频率关系对象", "频率管理配置", "连接态频率优先级", "connectedFreqPriority", "single", "连接态下的频率优先级", ""],
        ]
        
        for row_data in sample_data:
            ws.append(row_data)
        
        # 自动调整列宽
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

    def _create_validation_rules_sheet(self, wb: Workbook) -> None:
        """创建验证规则表"""
        ws = wb.create_sheet("验证规则")
        
        # 设置表头
        headers = ['校验ID', '校验类型', 'MO名称', '条件表达式', '期望值表达式', '错误描述', '继续校验ID']
        ws.append(headers)
        
        # 设置表头样式
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
        
        # 添加示例验证规则
        sample_rules = [
            # 复杂嵌套验证链示例
            ["MISS_001", "漏配", "NRCELL", "", "跟踪区码=100", "缺少跟踪区码为100的小区配置", "ERROR_001"],
            ["ERROR_001", "错配", "NRDUCELL", "跟踪区码=100", "小区半径(米)=500", "跟踪区码为100的小区，半径应配置为500米", "ERROR_002"],
            ["ERROR_002", "错配", "NRDUCELL", "跟踪区码=100and小区半径(米)=500", "最大传输功率=43", "半径500米的小区，功率应为43dBm", "ERROR_003"],
            ["ERROR_003", "错配", "NRDUCELLBEAM", "跟踪区码=100", "波束开关组合=beam1:开&beam2:关&beam3:开", "跟踪区码100的小区，波束组合应为beam1开beam2关beam3开", "MISS_002"],
            ["MISS_002", "漏配", "NRCELLFREQRELATION", "跟踪区码=100", "连接态频率优先级=1", "缺少跟踪区码100小区的频率优先级配置", "ERROR_004"],
            ["ERROR_004", "错配", "NRCELL", "跟踪区码=100and连接态频率优先级=1", "小区状态=激活", "已配置频率优先级的小区状态应为激活", ""],
            
            # 复杂条件示例
            ["COMPLEX_001", "错配", "NRDUCELL", "(跟踪区码=200or跟踪区码=300)and小区状态=激活", "小区半径(米)=1000", "特殊跟踪区的激活小区半径应为1000米", ""],
            ["COMPLEX_002", "漏配", "NRCELL", "小区半径(米)>500and最大传输功率>=40", "小区状态=激活", "大半径高功率小区必须激活", ""],
        ]
        
        for row_data in sample_rules:
            ws.append(row_data)
        
        # 自动调整列宽
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 60)
            ws.column_dimensions[column_letter].width = adjusted_width

    def run_validation_example(self) -> None:
        """运行验证示例"""
        logger.info("🧪 开始验证示例测试...")
        
        # 创建测试数据
        test_data = {
            "NRCELL": pd.DataFrame([
                {
                    "f_site_id": "13566583",
                    "f_cell_id": "1",
                    "跟踪区码": "200",  # 不符合期望值100
                    "小区状态": "激活",
                    "连接态频率优先级": "1"
                },
                {
                    "f_site_id": "13566583", 
                    "f_cell_id": "2",
                    "跟踪区码": "100",  # 符合期望值
                    "小区状态": "非激活",  # 可能触发后续错配
                    "连接态频率优先级": "1"
                },
                {
                    "f_site_id": "13566583", 
                    "f_cell_id": "3",
                    "跟踪区码": "300",  # 用于复杂条件测试
                    "小区状态": "激活",
                    "连接态频率优先级": "2"
                }
            ]),
            "NRDUCELL": pd.DataFrame([
                {
                    "f_site_id": "13566583",
                    "f_cell_id": "1",
                    "跟踪区码": "200",
                    "小区半径(米)": "1200",  # 用于复杂条件测试
                    "最大传输功率": "40",
                    "小区状态": "激活"
                },
                {
                    "f_site_id": "13566583",
                    "f_cell_id": "2",
                    "跟踪区码": "100",
                    "小区半径(米)": "300",  # 不符合期望的500
                    "最大传输功率": "40",
                    "小区状态": "非激活"
                },
                {
                    "f_site_id": "13566583",
                    "f_cell_id": "3",
                    "跟踪区码": "300",
                    "小区半径(米)": "800",  # 不符合复杂条件的期望1000
                    "最大传输功率": "42",
                    "小区状态": "激活"
                }
            ]),
            "NRDUCELLBEAM": pd.DataFrame([
                {
                    "f_site_id": "13566583",
                    "f_cell_id": "2",
                    "跟踪区码": "100",
                    "波束开关组合": "beam1:关&beam2:开&beam3:关"  # 不符合期望的beam1:开&beam2:关&beam3:开
                }
            ]),
            "NRCELLFREQRELATION": pd.DataFrame([
                {
                    "f_site_id": "13566583",
                    "f_cell_id": "2",
                    "跟踪区码": "100",
                    "连接态频率优先级": "1"  # 符合期望
                }
            ])
        }
        
        # 执行验证
        errors = self.validate_sector_data(test_data, "test_sector_001")
        
        # 输出结果
        if errors:
            logger.info(f"🔍 发现 {len(errors)} 个验证问题:")
            for i, error in enumerate(errors, 1):
                logger.info(f"   {i}. 【{error['check_type']}】{error.get('rule_id', 'N/A')} - {error['mo_name']}")
                if 'param_name' in error:
                    logger.info(f"      参数: {error['param_name']}")
                if 'param_names' in error:
                    logger.info(f"      参数: {', '.join(error['param_names'])}")
                logger.info(f"      错误: {error['message']}")
                if 'current_value' in error and 'expected_value' in error:
                    logger.info(f"      期望值: {error['expected_value']}")
                    logger.info(f"      实际值: {error['current_value']}")
                if error.get('error_description'):
                    logger.info(f"      说明: {error['error_description']}")
                logger.info("")
        else:
            logger.info("✅ 所有验证规则都通过了")


def main():
    """主程序入口"""
    try:
        logger.info("🚀 启动参数核查系统...")
        
        # 创建参数核查器实例
        checker = ParameterChecker()
        
        # 运行验证示例
        checker.run_validation_example()
        
        logger.info("✨ 参数核查系统运行完成！")
        logger.info("📋 系统特性:")
        logger.info("   • 双分表设计：参数信息与验证规则完全分离")
        logger.info("   • 复杂条件支持：(param1=value1and param2=value2)or(param3>value3)")
        logger.info("   • 嵌套验证链：支持漏配↔错配无限嵌套调用") 
        logger.info("   • 多值参数处理：beam1:开&beam2:关&beam3:开格式")
        logger.info("   • 智能条件筛选：先筛选符合条件的行再进行验证")
        
        return True
        
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)