import yt_dlp
import json
from datetime import datetime, timedelta
from jinja2 import Template
import os
import requests

CHANNEL_URL = 'https://www.youtube.com/playlist?list=PL0tDb4jw6kPwCDw0Ql9vTSD3Pc4Vd2EOn'


def fetch_videos():
    flat_opts = {'extract_flat': True, 'quiet': True, 'forcejson': True}
    with yt_dlp.YoutubeDL(flat_opts) as ydl:
        info = ydl.extract_info(CHANNEL_URL, download=False)
        entries = info.get('entries', [])
        video_ids = [e['id'] for e in entries if 'id' in e]

    # 获取每个视频的完整信息
    full_videos = []
    detail_opts = {'quiet': True, 'forcejson': True}
    with yt_dlp.YoutubeDL(detail_opts) as ydl:
        for vid in video_ids:
            try:
                info = ydl.extract_info(f'https://www.youtube.com/watch?v={vid}', download=False)
                full_videos.append(info)
            except Exception as e:
                print(f"Error fetching video {vid}: {e}")
    return full_videos




def get_video_stats(video_id):
    with yt_dlp.YoutubeDL({'quiet': True, 'forcejson': True}) as ydl:
        info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
        return {
            'views': info.get('view_count', 0),
            'title': info.get('title', ''),
            'url': info.get('webpage_url', ''),
            'thumbnail': info.get('thumbnail', '')
        }


def pick_top_recent(videos):
    one_week = datetime.utcnow() - timedelta(days=7)
    candidates = []
    for vid in videos:
        if 'upload_date' not in vid:
            continue
        ud = datetime.strptime(vid['upload_date'], '%Y%m%d')
        if ud > one_week:
            stats = get_video_stats(vid['id'])
            candidates.append(stats)
    return max(candidates, key=lambda x: x['views']) if candidates else None


def update_webpage(video):
    with open('templates/index_template.html') as f:
        tpl = Template(f.read())
    html = tpl.render(title=video['title'], url=video['url'], date=datetime.utcnow().strftime('%Y-%m-%d'))
    os.makedirs('output', exist_ok=True)
    with open('output/index.html', 'w') as f:
        f.write(html)
    # download thumbnail
    if video.get('thumbnail'):
        thumb = requests.get(video['thumbnail'])
        with open('output/thumb.jpg', 'wb') as f:
            f.write(thumb.content)


if __name__ == '__main__':
    vids = fetch_videos()
    top = pick_top_recent(vids)
    if top:
        update_webpage(top)
