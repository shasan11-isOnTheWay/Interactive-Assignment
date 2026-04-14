from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify
from django.core.files.storage import default_storage
import json
import uuid

from .models import (
    Page,
    MultimediaItem,
    ExpandableSection,
    Comment,
    ArticleMediaLink,
    Article,
    ArticleImage,
    ArticleAudio,
    ArticleVideo,
)


def index(request):
    """Redirect to first page or create one."""
    page = Page.objects.first()
    if not page:
        page = Page.objects.create(
            title='Interactive Teaching Platform',
            content='<p>Welcome to your interactive teaching platform. Click anywhere to start editing...</p>',
            order=0
        )
        # Create default expandable sections
        ExpandableSection.objects.create(page=page, title='Introduction', content='<p>Add introduction content here.</p>', order=0)
        ExpandableSection.objects.create(page=page, title='Detailed Explanation', content='<p>Add detailed explanation here.</p>', order=1)
        ExpandableSection.objects.create(page=page, title='Additional Resources', content='<p>Add additional resources here.</p>', order=2)
        Article.objects.create(page=page, content=page.content)
    elif not hasattr(page, 'article'):
        Article.objects.create(page=page, content=page.content)
    return redirect('editor:page_view', slug=page.slug)


def page_view(request, slug):
    page = get_object_or_404(Page, slug=slug)
    article, _ = Article.objects.get_or_create(page=page, defaults={'content': page.content})
    pages = Page.objects.all()
    multimedia_items = page.multimedia_items.all()
    expandable_sections = page.expandable_sections.all()
    comments = page.comments.all()
    article_media_links = page.article_media_links.select_related('multimedia_item').all()
    article_images = article.images.all()
    article_audios = article.audios.all()
    article_videos = article.videos.all()
    return render(request, 'editor/page.html', {
        'page': page,
        'article': article,
        'pages': pages,
        'multimedia_items': multimedia_items,
        'expandable_sections': expandable_sections,
        'comments': comments,
        'article_media_links': article_media_links,
        'article_images': article_images,
        'article_audios': article_audios,
        'article_videos': article_videos,
    })


# ─── Page CRUD ───────────────────────────────────────────────────────────────

def create_page(request):
    page = Page.objects.create(
        title='Untitled Page',
        content='<p>Start writing here...</p>',
        order=Page.objects.count()
    )
    ExpandableSection.objects.create(page=page, title='Introduction', content='<p>Add content here.</p>', order=0)
    ExpandableSection.objects.create(page=page, title='Detailed Explanation', content='<p>Add content here.</p>', order=1)
    ExpandableSection.objects.create(page=page, title='Additional Resources', content='<p>Add content here.</p>', order=2)
    Article.objects.create(page=page, content=page.content)
    return JsonResponse({'slug': page.slug, 'id': page.id, 'title': page.title})


@require_POST
def save_page(request, slug):
    page = get_object_or_404(Page, slug=slug)
    article, _ = Article.objects.get_or_create(page=page, defaults={'content': page.content})
    data = json.loads(request.body)
    if 'title' in data:
        page.title = data['title']
    if 'content' in data:
        page.content = data['content']
        article.content = data['content']
        article.save(update_fields=['content', 'updated_at'])
    page.save()
    return JsonResponse({'status': 'ok', 'updated_at': page.updated_at.isoformat()})


@require_POST
def delete_page(request, slug):
    page = get_object_or_404(Page, slug=slug)
    page.delete()
    first = Page.objects.first()
    if first:
        return JsonResponse({'redirect': f'/page/{first.slug}/'})
    # Create a new page if none left
    new_page = Page.objects.create(title='Untitled Page', content='<p>Start writing here...</p>')
    return JsonResponse({'redirect': f'/page/{new_page.slug}/'})


# ─── Multimedia CRUD ──────────────────────────────────────────────────────────

def add_multimedia(request, slug):
    page = get_object_or_404(Page, slug=slug)
    media_type = request.POST.get('media_type', 'text')
    title = request.POST.get('title', 'New Item')
    text_content = request.POST.get('text_content', '')
    youtube_url = request.POST.get('youtube_url', '')
    show_in_multimedia_raw = request.POST.get('show_in_multimedia', 'true').strip().lower()
    show_in_multimedia = show_in_multimedia_raw in ['1', 'true', 'yes', 'on']

    item = MultimediaItem(
        page=page,
        media_type=media_type,
        title=title,
        text_content=text_content,
        youtube_url=youtube_url,
        show_in_multimedia=show_in_multimedia,
        order=page.multimedia_items.count()
    )

    if 'file' in request.FILES:
        item.file = request.FILES['file']

    item.save()

    return JsonResponse({
        'id': item.id,
        'media_type': item.media_type,
        'title': item.title,
        'text_content': item.text_content,
        'file_url': item.file.url if item.file else '',
        'youtube_url': item.youtube_url,
        'embed_url': item.get_youtube_embed_url(),
        'show_in_multimedia': item.show_in_multimedia,
    })


@require_POST
def save_multimedia(request, item_id):
    item = get_object_or_404(MultimediaItem, id=item_id)
    data = json.loads(request.body)
    if 'title' in data:
        item.title = data['title']
    if 'text_content' in data:
        item.text_content = data['text_content']
    if 'youtube_url' in data:
        item.youtube_url = data['youtube_url']
    item.save()
    return JsonResponse({'status': 'ok', 'embed_url': item.get_youtube_embed_url()})


def upload_replace_multimedia(request, item_id):
    """Replace the file for an existing multimedia item."""
    item = get_object_or_404(MultimediaItem, id=item_id)
    if request.method == 'POST' and 'file' in request.FILES:
        if item.file:
            item.file.delete(save=False)
        item.file = request.FILES['file']
        item.save()
        return JsonResponse({'file_url': item.file.url})
    return JsonResponse({'error': 'no file'}, status=400)


@require_POST
def delete_multimedia(request, item_id):
    item = get_object_or_404(MultimediaItem, id=item_id)
    if item.file:
        item.file.delete(save=False)
    item.delete()
    return JsonResponse({'status': 'ok'})


# ─── Expandable Sections ──────────────────────────────────────────────────────

@require_POST
def save_expandable(request, section_id):
    section = get_object_or_404(ExpandableSection, id=section_id)
    data = json.loads(request.body)
    if 'title' in data:
        section.title = data['title']
    if 'content' in data:
        section.content = data['content']
    if 'is_open' in data:
        section.is_open = data['is_open']
    section.save()
    return JsonResponse({'status': 'ok'})


@require_POST
def add_expandable(request, slug):
    page = get_object_or_404(Page, slug=slug)
    data = json.loads(request.body)
    section = ExpandableSection.objects.create(
        page=page,
        title=data.get('title', 'New Section'),
        content=data.get('content', '<p>Add content here.</p>'),
        order=page.expandable_sections.count()
    )
    return JsonResponse({'id': section.id, 'title': section.title, 'content': section.content})


@require_POST
def delete_expandable(request, section_id):
    section = get_object_or_404(ExpandableSection, id=section_id)
    section.delete()
    return JsonResponse({'status': 'ok'})


# ─── Comments ─────────────────────────────────────────────────────────────────

@require_POST
def add_comment(request, slug):
    page = get_object_or_404(Page, slug=slug)
    data = json.loads(request.body)
    comment = Comment.objects.create(
        page=page,
        selected_text=data.get('selected_text', ''),
        comment_text=data.get('comment_text', ''),
    )
    return JsonResponse({'id': comment.id, 'created_at': comment.created_at.isoformat()})


@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    return JsonResponse({'status': 'ok'})


@require_POST
def update_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    data = json.loads(request.body)
    new_text = (data.get('comment_text') or '').strip()
    if not new_text:
        return JsonResponse({'error': 'comment_text is required'}, status=400)
    comment.comment_text = new_text
    comment.save(update_fields=['comment_text'])
    return JsonResponse({'status': 'ok', 'comment_text': comment.comment_text})


@require_POST
def add_article_media_link(request, slug):
    page = get_object_or_404(Page, slug=slug)
    data = json.loads(request.body)

    multimedia_item_id = data.get('multimedia_item_id')
    display_text = (data.get('display_text') or '').strip()
    if not multimedia_item_id:
        return JsonResponse({'error': 'multimedia_item_id is required'}, status=400)

    item = get_object_or_404(MultimediaItem, id=multimedia_item_id, page=page)
    if not display_text:
        display_text = f"Open {item.media_type}: {item.title or 'Untitled'}"

    link = ArticleMediaLink.objects.create(
        page=page,
        multimedia_item=item,
        display_text=display_text,
    )

    return JsonResponse({
        'id': link.id,
        'display_text': link.display_text,
        'multimedia_item_id': item.id,
        'media_type': item.media_type,
    })


@require_POST
def update_article_media_link(request, link_id):
    link = get_object_or_404(ArticleMediaLink, id=link_id)
    data = json.loads(request.body)
    display_text = (data.get('display_text') or '').strip()
    if not display_text:
        return JsonResponse({'error': 'display_text is required'}, status=400)

    link.display_text = display_text
    link.save(update_fields=['display_text'])
    return JsonResponse({'status': 'ok', 'display_text': link.display_text})


@require_POST
def add_article_image(request, slug):
    page = get_object_or_404(Page, slug=slug)
    article, _ = Article.objects.get_or_create(page=page, defaults={'content': page.content})
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'file is required'}, status=400)

    title = (request.POST.get('title') or '').strip() or 'Article Image'
    article_image = ArticleImage.objects.create(
        article=article,
        title=title,
        file=request.FILES['file'],
    )
    return JsonResponse({
        'id': article_image.id,
        'title': article_image.title,
        'file_url': article_image.file.url,
        'media_type': 'image',
    })


@require_POST
def add_article_audio(request, slug):
    page = get_object_or_404(Page, slug=slug)
    article, _ = Article.objects.get_or_create(page=page, defaults={'content': page.content})
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'file is required'}, status=400)

    title = (request.POST.get('title') or '').strip() or 'Article Audio'
    article_audio = ArticleAudio.objects.create(
        article=article,
        title=title,
        file=request.FILES['file'],
    )
    return JsonResponse({
        'id': article_audio.id,
        'title': article_audio.title,
        'file_url': article_audio.file.url,
        'media_type': 'audio',
    })


@require_POST
def add_article_video(request, slug):
    page = get_object_or_404(Page, slug=slug)
    article, _ = Article.objects.get_or_create(page=page, defaults={'content': page.content})
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'file is required'}, status=400)

    title = (request.POST.get('title') or '').strip() or 'Article Video'
    article_video = ArticleVideo.objects.create(
        article=article,
        title=title,
        file=request.FILES['file'],
    )
    return JsonResponse({
        'id': article_video.id,
        'title': article_video.title,
        'file_url': article_video.file.url,
        'media_type': 'video',
    })
