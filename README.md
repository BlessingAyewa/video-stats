# Social Media Video Stats Scraper

This project provides a Python-based solution to automatically extract views, likes, and comments from social media video posts on YouTube, Facebook, and TikTok. The extracted data is then updated directly into a Google Sheet, offering a streamlined way to monitor campaign performance.

## Features

- **YouTube API Integration**: Utilizes the official YouTube Data API for reliable and efficient data retrieval.

- **Facebook & TikTok Web Scraping**: Employs web scraping techniques to gather metrics from these platforms.

- **Google Sheet Integration**: Reads video links from a Google Sheet and writes the extracted statistics back to it.

- **Automated Campaign Monitoring**: Helps track the performance of your social media video content, enabling data-driven decisions.

## How it Works

The script reads video URLs and their corresponding social media platforms from a specified Google Sheet. It then uses the appropriate method (YouTube API for YouTube, web scraping for Facebook and TikTok) to fetch the view, like, and comment counts. Finally, these metrics are populated back into the Google Sheet.

## Configuration

- **Google Cloud Credentials**:
  - **YouTube API Key**: Obtain a developerKey from your Google Cloud Project.
  - **Google Sheets Service Account**: Create a service account in your Google Cloud Project, download its JSON key file (e.g., goolglesheet-connect.json), and share your Google Sheet with the service account's email address.

- **Update the Code**:
  - Replace 'INSERT-YOUR-KEY-HERE' with your actual YouTube API key.
  - Ensure the filename='goolglesheet-connect.json' points to the correct path of your Google Sheet service account JSON file.
  - Update 'GoogleSheet Name' to the exact name of your Google Sheet.
 
- **Python Packages**:
  - google-api-python-client
  - gspread
  - beautifulsoup4
  - requests-html

## Usage

- Organize your Google Sheet with video links in the first column and the corresponding platform (e.g., "YouTube", "Facebook", "TikTok") in the second column. 
