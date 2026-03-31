import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
import time

SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@example.com"
SMTP_PASSWORD = "your-password"

def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False

def read_csv(file_path):
    return pd.read_csv(file_path)

def main():
    csv_file = "emails.csv"
    df = read_csv(csv_file)

    for index, row in df.iterrows():
        to_email = row["email"]
        subject = f"Hello {row['name']}"
        body = f"Dear {row['name']},\n\nThis is a test email.\n\nBest regards,\nYour Company"

        max_retries = 3
        retries = 0
        while retries < max_retries:
            if send_email(to_email, subject, body):
                print(f"Email sent to {to_email}")
                break
            else:
                retries += 1
                print(f"Retrying to send email to {to_email} (attempt {retries}/{max_retries})")
                time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    main()