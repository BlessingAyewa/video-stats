from googleapiclient.discovery import build
import re
import gspread
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import json



# Initialize Session
session = HTMLSession()

# Defining Variables
api_service_name = 'youtube'
api_version = 'v3'
developer_key = 'INSERT-YOUR-KEY-HERE' # Get your developer key from Google Cloud
pattern = [r'([\w\W]+)v=([\w\W.]{11})', r'([\w\W]+)live/([\w\W.]{11})', r'([\w\W]+).be/([\w\W.]{11})', r'([\w\W]+)shorts/([\w\W.]{11})']
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/json,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

# Connecting to Google Sheet
try:
    gc = gspread.service_account(filename='key.json') # Get your JSON key from Google Cloud and give your service account email editor access to your Google Sheet.
    sh = gc.open('GoogleSheet Name')
    worksheet = sh.worksheet('Sheet1')
    worksheet_data = worksheet.get_all_values()[2:]
    link_col_index = 0
    platform_col_index = 1
    print('Successfully connected to Google Sheet.')
except Exception as e:
    print(f"Error connecting to Google Sheet: {e}")



# Initializing YouTube API
try:
    youtube = build(api_service_name, api_version, developerKey=developer_key)
    print("Successfully initialized YouTube API.")
except Exception as e:
    print(f"Error initializing YouTube API: {e}")


# Defining the scraper function for each platform
def youtube_scraper(video_link):
    for pat in pattern:
        match = re.search(pat, video_link)
        if match:
            video_id = match.group(2)
            request = youtube.videos().list(id=video_id, part="statistics")
            response = request.execute()
            scraped_views = int(response['items'][0]['statistics']['viewCount'])
            scraped_likes = int(response['items'][0]['statistics']['likeCount'])
            scraped_comments = int(response['items'][0]['statistics']['commentCount'])
            return scraped_views, scraped_likes, scraped_comments
            break


def tiktok_scraper(video_link):
    r = session.get(video_link)
    r.html.render(timeout=10, sleep = 10)
    soup = BeautifulSoup(r.html.html, 'html.parser')
    sub_html = soup.find('script', id = '__UNIVERSAL_DATA_FOR_REHYDRATION__')
    data = json.loads(sub_html.string)["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]['stats']
    scraped_views = data['playCount']
    scraped_likes = data['diggCount']
    scraped_comments = data['commentCount']
    return scraped_views, scraped_likes, scraped_comments


def facebook_scraper(video_link):
    r = session.get(video_link, headers=header)
    r.html.render(timeout=50, sleep = 40)
    soup = BeautifulSoup(r.html.html, 'html.parser')
    view_text = soup.find('span', class_ = '_26fq').text
    like_text = soup.find('span', class_ = "xt0b8zv").text
    comment_text = soup.select_one('span.html-span.xdj266r.x14z9mp.xat24cr.x1lziwak.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x1hl2dhg.x16tdsg8.x1vvkbs.xkrqix3.x1sur9pj').text
    
    # Clean View_text
    if 'K views' in view_text:
        view_str = view_text.replace('K views', '').strip()
        scraped_view = int(float(view_str) * 1000)
    elif 'M views' in view_text:
        view_str = view_text.replace('M views', '').strip()
        scraped_view = int(float(view_str) * 1000000)
    elif ',' in view_text:
        view_str = view_text.replace(' views', '').replace(',', '').strip()
        scraped_view = int(view_str)
    else:
        view_str = view_text.replace(' views', '').strip()
        scraped_view = int(view_str)

    # Clean like_text
    if 'K' in like_text:
        like_str = like_text.replace('K', '').strip()
        scraped_like = int(float(like_str) * 1000)
    elif 'M' in like_text:
        like_str = like_text.replace('M', '').strip()
        scraped_like = int(float(like_str) * 1000000)
    elif ',' in like_text:
        like_str = like_text.replace(',', '').strip()
        scraped_like = int(like_str)
    else:
        like_str = like_text.strip()
        scraped_like = int(like_str)

    # Clean comment_text
    if 'K comments' in comment_text:
        comment_str = comment_text.replace('K comments', '').strip()
        scraped_comment = int(float(comment_str) * 1000)
    elif ',' in comment_text:
        comment_str = comment_text.replace(' comments', '').replace(',', '').strip()
        scraped_comment = int(comment_str)
    else:
        comment_str = comment_text.replace(' comments', '').strip()
        scraped_comment = int(comment_str)
    
    return scraped_view, scraped_like, scraped_comment





# Data extraction logic
extracted_views = []
extracted_comments = []
extracted_likes = []

for index, row in enumerate(worksheet_data):
    views = 'N/A'
    likes = 'N/A'       
    comments = 'N/A'
    link = row[link_col_index]
    platform = row[platform_col_index].lower()
    print(f'Row {index + 2}: Evaluating {link} - {platform}')
    try:
        if 'youtube' in platform:
            views, likes, comments =  youtube_scraper(link)
        elif 'tiktok' in platform:
            views, likes, comments =  tiktok_scraper(link)
        elif 'facebook' in platform:
            views, likes, comments =  facebook_scraper(link)
    except Exception as e:
        print (f'Row {index + 2}: Error evaluating {link} - {e}')
    extracted_views.append(views)
    extracted_likes.append(likes)
    extracted_comments.append(comments)


session.close()

# Updating the googlesheet
update_views = [[view] for view in extracted_views]
worksheet.update(update_views, 'C3:C')

update_likes = [[like] for like in extracted_likes]
worksheet.update(update_likes, 'D3:D')

update_comments = [[comment] for comment in extracted_comments]
worksheet.update(update_comments, 'E3:E')
print('Views, Likes, and Comments count retrieved successfully!')
