from rest_framework import serializers

from .models import Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class PostAUthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email']
        
class PostSerializer(serializers.ModelSerializer):
    author = PostAUthorSerializer(read_only=True)
    class Meta:
        model = Post
        fields = "__all__"

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['author'] = user
        return super().create(validated_data)

class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['post_title', 'post_body']

    def validate(self, attrs):
        if not any(attrs.values()):
            raise serializers.ValidationError("At least one field (post_title or post_body) must be provided for update")
        return super().validate(attrs)

class CommentSerializer(serializers.ModelSerializer):
    comment_author = PostAUthorSerializer(read_only=True)
    class Meta:
        model = Comment
        exclude = ['post']

    def create(self, validated_data):
        user = self.context['request'].user
        post_id = self.context['view'].kwargs.get('post_id')
        validated_data['comment_author'] = user
        validated_data['post_id'] = post_id
        return super().create(validated_data)

class PostDetailSerializer(serializers.ModelSerializer):
    author = PostAUthorSerializer(read_only=True)
    post_comments = CommentSerializer(read_only=True, many=True)
    class Meta:
        model = Post
        fields = "__all__"

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['author'] = user
        return super().create(validated_data)