import imaplib
import email
import mysqlinserts

import configfile as conf

# Creating lists
mail_uids_list = []
retrieved_raw_mails = []
processed_mails = []


def extract_email(string, start="<", stop=">"):
    '''Function to search between "<" and ">" for emails.'''
    return string[string.index(start) + 1:string.index(stop)]


def stripchars(mail):
    ''' For loop which strips "<", ">", and ","
    from the "TO", "FROM", and "DATE" fields respectively.'''
    if '<' in mail['TO']:
        mail['TO'] = extract_email(mail['TO'])
    if '<' in mail['FROM']:
        mail['FROM'] = extract_email(mail['FROM'])
    if ',' in mail['DATE']:
        mail['DATE'] = mail['DATE'].replace('.', '')


def get_mail_uids(my_imap):
    ''' This function retrieves emails from selected mailbox
    and stores them in a list'''
    result, data = my_imap.uid('search', None, conf.MODE)

    if result != 'OK':
        print("failure to retrieve emails")
        return False

    for num in data[0].split():
        mail_uids_list.append(num)


def process_mails():
    '''This function iterates through the raw emails
    stored in retrieved_raw_mails and extracts the header information,
    the plaintext body of the email, and stores this data
    in a dictionary if certain criteria are met. '''
    for mail_unprocessed in retrieved_raw_mails:

        mail_unprocessed = email.message_from_bytes(mail_unprocessed)

        mail_from = mail_unprocessed['from']
        mail_cc = mail_unprocessed['cc']
        mail_date = mail_unprocessed['Date']
        for part in mail_unprocessed.walk():
            if part.get_content_type() == 'text/plain':
                mail_body = part.get_payload()

        if mail_cc:
            mail =\
                {
                    'FROM': mail_from,
                    'REASON': mail_body,
                    'TO': mail_cc,
                    'DATE': mail_date
                }

            processed_mails.append(mail)


# IMAP connection is defined and established here
try:
    my_imap = imaplib.IMAP4_SSL('imap.gmail.com')
    my_imap.login(conf.MY_ACCOUNT, conf.MY_PASS)

    # Mailbox is selected here
    my_imap.select(conf.MY_MAILBOX)
    # get mail UIDs
    get_mail_uids(my_imap)

except imaplib.IMAP4.error:
    print("IMAP Error, exiting script now...")
    exit()


# Check if **no** mails have been retrieved from google mail.
if not mail_uids_list:
    print("No new emails found, script exiting now.")
    exit()

else:
    # retrieve raw emails for each uid and append to retrieved_raw_mails
    for uid in mail_uids_list:
        result, data = my_imap.uid('fetch', uid, '(RFC822)')
        raw_email = data[0][1]
        retrieved_raw_mails.append(raw_email)
    # Process mails and close imap connection
    process_mails()

    my_imap.close()
    my_imap.logout()

    for mail in processed_mails:
        stripchars(mail)

    mysqlinserts.mysqlinserts(processed_mails)

exit()
