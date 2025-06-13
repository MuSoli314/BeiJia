#!/usr/bin/env python3
"""
验证码生成器 - 生成随机数字验证码
"""

import random

def get_ver_code():
    """
    生成6位数字验证码的便捷函数
    Returns:
        str: 生成的数字验证码
    """
    # 生成指定长度的随机数字验证码
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return code



# 使用示例
if __name__ == "__main__":
    # 生成6位验证码
    code = get_ver_code()
    print(f"生成的验证码: {code}")
