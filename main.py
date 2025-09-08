#!/usr/bin/env python3
"""
参数核查系统主程序
Parameter Checker System Main Program
"""

import logging
from ParameterChecker import ParameterChecker

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('parameter_checker.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """主程序入口"""
    try:
        logger.info("启动参数核查系统...")
        
        # 第一步：生成新版本双分表Excel文件
        logger.info("生成示例参数知识库...")
        temp_checker = ParameterChecker()
        temp_checker.create_sample_excel()
        
        # 第二步：重新创建实例来测试新版本双分表结构加载
        logger.info("测试新版本双分表结构加载...")
        checker = ParameterChecker()
        
        if checker.validation_rules:
            logger.info(f"✅ 新版本双分表结构加载成功！")
            logger.info(f"   📋 加载了 {len(checker.parameter_knowledge)} 个MO配置")
            logger.info(f"   🔍 加载了 {len(checker.validation_rules)} 个验证规则")
            
            # 展示加载的验证规则
            logger.info("📝 验证规则链:")
            for rule_id, rule in checker.validation_rules.items():
                logger.info(f"   {rule_id}: {rule['check_type']} - {rule['mo_name']}.{rule['param_name']}")
                if rule['next_check']:
                    logger.info(f"      → 继续校验: {rule['next_check']}")
            
            # 第三步：测试验证功能
            logger.info("🧪 测试验证功能...")
            test_validation(checker)
            
        else:
            logger.warning("⚠️ 新版本双分表结构加载失败，使用老版本结构")
            logger.info("可能原因：Excel文件结构不符合新版本要求")
        
        logger.info("参数核查系统启动完成！")
        logger.info("已生成示例文件：参数知识库.xlsx")
        logger.info("✨ 新版本支持复杂的嵌套验证规则和条件表达式！")
        
        return True
        
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        return False

def test_validation(checker):
    """测试验证功能"""
    import pandas as pd
    
    # 创建测试数据
    test_data = {
        "NRCELL": pd.DataFrame([
            {
                "f_site_id": "13566583",
                "f_cell_id": "1",
                "跟踪区码": "200",  # 不符合期望值100，会触发漏配错误
                "小区状态": "激活"
            },
            {
                "f_site_id": "13566583", 
                "f_cell_id": "2",
                "跟踪区码": "100",  # 符合期望值，漏配检查会通过
                "小区状态": "非激活"  # 可能触发后续错配
            }
        ]),
        "NRDUCELL": pd.DataFrame([
            {
                "f_site_id": "13566583",
                "f_cell_id": "1",
                "小区半径(米)": "300",  # 不符合期望的500
                "最大传输功率": "40"
            },
            {
                "f_site_id": "13566583",
                "f_cell_id": "2", 
                "小区半径(米)": "500",  # 符合期望
                "最大传输功率": "43"   # 符合期望
            }
        ]),
        "NRDUCELLBEAM": pd.DataFrame([
            {
                "f_site_id": "13566583",
                "f_cell_id": "1",
                "波束开关组合": "beam1:关&beam2:开&beam3:关"  # 不符合期望的beam1:开&beam2:关&beam3:开
            }
        ])
    }
    
    # 执行新版本验证
    logger.info("执行新版本嵌套验证...")
    errors = checker.validate_with_new_rules(test_data, "test_sector_001")
    
    if errors:
        logger.info(f"🔍 发现 {len(errors)} 个验证问题:")
        for i, error in enumerate(errors, 1):
            logger.info(f"   {i}. 【{error['check_type']}】{error['mo_name']}.{error['param_name']}")
            logger.info(f"      错误: {error['message']}")
            logger.info(f"      期望值: {error['expected_value']}")
            logger.info(f"      实际值: {error['current_value']}")
            logger.info("")
    else:
        logger.info("✅ 所有验证规则都通过了")

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)