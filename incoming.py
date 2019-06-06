import outgoing
import messaging
import filesystems

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP
from fs import open_fs

from main import config
from main import logging


class SMTPController(Controller):
    def factory(self):
        """Used to define greater data size limit"""
        return SMTP(self.handler, data_size_limit=99999999999, decode_data=False)


class AttachHarvester:
    async def handle_DATA(self, server, session, envelope):
        """
        Callback method which is called every time we receive message. Here we do all the magic.
        :param server: not used
        :param session: not used
        :param envelope: received message
        :return: SMTP status string
        """
        logging.info('Incoming message. Handling data')
        message = messaging.Mutator(envelope.content)

        destination = filesystems.Uploader(config.upload.service, config.upload.creds, config.upload.path)
        if not destination.service:
            logging.error(f'Cannot authorize to "{config.upload.service}"')
            return '554 Authorization failed for filesharing service'

        with open_fs('mem://') as ramdisk:
            attachments = message.extract_attachments(ramdisk)
            if attachments:
                if not destination.upload(attachments, ramdisk):
                    logging.error('Cannot upload files')
                    return '554 Error while uploading attachments to filesharing service'
                message.content = message.strip_attachments()
                message.content = message.add_links(attachments)
            elif attachments is not None:
                logging.debug('No attachments, passing mail untouched')
            else:
                return '554 Cannot save attachment(s) to process'

        sendmail = outgoing.Sender(config.mail)
        error = sendmail.service(message.content)
        return error or '250 Message accepted for delivery'


async def smtp_server(hostname, port):
    """Function to start aiosmtpd as receiving SMTP server on defined hostname and port"""
    logging.debug('Starting SMTP server')
    handler = AttachHarvester()
    controller = SMTPController(handler, hostname=hostname, port=port)
    controller.start()
    logging.debug('SMTP server started')
