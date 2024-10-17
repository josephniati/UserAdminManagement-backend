from dotenv import load_dotenv
import smtplib
import os, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

server = smtplib.SMTP("smtp.gmail.com", 587)

def send_email(url:str, title:str, email_opt:str):

    EMAIL = os.getenv("EMAIL")
    GMAIL_PASSWD = os.getenv("GMAIL_PASSWD")


    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"{title}"
    msg['From'] = EMAIL
    msg['To'] = email_opt

    # Set priority headers
    msg['X-Priority'] = '1'  # Highest priority
    msg['X-MSMail-Priority'] = 'High'
    msg['Importance'] = 'High'

    # Create the body of the message (a plain-text and an HTML version).
    html = f"""
    <html>
    <head></head>
   <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; ">
        <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <h2 style="color: red; margin-bottom: 20px;">Reset your password here.</h2>
            <p style="color: #555; font-size: 16px; ">Click on the URL below: </p>
            <a href="{url}" style="display: inline-block;  margin-top: 20px; color: black; border-radius: 5px;">{url}</a>
        </div>
    </body>
    </html>
    """

    # Record the MIME types of both parts - text/plain and text/html.
    part = MIMEText(html, 'html')

    # Attach parts into message container.
    msg.attach(part)

    # Send the message via local SMTP server.
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL, GMAIL_PASSWD)
            server.sendmail(EMAIL, email_opt, msg.as_string())
            print("===== Email sent! =====")
    except Exception as e:
        print(f"Something went wrong while sending the email: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        title = sys.argv[2]
        email_opt = sys.argv[3]
        send_email(url, title, email_opt)
    else:
        print("No URL provided.")