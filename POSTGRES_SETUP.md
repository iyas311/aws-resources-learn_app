# PostgreSQL on EC2 + CloudLearn Integration

## STEP 1: Launch EC2 Instance

In AWS Console:
1. Go to **EC2** → **Instances** → **Launch Instance**
2. **AMI**: Ubuntu 24.04 LTS (free tier eligible)
3. **Instance Type**: t3.micro (free tier)
4. **Key Pair**: Create new → download `.pem` file (save safely)
5. **Security Group**: 
   - Inbound: SSH (22) from your IP
   - Inbound: PostgreSQL (5432) from your app's security group
   - Outbound: All (default)
6. **Storage**: 20GB gp2 (free tier)
7. **Launch**

Get the **Public IP** (e.g., `3.14.159.265`)

## STEP 2: Connect to EC2

```bash
# On your local machine
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@3.14.159.265
```

## STEP 3: Install PostgreSQL on EC2

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
psql --version
```

## STEP 4: Create CloudLearn Database & User

```bash
# Connect to PostgreSQL
sudo sudo -u postgres psql

# Inside PostgreSQL prompt (postgres=#)
CREATE DATABASE cloudlearn;

CREATE USER cloudlearn WITH PASSWORD 'GenerateStrongPassword123!';

ALTER ROLE cloudlearn SET client_encoding TO 'utf8';
ALTER ROLE cloudlearn SET default_transaction_isolation TO 'read committed';
ALTER ROLE cloudlearn SET default_transaction_deferrable TO on;
ALTER ROLE cloudlearn SET default_transaction_read_uncommitted TO off;

GRANT ALL PRIVILEGES ON DATABASE cloudlearn TO cloudlearn;

# Verify
\l

# Exit
\q
```

## STEP 5: Enable Remote Connections (if needed)

```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/*/main/postgresql.conf

# Find and uncomment:
# listen_addresses = 'localhost'
# Change to:
listen_addresses = '0.0.0.0'

# Save (Ctrl+O, Enter, Ctrl+X)

# Edit pg_hba.conf for authentication
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Add at the end:
host    all             all             0.0.0.0/0               md5

# Restart PostgreSQL
sudo systemctl restart postgresql

# Verify it's listening
sudo netstat -tulpn | grep postgresql
```

## STEP 6: Store All Credentials in Single Secret

In AWS Console:
1. Go to **Secrets Manager** → **Store a New Secret**
2. **Secret Type**: Other type of secret
3. **Key/value pairs** (consolidate all secrets in ONE):
   ```json
   {
     "bucket_name": "your-s3-bucket-name",
     "username": "cloudlearn",
     "password": "GenerateStrongPassword123!",
     "host": "3.14.159.265",
     "port": "5432",
     "database": "cloudlearn"
   }
   ```
4. **Secret Name**: `cloudlearn-app`
5. **Store**

All credentials are now in a single secret!

## STEP 7: Update Code

See `app/database.py` and updated `app/aws/secrets.py`

Your EC2 instance is now ready!
