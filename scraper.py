import requests
from bs4 import BeautifulSoup
import json
import urllib3
from datetime import datetime
import re

# SSL Certificate errors ko ignore karne ke liye
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extract_date_from_text(text):
    """
    Text se date extract karo using regex
    Expected formats: DD-MM-YYYY, DD/MM/YYYY, etc.
    """
    date_patterns = [
        r'\d{1,2}-\d{1,2}-\d{4}',  # DD-MM-YYYY
        r'\d{1,2}/\d{1,2}/\d{4}',  # DD/MM/YYYY
        r'\d{1,2}\.\d{1,2}\.\d{4}',  # DD.MM.YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

def classify_priority(title):
    """
    Title ke base par priority assign karo
    High priority: Exam, Result, Oral, Interview, Final
    Medium priority: Notification, Schedule, Instruction, Provisional
    Low priority: Others, Library, Citizen Corner, etc.
    """
    title_lower = title.lower()
    
    high_priority_keywords = [
        'exam', 'examination', 'oral', 'interview', 'result', 'final',
        'manager', 'sirdar', 'foreman', 'overman', 'surveyor'
    ]
    
    medium_priority_keywords = [
        'notification', 'schedule', 'instruction', 'provisional', 'call',
        'declared', 'list', 'slot', 'booking', 'verification'
    ]
    
    for keyword in high_priority_keywords:
        if keyword in title_lower:
            return 'high'
    
    for keyword in medium_priority_keywords:
        if keyword in title_lower:
            return 'medium'
    
    return 'low'

def scrape_dgms():
    """
    DGMS notifications ko scrape karo
    New URL: https://www.dgms.gov.in/UserView/index?mid=1603
    """
    url = "https://www.dgms.gov.in/UserView/index?mid=1603"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            notification_list = []
            
            # Find all notification items
            items = soup.find_all(['tr', 'li', 'div'], class_=re.compile(r'.*item.*|.*notification.*', re.I))
            
            # Agar specific class se nahi mile to generic elements se search karo
            if not items:
                items = soup.find_all(['tr', 'li'])
            
            for item in items:
                link_tag = item.find('a', href=True)
                
                if link_tag:
                    title = item.get_text(separator=" ", strip=True)
                    
                    # Title ko clean karo - file size indicator se pehle ka text
                    clean_title = re.sub(r'\s*\(\s*\d+\s*[KMG]B\s*\).*', '', title).strip()
                    
                    href = link_tag['href']
                    full_url = href if href.startswith('http') else f"https://www.dgms.gov.in{href}"
                    
                    if clean_title and len(clean_title) > 10:  # Minimum length check
                        published_date = extract_date_from_text(title)
                        priority = classify_priority(clean_title)
                        scraped_at = datetime.now().isoformat()
                        
                        notification_item = {
                            "title": clean_title,
                            "link": full_url,
                            "published_date": published_date,
                            "scraped_at": scraped_at,
                            "priority": priority,
                            "file_type": "PDF" if ".pdf" in full_url.lower() else "Document"
                        }
                        
                        notification_list.append(notification_item)
            
            if notification_list:
                # Duplicates remove karo (same title aur link)
                seen = set()
                final_notifications = []
                
                for n in notification_list:
                    key = (n['title'], n['link'])
                    if key not in seen:
                        final_notifications.append(n)
                        seen.add(key)
                
                # Priority ke hisaab se sort karo (high -> medium -> low)
                priority_order = {'high': 0, 'medium': 1, 'low': 2}
                final_notifications.sort(key=lambda x: (
                    priority_order.get(x['priority'], 3),
                    x['published_date'] or '0000-00-00'
                ), reverse=True)
                
                # JSON file mein save karo
                with open('notification.json', 'w', encoding='utf-8') as f:
                    json.dump(final_notifications, f, indent=4, ensure_ascii=False)
            else:
                # Agar website layout change ho gaya aur data nahi mila
                raise Exception("No notifications found. HTML structure might have changed.")
                
        else:
            raise Exception(f"HTTP Request failed with status code: {response.status_code}")
            
    except Exception as e:
        # Raise error explicitly so GitHub Actions workflow fails and alerts you
        raise e

if __name__ == "__main__":
    scrape_dgms()
