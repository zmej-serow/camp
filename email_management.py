from email.header import decode_header
from email.mime.text import MIMEText
from main import config

import email
import logging


class Mutator:
    """Class to work with email messages"""
    def __init__(self, content):
        self.content = email.message_from_bytes(content)

    def add_links(self, attachments):
        """
        Add HTML links section after message body.
        :param attachments: dictionary of {filename:link} pairs
        :return: updated message object (with links)
        """
        attachments_list = []
        for file, link in attachments.items():
            attachments_list.append(f'<li><a href={link}>{file}</a>')
        html_begin = f'<html><body><hr>{config.main.message}<ul>'
        html_end = '</ul></body></html>'
        html = html_begin + ''.join(attachments_list) + html_end
        links_block = MIMEText(html, 'html')
        self.content.attach(links_block)
        return self.content

    def strip_attachments(self):
        """
        Strip attachments from message
        :param message: message object
        :return: message object without attachments
        """
        no_attachments = []
        payloads = self.content.get_payload()
        for item in payloads:
            if not item.get_filename():
                no_attachments.append(item)
        self.content.set_payload(no_attachments)
        return self.content

    def extract_attachments(self, storage):
        """
        Save all attachments to disk with their respective filenames and make a record for future uploading
        :return: None in case of fail or dict of pairs: {filename:None}
        """
        attachments = {}
        payloads = self.content.get_payload()
        for part in payloads:
            filename = part.get_filename()
            if filename:
                decoded_header = decode_header(filename)
                encoding = decoded_header[0][1]
                if encoding is not None:
                    logging.info('Have to decode filename:', filename)
                    filename = decoded_header[0][0].decode(encoding)

                logging.info(f'File {filename} found')
                attachment = part.get_payload(decode=True)

                logging.debug(f'Length of attachment is {len(attachment)}')
                try:
                    with storage.open(filename, 'wb') as file:
                        file.write(attachment)
                    attachments[filename] = ""
                except IOError as e:
                    logging.error(f'Cannot save file {filename}: {e}')
                    return None

        return attachments
