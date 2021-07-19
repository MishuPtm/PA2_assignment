from django.db import models
from django.contrib.auth.models import User
# Create your models here.
"""
Programing and algorithms 2 Assignment
Student: Ionut Petrescu
ID: D19124760
Course: DT249
Stage 2

Django API
"""

class Category(models.Model):
    class Meta:
        verbose_name_plural = "Categories"
    description = models.CharField(max_length=50, unique=True)
    hashtag = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    @property
    def as_dict(self):
        return {"name": self.description,
                "hashtag": self.hashtag,
                "created": self.created,
                "updated": self.updated
                }

    @staticmethod
    def get_from_description(desc):
        selected_category = Category.objects.filter(description=desc)
        return selected_category[0]

    @staticmethod
    def get_categories():
        categories = Category.objects.all()
        lst = []
        for cat in categories:
            lst.append(cat.as_dict)
        return lst

    def __repr__(self):
        return self.description

    def __str__(self):
        return self.description


class Post(models.Model):
    class Meta:
        verbose_name_plural = "Posts"
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=50)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    @property
    def as_dict(self):
        return {"title": self.title,
                "content": self.content,
                "created": self.created,
                "updated": self.updated,
                "author": f"{self.author.first_name.title()}"
                          f" {self.author.last_name.title()}",
                "category": self.category.description,
                "tag": self.category.hashtag
        }

    @classmethod
    def get_category(cls, cat):
        posts = Post(description=cat)
        lst = []
        if posts:
            for post in posts:
                d = post.as_dict
                lst.append(d)
        return lst

    def __str__(self):
        return f"{self.title} - #{self.category.hashtag}"
