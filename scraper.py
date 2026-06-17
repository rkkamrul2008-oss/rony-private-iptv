import urllib.request
import os
import re

def get_youtube_m3u8(youtube_url):
    """ইউটিউব লাইভ পেজ থেকে সরাসরি এবং দ্রুত .m3u8 লিংক বের করার ফাংশন"""
    try:
        print(f"-> [ইউটিউব] লিংক এক্সট্র্যাক্ট করা হচ্ছে: {youtube_url}")
        req = urllib.request.Request(
            youtube_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            match = re.search(r'hlsManifestUrl[:"\']+(https://[^"\']+\.m3u8)', html)
            if match:
                raw_m3u8 = match.group(1)
                clean_m3u8 = raw_m3u8.replace(r'\u0026', '&')
                return clean_m3u8
        return None
    except Exception as e:
        print(f"-> [ভুল] ইউটিউব লিংক প্রসেস করা যায়নি: {e}")
        return None

def clean_token_from_url(url):
    """লিংকের শেষে থাকা টোকেন (?token=...) স্বয়ংক্রিয়ভাবে কেটে বাদ দেওয়ার ফাংশন"""
    if "?token=" in url:
        return url.split("?token=")[0]
    return url

def auto_assign_group(url, current_group_from_file, channel_name):
    """লিংক এবং নাম বিশ্লেষণ করে নিখুঁত ও একক ক্যাটাগরি গ্রুপ নির্ধারণ করার স্মার্ট ফাংশন"""
    url_lower = url.lower()
    name_lower = channel_name.lower()
    
    # ১. ইউটিউব চ্যানেল সেকশন
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "YouTube Live Channels"
        
    # ২. আন্তর্জাতিক নিউজ বা চ্যানেল সেকশন
    if "ndtv" in url_lower or "newsmax" in url_lower or "internasional" in current_group_from_file.lower():
        return "International News"
        
    # ৩. টোকেন যুক্ত, লোকাল আইএসপি বা এক্সপায়ার হতে যাওয়া চ্যানেল সেকশন
    if "token" in url_lower or "10.99.99" in url_lower or "172.17." in url_lower or "expires" in name_lower:
        return "ISP Restricted / Temporary"
        
    # ৪. বিডিক্স বা নির্দিষ্ট আইপি সেকশন
    if "banglavu.top" in url_lower or "bdix" in name_lower:
        return "BDIX Channels"
        
    # ৫. স্থায়ী বা ডিরেক্ট বাংলাদেশী চ্যানেল সেকশন (ডিফল্ট)
    return "Bangladeshi Channels"

def check_and_scrape():
    source_file = "sources.txt"
    user_file = "users.txt"
    
    if not os.path.exists(source_file):
        print("Error: sources.txt পাওয়া যায়নি!")
        return

    print("--- লিংক যাচাইকরণ ও এক্সট্র্যাকশন শুরু হলো ---")
    
    valid_urls = []
    file_group_context = "Bangladeshi Channels"
    current_channel_name = ""

    with open(source_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # ১. ক্যাটাগরি বা বড় সেকশন ডিটেক্ট করা (যেমন: # ১. DIRECT / PERMANENT LINKS)
            if line.startswith("# ===") or (line.startswith("#") and any(char.isdigit() for char in line)):
                clean_group = line.replace("#", "").replace("=", "").strip()
                clean_group = re.sub(r'^[০-৯\d]+\.\s*', '', clean_group)
                if clean_group:
                    file_group_context = clean_group
                continue
            
            # ২. একক চ্যানেলের নাম ডিটেক্ট করা (যেমন: # Ekattor TV)
            if line.startswith("#"):
                current_channel_name = line.replace("#", "").strip()
                continue
            
            # ৩. লিংক প্রসেস করা
            if line.startswith("http"):
                url = line
                
                # যদি চ্যানেলের নাম খুঁজে না পাওয়া যায়, তবে ব্যাকআপ নাম নির্ধারণ
                if not current_channel_name:
                    if "bd.m3u" in url:
                        current_channel_name = "Global BD IPTV List"
                    elif "1715" in url:
                        current_channel_name = "GP Live 1715"
                    elif "1729" in url:
                        current_channel_name = "GP Live 1729"
                    else:
                        current_channel_name = "Live Channel"

                # স্মার্ট ফাংশনের মাধ্যমে প্রতিটি চ্যানেলের জন্য একক গ্রুপ ফিক্স করা হচ্ছে
                assigned_group = auto_assign_group(url, file_group_context, current_channel_name)
                
                # যাচাইকরণের আগে টোকেন ক্লিন করা
                clean_url = clean_token_from_url(url)

                # ইউটিউব লিংকের ক্ষেত্রে প্রসেসিং
                if "youtube.com" in clean_url or "youtu.be" in clean_url:
                    yt_m3u8 = get_youtube_m3u8(clean_url)
                    if yt_m3u8:
                        valid_urls.append((current_channel_name, assigned_group, yt_m3u8))
                        print(f"-> [সফল] {current_channel_name} (YouTube) -> Group: {assigned_group}")
                    else:
                        print(f"-> [বাদ] {current_channel_name} লাইভ নেই।")
                
                # সাধারণ আইপিটিভি লিংকের ক্ষেত্রে প্রসেসিং
                else:
                    try:
                        req = urllib.request.Request(clean_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=5) as response:
                            if response.getcode() == 200:
                                valid_urls.append((current_channel_name, assigned_group, clean_url))
                                print(f"-> [সচল] {current_channel_name} -> Group: {assigned_group}")
                    except:
                        print(f"-> [বাদ] {current_channel_name} কাজ করছে না বা টাইমআউট।")
                
                # পরবর্তী লাইনের জন্য চ্যানেলের নাম রিসেট
                current_channel_name = ""

    # ইউজারদের জন্য আলাদা আলাদা প্লেলিস্ট তৈরি করা
    if os.path.exists(user_file):
        with open(user_file, "r", encoding="utf-8") as f:
            users = [line.strip() for line in f if line.strip()]
    else:
        users = ["default"]

    print(f"\n--- ইউজারদের জন্য সিকিউর ফাইল তৈরি হচ্ছে ---")
    for user in users:
        # ইউজারনেম ফিল্টার করা (যেমন: "1 rony" থেকে শুধু "rony")
        user_name = user.split()[-1] if " " in user else user
        output_file = f"live_{user_name}.m3u"
        
        with open(output_file, "w", encoding="utf-8") as out:
            out.write("#EXTM3U\n\n")
            for name, group, url_str in valid_urls:
                # নিখুঁত আইপিটিভি স্ট্যান্ডার্ড ফরম্যাট যা সব প্লেয়ার সহজে রিড করতে পারে
                out.write(f'#EXTINF:-1 group-title="{group}" tvg-name="{name}" tvg-id="" tvg-logo="", {name}\n')
                out.write(f"{url_str}\n\n")
        print(f"-> {user_name}-এর জন্য তৈরি হয়েছে: {output_file}")

if __name__ == "__main__":
    check_and_scrape()  # পূর্বের টাইপো বা স্পেলিং ভুলটি (check_and _scrape) এখানে ঠিক করা হয়েছে
