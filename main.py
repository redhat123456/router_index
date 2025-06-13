import yt_dlp
from datetime import datetime, timedelta

CHANNEL_URL = 'https://www.youtube.com/@NBCNewsKids'

def fetch_videos():
    ydl_opts = {'extract_flat': True, 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(CHANNEL_URL, download=False)
        return info.get('entries', [])

def get_video_info(video_id):
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
        return {
            'id': video_id,
            'title': info.get('title', ''),
            'url': info.get('webpage_url', ''),
            'views': info.get('view_count', 0),
            'upload_date': info.get('upload_date', '')
        }

def main():
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    videos = fetch_videos()
    recent_videos = []

    for vid in videos:
        upload_date_str = vid.get('upload_date')
        if not upload_date_str:
            continue
        upload_date = datetime.strptime(upload_date_str, '%Y%m%d')
        if upload_date >= one_week_ago:
            info = get_video_info(vid['id'])
            recent_videos.append(info)

    if not recent_videos:
        print("No videos uploaded in the last week.")
        return

    # 找播放量最高的视频
    top_video = max(recent_videos, key=lambda v: v['views'])
    print("Top video in the last week:")
    print(f"Title: {top_video['title']}")
    print(f"Views: {top_video['views']}")
    print(f"URL: {top_video['url']}")

if __name__ == '__main__':
    main()
