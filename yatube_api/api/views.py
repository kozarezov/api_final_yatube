from rest_framework import viewsets
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination

from posts.models import Group, Post
from .serializers import (CommentSerializer, FollowSerializer,
                          GroupSerializer, PostSerializer)
from .permissions import IsAuthorOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(author=self.request.user, post=post)

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        queryset = post.comments.all()
        return queryset


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class FollowViewSet(viewsets.ViewSetMixin, generics.ListCreateAPIView):
    serializer_class = FollowSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('user__username', 'following__username')
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        current_user = self.request.user
        return current_user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
