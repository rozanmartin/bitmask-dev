# -*- coding: utf-8 -*-
# interfaces.py
# Copyright (C) 2014,2015 LEAP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Interfaces for the leap.mail module.
"""
from zope.interface import Interface, Attribute


class IMessageWrapper(Interface):
    """
    I know how to access the different parts into which a given message is
    splitted into.

    :ivar fdoc: dict with flag document.
    :ivar hdoc: dict with flag document.
    :ivar cdocs: dict with content-documents, one-indexed.
    """

    fdoc = Attribute('A dictionaly-like containing the flags document '
                     '(mutable)')
    hdoc = Attribute('A dictionary-like containing the headers document '
                     '(immutable)')
    cdocs = Attribute('A dictionary with the content-docs, one-indexed')

    def create(self, store):
        """
        Create the underlying wrapper.
        """

    def update(self, store):
        """
        Update the only mutable parts, which are within the flags document.
        """

    def delete(self, store):
        """
        Delete the parts for this wrapper that are not referenced from anywhere
        else.
        """

    def copy(self, store, new_mbox_uuid):
        """
        Return a copy of this IMessageWrapper in a new mailbox.
        """

    def set_mbox_uuid(self, mbox_uuid):
        """
        Set the mailbox for this wrapper.
        """

    def set_flags(self, flags):
        """
        """

    def set_tags(self, tags):
        """
        """

    def set_date(self, date):
        """
        """

    def get_subpart_dict(self, index):
        """
        :param index: the part to lookup, 1-indexed
        """

    def get_subpart_indexes(self):
        """
        """

    def get_body(self, store):
        """
        """


# TODO -- split into smaller interfaces? separate mailbox interface at least?

class IMailAdaptor(Interface):
    """
    I know how to store the standard representation for messages and mailboxes,
    and how to update the relevant mutable parts when needed.
    """

    def initialize_store(self, store):
        """
        Performs whatever initialization is needed before the store can be
        used (creating indexes, sanity checks, etc).

        :param store: store
        :returns: a Deferred that will fire when the store is correctly
                  initialized.
        :rtype: deferred
        """

    def get_msg_from_string(self, MessageClass, raw_msg):
        """
        Get an instance of a MessageClass initialized with a MessageWrapper
        that contains all the parts obtained from parsing the raw string for
        the message.

        :param MessageClass: an implementor of IMessage
        :type raw_msg: str
        :rtype: implementor of leap.mail.IMessage
        """

    def get_msg_from_docs(self, MessageClass, mdoc, fdoc, hdoc, cdocs=None,
                          uid=None):
        """
        Get an instance of a MessageClass initialized with a MessageWrapper
        that contains the passed part documents.

        This is not the recommended way of obtaining a message, unless you know
        how to take care of ensuring the internal consistency between the part
        documents, or unless you are glueing together the part documents that
        have been previously generated by `get_msg_from_string`.
        """

    def get_flags_from_mdoc_id(self, store, mdoc_id):
        """
        """

    def create_msg(self, store, msg):
        """
        :param store: an instance of soledad, or anything that behaves alike
        :param msg: a Message object.

        :return: a Deferred that is fired when all the underlying documents
                 have been created.
        :rtype: defer.Deferred
        """

    def update_msg(self, store, msg):
        """
        :param msg: a Message object.
        :param store: an instance of soledad, or anything that behaves alike
        :return: a Deferred that is fired when all the underlying documents
                 have been updated (actually, it's only the fdoc that's allowed
                 to update).
        :rtype: defer.Deferred
        """

    def get_count_unseen(self, store, mbox_uuid):
        """
        Get the number of unseen messages for a given mailbox.

        :param store: instance of Soledad.
        :param mbox_uuid: the uuid for this mailbox.
        :rtype: int
        """

    def get_count_recent(self, store, mbox_uuid):
        """
        Get the number of recent messages for a given mailbox.

        :param store: instance of Soledad.
        :param mbox_uuid: the uuid for this mailbox.
        :rtype: int
        """

    def get_mdoc_id_from_msgid(self, store, mbox_uuid, msgid):
        """
        Get the UID for a message with the passed msgid (the one in the headers
        msg-id).
        This is used by the MUA to retrieve the recently saved draft.
        """

    # mbox handling

    def get_or_create_mbox(self, store, name):
        """
        Get the mailbox with the given name, or create one if it does not
        exist.

        :param store: instance of Soledad
        :param name: the name of the mailbox
        :type name: str
        """

    def update_mbox(self, store, mbox_wrapper):
        """
        Update the documents for a given mailbox.
        :param mbox_wrapper: MailboxWrapper instance
        :type mbox_wrapper: MailboxWrapper
        :return: a Deferred that will be fired when the mailbox documents
                 have been updated.
        :rtype: defer.Deferred
        """

    def delete_mbox(self, store, mbox_wrapper):
        """
        """

    def get_all_mboxes(self, store):
        """
        Retrieve a list with wrappers for all the mailboxes.

        :return: a deferred that will be fired with a list of all the
                 MailboxWrappers found.
        :rtype: defer.Deferred
        """
