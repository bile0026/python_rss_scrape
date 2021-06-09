import requests  # pulling data
from bs4 import BeautifulSoup  # xml parsing
import json  # exporting to files
import datetime  # compare dates with article published
import smtplib  # for email notification
from email.mime.text import MIMEText  # for email notification
from email.mime.multipart import MIMEMultipart  # for email notification
from configparser import ConfigParser  # for email notification
from email.message import EmailMessage  # for email notification


# initialize variables
scrape_url = 'https://rss.com/rss.xml'
url_type = 'xml'
smtp_server = 'smtp.example.com'
from_email_address = 'cve_notifications@example.com'
to_email_address = 'user@example.com'
send_email = True  # set to false if you don't want email notifications

# send email notification function


def sendEmailAlert(rss_items):
    email_body_list = []

    message = MIMEMultipart('alternative')
    message['Subject'] = 'New RSS CVE Alert'
    message['From'] = from_email_address
    message['To'] = to_email_address

    # build list of articles(items) to put in the email body
    for item in rss_items:
        email_body_part = """\
        Title: """ + item['title'] + """</br>
        Published: """ + item['published'] + """</br>
        Link: """ + item['link'] + """</br>
        """
        email_body_list.append(email_body_part)

    # build email body
    email_body = ''.join(email_body_list)

    # build chunks of email into a list
    message.attach(MIMEText(email_body, "html"))

    # Send the email
    if(len(email_body) > 0):
        with smtplib.SMTP(smtp_server, 25) as server:
            server.sendmail(from_email_address, to_email_address,
                            message.as_string())
    else:
        print("No new articles found")

# scraping function


def scrape_rss():
    article_list = []
    today = datetime.datetime.today()
    date_format = "%Y-%m-%d"
    yesterday = today - datetime.timedelta(days=1)
    # print(today)

    try:
        # execute my request, parse the data using XML
        # parser in BS4
        r = requests.get(scrape_url)
        soup = BeautifulSoup(r.content, features=url_type)

        # select only the "items" I want from the data
        articles = soup.findAll('item')

        # for each "item" I want, parse it into a list
        for a in articles:
            title = a.find('title').text
            link = a.find('link').text
            published = a.find('date').text

            # create an "article" object with the data
            # from each "item"
            article = {
                'title': title,
                'link': link,
                'published': published
            }

            # print(article)

            # append my "article_list" with each "article" object
            if datetime.datetime.strptime(published.split('T', 1)[0], date_format) <= today and datetime.datetime.strptime(published.split('T', 1)[0], date_format) >= yesterday:
                article_list.append(article)

        if send_email:
            sendEmailAlert(article_list)

        # return the list of articles
        return article_list
    except Exception as e:
        print('The scraping job failed. See exception:')
        print(e)


print('Starting scraping')
scrape_rss()
print('Finished scraping')
