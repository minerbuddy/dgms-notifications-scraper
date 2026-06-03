import requests
from bs4 import BeautifulSoup
import json
import urllib3
from datetime import datetime
import re

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
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            notification_list = []
            
            # CRITICAL FIX: Find the specific form that contains the notification list
            form_tag = soup.find('form', action="/UserView")
            
            if form_tag:
                # Find all list items ONLY inside that specific form
                items = form_tag.find_all('li')
                
                for item in items:
                    link_tag = item.find('a', href=True)
                    
                    if link_tag:
                        title = item.get_text(separator=" ", strip=True)
                        
                        # Clean title: Remove "(530 KB)" type text
                        clean_title = re.sub(r'\s*\(\s*\d+\.?\d*\s*[KMG]B\s*\).*', '', title).strip()
                        
                        href = link_tag['href']
                        full_url = href if href.startswith('http') else f"https://www.dgms.gov.in{href}"
                        
                        if clean_title and len(clean_title) > 5:
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
                            
                            notification_list.append(notification_item)
            
            if notification_list:
                seen = set()
                final_notifications = []
                
                for n in notification_list:
                    key = (n['title'], n['link'])
                    if key not in seen:
                        final_notifications.append(n)
                        seen.add(key)
                
                priority_order = {'high': 0, 'medium': 1, 'low': 2}
                final_notifications.sort(key=lambda x: (
                    priority_order.get(x['priority'], 3),
                    x['published_date'] or '0000-00-00'
                ), reverse=True)
                
                with open('notification.json', 'w', encoding='utf-8') as f:
                    json.dump(final_notifications, f, indent=4, ensure_ascii=False)
                    
                # Hata dena ya rakhna aapki marzi hai local testing ke liye
                # print(f"✅ Success! Found {len(final_notifications)} notifications.")
            else:
                raise Exception("No notifications found inside the <form action='/UserView'> tag.")
                
        else:
            raise Exception(f"HTTP Request failed with status code: {response.status_code}")
            
    except Exception as e:
        raise e

if __name__ == "__main__":
    scrape_dgms()
