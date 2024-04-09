from .configs import Configs


class DocumentConfigs(Configs):
    def __init__(self, document, senior=None, data=None):
        super(DocumentConfigs, self).__init__(document, senior, data)

    @property
    def title(self): return self['title']

    @title.setter
    def title(self, title: str): self['title'] = title

    @property
    def author(self): return self['author']

    @author.setter
    def author(self, author: str): self['author'] = author

    @property
    def subject(self): return self['subject']

    @subject.setter
    def subject(self, subject: str): self['subject'] = subject

    @property
    def keywords(self): return self['keywords']

    @keywords.setter
    def keywords(self, keywords: str): self['keywords'] = keywords

    @property
    def encrypted(self): return self['encrypted']

    @encrypted.setter
    def encrypted(self, enable: bool = True): self['encrypted'] = enable

    @property
    def encrypt_user_password(self): return self['encrypt_user_password']

    @encrypt_user_password.setter
    def encrypt_user_password(self, password: str = None): self['encrypt_user_password'] = password

    @property
    def encrypt_owner_password(self): return self['encrypt_owner_password']

    @encrypt_owner_password.setter
    def encrypt_owner_password(self, password: str = None): self['encrypt_owner_password'] = password
