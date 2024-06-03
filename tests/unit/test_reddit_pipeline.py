import pytest
from unittest.mock import patch, MagicMock
from pipelines.reddit_pipeline import RedditPipeline

@pytest.fixture
def reddit_pipeline():
    return RedditPipeline()

def test_reddit_pipeline_initialization():
    """Test RedditPipeline initialization"""
    pipeline = RedditPipeline()
    assert pipeline is not None

@patch('pipelines.reddit_pipeline.requests.get')
def test_fetch_subreddit_posts(mock_get):
    """Test fetching posts from a subreddit"""
    # Mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'data': {
            'children': [
                {
                    'data': {
                        'id': 'test_id',
                        'title': 'Test Post',
                        'author': 'test_author',
                        'score': 100,
                        'created_utc': 1234567890,
                        'num_comments': 50,
                        'url': 'https://test.com'
                    }
                }
            ]
        }
    }
    mock_get.return_value = mock_response

    pipeline = RedditPipeline()
    posts = pipeline.fetch_subreddit_posts('test_subreddit', limit=1)
    
    assert len(posts) == 1
    assert posts[0]['id'] == 'test_id'
    assert posts[0]['title'] == 'Test Post'

@patch('pipelines.reddit_pipeline.requests.get')
def test_fetch_post_comments(mock_get):
    """Test fetching comments for a post"""
    # Mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'data': {
            'children': [
                {
                    'data': {
                        'id': 'comment_id',
                        'author': 'comment_author',
                        'body': 'Test comment',
                        'score': 10,
                        'created_utc': 1234567890
                    }
                }
            ]
        }
    }
    mock_get.return_value = mock_response

    pipeline = RedditPipeline()
    comments = pipeline.fetch_post_comments('test_subreddit', 'test_post_id', limit=1)
    
    assert len(comments) == 1
    assert comments[0]['id'] == 'comment_id'
    assert comments[0]['body'] == 'Test comment'

def test_data_validation():
    """Test data validation"""
    pipeline = RedditPipeline()
    
    # Test valid data
    valid_post = {
        'id': 'test_id',
        'title': 'Test Post',
        'author': 'test_author',
        'score': 100,
        'created_utc': 1234567890,
        'num_comments': 50,
        'url': 'https://test.com'
    }
    assert pipeline.validate_post_data(valid_post) is True
    
    # Test invalid data
    invalid_post = {
        'id': 'test_id',
        'title': 'Test Post',
        # Missing required fields
    }
    assert pipeline.validate_post_data(invalid_post) is False 