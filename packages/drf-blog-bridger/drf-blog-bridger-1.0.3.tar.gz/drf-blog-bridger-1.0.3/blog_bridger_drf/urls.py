from django.urls import path

from . import views

urlpatterns = [
    path('list/', views.PostListCreateView.as_view(), name="list-post"),
    path('create/', views.PostListCreateView.as_view(), name="create-post"),
    path('<int:post_id>/', views.RetrieveUpdateDeletePostView.as_view(), name='post-retrieve-delete-update'),
    path('<int:post_id>/comment/', views.CommentView.as_view(), name="create-comment")
]
