# application.py - Entry point for AWS Elastic Beanstalk
# EB looks for either application.py or app.py with an 'application' variable

from app import app as application

# For debugging
if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8000)
