from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.forms import ValidationError
from organisations.models import Organisation


# Create your models here.
class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name="chats")
    organisation = models.ForeignKey(
        "organisations.Organisation", on_delete=models.CASCADE, related_name="chats"
    )
    broadcast = models.BooleanField(default=False)

    def is_participant(self, user):
        return user in self.participants.all()


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )

    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.chat.is_participant(self.sender):
            raise ValidationError("Invalid participants for the message.")

        if (self.chat.broadcast) and (
            not self.sender.id in self.chat.organisation.get_orgnanisation_admin_users()
        ):
            raise ValidationError(
                "User is not an admin of the organisation. only admins can send group broadcasts."
            )


class MessageSeen(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["message", "user"]
