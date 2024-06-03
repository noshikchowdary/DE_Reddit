# Deployment Guide

This guide provides detailed instructions for deploying the Reddit Data Engineering Pipeline.

## Prerequisites

Before deploying, ensure you have:

1. **Required Software**:
   - Docker (version 20.10.0 or higher)
   - Docker Compose (version 2.0.0 or higher)
   - Python 3.9 or higher
   - Git

2. **Required Accounts**:
   - AWS Account with appropriate permissions
   - Reddit API credentials
   - GitHub account (for CI/CD)

3. **Required Environment Variables**:
   Create a `.env` file in the project root with the following variables:
   ```bash
   # Database Configuration
   POSTGRES_USER=your_username
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_DB=airflow_reddit
   POSTGRES_PORT=5432

   # Airflow Configuration
   AIRFLOW_ADMIN_USER=your_admin_username
   AIRFLOW_ADMIN_PASSWORD=your_secure_password
   AIRFLOW_ADMIN_EMAIL=your_email@example.com
   AIRFLOW_WEBSERVER_PORT=8080

   # AWS Configuration
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   AWS_DEFAULT_REGION=your_aws_region
   AWS_BUCKET_NAME=your_s3_bucket_name

   # Reddit API Configuration
   REDDIT_CLIENT_ID=your_reddit_client_id
   REDDIT_SECRET_KEY=your_reddit_secret_key
   ```

## Deployment Steps

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd reddit-data-engineering
```

### 2. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure the Project

1. Copy the example configuration:
   ```bash
   cp config/config.conf.example config/config.conf
   ```

2. Edit `config/config.conf` with your settings:
   ```ini
   [database]
   database_host = localhost
   database_name = airflow_reddit
   database_port = 5432
   database_username = your_username
   database_password = your_secure_password

   [api_keys]
   reddit_secret_key = your_reddit_secret_key
   reddit_client_id = your_reddit_client_id

   [aws]
   aws_access_key_id = your_aws_access_key
   aws_secret_access_key = your_aws_secret_key
   aws_region = your_aws_region
   aws_bucket_name = your_s3_bucket_name
   ```

### 4. Deploy the Pipeline

1. Make the deployment script executable:
   ```bash
   chmod +x scripts/deployment/deploy.sh
   ```

2. Run the deployment script:
   ```bash
   ./scripts/deployment/deploy.sh
   ```

The script will:
- Check prerequisites
- Validate environment variables
- Build and start Docker containers
- Perform health checks
- Initialize the database
- Start Airflow services

### 5. Verify Deployment

1. Check service status:
   ```bash
   docker-compose ps
   ```

2. Access the Airflow UI:
   ```bash
   open http://localhost:8080
   ```

3. Check logs if needed:
   ```bash
   docker-compose logs -f
   ```

## Monitoring

### Health Checks

The deployment script includes health checks for:
- Airflow webserver
- PostgreSQL database
- Redis broker
- Celery workers

### Logs

Access logs for different services:
```bash
# Airflow webserver logs
docker-compose logs -f airflow-webserver

# Airflow scheduler logs
docker-compose logs -f airflow-scheduler

# Airflow worker logs
docker-compose logs -f airflow-worker
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   - Error: "Port XXXX is already in use"
   - Solution: Stop the service using the port or change the port in configuration

2. **Database Connection Issues**
   - Error: "Could not connect to PostgreSQL"
   - Solution: Check PostgreSQL credentials and ensure the service is running

3. **Airflow Initialization Issues**
   - Error: "Airflow db init failed"
   - Solution: Check database permissions and connection settings

### Debugging

1. Check container status:
   ```bash
   docker-compose ps
   ```

2. View detailed logs:
   ```bash
   docker-compose logs -f
   ```

3. Access container shell:
   ```bash
   docker-compose exec airflow-webserver bash
   ```

## Maintenance

### Backup

1. Database backup:
   ```bash
   docker-compose exec postgres pg_dump -U postgres airflow_reddit > backup.sql
   ```

2. Configuration backup:
   ```bash
   tar -czf config_backup.tar.gz config/
   ```

### Update

1. Pull latest changes:
   ```bash
   git pull origin main
   ```

2. Rebuild and restart:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

## Security Considerations

1. **Credentials**
   - Never commit `.env` or `config.conf` files
   - Use secure passwords
   - Rotate credentials regularly

2. **Network**
   - Use internal Docker network
   - Limit exposed ports
   - Use HTTPS for web interfaces

3. **Updates**
   - Keep dependencies updated
   - Monitor security advisories
   - Regular security scanning

## Support

For issues and support:
1. Check the [GitHub Issues](https://github.com/yourusername/reddit-data-engineering/issues)
2. Review the [Documentation](docs/)
3. Contact: [Your Email] 