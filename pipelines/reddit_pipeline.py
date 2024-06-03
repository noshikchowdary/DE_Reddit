import pandas as pd
import requests
import logging
from typing import List, Dict, Any, Optional

from etls.reddit_etl import connect_reddit, extract_posts, transform_data, load_data_to_csv
from utils.constants import CLIENT_ID, SECRET, OUTPUT_PATH

logger = logging.getLogger(__name__)

class RedditPipeline:
    """A pipeline for fetching and processing Reddit data."""
    
    def __init__(self, base_url: str = "https://www.reddit.com"):
        """Initialize the Reddit pipeline.
        
        Args:
            base_url: The base URL for Reddit API
        """
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'RedditDataPipeline/1.0'
        }
    
    def fetch_subreddit_posts(self, subreddit: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch posts from a subreddit.
        
        Args:
            subreddit: The subreddit to fetch posts from
            limit: Maximum number of posts to fetch
            
        Returns:
            List of post data dictionaries
        """
        url = f"{self.base_url}/r/{subreddit}/hot.json"
        params = {'limit': limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for post in data['data']['children']:
                if self.validate_post_data(post['data']):
                    posts.append(post['data'])
            
            return posts
            
        except requests.RequestException as e:
            logger.error(f"Error fetching posts from {subreddit}: {str(e)}")
            return []
    
    def fetch_post_comments(self, subreddit: str, post_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch comments for a specific post.
        
        Args:
            subreddit: The subreddit where the post is located
            post_id: The ID of the post
            limit: Maximum number of comments to fetch
            
        Returns:
            List of comment data dictionaries
        """
        url = f"{self.base_url}/r/{subreddit}/comments/{post_id}.json"
        params = {'limit': limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            comments = []
            for comment in data[1]['data']['children']:
                if comment['kind'] == 't1':  # Only include actual comments
                    comments.append(comment['data'])
            
            return comments
            
        except requests.RequestException as e:
            logger.error(f"Error fetching comments for post {post_id}: {str(e)}")
            return []
    
    def validate_post_data(self, post_data: Dict[str, Any]) -> bool:
        """Validate post data structure.
        
        Args:
            post_data: The post data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['id', 'title', 'author', 'score', 'created_utc', 'num_comments', 'url']
        return all(field in post_data for field in required_fields)
    
    def process_post(self, post_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single post's data.
        
        Args:
            post_data: The post data to process
            
        Returns:
            Processed post data or None if invalid
        """
        if not self.validate_post_data(post_data):
            return None
            
        return {
            'post_id': post_data['id'],
            'title': post_data['title'],
            'author': post_data['author'],
            'score': post_data['score'],
            'created_at': post_data['created_utc'],
            'comment_count': post_data['num_comments'],
            'url': post_data['url']
        }

def reddit_pipeline(file_name: str, subreddit: str, time_filter='day', limit=None):
    # connecting to reddit instance
    instance = connect_reddit(CLIENT_ID, SECRET, 'Airscholar Agent')
    # extraction
    posts = extract_posts(instance, subreddit, time_filter, limit)
    post_df = pd.DataFrame(posts)
    # transformation
    post_df = transform_data(post_df)
    # loading to csv
    file_path = f'{OUTPUT_PATH}/{file_name}.csv'
    load_data_to_csv(post_df, file_path)

    return file_path
