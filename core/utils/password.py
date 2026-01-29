"""
Password - 密码工具函数
"""
import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        验证结果
    """
    try:
        # bcrypt需要bytes类型
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def hash_password(password: str) -> str:
    """
    哈希密码
    
    Args:
        password: 明文密码
        
    Returns:
        哈希后的密码
    """
    # 生成salt并加密
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
