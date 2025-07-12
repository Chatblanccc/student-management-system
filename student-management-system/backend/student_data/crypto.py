from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import time
import logging

logger = logging.getLogger(__name__)

# 固定密钥 - 与前端保持完全一致
SECRET_KEY_STRING = 'jnua-student-system-2024-secure-key-!@#'

def decrypt_password(encrypted_password, iv_string, timestamp=None):
    """
    解密前端自定义加密的密码 - 完全兼容版本
    """
    try:
        # 检查时间戳
        if timestamp:
            current_time = int(time.time() * 1000)
            if current_time - timestamp > 5 * 60 * 1000:
                raise ValueError("请求已过期，请重新登录")
        
        logger.info(f"🔧 开始自定义解密，IV: {iv_string[:16]}...")
        
        # 🔧 与前端完全一致的密钥处理
        # 填充到32字节，与前端 padEnd(32, '\0') 完全一致
        key_string = SECRET_KEY_STRING
        if len(key_string) < 32:
            key_string = key_string + '\0' * (32 - len(key_string))
        else:
            key_string = key_string[:32]
        
        key = key_string.encode('utf-8')
        
        # 解析IV（16字节十六进制）
        iv = bytes.fromhex(iv_string)
        
        # 解析加密数据（Base64格式）
        encrypted_data = base64.b64decode(encrypted_password)
        
        logger.info(f"密钥长度: {len(key)}, IV长度: {len(iv)}, 密文长度: {len(encrypted_data)}")
        
        # 解密
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        
        result = decrypted_data.decode('utf-8')
        logger.info("✅ 自定义解密成功")
        return result
        
    except ValueError as ve:
        logger.error(f"❌ 数值错误: {str(ve)}")
        raise ve
    except Exception as e:
        logger.error(f"❌ 解密失败: {str(e)} (类型: {type(e).__name__})")
        raise ValueError(f"密码解密失败: {str(e)}")

def is_encrypted_request(request_data):
    """检查是否是加密请求"""
    return (
        request_data.get('isEncrypted') and
        'encryptedPassword' in request_data and
        'iv' in request_data
    ) 