from flask import flash


class Notification:
    def __init__(self):
        self.notification_data: dict = {}

    @classmethod
    def make(self, name: str):
        obj = self()
        return obj

    def to(self, to: str):
        self.notification_data["to"] = to
        return self

    def title(self, title: str):
        self.notification_data["title"] = title
        return self

    def body(self, body: str):
        self.notification_data["body"] = body
        return self

    def warning(self):
        self.notification_data["category"] = "warning"
        return self

    def info(self):
        self.notification_data["category"] = "info"
        return self

    def success(self):
        self.notification_data["category"] = "success"
        return self

    def error(self):
        self.notification_data["category"] = "error"
        return self

    def link(self, text, link: str):
        self.notification_data["link"] = f"<a href='{link}'>{text}</a>"
        return self

    def send(self, channel=None):
        if not channel:
            flash(self.notification_data)
        if channel == "email":
            pass
        if channel == "outlook":
            from win32com.client.gencache import EnsureDispatch
            from win32com.client import GetActiveObject
            import pythoncom
            outlook = GetActiveObject("Outlook.Application", pythoncom.CoInitialize())
            mail = outlook.CreateItem(0)  # 0 represents the MailItem type
            mail.Display()
            mail.Subject = self.notification_data["title"]
            mail.HTMLBody = self.notification_data["body"] + "<br><br>" + self.notification_data["link"]
            if isinstance(self.notification_data["to"], list):
                mail.To = ";".join(self.notification_data["to"])
            else:
                mail.To = self.notification_data["to"]
            #mail.Display()
            mail.Send()

        if channel == "sms":
            pass
        if channel == "slack":
            pass
        if channel == "telegram":
            pass
        if channel == "whatsapp":
            pass
        if channel == "push":
            pass
        if channel == "webhook":
            pass
