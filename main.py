import httpx
import time
import os
import re
from flask import Flask
from threading import Thread

# ==========================================
# 🌐 ফ্লাস্ক সার্ভার (রেন্ডার ফ্রি রাখার জন্য)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Domain Hunter Bot is Alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ==========================================
# 🧠 ১. পার্মানেন্ট ফাইল-মেমোরি সিস্টেম
# ==========================================
MEMORY_FILE = "seen_domains.txt"

def load_seen_domains():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_domain_to_memory(domain):
    with open(MEMORY_FILE, "a") as f:
        f.write(domain + "\n")

seen_domains = load_seen_domains()
print(f"[*] মেমোরি লোড হয়েছে: ইতিমধ্যে {len(seen_domains)} টি ডোমেইন মেমোরিতে সংরক্ষিত আছে।\n", flush=True)

# ==========================================
# ⚙️ ২. টেলিগ্রাম কনফিগারেশন
# ==========================================
TELEGRAM_BOT_TOKEN = "8887958648:AAFxD9U3XzmR4G-dKKNBbfuRRaWqS9ORyb4"
TELEGRAM_CHAT_IDS = [
          "8039516027", "7269487985", "6245614648", 
          "1852918448", "7709102746", "5632044849", 
          "1954309535", "6878096460",
]

def send_telegram_alert(url, source, phone_det, signup_det):
    msg = (
        f"🗽 *New Website!*\n\n"
        f"🌐 *URL:* `{url}`\n\n"
        f"🗿 *Status:* TRY or GAY..."
    )
    
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    for chat_id in TELEGRAM_CHAT_IDS:
        payload = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
        try:
            res = httpx.post(tg_url, json=payload, timeout=5)
            if res.status_code == 200:
                print(f"[📲] নোটিফিকেশন পাঠানো হয়েছে (Chat ID: {chat_id})", flush=True)
            else:
                print(f"[!] টেলিগ্রাম এরর ({chat_id}): {res.text}", flush=True)
        except Exception as e:
            print(f"[!] টেলিগ্রাম কানেকশন এরর ({chat_id}): {e}", flush=True)

# ==========================================
# 🌐 ৩. সুনির্দিষ্ট ২০টি ক্যাটাগরি ও ২০টি সোর্স
# ==========================================
categories = [
    "wallet", "pay", "banking", "exchange", "crypto", 
    "shop", "store", "delivery", "market", "order", 
    "login", "signup", "register", "account", "dashboard", 
    "portal", "panel", "auth", "verify", "billing"
]

def process_and_filter_domains(raw_domains):
    new_unique_domains = []
    for domain in raw_domains:
        domain = domain.strip().lower()
        if domain and not domain.startswith('*') and '.' in domain and ' ' not in domain:
            if domain not in seen_domains:
                seen_domains.add(domain)
                save_domain_to_memory(domain)
                new_unique_domains.append(domain)
    return new_unique_domains

def get_base_domains(data):
    if not isinstance(data, list):
        return []
    domains = []
    for entry in data:
        name_value = entry.get('name_value', '')
        for domain in name_value.split('\n'):
            domains.append(domain)
    return process_and_filter_domains(domains)

# --- মূল ২০টি সোর্স এন্ডপয়েন্ট ---
def source_1(kw):
    try:
        res = httpx.get(f"https://crt.sh/?q={kw}&output=json", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        return get_base_domains(res.json()) if res.status_code == 200 else []
    except: return []

def source_2(kw):
    try:
        res = httpx.get(f"https://crt.sh/?q=%.{kw}.com&output=json", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        return get_base_domains(res.json()) if res.status_code == 200 else []
    except: return []

def source_3(kw):
    try:
        res = httpx.get(f"https://urlscan.io/api/v1/search/?q={kw}", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        if res.status_code == 200:
            raw = [item.get('page', {}).get('domain', '') for item in res.json().get('results', [])]
            return process_and_filter_domains(raw)
    except: pass
    return []

def source_4(kw):
    try:
        res = httpx.get(f"https://crt.sh/?q={kw}&exclude=expired&output=json", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        return get_base_domains(res.json()) if res.status_code == 200 else []
    except: return []

def source_5(kw):
    try:
        res = httpx.get(f"https://crt.sh/?q=%{kw}%&output=json", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        return get_base_domains(res.json()) if res.status_code == 200 else []
    except: return []

def source_6(kw):
    try:
        res = httpx.get(f"https://urlscan.io/api/v1/search/?q=domain:{kw}", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        if res.status_code == 200:
            raw = [item.get('page', {}).get('domain', '') for item in res.json().get('results', [])]
            return process_and_filter_domains(raw)
    except: pass
    return []

def source_7(kw):
    try:
        res = httpx.get(f"https://crt.sh/?q={kw}&match=like&output=json", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        return get_base_domains(res.json()) if res.status_code == 200 else []
    except: return []

def source_8(kw):
    try:
        res = httpx.get(f"https://crt.sh/?q=%25{kw}%25&output=json", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        return get_base_domains(res.json()) if res.status_code == 200 else []
    except: return []

def source_9(kw):
    try:
        res = httpx.get(f"https://urlscan.io/api/v1/search/?q=page.title:{kw}", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        if res.status_code == 200:
            raw = [item.get('page', {}).get('domain', '') for item in res.json().get('results', [])]
            return process_and_filter_domains(raw)
    except: pass
    return []

def source_10(kw):
    try:
        res = httpx.get(f"https://crt.sh/?q=*.{kw}.*&output=json", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        return get_base_domains(res.json()) if res.status_code == 200 else []
    except: return []

def source_11(kw):
    try:
        res = httpx.get(f"https://api.certspotter.com/v1/issuances?domain={kw}&include_subdomains=1&expand=dns_names", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        if res.status_code == 200:
            domains = []
            for item in res.json():
                for dns in item.get('dns_names', []):
                    domains.append(dns)
            return process_and_filter_domains(domains)
    except: pass
    return []

def source_12(kw):
    try:
        res = httpx.get(f"https://dns.bufferover.cc/dns?q={kw}", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        if res.status_code == 200:
            data = res.json()
            raw = []
            for entry in data.get('FDNS_A', []):
                parts = entry.split(',')
                if len(parts) > 1:
                    raw.append(parts[1])
            for entry in data.get('RDNS', []):
                parts = entry.split(',')
                if len(parts) > 1:
                    raw.append(parts[1])
            return process_and_filter_domains(raw)
    except: pass
    return []

def source_13(kw):
    try:
        res = httpx.get(f"https://api.threatminer.org/v2/domain.php?q={kw}&rt=5", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        if res.status_code == 200:
            raw = res.json().get('results', [])
            return process_and_filter_domains(raw)
    except: pass
    return []

def source_14(kw):
    try:
        res = httpx.get(f"https://api.hackertarget.com/hostsearch/?q={kw}", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        if res.status_code == 200 and "API count exceeded" not in res.text:
            domains = []
            for line in res.text.split('\n'):
                if ',' in line:
                    domains.append(line.split(',')[0])
            return process_and_filter_domains(domains)
    except: pass
    return []

def source_15(kw):
    try:
        res = httpx.get(f"https://crt.sh/?q=%.{kw}&output=json", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        return get_base_domains(res.json()) if res.status_code == 200 else []
    except: return []

def source_16(kw):
    try:
        res = httpx.get(f"https://crt.sh/?q=login.{kw}&output=json", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        return get_base_domains(res.json()) if res.status_code == 200 else []
    except: return []

def source_17(kw):
    try:
        res = httpx.get(f"https://urlscan.io/api/v1/search/?q=host:{kw}", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        if res.status_code == 200:
            raw = [item.get('page', {}).get('domain', '') for item in res.json().get('results', [])]
            return process_and_filter_domains(raw)
    except: pass
    return []

def source_18(kw):
    try:
        res = httpx.get(f"https://urlscan.io/api/v1/search/?q=task.domain:{kw}", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        if res.status_code == 200:
            raw = [item.get('page', {}).get('domain', '') for item in res.json().get('results', [])]
            return process_and_filter_domains(raw)
    except: pass
    return []

def source_19(kw):
    try:
        res = httpx.get(f"https://crt.sh/?q=%.{kw}&exclude=expired&output=json", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        return get_base_domains(res.json()) if res.status_code == 200 else []
    except: return []

def source_20(kw):
    try:
        res = httpx.get(f"https://crt.sh/?q=app.{kw}.*&output=json", timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        return get_base_domains(res.json()) if res.status_code == 200 else []
    except: return []

sources_list = [
    ("crt.sh-Standard", source_1),
    ("crt.sh-Wildcard-Com", source_2),
    ("urlscan-Search", source_3),
    ("crt.sh-No-Expired", source_4),
    ("crt.sh-Double-Wildcard", source_5),
    ("urlscan-Domain-Query", source_6),
    ("crt.sh-Match-Like", source_7),
    ("crt.sh-Org-Pattern", source_8),
    ("urlscan-Page-Title", source_9),
    ("crt.sh-Subdomain-Variant", source_10),
    ("CertSpotter-API", source_11),
    ("BufferOver-DNS", source_12),
    ("ThreatMiner-API", source_13),
    ("HackerTarget-HostSearch", source_14),
    ("crt.sh-Reverse-Query", source_15),
    ("crt.sh-Specific-Login", source_16),
    ("urlscan-Host-Search", source_17),
    ("urlscan-Task-Domain", source_18),
    ("crt.sh-Wildcard-Exclude", source_19),
    ("crt.sh-App-Prefix", source_20)
]

# ==========================================
# 🚀 ৪. স্মার্ট ব্যাকঅফ ও হান্টিং লুপ
# ==========================================
print("[🚀] ২০টি সোর্স সমেত স্মার্ট ভ্যালিডেশন ইঞ্জিন চালু হয়েছে...\n", flush=True)

if __name__ == '__main__':
    keep_alive()  
    print("[🚀] ফ্লাস্ক ও হান্টিং ইঞ্জিন ব্যাকগ্রাউন্ডে চালু হয়েছে...\n", flush=True)

cat_index = 0
attempt = 0

while True:
    attempt += 1
    kw = categories[cat_index]
    cat_index = (cat_index + 1) % len(categories)
    
    domains = []
    used_source = ""
    
    for source_name, fetch_func in sources_list:
        print(f"[🔍 চেষ্টা #{attempt}] ক্যাটাগরি: '{kw}' | সোর্স: [{source_name}]", flush=True)
        try:
            res_domains = fetch_func(kw)
            if res_domains:
                domains = res_domains
                used_source = source_name
                break
        except Exception as e:
            print(f"   [!] সোর্স এরর: {e}", flush=True)
        
        # রেট-লিমিট ও ব্লক এড়াতে নিরাপদ বিরতি
        time.sleep(1)
        
    if domains:
        print(f"[✔] ইউনিক ডোমেইন পাওয়া গেছে ({len(domains)} টি) [{used_source}]। স্ট্রাকচারাল ফর্ম চেক হচ্ছে...", flush=True)
        
        for domain in domains[:5]:
            target_url = f"https://{domain}"
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                live_res = httpx.get(target_url, timeout=4, headers=headers, follow_redirects=True)
                
                if live_res.status_code == 200:
                    html_content = live_res.text.lower()
                    
                    has_form = bool(re.search(r'<form\b[^>]*>', html_content))
                    inputs = re.findall(r'<input\b[^>]*>', html_content, re.IGNORECASE)
                    phone_detected = False
                    signup_detected = False
                    
                    for inp in inputs:
                        inp_l = inp.lower()
                        if any(k in inp_l for k in ['phone', 'mobile', 'otp', 'sms', 'whatsapp', 'verif', 'pin', 'tel']):
                            if 'type="hidden"' not in inp_l and 'type=\'hidden\'' not in inp_l:
                                phone_detected = True
                        if any(k in inp_l for k in ['password', 'register', 'signup', 'create']):
                            signup_detected = True
                    
                    forms = re.findall(r'<form\b[^>]*>(.*?)</form>', html_content, re.IGNORECASE | re.DOTALL)
                    form_text = " ".join(forms).lower()
                    has_signup_text = any(k in form_text for k in ['sign up', 'register', 'create account', 'signup', 'sign-up'])
                    
                    is_valid_phone = phone_detected
                    is_valid_signup = has_form and (signup_detected or has_signup_text)
                    
                    if is_valid_phone or is_valid_signup:
                        print(f"\n🎉 [🎯 আসল টার্গেট সাইট ভেরিফাইড!]", flush=True)
                        print(f"👉 URL: {target_url}", flush=True)
                        print(f"👉 Source: {used_source}", flush=True)
                        
                        send_telegram_alert(target_url, used_source, is_valid_phone, is_valid_signup)
                    else:
                        print(f"   [x] স্কিপড (আসল ফর্ম বা ফোন ইনপুট নেই): {domain}", flush=True)
                else:
                    print(f"   [x] ডেড সাইট: {domain} ({live_res.status_code})", flush=True)
                
                time.sleep(0.5)
            except:
                continue
    else:
        print(f"[-] এই ক্যাটাগরিতে ডেটা আসেনি, পরবর্তী ক্যাটাগরিতে যাচ্ছি...\n", flush=True)
       
    time.sleep(3)
