# API Documentation

This document provides detailed information about the APIs used in the Reddit Data Engineering Pipeline.

## Reddit API Integration

### Authentication

The pipeline uses Reddit's OAuth2 authentication. To set up:

1. Create a Reddit application at https://www.reddit.com/prefs/apps
2. Get your client ID and secret
3. Configure in `config/config.conf`:
   ```ini
   [api_keys]
   reddit_client_id = your_client_id
   reddit_secret_key = your_secret_key
   ```

### Endpoints

#### 1. Subreddit Data Collection

```python
GET /r/{subreddit}/hot
GET /r/{subreddit}/new
GET /r/{subreddit}/top
```

**Parameters**:
- `subreddit`: Name of the subreddit
- `limit`: Number of posts to fetch (default: 100)
- `after`: Fullname of the last item in the previous listing

**Response Format**:
```json
{
    "data": {
        "children": [
            {
                "data": {
                    "id": "string",
                    "title": "string",
                    "author": "string",
                    "score": "integer",
                    "created_utc": "integer",
                    "num_comments": "integer",
                    "url": "string"
                }
            }
        ]
    }
}
```

#### 2. Comment Data Collection

```python
GET /r/{subreddit}/comments/{article_id}
```

**Parameters**:
- `subreddit`: Name of the subreddit
- `article_id`: ID of the post
- `limit`: Number of comments to fetch (default: 100)

**Response Format**:
```json
{
    "data": {
        "children": [
            {
                "data": {
                    "id": "string",
                    "author": "string",
                    "body": "string",
                    "score": "integer",
                    "created_utc": "integer"
                }
            }
        ]
    }
}
```

## AWS Services Integration

### S3

#### Bucket Structure

```
s3://{bucket_name}/
├── raw/
│   ├── posts/
│   │   └── {date}/
│   └── comments/
│       └── {date}/
├── processed/
│   ├── posts/
│   │   └── {date}/
│   └── comments/
│       └── {date}/
└── analytics/
    └── {date}/
```

#### File Formats

1. **Raw Data**:
   - Format: JSON
   - Compression: GZIP
   - Naming: `{type}_{timestamp}.json.gz`

2. **Processed Data**:
   - Format: Parquet
   - Partitioning: By date
   - Naming: `{type}_{date}.parquet`

### AWS Glue

#### ETL Jobs

1. **Post Processing**:
   - Input: S3 raw posts
   - Output: S3 processed posts
   - Transformations:
     - Data cleaning
     - Schema enforcement
     - Partitioning

2. **Comment Processing**:
   - Input: S3 raw comments
   - Output: S3 processed comments
   - Transformations:
     - Data cleaning
     - Schema enforcement
     - Partitioning

### Amazon Athena

#### Tables

1. **Posts Table**:
```sql
CREATE EXTERNAL TABLE posts (
    id STRING,
    title STRING,
    author STRING,
    score INT,
    created_utc BIGINT,
    num_comments INT,
    url STRING,
    subreddit STRING
)
PARTITIONED BY (date STRING)
STORED AS PARQUET
LOCATION 's3://{bucket_name}/processed/posts/'
```

2. **Comments Table**:
```sql
CREATE EXTERNAL TABLE comments (
    id STRING,
    author STRING,
    body STRING,
    score INT,
    created_utc BIGINT,
    post_id STRING,
    subreddit STRING
)
PARTITIONED BY (date STRING)
STORED AS PARQUET
LOCATION 's3://{bucket_name}/processed/comments/'
```

## Airflow DAGs

### 1. Reddit Data Collection DAG

**Schedule**: `0 */6 * * *` (Every 6 hours)

**Tasks**:
1. `collect_subreddit_posts`
   - Collects posts from specified subreddits
   - Saves to S3 raw bucket

2. `collect_post_comments`
   - Collects comments for collected posts
   - Saves to S3 raw bucket

### 2. Data Processing DAG

**Schedule**: `0 */12 * * *` (Every 12 hours)

**Tasks**:
1. `process_posts`
   - Runs Glue job for post processing
   - Updates Athena partitions

2. `process_comments`
   - Runs Glue job for comment processing
   - Updates Athena partitions

### 3. Analytics DAG

**Schedule**: `0 0 * * *` (Daily)

**Tasks**:
1. `generate_daily_metrics`
   - Calculates daily statistics
   - Saves to S3 analytics bucket

2. `update_redshift`
   - Loads processed data to Redshift
   - Updates materialized views

## Error Handling

### API Rate Limits

- Reddit API: 60 requests per minute
- Implementation: Token bucket algorithm
- Retry strategy: Exponential backoff

### AWS Service Limits

- S3: No hard limits
- Glue: 100 concurrent runs
- Athena: 20 concurrent queries
- Redshift: Based on cluster size

## Monitoring

### Metrics

1. **API Metrics**:
   - Request count
   - Error rate
   - Response time
   - Rate limit hits

2. **Processing Metrics**:
   - Records processed
   - Processing time
   - Error count
   - Success rate

### Alerts

1. **Critical Alerts**:
   - API authentication failures
   - Processing job failures
   - Data quality violations

2. **Warning Alerts**:
   - High error rates
   - Slow processing
   - Rate limit approaching

## Best Practices

1. **API Usage**:
   - Implement rate limiting
   - Use exponential backoff
   - Cache responses when possible

2. **Data Processing**:
   - Validate data before processing
   - Implement idempotency
   - Use appropriate file formats

3. **Error Handling**:
   - Log all errors
   - Implement retry mechanisms
   - Monitor error patterns 