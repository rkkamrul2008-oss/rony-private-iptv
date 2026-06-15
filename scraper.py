import urllib.request
import os

def check_and_scrape():
    source_file = "sources.txt"
    user_file = "users.txt"
    
    if not os.path.exists(source_file):
        print("Error: sources.txt পাওয়া যায়নি!")
        return

    # ১. সচল লিংকগুলো স্ক্র্যাপ করা
    print("--- লিংক যাচাইকরণ শুরু হলো ---")
    with open(source_file, "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    valid_urls = []
    for index, url in enumerate(urls, start=1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.getcode() == 200:
                    valid_urls.append((f"Premium Channel {index}", url))
                    print(f"-> [সচল] Channel {index}")
        except:
            print(f"-> [বাদ] Channel {index} কাজ করছে না")

    # ২. ইউজারদের জন্য আলাদা আলাদা প্লেলিস্ট তৈরি করা
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            users = [line.strip() for line in f if line.strip()]
    else:
        users = ["default"] # ইউজার ফাইল না থাকলে একটি ডিফল্ট ফাইল হবে

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
