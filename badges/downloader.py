import os
import requests
from urllib.parse import quote
from time import sleep

output_dir = os.path.dirname(__file__)
os.makedirs(output_dir, exist_ok=True)

# badges to download (filename, label, color, shields.io logo)
BADGES = [

]

STYLE = "for-the-badge"
ATTEMPTS = 3
TIMEOUT = 15
SLEEP_BETWEEN = 1.0  # seconds between retries

def shields_url(label, message, color, style, logo=None, fmt="svg"):
    qlabel = quote(label)
    qmessage = quote(message)
    if logo:
        return f"https://img.shields.io/badge/{qlabel}-{qmessage}-{color}?style={style}&logo={logo}&logoColor=white&format={fmt}"
    return f"https://img.shields.io/badge/{qlabel}-{qmessage}-{color}?style={style}&format={fmt}"

def download_file(url, out_path, timeout=TIMEOUT):
    headers = {
        "User-Agent": "python-requests/BadgesDownloader/1.0",
        "Accept": "image/svg+xml, */*"
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    content = resp.content
    # Basic SVG sanity check (look for '<svg' near start)
    head = content[:512].lower()
    if b"<svg" not in head and not head.strip().startswith(b"<?xml"):
        raise ValueError("Downloaded content does not look like an SVG")
    with open(out_path, "wb") as f:
        f.write(content)

def fetch_badge(b):
    url = shields_url(b["label"], b["message"], b["color"], STYLE, logo=b.get("logo"), fmt="svg")
    out_path = os.path.join(output_dir, f"{b['filename']}.svg")
    for i in range(1, ATTEMPTS + 1):
        try:
            print(f"[{i}/{ATTEMPTS}] Downloading: {b['filename']} <- {url}")
            download_file(url, out_path)
            size = os.path.getsize(out_path)
            print(f"Saved: {out_path} ({size} bytes)")
            return True
        except Exception as e:
            print(f"Attempt {i} for {b['filename']} failed: {e}")
            if i < ATTEMPTS:
                sleep(SLEEP_BETWEEN)
    # fallback: create small metadata file so LaTeX won't fail with missing file
    txt_path = os.path.join(output_dir, f"{b['filename']}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Badge: {b['label']}\nSource: {url}\n")
    print(f"All attempts failed for {b['filename']}. Created fallback: {txt_path}")
    return False

def main():
    results = {}
    for b in BADGES:
        ok = fetch_badge(b)
        results[b["filename"]] = ok
    print("Summary:")
    for name, ok in results.items():
        print(f" - {name}: {'OK' if ok else 'FAILED (fallback)'}")

if __name__ == "__main__":
    main()