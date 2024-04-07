
import os
import email
import imaplib

from django.conf import settings


FILE_FORMATS = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
]

ATTACHMENTS_DIR = os.path.join(settings.BASE_DIR, 'tmp', 'email_attachments')


# from suppliers.email import get_new_messages
# print(get_new_messages(sender='mp.team.ua@gmail.com'))


def get_new_messages(sender=None):

    imap = imaplib.IMAP4_SSL('imap.gmail.com')
    imap.login(
        settings.SUPPLIER_PRODUCTS_RECIPIENT_EMAIL,
        settings.SUPPLIER_PRODUCTS_RECIPIENT_PASSWORD
    )
    imap.select('inbox')

    result, data = imap.uid('search', None, 'FROM "{}"'.format(sender))

    if result != 'OK':
        raise Exception('Bad response: {}'.format(result))

    for msg_id in data[0].split():

        print('Found message #{}'.format(str(msg_id)))

        result, data = imap.uid('fetch', msg_id, '(RFC822)')

        if result != 'OK':
            raise Exception('Can not read message: {}'.format(result))

        email_message = email.message_from_bytes(data[0][1])

        if not email_message.is_multipart():
            print('Message has no files')
            continue

        for part in email_message.walk():

            if part.get_content_type() in FILE_FORMATS:
                open(part.get_filename(), 'wb').write(
                    part.get_payload(decode=True))

            if (
                    part.get_content_maintype() == 'multipart' or
                    part.get('Content-Disposition') is None or
                    not part.get_filename()):
                continue

            file_path = os.path.join(ATTACHMENTS_DIR, part.get_filename())

            if not os.path.isfile(file_path):
                fp = open(file_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()

    imap.close()
    imap.logout()

    return 'Result'
