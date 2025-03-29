import os
import json
import requests
import time
from datetime import datetime
import re
import logging
from typing import Dict, List, Optional, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("wechat_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================
# 微信公众号相关配置
# ============================
class WeChatConfig:
    """微信公众号配置"""
    def __init__(self):
        self.app_id = "wx5526a100d33d6283"  # 微信公众号AppID
        self.app_secret = "bad96b0ab8562044bf4d80e212ac60e5"  # 微信公众号AppSecret
        self.token = "mytoken123456"  # 微信公众号Token
        self.encoding_aes_key = "BwZ49IJVf5CDjaLEd1vsy9APGVjt4qWISD34JNgz5tT"  # 微信公众号EncodingAESKey
        self.access_token = None
        self.access_token_expires_at = 0

    def get_access_token(self) -> str:
        """获取微信公众号access_token"""
        current_time = time.time()
        
        # 如果token未过期，直接返回
        if self.access_token and current_time < self.access_token_expires_at:
            return self.access_token
            
        # 获取新token
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        response = requests.get(url)
        result = response.json()
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            self.access_token_expires_at = current_time + result["expires_in"] - 200  # 提前200秒过期
            return self.access_token
        else:
            logger.error(f"获取access_token失败: {result}")
            raise Exception(f"获取access_token失败: {result}")

# ============================
# B站视频下载
# ============================
class BilibiliDownloader:
    """哔哩哔哩视频下载器"""
    def __init__(self, save_path: str = "./downloads"):
        self.save_path = save_path
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            
    def extract_video_id(self, url: str) -> str:
        """从URL中提取视频ID"""
        # 支持多种B站URL格式
        patterns = [
            r'bilibili\.com/video/([^/?]+)',  # 标准格式 https://www.bilibili.com/video/BV1xx411c7mD
            r'b23\.tv/([^/?]+)'              # 短链接 https://b23.tv/xxxxxx
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
                
        raise ValueError(f"无法从URL '{url}' 中提取视频ID")
        
    def download_video(self, url: str) -> str:
        """
        下载B站视频
        
        Args:
            url: B站视频链接
            
        Returns:
            下载的视频文件路径
        """
        video_id = self.extract_video_id(url)
        logger.info(f"开始下载视频: {video_id}")
        
        # 注意：这里使用you-get或者其他第三方工具下载
        # 你需要先安装: pip install you-get
        
        output_path = os.path.join(self.save_path, video_id)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        # 使用you-get下载视频
        import subprocess
        cmd = ["you-get", "--output-dir", output_path, url]
        
        try:
            subprocess.run(cmd, check=True)
            
            # 查找下载的视频文件
            for file in os.listdir(output_path):
                if file.endswith(('.mp4', '.flv', '.mkv')):
                    video_path = os.path.join(output_path, file)
                    logger.info(f"视频下载完成: {video_path}")
                    return video_path
                    
            raise FileNotFoundError(f"下载完成但找不到视频文件: {output_path}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"视频下载失败: {e}")
            raise RuntimeError(f"视频下载失败: {e}")

# ============================
# 文件转换与处理
# ============================
class MediaProcessor:
    """媒体处理类"""
    def __init__(self, output_dir: str = "./outputs"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def video_to_text(self, video_path: str) -> Dict[str, str]:
        """
        视频转文字（调用你已有的代码）
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            包含txt和srt路径的字典
        """
        logger.info(f"开始处理视频: {video_path}")
        
        # 这里应该调用你已有的视频转文字代码
        # 下面是一个示例实现
        
        video_name = os.path.basename(os.path.dirname(video_path))
        txt_path = os.path.join(self.output_dir, f"{video_name}.txt")
        srt_path = os.path.join(self.output_dir, f"{video_name}.srt")
        
        # TODO: 替换为你已有的视频转文字代码
        # video_to_text_implementation(video_path, txt_path, srt_path)
        
        # 模拟处理过程
        logger.info("视频转文字处理完成")
        
        # 如果文件不存在，创建空文件（实际使用时去掉这行）
        if not os.path.exists(txt_path):
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("视频转文字内容示例")
                
        if not os.path.exists(srt_path):
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write("1\n00:00:00,000 --> 00:00:05,000\n视频转字幕示例\n")
        
        return {
            "txt": txt_path,
            "srt": srt_path
        }

# ============================
# 大模型API调用
# ============================
class AIModelClient:
    """AI大模型客户端"""
    def __init__(self, model_type: str = "kimi"):
        self.model_type = model_type
        
    def ask_question(self, question: str, context: str) -> str:
        """
        向大模型提问
        
        Args:
            question: 用户的问题
            context: 文本上下文（视频转写的文本）
            
        Returns:
            大模型的回答
        """
        logger.info(f"开始调用AI模型: {self.model_type}")
        
        if self.model_type == "kimi":
            return self._call_kimi_api(question, context)
        else:
            # 你可以添加其他模型的支持
            return self._call_other_api(question, context)
            
    def _call_kimi_api(self, question: str, context: str) -> str:
        """调用Kimi API"""
        # 实际实现时需要替换为真实的API调用
        # 这里是一个示例
        
        api_key = "your_kimi_api_key"
        url = "https://kimi-api.example.com/chat"
        
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messages": [
                    {"role": "system", "content": "你是一个视频内容助手，根据视频文字回答用户问题。"},
                    {"role": "user", "content": f"基于以下视频内容，回答问题：\n\n{context}\n\n问题：{question}"}
                ]
            }
            
            # response = requests.post(url, headers=headers, json=data)
            # result = response.json()
            # return result["choices"][0]["message"]["content"]
            
            # 模拟返回结果
            logger.info("AI模型调用完成")
            return f"这是关于'{question}'的回答，基于视频内容分析。"
            
        except Exception as e:
            logger.error(f"调用AI模型失败: {e}")
            return f"抱歉，AI模型调用失败: {str(e)}"
            
    def _call_other_api(self, question: str, context: str) -> str:
        """调用其他API"""
        # 实现其他模型的API调用
        logger.info("调用其他AI模型")
        return f"这是其他模型对'{question}'的回答"

# ============================
# 微信公众号消息处理
# ============================
class WeChatMessageHandler:
    """微信公众号消息处理器"""
    def __init__(
        self, 
        wechat_config: WeChatConfig,
        bilibili_downloader: BilibiliDownloader,
        media_processor: MediaProcessor,
        ai_model: AIModelClient
    ):
        self.wechat_config = wechat_config
        self.downloader = bilibili_downloader
        self.processor = media_processor
        self.ai_model = ai_model
        self.user_states = {}  # 用户状态管理
        
    def handle_message(self, message_data: Dict) -> Dict:
        """
        处理收到的微信消息
        
        Args:
            message_data: 微信消息数据
            
        Returns:
            回复消息
        """
        msg_type = message_data.get("MsgType")
        from_user = message_data.get("FromUserName")
        to_user = message_data.get("ToUserName")
        
        # 文本消息处理
        if msg_type == "text":
            content = message_data.get("Content", "").strip()
            return self._handle_text_message(from_user, to_user, content)
            
        # 其他类型消息
        return {
            "ToUserName": from_user,
            "FromUserName": to_user,
            "CreateTime": int(time.time()),
            "MsgType": "text",
            "Content": "目前只支持文本消息，请发送文本内容。"
        }
        
    def _handle_text_message(self, from_user: str, to_user: str, content: str) -> Dict:
        """处理文本消息"""
        # 检查是否是B站链接
        if "bilibili.com/video" in content or "b23.tv" in content:
            return self._handle_video_url(from_user, to_user, content)
            
        # 检查用户当前状态，判断是否在等待格式选择
        if from_user in self.user_states and self.user_states[from_user]["state"] == "waiting_format":
            return self._handle_format_selection(from_user, to_user, content)
            
        # 检查是否是提问
        if from_user in self.user_states and self.user_states[from_user]["state"] == "has_video":
            return self._handle_question(from_user, to_user, content)
            
        # 默认回复
        return {
            "ToUserName": from_user,
            "FromUserName": to_user,
            "CreateTime": int(time.time()),
            "MsgType": "text",
            "Content": "欢迎使用视频助手！\n请发送B站视频链接，我将为您下载并处理视频内容。"
        }
        
    def _handle_video_url(self, from_user: str, to_user: str, url: str) -> Dict:
        """处理视频URL"""
        try:
            # 通知用户开始处理
            self._send_custom_message(from_user, "收到您的视频链接，正在处理中，请稍候...")
            
            # 下载视频
            video_path = self.downloader.download_video(url)
            
            # 处理视频
            text_files = self.processor.video_to_text(video_path)
            
            # 更新用户状态
            self.user_states[from_user] = {
                "state": "waiting_format",
                "video_id": os.path.basename(os.path.dirname(video_path)),
                "txt_path": text_files["txt"],
                "srt_path": text_files["srt"]
            }
            
            # 返回格式选择提示
            return {
                "ToUserName": from_user,
                "FromUserName": to_user,
                "CreateTime": int(time.time()),
                "MsgType": "text",
                "Content": "视频处理完成！请选择您需要的格式：\n1. TXT格式\n2. SRT格式\n\n回复数字1或2进行选择。"
            }
            
        except Exception as e:
            logger.error(f"处理视频URL失败: {e}")
            return {
                "ToUserName": from_user,
                "FromUserName": to_user,
                "CreateTime": int(time.time()),
                "MsgType": "text",
                "Content": f"处理视频时出错: {str(e)}"
            }
            
    def _handle_format_selection(self, from_user: str, to_user: str, content: str) -> Dict:
        """处理格式选择"""
        if content not in ["1", "2"]:
            return {
                "ToUserName": from_user,
                "FromUserName": to_user,
                "CreateTime": int(time.time()),
                "MsgType": "text",
                "Content": "请回复数字1(TXT格式)或2(SRT格式)进行选择。"
            }
            
        user_state = self.user_states[from_user]
        
        # 发送文件
        if content == "1":
            # 发送TXT文件
            file_path = user_state["txt_path"]
            media_id = self._upload_temporary_material(file_path)
            
            # 更新用户状态
            self.user_states[from_user]["state"] = "has_video"
            self.user_states[from_user]["current_format"] = "txt"
            
            # 通知用户
            return {
                "ToUserName": from_user,
                "FromUserName": to_user,
                "CreateTime": int(time.time()),
                "MsgType": "text",
                "Content": "TXT文件已准备就绪！\n\n您现在可以询问关于视频内容的任何问题，我会根据视频内容为您解答。"
            }
            
        else:  # content == "2"
            # 发送SRT文件
            file_path = user_state["srt_path"]
            media_id = self._upload_temporary_material(file_path)
            
            # 更新用户状态
            self.user_states[from_user]["state"] = "has_video"
            self.user_states[from_user]["current_format"] = "srt"
            
            # 通知用户
            return {
                "ToUserName": from_user,
                "FromUserName": to_user,
                "CreateTime": int(time.time()),
                "MsgType": "text",
                "Content": "SRT字幕文件已准备就绪！\n\n您现在可以询问关于视频内容的任何问题，我会根据视频内容为您解答。"
            }
            
    def _handle_question(self, from_user: str, to_user: str, question: str) -> Dict:
        """处理用户问题"""
        user_state = self.user_states[from_user]
        
        try:
            # 读取文本内容
            if user_state["current_format"] == "txt":
                with open(user_state["txt_path"], 'r', encoding='utf-8') as f:
                    context = f.read()
            else:
                with open(user_state["srt_path"], 'r', encoding='utf-8') as f:
                    # 简单处理SRT文件，提取纯文本
                    lines = f.readlines()
                    text_lines = []
                    for line in lines:
                        if not line.strip().isdigit() and not '-->' in line and line.strip():
                            text_lines.append(line.strip())
                    context = '\n'.join(text_lines)
            
            # 调用AI模型
            answer = self.ai_model.ask_question(question, context)
            
            # 返回回答
            return {
                "ToUserName": from_user,
                "FromUserName": to_user,
                "CreateTime": int(time.time()),
                "MsgType": "text",
                "Content": answer
            }
            
        except Exception as e:
            logger.error(f"处理问题失败: {e}")
            return {
                "ToUserName": from_user,
                "FromUserName": to_user,
                "CreateTime": int(time.time()),
                "MsgType": "text",
                "Content": f"处理问题时出错: {str(e)}"
            }
            
    def _upload_temporary_material(self, file_path: str) -> str:
        """上传临时素材，获取media_id"""
        url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={self.wechat_config.get_access_token()}&type=file"
        
        with open(file_path, 'rb') as f:
            files = {'media': (os.path.basename(file_path), f, 'application/octet-stream')}
            response = requests.post(url, files=files)
            result = response.json()
            
        if "media_id" in result:
            return result["media_id"]
        else:
            logger.error(f"上传临时素材失败: {result}")
            raise Exception(f"上传临时素材失败: {result}")
            
    def _send_custom_message(self, to_user: str, content: str) -> None:
        """发送客服消息"""
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={self.wechat_config.get_access_token()}"
        
        data = {
            "touser": to_user,
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get("errcode", 0) != 0:
            logger.error(f"发送客服消息失败: {result}")

# ============================
# Flask Web服务
# ============================
def create_flask_app():
    """创建Flask应用"""
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
    # 初始化各个组件
    wechat_config = WeChatConfig()
    bilibili_downloader = BilibiliDownloader()
    media_processor = MediaProcessor()
    ai_model = AIModelClient()
    
    # 创建消息处理器
    message_handler = WeChatMessageHandler(
        wechat_config,
        bilibili_downloader,
        media_processor,
        ai_model
    )
    @app.route('/')
    def home():
        return "Hello World! Flask is running."
    
    @app.route('/wechat', methods=['GET', 'POST'])
    def wechat():
        # 微信公众号接入验证
        if request.method == 'GET':
            signature = request.args.get('signature', '')
            timestamp = request.args.get('timestamp', '')
            nonce = request.args.get('nonce', '')
            echostr = request.args.get('echostr', '')
            
            # 这里应该验证签名，但为了简单起见，我们直接返回echostr
            return echostr
            
        # 处理接收到的消息
        if request.method == 'POST':
            try:
                xml_data = request.data
                from xml.etree import ElementTree as ET
                
                # 解析XML数据
                root = ET.fromstring(xml_data)
                data = {}
                for child in root:
                    data[child.tag] = child.text
                    
                # 处理消息
                response = message_handler.handle_message(data)
                
                # 构建XML响应
                xml_response = "<xml>"
                for key, value in response.items():
                    if isinstance(value, int):
                        xml_response += f"<{key}>{value}</{key}>"
                    else:
                        xml_response += f"<{key}><![CDATA[{value}]]></{key}>"
                xml_response += "</xml>"
                
                return xml_response
                
            except Exception as e:
                logger.error(f"处理微信消息失败: {e}")
                return ""
    
    return app

# ============================
# 主函数
# ============================
def main():
    """主函数"""
    app = create_flask_app()
    app.run(host='localhost', port=8080, debug=True)

if __name__ == "__main__":
    main()
