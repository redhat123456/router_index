import requests
import json
from datetime import datetime, timedelta
import os
import re

# B站UID
UID = 1689628906
API_URL = f'https://api.bilibili.com/x/space/arc/search?mid={UID}&pn=1&ps=25'
HISTORY_FILE = 'bilibili_recent_videos.json'
HTML_FILE = 'index.html'

def fetch_bilibili_videos():
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(API_URL, headers=headers)
    data = response.json()
    videos = data.get('data', {}).get('list', {}).get('vlist', [])
    return videos

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def update_html_in_place(videos, html_path=HTML_FILE):
    if not os.path.exists(html_path):
        print(f"{html_path} 文件不存在，跳过 HTML 更新。")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 构造新的视频 HTML 块
    new_html_block = ""
    for v in sorted(videos, key=lambda x: x['created'], reverse=True):
        new_html_block += f'''
        <div class="video">
            <a class="title" href="{v['url']}" target="_blank">{v['title']}</a>
            <div class="meta">播放量: {v['play']} | 发布时间: {v['created']}</div>
        </div>
        '''

    # 替换标记区域
    updated_html = re.sub(
        r'<!-- BEGIN BILIBILI -->.*?<!-- END BILIBILI -->',
        f'<!-- BEGIN BILIBILI -->\n{new_html_block}\n<!-- END BILIBILI -->',
        html_content,
        flags=re.DOTALL
    )

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(updated_html)

    print(f"{html_path} 页面已成功更新 BILIBILI 视频区域。")

def main():
    videos = fetch_bilibili_videos()
    one_week_ago = datetime.now() - timedelta(days=7)

    # 筛选出最近一周的视频
    recent_videos = []
    for v in videos:
        ctime = datetime.fromtimestamp(v['created'])
        if ctime >= one_week_ago:
            recent_videos.append({
                'title': v['title'],
                'bvid': v['bvid'],
                'url': f'https://www.bilibili.com/video/{v["bvid"]}',
                'created': ctime.strftime('%Y-%m-%d %H:%M:%S'),
                'play': v.get('play')
            })

    # 合并历史并去重（仅保留7天内的）
    old_history = load_history()
    all_videos = {v['bvid']: v for v in old_history + recent_videos}
    cleaned = [
        v for v in all_videos.values()
        if datetime.strptime(v['created'], '%Y-%m-%d %H:%M:%S') >= one_week_ago
    ]
    save_history(cleaned)

    print("最近一周上传的视频：")
    for v in sorted(cleaned, key=lambda x: x['created'], reverse=True):
        print(f"- {v['title']} | 播放量: {v['play']} | 链接: {v['url']}")

    update_html_in_place(cleaned)

if __name__ == '__main__':
    main()
