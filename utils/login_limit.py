import time
from flask import session

# 登录尝试记录，格式：{'ip': {'attempts': count, 'last_attempt': timestamp}}
login_attempts = {}

def check_login_limit(ip_address, max_attempts=5, lockout_time=300):
    """
    检查登录限制
    :param ip_address: IP地址
    :param max_attempts: 最大尝试次数
    :param lockout_time: 锁定时间（秒）
    :return: (是否允许登录, 剩余等待时间)
    """
    current_time = time.time()
    ip_record = login_attempts.get(ip_address, {'attempts': 0, 'last_attempt': 0})
    
    # 如果已经过了锁定时间，重置尝试次数
    if current_time - ip_record['last_attempt'] > lockout_time:
        ip_record['attempts'] = 0
    
    # 如果超过最大尝试次数
    if ip_record['attempts'] >= max_attempts:
        wait_time = lockout_time - (current_time - ip_record['last_attempt'])
        if wait_time > 0:
            return False, int(wait_time)
        # 锁定时间已过，重置尝试次数
        ip_record['attempts'] = 0
    
    return True, 0

def record_login_attempt(ip_address, success):
    """
    记录登录尝试
    :param ip_address: IP地址
    :param success: 是否登录成功
    """
    if ip_address not in login_attempts:
        login_attempts[ip_address] = {'attempts': 0, 'last_attempt': 0}
    
    if success:
        # 登录成功，清除记录
        login_attempts[ip_address]['attempts'] = 0
    else:
        # 登录失败，增加尝试次数
        login_attempts[ip_address]['attempts'] += 1
        login_attempts[ip_address]['last_attempt'] = time.time()

def get_remaining_attempts(ip_address, max_attempts=5):
    """
    获取剩余的登录尝试次数
    :param ip_address: IP地址
    :param max_attempts: 最大尝试次数
    :return: 剩余尝试次数
    """
    if ip_address not in login_attempts:
        return max_attempts
    return max_attempts - login_attempts[ip_address]['attempts']
