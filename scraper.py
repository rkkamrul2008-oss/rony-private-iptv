import urllib.request
import re
import os

def check_and_scrape():
    input_file = "sources.txt"
    output_file = "live.m3u"
    
    # sources.txt ফাইলটি আছে কিনা চেক করা
    if not os.path.exists(input_file):
        print(f"Error: {input_file} found না!")
        return

    print("--- স্ক্রিপ্ট রান হচ্ছে: লিংক যাচাইকরণ শুরু হলো ---")
    
    with open(input_file, "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    valid_channels = []
    
    # প্রতিটি লিংক চেক করার লুপ
    for index, url in enumerate(urls, start=1):
        try:
            print(f"চেক করা হচ্ছে ({index}/{len(urls)}): {url}")
            
            # লিংকটি সচল কিনা যাচাই করার জন্য রিকোয়েস্ট পাঠানো
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.getcode() == 200:
                    # সচল হলে চ্যানেলের নাম অটো-জেনারেট করা (যেমন: Channel 1, Channel 2)
                    channel_name = f"Premium Channel {index}"
                    valid_channels.append((channel_name, url))
                    print("-> [সফল] লিংকটি সচল আছে!")
        except Exception as e:
            print(f"-> [বাদ] লিংকটি কাজ করছে না বা টাইমআউট হয়েছে।")

    # নতুন প্রটেক্টেড M3U ফাইল তৈরি
    with open(output_file, "w", encoding="utf-8") as out:
        out.write("#EXTM3U\n")
        for name, url in valid_channels:
            out.write(f'#EXTINF:-1 tvg-id="" tvg-name="{name}" tvg-logo="", {name}\n')
            out.write(f"{url}\n")

    print(f"\n--- কাজ শেষ! মোট {len(valid_channels)}টি সচল চ্যানেল নিয়ে '{output_file}' ফাইল তৈরি হয়েছে। ---")

if __name__ == "__main__":
    check_and_scrape()
