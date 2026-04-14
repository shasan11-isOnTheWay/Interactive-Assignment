from django.urls import path
from . import views

app_name = 'editor'

urlpatterns = [
    path('', views.index, name='index'),
    path('page/<slug:slug>/', views.page_view, name='page_view'),
    path('api/page/create/', views.create_page, name='create_page'),
    path('api/page/<slug:slug>/save/', views.save_page, name='save_page'),
    path('api/page/<slug:slug>/delete/', views.delete_page, name='delete_page'),

    path('api/page/<slug:slug>/multimedia/add/', views.add_multimedia, name='add_multimedia'),
    path('api/multimedia/<int:item_id>/save/', views.save_multimedia, name='save_multimedia'),
    path('api/multimedia/<int:item_id>/upload/', views.upload_replace_multimedia, name='upload_multimedia'),
    path('api/multimedia/<int:item_id>/delete/', views.delete_multimedia, name='delete_multimedia'),

    path('api/page/<slug:slug>/expandable/add/', views.add_expandable, name='add_expandable'),
    path('api/expandable/<int:section_id>/save/', views.save_expandable, name='save_expandable'),
    path('api/expandable/<int:section_id>/delete/', views.delete_expandable, name='delete_expandable'),

    path('api/page/<slug:slug>/comment/add/', views.add_comment, name='add_comment'),
    path('api/comment/<int:comment_id>/update/', views.update_comment, name='update_comment'),
    path('api/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('api/page/<slug:slug>/article-media/add/', views.add_article_media_link, name='add_article_media_link'),
    path('api/article-media/<int:link_id>/update/', views.update_article_media_link, name='update_article_media_link'),
    path('api/page/<slug:slug>/article-image/add/', views.add_article_image, name='add_article_image'),
    path('api/page/<slug:slug>/article-audio/add/', views.add_article_audio, name='add_article_audio'),
    path('api/page/<slug:slug>/article-video/add/', views.add_article_video, name='add_article_video'),
]
