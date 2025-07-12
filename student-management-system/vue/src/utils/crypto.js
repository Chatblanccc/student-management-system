import CryptoJS from 'crypto-js'

// 固定密钥 - 32字节
const SECRET_KEY_STRING = 'jnua-student-system-2024-secure-key-!@#'

/**
 * 自定义AES加密 - 确保与后端完全兼容
 */
export function encryptPassword(password) {
  try {
    // 🔧 自定义加密：确保兼容性
    
    // 1. 生成随机IV
    const iv = CryptoJS.lib.WordArray.random(16)
    
    // 2. 创建固定长度的密钥（32字节）
    const keyBytes = CryptoJS.enc.Utf8.parse(SECRET_KEY_STRING.padEnd(32, '\0').substring(0, 32))
    
    // 3. 加密
    const encrypted = CryptoJS.AES.encrypt(
      CryptoJS.enc.Utf8.parse(password), // 明确解析密码
      keyBytes,
      {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
      }
    )
    
    // 4. 返回结果
    return {
      encryptedPassword: CryptoJS.enc.Base64.stringify(encrypted.ciphertext), // 只返回密文，不包含盐值
      iv: iv.toString(CryptoJS.enc.Hex),
      timestamp: Date.now()
    }
  } catch (error) {
    console.error('密码加密失败:', error)
    throw new Error('密码加密失败')
  }
}

/**
 * 自定义解密函数（测试用）
 */
export function decryptPassword(encryptedPassword, ivString) {
  try {
    const keyBytes = CryptoJS.enc.Utf8.parse(SECRET_KEY_STRING.padEnd(32, '\0').substring(0, 32))
    const iv = CryptoJS.enc.Hex.parse(ivString)
    const ciphertext = CryptoJS.enc.Base64.parse(encryptedPassword)
    
    const decrypted = CryptoJS.AES.decrypt(
      { ciphertext: ciphertext },
      keyBytes,
      {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
      }
    )
    
    return decrypted.toString(CryptoJS.enc.Utf8)
  } catch (error) {
    console.error('密码解密失败:', error)
    throw new Error('密码解密失败')
  }
}

/**
 * 生成请求签名
 */
export function generateSignature(data) {
  const timestamp = Date.now()
  const dataString = JSON.stringify(data) + timestamp
  return CryptoJS.HmacSHA256(dataString, SECRET_KEY_STRING).toString()
} 