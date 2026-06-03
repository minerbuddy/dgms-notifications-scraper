# 🔍 DGMS Notification Scraper - Enhanced Version

## 📋 Overview

Ek automated news tracking system hai jo DGMS (Directorate General of Mine Safety) ke official website se notifications scrape karta hai. Ye system specially designed hai mining students aur professionals ke liye.

**GitHub Repository**: `minerbuddy/dgms-news-scraper`

---

## ✨ New Features (v2.0)

### 1. **Published Date Tracking** 📅
- Notification ke published date ko automatically extract karta hai
- Format: DD-MM-YYYY
- Machine learning training ke liye historical data collect hota hai

### 2. **Scrape Timestamp** ⏱️
- `scraped_at` field mein exact time store hota hai (ISO 8601 format)
- Data collection history maintain hoti hai
- Future analysis ke liye useful hai

### 3. **Priority Classification** 🚨
System automatically notifications ko 3 levels mein categorize karta hai:

| Priority | Keywords | Use Case |
|----------|----------|----------|
| **HIGH** | Exam, Oral, Result, Manager, Sirdar, Foreman, Overman, Surveyor | Critical notifications - immediate action needed |
| **MEDIUM** | Notification, Schedule, Instruction, Provisional, Declared | Important - should check soon |
| **LOW** | Others, Library, Citizen Corner | General information |

### 4. **Better Data Structure** 📊

Har notification mein ab ये fields hoti hain:

```json
{
  "title": "Notification ka pura title",
  "link": "https://www.dgms.gov.in/...",
  "published_date": "03-06-2025",
  "scraped_at": "2025-06-03T18:45:30.123456",
  "priority": "high",
  "file_type": "PDF"
}
```

---

## 🛠️ Installation & Setup

### Step 1: Repository Prepare Karo
```bash
git clone https://github.com/minerbuddy/dgms-news-scraper.git
cd dgms-news-scraper
```

### Step 2: Files Replace Karo
1. `scraper.py` ko replace karo new version ke saath
2. `.github/workflows/scrape.yml` ko update karo (ya create karo agar nahi hai)

### Step 3: Dependencies Install Karo
```bash
pip install -r requirements.txt
```

**requirements.txt** mein ye hone chahiye:
```
requests>=2.28.0
beautifulsoup4>=4.11.0
```

### Step 4: GitHub Actions Enable Karo
1. GitHub repository settings mein jao
2. `Settings` → `Actions` → `General`
3. "Allow all actions and reusable workflows" select karo

---

## 📱 Usage

### Local Testing (Apne computer par)
```bash
python scraper.py
```

**Output**:
- `news.json` file create hoga
- Console mein statistics print hogi
- Logs dekh sakte ho

### Automatic Execution (GitHub Actions via)
- **Default Schedule**: Har 6 ghante mein chalega
  - 5:30 AM IST
  - 11:30 AM IST
  - 5:30 PM IST
  - 11:30 PM IST

- **Manual Trigger**: GitHub Actions tab mein "Run workflow" button dabao

---

## 📊 JSON Output Structure

```json
[
  {
    "title": "PROVISIONAL LIST OF CANDIDATES CALLED FOR ORAL EXAMINATION...",
    "link": "https://www.dgms.gov.in/...",
    "published_date": "03-06-2025",
    "scraped_at": "2025-06-03T18:45:30.123456",
    "priority": "high",
    "file_type": "PDF"
  }
]
```

### Fields Explanation:

| Field | Description | Example |
|-------|-------------|---------|
| `title` | Notification ka title | "ORAL EXAMINATION 2025" |
| `link` | Document ka full URL | "https://www.dgms.gov.in/..." |
| `published_date` | Jab notification publish hua | "03-06-2025" |
| `scraped_at` | Jab data scrape hua (ISO format) | "2025-06-03T18:45:30" |
| `priority` | Importance level | "high", "medium", "low" |
| `file_type` | Document type | "PDF", "Document" |

---

## 🔬 Machine Learning Training Data

Isse JSON output future mein **notification classifier** banane ke liye use ho sakta hai:

### Data Collection Ke Liye:
```python
# Analysis script (future use)
import json

with open('news.json', 'r') as f:
    data = json.load(f)

# Priority distribution analyze karo
priority_stats = {
    'high': len([x for x in data if x['priority'] == 'high']),
    'medium': len([x for x in data if x['priority'] == 'medium']),
    'low': len([x for x in data if x['priority'] == 'low'])
}

print(priority_stats)
```

---

## 🐛 Troubleshooting

### Problem: "No items found"
**Solution**:
1. Website ka HTML structure change hua ho sakta hai
2. `scraper.py` mein print statements uncomment karo
3. Latest HTML inspect karo browser se

### Problem: "SSL Certificate Error"
**Solution**: Script mein pehle se `verify=False` hai, so ye kam karega

### Problem: "Date not extracted"
**Solution**: Agar site par date format different hai to `extract_date_from_text()` function ko update karo

### Problem: GitHub Actions nahi chal raha
**Solution**:
```yaml
# Ye line add karo .github/workflows/scrape.yml mein
permissions:
  contents: write
```

---

## 📈 Monitoring & Analytics

### News Count Over Time:
```
June 2025: 47 notifications
- High: 23
- Medium: 18
- Low: 6
```

### Using GitHub Actions Summary:
- Har execution ke baad automatic summary generate hota hai
- "Actions" tab mein dekh sakte ho

---

## 🔐 Security Best Practices

1. **API Keys**: Koi API key use nahi ho raha (good!)
2. **SSL Verification**: Production mein `verify=True` use karo
3. **Rate Limiting**: Website ko overload mat karo, 6 hours interval rakha hai
4. **User Agent**: Legitimate browser identify karte ho

---

## 🚀 Future Enhancements

### Planned Features:
- [ ] Email notifications for HIGH priority items
- [ ] Telegram bot integration
- [ ] Web dashboard for visualization
- [ ] ML-based auto-priority classification
- [ ] Duplicate detection improvement
- [ ] Database storage (instead of JSON)
- [ ] API endpoint for querying data

### Custom Priority Rules:
Agar apne rules add karna ho:

```python
def classify_priority(title):
    # Apne custom keywords add karo
    custom_keywords = {
        'high': ['Exam', 'Result', 'Your_Custom_Keyword'],
        'medium': ['..'],
        'low': ['..']
    }
    # Implementation...
```

---

## 📞 Support & Contributions

- **Issues**: GitHub Issues mein report karo
- **Improvements**: Pull requests welcome hain
- **Questions**: Discussions tab use karo

---

## 📄 License

MIT License - Free to use and modify

---

## 🎯 Use Cases

### 1. **Personal Notification Tracker**
```python
# High priority notifications check karo
import json

with open('news.json') as f:
    data = json.load(f)

high_priority = [x for x in data if x['priority'] == 'high']
print(f"🚨 {len(high_priority)} HIGH PRIORITY notifications!")
for item in high_priority:
    print(f"- {item['title']}")
```

### 2. **Daily Digest Email** (Future)
```python
# Roz subah 6 AM ko email bhej do
from datetime import datetime

last_24h = [x for x in data if 
    datetime.fromisoformat(x['scraped_at']) > 
    datetime.now() - timedelta(days=1)]
```

### 3. **Dashboard Integration**
```python
# Web dashboard par display karo
json_url = "https://raw.githubusercontent.com/minerbuddy/dgms-news-scraper/main/news.json"
# Fetch karo aur visualize karo
```

---

## 📝 Sample Cron Schedules

Agar timing change karna ho:

```yaml
# Har 3 ghante mein
- cron: '0 */3 * * *'

# Roz 8 AM IST (2:30 AM UTC)
- cron: '30 2 * * *'

# Roz 2 times - 8 AM aur 5 PM IST
- cron: '30 2,11 * * *'

# Weekdays only (Mon-Fri)
- cron: '0 */6 * * 1-5'
```

---

## 🎓 Learning Resources

- **Beautiful Soup**: https://www.crummy.com/software/BeautifulSoup/
- **GitHub Actions**: https://docs.github.com/en/actions
- **Python Datetime**: https://docs.python.org/3/library/datetime.html
- **Regex**: https://regex101.com/

---

**Last Updated**: June 2025  
**Version**: 2.0  
**Status**: ✅ Production Ready
