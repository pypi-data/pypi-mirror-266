from flask import Flask, request, jsonify
from todaydiscourse import log, core, config
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    log.info(f"请求IP: {request.remote_addr} 请求内容: 错误！调用方式错误！")
    return "欢迎来到 TodayDiscourse 今日话语！", 200

@app.route('/text/', methods=['GET'])
def text_endpoint():
    log.info(f"请求IP: {request.remote_addr} 请求内容: 文本")
    result = core.get_discourse(os.getcwd())
    text = result.get('content', 0)
    return text, 200, {'Content-Type': 'text/plain'}

@app.route('/json/', methods=['GET'])
def json_endpoint():
    log.info(f"请求IP: {request.remote_addr} 请求内容: JSON")
    response_data = core.get_discourse(os.getcwd())
    return jsonify(response_data), 200

def start():
    log.info("欢迎使用 TodayDiscourse 今日话语")
    log.info("开发团队: XingchenOpenSource 星辰开源")
    log.info("项目地址: https://github.com/XingchenOpenSource/TodayDiscourse")
    log.info("官方文档: https://xingchenopensource.github.io/apis/todaydiscourse/")
    config.get_config(os.getcwd())
    server_port = config.get_config_port(os.getcwd())
    server_host = config.get_config_host(os.getcwd())
    log.info(f"🎉恭喜您！今日话语已在 http://localhost:{server_port} 上启动，请参阅官方文档以查看如何调用。")
    app.run(host=server_host, port=server_port, threaded=True)

if __name__ == '__main__':
    start()