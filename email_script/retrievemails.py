import imaplib
import email
import re
import mysqlinserts
import configfile as conf

from send_alert import alert_failed_award

ADDR_PATTERN = re.compile('<(.*?)>')
# Creating lists
mail_uids_list = []
retrieved_raw_mails = []
processed_mails = []

def reject_awward(sender):
    msg = EmailMessage()

def get_mail_uids(my_imap):
    """This function retrieves emails from selected mailbox
    and stores them in a list
    """
    result, data = my_imap.uid('search', None, conf.MODE)

    if result != 'OK':
        print('\nfailure to retrieve emails\n')
        return False

    for num in data[0].split():
        mail_uids_list.append(num)


def process_mails():
    """This function iterates through the raw emails
    stored in retrieved_raw_mails and extracts the header information,
    the plaintext body of the email, and stores this data
    in a dictionary if certain criteria are met.
    """
    for mail_unprocessed in retrieved_raw_mails:
        mail_unprocessed = email.message_from_bytes(mail_unprocessed)
        mail_from = mail_unprocessed['FROM']
        mail_date = mail_unprocessed['DATE']
        mail_cc = mail_unprocessed.get('Cc', "")
        mail_to = mail_unprocessed.get('To', "")
        mail_subj = mail_unprocessed['SUBJECT']

        if not mail_subj.strip():
            alert_failed_award(mail_from)

        else:
            for part in mail_unprocessed.walk():
                if part.get_content_type() == 'text/plain':
                    mail_body = part.get_payload()

            recips = []
            rlist = re.findall(ADDR_PATTERN, mail_cc)
            to_list = re.findall(ADDR_PATTERN, mail_to)
            recips.extend(rlist)
            recips.extend(to_list)

            for recip in recips:
                mail = {
                    'FROM': mail_from,
                    'REASON': mail_subj.encode(encoding='UTF-8', errors='ignore'),
                    'TO': recip,
                    'DATE': mail_date
                }

                processed_mails.append(mail)


# IMAP connection is defined and established here

my_imap = imaplib.IMAP4_SSL('outlook.office365.com')
my_imap.login(conf.MY_ACCOUNT, conf.MY_PASS)

# Mailbox is selected here
my_imap.select(conf.MY_MAILBOX)

# Get mail UIDs
get_mail_uids(my_imap)


# Check if **no** mails have been retrieved from google mail.
if not mail_uids_list:
    print('\nNo emails found, script exiting now.\n')
    exit()

else:
    # Retrieve raw emails for each uid and append to retrieved_raw_mails
    for uid in mail_uids_list:
        result, data = my_imap.uid('fetch', uid, '(RFC822)')
        raw_email = data[0][1]
        retrieved_raw_mails.append(raw_email)
    # Process mails and close imap connection
    process_mails()

    my_imap.close()
    my_imap.logout()

    mysqlinserts.mysqlinserts(processed_mails)

exit()

