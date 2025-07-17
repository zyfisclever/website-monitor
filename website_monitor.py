import requests
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os
import json
from datetime import datetime

# 配置参数
WEBSITE_URL = os.getenv('WEBSITE_URL', 'https://example.com')  # 要监控的网站URL
HISTORY_FILE = 'website_history.json'  # 存储历史记录的JSON文件
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.example.com')  # SMTP服务器地址
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))  # SMTP端口
SMTP_USER = os.getenv('SMTP_USER', 'your_email@example.com')  # SMTP用户名
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'your_password')  # SMTP密码
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL', 'notify@example.com')  # 接收通知的邮箱

def get_website_content(url):
    """获取网站内容并返回哈希值"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"Error fetching website: {e}")
        return None

def load_history():
    """加载历史记录"""
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'last_hash': None, 'last_check': None}

def save_history(current_hash):
    """保存当前记录"""
    history = {
        'last_hash': current_hash,
        'last_check': datetime.now().isoformat()
    }
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def send_email(subject, body):
    """发送邮件通知"""
    message = MIMEText(body, 'plain', 'utf-8')
    message['From'] = SMTP_USER
    message['To'] = RECEIVER_EMAIL
    message['Subject'] = Header(subject, 'utf-8')
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [RECEIVER_EMAIL], message.as_string())
        print("Notification email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    print(f"Checking website: {WEBSITE_URL}")
    current_hash = get_website_content(WEBSITE_URL)
    if current_hash is None:
        return
    
    history = load_history()
    
    if history['last_hash'] is None:
        print("First run, saving initial hash")
        save_history(current_hash)
        return
    
    if current_hash != history['last_hash']:
        print("Website content has changed!")
        subject = f"Website Changed: {WEBSITE_URL}"
        body = f"""The website {WEBSITE_URL} has changed.
        
Previous check: {history['last_check']}
Current check: {datetime.now().isoformat()}

Please check the website for updates."""
        
        send_email(subject, body)
        save_history(current_hash)
    else:
        print("No changes detected")

if __name__ == '__main__':
    main()
