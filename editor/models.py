from django.db import models
import json
from urllib.parse import parse_qs, urlparse
import re


class Page(models.Model):
    title = models.CharField(max_length=500, default='Untitled Page')
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            base_slug = slugify(self.title) or 'page'
            self.slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        super().save(*args, **kwargs)


class MultimediaItem(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('youtube', 'YouTube'),
    ]

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='multimedia_items')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)
    title = models.CharField(max_length=300, default='')
    text_content = models.TextField(blank=True, default='')
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    youtube_url = models.URLField(blank=True, default='')
    show_in_multimedia = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.media_type}: {self.title}"

    def get_youtube_embed_url(self):
        if not self.youtube_url:
            return ''
        raw = (self.youtube_url or '').strip()
        parsed = urlparse(raw)
        host = (parsed.netloc or '').lower()
        path = parsed.path or ''
        query = parse_qs(parsed.query or '')

        video_id = ''

        if '/embed/' in path:
            video_id = path.split('/embed/')[-1].split('/')[0].strip()
        elif 'youtu.be' in host:
            video_id = path.lstrip('/').split('/')[0].strip()
        elif 'youtube.com' in host or 'youtube-nocookie.com' in host:
            if 'v' in query and query['v']:
                video_id = query['v'][0].strip()
            elif '/shorts/' in path:
                video_id = path.split('/shorts/')[-1].split('/')[0].strip()
            elif '/live/' in path:
                video_id = path.split('/live/')[-1].split('/')[0].strip()

        if not video_id:
            match = re.search(r'([A-Za-z0-9_-]{11})', raw)
            if match:
                video_id = match.group(1)

        if not video_id:
            return ''

        # Use nocookie embed endpoint for better compatibility in iframe contexts.
        return f'https://www.youtube-nocookie.com/embed/{video_id}?rel=0'


class Article(models.Model):
    page = models.OneToOneField(Page, on_delete=models.CASCADE, related_name='article')
    content = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Article: {self.page.title}"


class ExpandableSection(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='expandable_sections')
    title = models.CharField(max_length=300, default='New Section')
    content = models.TextField(blank=True, default='')
    is_open = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='comments')
    selected_text = models.TextField()
    comment_text = models.TextField()
    range_start = models.IntegerField(default=0)
    range_end = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on: {self.selected_text[:50]}"


class ArticleMediaLink(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='article_media_links')
    multimedia_item = models.ForeignKey(MultimediaItem, on_delete=models.CASCADE, related_name='article_links')
    display_text = models.CharField(max_length=300, default='Open media')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Article link: {self.display_text}"


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    title = models.CharField(max_length=300, default='Article Image')
    file = models.ImageField(upload_to='article/images/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.title


class ArticleAudio(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='audios', null=True, blank=True)
    title = models.CharField(max_length=300, default='Article Audio')
    file = models.FileField(upload_to='article/audio/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.title


class ArticleVideo(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='videos', null=True, blank=True)
    title = models.CharField(max_length=300, default='Article Video')
    file = models.FileField(upload_to='article/video/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.title
