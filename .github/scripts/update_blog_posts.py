import re
import xml.etree.ElementTree as ET
from datetime import datetime
import requests

RSS_URL = "https://lafayettegabe.me/index.xml"
README_PATH = "README.md"

def parse_rss(url):
    response = requests.get(url)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    
    posts = []
    for item in root.findall('.//item'):
        pub_date = item.find('pubDate').text
        try:
            parsed_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
            formatted_date = parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            continue
            
        title = item.find('title').text
        link = item.find('link').text
        
        if 'readme' in link.lower():
            continue
            
        posts.append({
            'date': formatted_date,
            'title': title,
            'link': link
        })
    
    return posts[:5]

def update_readme(posts):
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_section = '<!--START_SECTION:blog-posts-->\n'
    for post in posts:
        new_section += f"-   {post['date']} [{post['title']}]({post['link']})\n"
    new_section += '<!--END_SECTION:blog-posts-->'
    
    updated_content = re.sub(
        r'<!--START_SECTION:blog-posts-->.*?<!--END_SECTION:blog-posts-->',
        new_section,
        content,
        flags=re.DOTALL
    )
    
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(updated_content)

if __name__ == "__main__":
    posts = parse_rss(RSS_URL)
    if posts:
        update_readme(posts)
    else:
        print("No valid blog posts found in RSS feed")
