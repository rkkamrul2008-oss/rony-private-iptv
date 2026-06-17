import urllib.request
import os
import re

def get_youtube_m3u8(youtube_url):
    """ইউটিউব লাইভ পেজ থেকে সরাসরি এবং দ্রুত .m3u8 লিংক বের করার ফাংশন"""
    try:
        print(f"-> [ইউটিউব] লিংক এক্সট্র্যাক্ট করা হচ্ছে: {youtube_url}")
        
        # ইউটিউব পেজ রিকোয়েস্ট করা
        req = urllib.request.Request(
            youtube_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
            # পেজের সোর্স কোড থেকে hlsManifestUrl খুঁজে বের করা (Regex)
            match = re.search(r'hlsManifestUrl[:"\']+(https://[^"\']+\.m3u8)', html)
            
            if match:
                raw_m3u8 = match.group(1)
                # জাভাস্ক্রিপ্টের ক্যারেক্টার কোড (যেমন \u0026) পরিষ্কার করে আসল & চিহ্নে রূপান্তর
                clean_m3u8 = raw_m3u8.replace(r'\u0026', '&')
                return clean_m3u8
                
        return None
    except Exception as e:
        print(f"-> [ভুল] ইউটিউব লিংক প্রসেস করা যায়নি: {e}")
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
                valid_urls.append((f"YouTube Channel {index}", yt_m3u8))
                print(f"-> [সফল] YouTube Channel {index} যুক্ত করা হয়েছে।")
            else:
                print(f"-> [বাদ] YouTube Channel {index} লাইভ নেই বা লিংক ভুল।")
        
        # সাধারণ আইপিটিভি লিংকের জন্য আগের নিয়ম
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
        # এখানে ইউজারের নাম অনুযায়ী ফাইল তৈরি হবে (যেমন: live_rony.m3u)
        user_name = user.split()[-1] if " " in user else user
        output_file = f"live_{user_name}.m3u"
        with open(output_file, "w", encoding="utf-8") as out:
            out.write("#EXTM3U\n")
            for name, url_str in valid_urls:
                out.write(f'#EXTINF:-1 tvg-name="${name}" tvg-id="" tvg-logo="", {name}\n')
                out.write(f"{url_str}\n")
        print(f"-> {user_name}-এর জন্য তৈরি হয়েছে: {output_file}")

if __name__ == "__main__":
    check_and_scrape()
