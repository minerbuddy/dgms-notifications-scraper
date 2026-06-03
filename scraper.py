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
        print("🔄 Scraping shuru ho rahi hai...")
        print(f"📍 URL: {url}")
        
        response = requests.get(url, headers=headers, verify=False, timeout=20)
        
        if response.status_code == 200:
            print("✅ Page successfully loaded")
            soup = BeautifulSoup(response.content, 'html.parser')
            news_list = []
            
            # Find all notification items
            # Looking for list items or table rows containing notifications
            items = soup.find_all(['tr', 'li', 'div'], class_=re.compile(r'.*item.*|.*notification.*', re.I))
            
            # Agar specific class se nahi mile to generic elements se search karo
            if not items:
                items = soup.find_all(['tr', 'li'])
            
            print(f"📊 Total items found: {len(items)}")
            
            for item in items:
                # Link extract karo
                link_tag = item.find('a', href=True)
                
                if link_tag:
                    # Title/Text extract karo
                    title = item.get_text(separator=" ", strip=True)
                    
                    # Title ko clean karo - file size indicator se pehle ka text
                    clean_title = re.sub(r'\s*\(\s*\d+\s*[KMG]B\s*\).*', '', title)
                    clean_title = clean_title.strip()
                    
                    # PDF links ko prefer karo but other docs bhi le lo
                    href = link_tag['href']
                    full_url = href if href.startswith('http') else f"https://www.dgms.gov.in{href}"
                    
                    if clean_title and len(clean_title) > 10:  # Minimum length check
                        # Published date extract karo
                        published_date = extract_date_from_text(title)
                        
                        # Priority assign karo
                        priority = classify_priority(clean_title)
                        
                        # Scraped timestamp add karo (ISO format)
                        scraped_at = datetime.now().isoformat()
                        
                        news_item = {
                            "title": clean_title,
                            "link": full_url,
                            "published_date": published_date,  # Date jab notification publish hua
                            "scraped_at": scraped_at,  # Jab hum scrape kiye
                            "priority": priority,  # high, medium, low
                            "file_type": "PDF" if ".pdf" in full_url.lower() else "Document"
                        }
                        
                        news_list.append(news_item)
            
            if news_list:
                # Duplicates remove karo (same title aur link)
                seen = set()
                final_news = []
                
                for n in news_list:
                    key = (n['title'], n['link'])
                    if key not in seen:
                        final_news.append(n)
                        seen.add(key)
                
                # Priority ke hisaab se sort karo (high -> medium -> low)
                priority_order = {'high': 0, 'medium': 1, 'low': 2}
                final_news.sort(key=lambda x: (
                    priority_order.get(x['priority'], 3),
                    x['published_date'] or '0000-00-00'
                ), reverse=True)
                
                # JSON file mein save karo
                with open('news.json', 'w', encoding='utf-8') as f:
                    json.dump(final_news, f, indent=4, ensure_ascii=False)
                
                print(f"✅ Bhai, {len(final_news)} news items mil gayi hain!")
                print(f"   - High priority: {sum(1 for n in final_news if n['priority'] == 'high')}")
                print(f"   - Medium priority: {sum(1 for n in final_news if n['priority'] == 'medium')}")
                print(f"   - Low priority: {sum(1 for n in final_news if n['priority'] == 'low')}")
                print(f"📁 File saved: news.json")
                
                # First 5 items print karo for debugging
                print("\n🔝 Top 5 notifications:")
                for i, news in enumerate(final_news[:5], 1):
                    print(f"{i}. [{news['priority'].upper()}] {news['title'][:80]}...")
                    if news['published_date']:
                        print(f"   📅 Published: {news['published_date']}")
                    print(f"   ⏱️  Scraped: {news['scraped_at']}")
                    print()
            else:
                print("❌ Yaar, list khali reh gayi. HTML structure check karna padega.")
                print("💡 Content preview:")
                print(soup.prettify()[:500])
        else:
            print(f"❌ Error: Status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ Galti ho gayi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    scrape_dgms()
