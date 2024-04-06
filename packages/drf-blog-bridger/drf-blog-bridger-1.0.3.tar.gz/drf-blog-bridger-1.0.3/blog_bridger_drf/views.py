from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404

# from .models import Comment
from .serializers import PostSerializer, CommentSerializer, PostDetailSerializer, PostUpdateSerializer
from .permissions import IsPostOwnerOrReadOnly

from django.conf import settings
from django.utils.module_loading import import_string
from .default_settings import *

Post = import_string(getattr(settings, 'BLOG_BRIDGER_POST', BLOG_BRIDGER_POST))
Comment = import_string(getattr(settings, "BLOG_BRIDGER_COMMENT", BLOG_BRIDGER_COMMENT))

class PostListCreateView(generics.GenericAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        queryset = Post.objects.all()
        author = self.request.query_params.get('author')
        title = self.request.query_params.get('title')
        if author:
            queryset = queryset.filter(author__username=author)
        if title:
            queryset = queryset.filter(post_title__icontains=title)
        return queryset

    def get(self, request:Request):
         queryset = self.get_queryset()
         serializer = self.serializer_class(instance=queryset, many=True, context={'request': request})

         response = {
             "message":"successful",
             "data": serializer.data
         }
         return Response(data=response, status=status.HTTP_200_OK)



    def post(self, request:Request):
        serializer = self.serializer_class(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            response = {
                "message":"successful",
                "data": serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        
        response = {
                "message":"failed",
                "info": serializer.errors
            }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

class RetrieveUpdateDeletePostView(generics.GenericAPIView):
    serializer_class = PostDetailSerializer
    permission_classes = [IsPostOwnerOrReadOnly, IsAuthenticatedOrReadOnly]

    def patch(self, request:Request, post_id:int):
        post = get_object_or_404(Post, pk=post_id)
        self.check_object_permissions(request, post)

        serializer = PostUpdateSerializer(instance=post, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            response = {
                "message":"successful",
                "data": serializer.data
            }
            return Response(data=response, status=status.HTTP_200_OK)
        
        response = {
                "message":"failed",
                "info": serializer.errors
            }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request:Request, post_id:int):
        post = get_object_or_404(Post, id=post_id)

        serializer = self.serializer_class(instance=post)
        response = {
             "message":"successful",
             "data": serializer.data
         }
        return Response(data=response, status=status.HTTP_200_OK)


    def delete(self, request:Request, post_id:int):
        post = get_object_or_404(Post, pk=post_id)
        self.check_object_permissions(request, post)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentView(generics.GenericAPIView):
    serializer_class = CommentSerializer

    def get(self, request:Request, post_id:int):
        post = get_object_or_404(Post, id=post_id)

        comments = Comment.objects.filter(post=post)
        serializer = self.serializer_class(instance=comments, many=True)
        response = {
             "message":"successful",
             "data": serializer.data
         }
        return Response(data=response, status=status.HTTP_200_OK)

    def post(self, request:Request, post_id:int, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id)

        data = request.data
        data['post']=post

        serializer = self.serializer_class(data=data, context= {'request':request, 'view':self})

        if serializer.is_valid():
            serializer.save()
            
            response = {
                "message":"successful",
                "data": serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        
        response = {
                "message":"failed",
                "info": serializer.errors
            }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)