import os
import json
import urllib.request
import yt_dlp

def download_youtube_transcript(url: str, output_dir: str = "transcribe", save_files: bool = True):
    """
    Downloads subtitles/transcripts for a single video or full playlist URL.
    Returns a list of dicts with id, title, full_text, and timestamped segments.
    """
    if save_files:
        os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
    }

    results = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        # Handle playlist or single video
        entries = info.get("entries") if "entries" in info else [info]

        for idx, entry in enumerate(entries, start=1):
            if not entry:
                continue

            video_id = entry.get("id")
            title = entry.get("title", f"video_{video_id}")
            # Sanitize title for filename
            clean_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).rstrip()

            subtitles = entry.get("subtitles", {})
            auto_subtitles = entry.get("automatic_captions", {})

            # Priority: manual English -> en-orig (original auto captions) -> standard en
            sub_formats = None
            if subtitles and "en" in subtitles:
                sub_formats = subtitles["en"]
            elif auto_subtitles and "en-orig" in auto_subtitles:
                sub_formats = auto_subtitles["en-orig"]
            elif auto_subtitles and "en" in auto_subtitles:
                sub_formats = auto_subtitles["en"]

            if not sub_formats:
                print(f"[-] No English transcript found for: {title}")
                continue

            # Fetch the json3 track
            json3_track = next((f for f in sub_formats if f.get("ext") == "json3"), None)
            if not json3_track:
                print(f"[-] json3 format unavailable for: {title}")
                continue

            req = urllib.request.Request(json3_track["url"], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            segments = []
            full_text_list = []
            for ev in data.get("events", []):
                if "segs" not in ev:
                    continue
                text = " ".join("".join(s.get("utf8", "") for s in ev["segs"]).split())
                if not text:
                    continue
                segments.append({
                    "text": text,
                    "start": round(ev.get("tStartMs", 0) / 1000.0, 3),
                    "duration": round(ev.get("dDurationMs", 0) / 1000.0, 3)
                })
                full_text_list.append(text)

            full_text = " ".join(full_text_list)
            video_data = {
                "id": video_id,
                "title": title,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "full_text": full_text,
                "segments": segments
            }
            results.append(video_data)

            # Save to disk
            if save_files:
                prefix = f"{idx:02d}_{video_id}_{clean_title[:40]}"
                # 1. JSON format
                with open(os.path.join(output_dir, f"{prefix}.json"), "w", encoding="utf-8") as f:
                    json.dump(video_data, f, indent=2, ensure_ascii=False)
                # 2. Text format
                with open(os.path.join(output_dir, f"{prefix}.txt"), "w", encoding="utf-8") as f:
                    f.write(full_text)

            print(f"[+] Downloaded transcript: {title} ({len(segments)} segments)")

    return results


def download_youtube_video(url: str, output_dir: str = "downloads"):
    """
    Downloads the video file (best MP4 quality) for any YouTube URL or playlist.
    """
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": os.path.join(output_dir, "%(playlist_index)02d_%(id)s_%(title)s.%(ext)s"),
        "ignoreerrors": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
