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
        
        # 创建参数核查器实例
        checker = ParameterChecker()
        
        # 生成示例Excel文件
        logger.info("生成示例参数知识库...")
        checker.create_sample_excel()
        
        logger.info("参数核查系统启动完成！")
        logger.info("已生成示例文件：参数知识库.xlsx")
        logger.info("请根据您的需求修改参数配置，然后使用 ParameterChecker 类进行参数核查。")
        
        return True
        
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)