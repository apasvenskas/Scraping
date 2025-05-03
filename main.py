import requests
import selectorlib
import time
import smtplib, ssl
import os
from dotenv import load_dotenv
import sqlite3

# --- Configuration ---
load_dotenv()
db_file = "data.db"
URL = "https://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "audrius13toto@gmail.com" # Use your email
RECEIVER_EMAIL = "audrius13toto@gmail.com" # Use recipient email
EMAIL_PASSWORD = os.getenv("PASSWORD") # Ensure PASSWORD is set in your .env file

# --- Database Setup ---
connection = sqlite3.connect(db_file)
cursor = connection.cursor()
# Optional: Create table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS events (band TEXT, city TEXT, date TEXT, UNIQUE(band, city, date))")
connection.commit()


# --- Functions ---

def scrape(url):
    """ Scrape the pages source from webpage URL. """
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        source = response.text
        return source
    except requests.exceptions.RequestException as e:
        print(f"Error during requests to {url}: {e}")
        return None

def extract(source):
    """ Extract tour data using selectorlib """
    if source is None:
        return None
    try:
        extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
        value = extractor.extract(source)["tours"]
        return value
    except Exception as e:
        print(f"Error during extraction: {e}")
        return None # Or return a specific error indicator

def send_email(message):
    """ Sends an email notification. """
    if not EMAIL_PASSWORD:
        print("Error: Email password not found in environment variables!")
        return

    my_context = ssl.create_default_context()
    email_message = f"Subject: New Tour Found!\n\n{message}" # Add Subject line

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=my_context) as server:
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, email_message.encode('utf-8')) # Encode message
            print("Email sent successfully!")
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error: Check email/password and Gmail 'less secure app access' settings.")
    except Exception as e:
        print(f"Error sending email: {e}")

def store(extraction):
    """ Stores a new event found in the database. """
    try:
        row = extraction.split(",")
        row = [item.strip() for item in row]
        if len(row) == 3: # Ensure we have 3 items before inserting
            cursor.execute("INSERT INTO events VALUES(?,?,?)", row)
            connection.commit()
            print(f"Stored new event: {row}")
        else:
            print(f"Error storing: Expected 3 items, got {len(row)} from '{extraction}'")
    except sqlite3.IntegrityError:
        # This can happen if the UNIQUE constraint is violated (event already exists)
        # Although 'read' should prevent this, it's good practice to handle it.
        print(f"Event already exists in DB (IntegrityError): {row}")
    except Exception as e:
        print(f"Error storing data in database: {e}")


def read(extraction):
    """ Checks if a specific event exists in the database. """
    try:
        row_data = extraction.split(",")
        row_data = [item.strip() for item in row_data]
        if len(row_data) == 3:
            band, city, date = row_data
            cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?", (band, city, date))
            rows = cursor.fetchall()
            # print(f"Checked DB for {row_data}. Found rows: {rows}") # For debugging
            return rows # Returns a list of matching rows (empty list if none found)
        else:
            print(f"Error reading: Expected 3 items, got {len(row_data)} from '{extraction}'")
            return None # Indicate an error or invalid input
    except Exception as e:
        print(f"Error reading data from database: {e}")
        return None # Indicate an error

# --- Main Execution Logic ---
if __name__ == "__main__":
    try:
        while True:
            print("Checking for tours...")
            scraped_data = scrape(URL)
            if scraped_data: # Proceed only if scraping was successful
                extracted_data = extract(scraped_data)
                print(f"Extracted: {extracted_data}")

                if extracted_data and extracted_data != "No upcoming tours":
                    # Check if this specific event already exists in the database
                    existing_rows = read(extracted_data)

                    if existing_rows is not None and not existing_rows: # If read didn't error and returned an empty list
                        print(f"New event found: {extracted_data}")
                        store(extracted_data) # Store the new event
                        send_email(message=f"New event found: {extracted_data}") # Send notification
                    elif existing_rows:
                         print(f"Event already in database: {extracted_data}")
                    # else: An error occurred during read, message already printed by read()

            print(f"Waiting for {2} seconds...")
            time.sleep(2) # keeps the script running non stop, every 2 seconds

    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
    finally:
        # Ensure the database connection is closed when the script stops
        if connection:
            connection.close()
            print("Database connection closed.")