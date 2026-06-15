import urllib.request
import os
import subprocess

def get_youtube_m3u8(youtube_url):
    """yt-dlp ব্যবহার করে ইউটিউব লাইভ থেকে আসল m3u8 লিংক বের করার ফাংশন"""
    try:
        print(f"-> [ইউটিউব] লিংক এক্সট্র্যাক্ট করা হচ্ছে: {youtube_url}")
        # yt-dlp কমান্ড রান করে ডিরেক্ট m3u8 ইউআরএল নেওয়া
        result = subprocess.run(
            ['yt-dlp', '-g', '-f', 'best', youtube_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            m3u8_url = result.stdout.strip()
            if ".m3u8" in m3u8_url:
                return m3u8_url
        return None
    except Exception as e:
        print(f"-> [ভুল] ইউটিউব লিংক প্রসেস করা যায়নি।")
        return None

def check_and_scrape():
    source_file = "sources.txt"
    user_file = "users.txt"
    
    if not os.path.exists(source_file):
        print("Error: sources.txt পাওয়া যায়নি!")
        return

    print("--- লিংক যাচাইকরণ ও এক্সট্র্যাকশন শুরু হলো ---")
    with open(source_file, "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    valid_urls = []
    for index, url in enumerate(urls, start=1):
        # যদি লিংকটি ইউটিউবের হয়
        if "youtube.com" in url or "youtu.be" in url:
            yt_m3u8 = get_youtube_m3u8(url)
            if yt_m3u8:
                valid_urls.append((f"Premium Channel {index}", yt_m3u8))
                print(f"-> [সফল] YouTube Channel {index} যুক্ত করা হয়েছে।")
            else:
                print(f"-> [বাদ] YouTube Channel {index} লাইভ নেই বা লিংক ভুল।")
        
        # সাধারণ আইপিটিভি লিংকের জন্য পূর্বের নিয়ম
        else:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.getcode() == 200:
                        valid_urls.append((f"Premium Channel {index}", url))
                        print(f"-> [সচল] Channel {index}")
            except:
                print(f"-> [বাদ] Channel {index} কাজ করছে না বা টাইমআউট।")

    # ইউজারদের জন্য আলাদা আলাদা প্লেলিস্ট তৈরি করা
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            users = [line.strip() for line in f if line.strip()]
    else:
        users = ["default"]

    print(f"\n--- ইউজারদের জন্য সিকিউর ফাইল তৈরি হচ্ছে ---")
    for user in users:
        output_file = f"live_{user}.m3u"
        with open(output_file, "w", encoding="utf-8") as out:
            out.write("#EXTM3U\n")
            for name, url in valid_urls:
                out.write(f'#EXTINF:-1 tvg-name="{name}", {name}\n')
                out.write(f"{url}\n")
        print(f"-> {user}-এর জন্য তৈরি হয়েছে: {output_file}")

if __name__ == "__main__":
    check_and_scrape()
