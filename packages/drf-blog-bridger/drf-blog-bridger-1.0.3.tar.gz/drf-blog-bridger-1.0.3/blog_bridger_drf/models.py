from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

def get_default_user():
    user, _ = User.objects.get_or_create(first_name="Deleted", last_name="User", username="Deleted User", email='test@email.com')
    return user


class Post(models.Model):
    post_title = models.CharField(max_length=50)
    post_body = models.TextField()
    created_at = models.DateField(auto_now=True, auto_now_add=False)
    author = models.ForeignKey(User, related_name="posts", on_delete=models.SET(get_default_user))

    class Meta:
        ordering = ['-id']
    
    def __str__(self) -> str:
        return self.post_title

class Comment(models.Model):
    comment = models.TextField(null=True, blank=True)
    comment_author = models.ForeignKey(User,related_name="comment_author", on_delete=models.SET(get_default_user))
    post = models.ForeignKey(Post, related_name="post_comments", on_delete=models.CASCADE)
    created_at = models.DateField(auto_now=True, auto_now_add=False)
