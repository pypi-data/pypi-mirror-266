from fastapi import FastAPI, HTTPException
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import uvicorn

app = FastAPI()

# SQLite database connection
conn = sqlite3.connect('database.db')
c = conn.cursor()


@app.post("/send_email/")
async def send_email(subject: str, message: str, sender_email: str, password: str):
    try:
        # Fetch emails from SQLite database
        c.execute("SELECT email FROM database.companies")
        emails = c.fetchall()
        
        if not emails:
            raise HTTPException(status_code=404, detail="No emails found in the database")

        # Set up the SMTP server
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(sender_email, password)

        # Send email to each recipient
        for email in emails:
            unique_link = f"http://a-unique-link/mark_interested/"
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email[0]
            msg['Subject'] = subject
            msg.attach(MIMEText(message + f"\n\nClick here to mark as interested: {unique_link}", 'plain'))

            smtp_server.send_message(msg)

        # Close the SMTP server
        smtp_server.quit()

        return {"message": "Email sent successfully"}
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/mark_interested/{email}")
async def mark_interested(email: str):
    try:
        # Update interested column in the database
        c.execute("UPDATE emails SET interested = 1 WHERE email = ?", (email,))
        conn.commit()
        return {"message": f"Email {email} marked as interested"}
    except Exception as e:
        return {"error": str(e)}
    
@app.put("/update_email/")
async def update_email(old_email: str, new_email: str):
    try:
        # Update email address in the database
        c.execute("UPDATE emails SET email = ? WHERE email = ?", (new_email, old_email,))
        conn.commit()
        return {"message": f"Email address updated from {old_email} to {new_email}"}
    except Exception as e:
        return {"error": str(e)}

def run_api():
    uvicorn.run(app, host="127.0.0.1", port=5000,)