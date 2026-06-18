import requests
from bs4 import BeautifulSoup
import json
import urllib3
from datetime import datetime
import re
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extract_date_from_text(text):
    date_patterns = [
        r'\d{1,2}-\d{1,2}-\d{4}',  
        r'\d{1,2}/\d{1,2}/\d{4}',  
        r'\d{1,2}\.\d{1,2}\.\d{4}',  
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

def classify_priority(title):
    title_lower = title.lower()
    high_priority_keywords = ['exam', 'examination', 'oral', 'interview', 'result', 'final', 'manager', 'sirdar', 'foreman', 'overman', 'surveyor']
    medium_priority_keywords = ['notification', 'schedule', 'instruction', 'provisional', 'call', 'declared', 'list', 'slot', 'booking', 'verification']
    
    for keyword in high_priority_keywords:
        if keyword in title_lower:
            return 'high'
    for keyword in medium_priority_keywords:
        if keyword in title_lower:
            return 'medium'
    return 'low'

def scrape_dgms():
    url = "https://www.dgms.gov.in/UserView/index?mid=1603"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 1. Purana data load karo taaki history safe rahe
    existing_data = []
    if os.path.exists('notification.json'):
        with open('notification.json', 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
                
    # 2. Purane titles ka set bana lo match karne ke liye
    existing_titles = {item['title'] for item in existing_data if 'title' in item}
    new_items_added = 0
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            form_tag = soup.find('form', action="/UserView")
            
            if form_tag:
                items = form_tag.find_all('li')
                
                for item in items:
                    link_tag = item.find('a', href=True)
                    
                    if link_tag:
                        title = item.get_text(separator=" ", strip=True)
                        clean_title = re.sub(r'\s*\(\s*\d+\.?\d*\s*[KMG]B\s*\).*', '', title).strip()
                        href = link_tag['href']
                        full_url = href if href.startswith('http') else f"https://www.dgms.gov.in{href}"
                        
                        if clean_title and len(clean_title) > 5:
                            
                            # 3. Yahan check hoga ki NAYA notification hai ya nahi
                            if clean_title not in existing_titles:
                                published_date = extract_date_from_text(title)
                                priority = classify_priority(clean_title)
                                scraped_at = datetime.now().isoformat()
                                
                                notification_item = {
                                    "title": clean_title,
                                    "link": full_url,
                                    "published_date": published_date,
                                    "scraped_at": scraped_at,
                                    "priority": priority,
                                    "file_type": "PDF" if ".pdf" in full_url.lower() else "Link"
                                }
                                
                                existing_data.append(notification_item)
                                existing_titles.add(clean_title)
                                new_items_added += 1
            
            # 4. Agar naye items mile hain, tabhi file save karo
            if new_items_added > 0:
                priority_order = {'high': 0, 'medium': 1, 'low': 2}
                
                # Priority aur Date dono ke hisaab se sort karo
                existing_data.sort(key=lambda x: (
                    priority_order.get(x.get('priority', 'low'), 3),
                    x.get('published_date') or '0000-00-00'
                ), reverse=True)
                
                with open('notification.json', 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=4, ensure_ascii=False)
                    
                print(f"âœ… Success! Naye {new_items_added} notifications add kiye gaye.")
            else:
                print("ðŸ“­ Koi naya notification nahi mila. File update nahi hui.")
                
        else:
            raise Exception(f"HTTP Request failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"âŒ Error: {e}")
        raise e

if __name__ == "__main__":
    scrape_dgms()
