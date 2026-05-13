from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Community, CommunityPost, Comment
from .forms import CommunityForm, CommunityPostForm, CommentForm


class CommunityHubView(LoginRequiredMixin, View):
    """Main community hub page"""
    template_name = 'community/community_hub.html'
    login_url = 'login'
    paginate_by = 10
    
    def get(self, request):
        # Get all communities
        communities = Community.objects.all()
        
        # Get user's communities
        user_communities = request.user.communities.all()
        
        # Get recent posts from user's communities
        posts = CommunityPost.objects.filter(
            community__in=user_communities
        ).order_by('-created_at')
        
        # Paginate posts
        paginator = Paginator(posts, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'communities': communities,
            'user_communities': user_communities,
            'page_obj': page_obj,
            'posts': page_obj.object_list,
        }
        return render(request, self.template_name, context)


class CreateCommunityView(LoginRequiredMixin, View):
    """Create a new community"""
    template_name = 'community/create_community.html'
    form_class = CommunityForm
    login_url = 'login'
    
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.creator = request.user
            community.save()
            community.members.add(request.user)
            messages.success(request, f'Community "{community.name}" created successfully!')
            return redirect('community_detail', pk=community.pk)
        return render(request, self.template_name, {'form': form})


class CommunityDetailView(LoginRequiredMixin, View):
    """View a specific community and its posts"""
    template_name = 'community/community_detail.html'
    login_url = 'login'
    paginate_by = 10
    
    def get(self, request, pk):
        community = get_object_or_404(Community, pk=pk)
        posts = community.posts.all().order_by('-created_at')
        
        # Paginate posts
        paginator = Paginator(posts, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Check if user is member
        is_member = request.user in community.members.all()
        
        context = {
            'community': community,
            'page_obj': page_obj,
            'posts': page_obj.object_list,
            'is_member': is_member,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        community = get_object_or_404(Community, pk=pk)
        action = request.POST.get('action')
        
        if action == 'join':
            community.members.add(request.user)
            messages.success(request, f'Joined community "{community.name}"!')
        elif action == 'leave':
            community.members.remove(request.user)
            messages.success(request, f'Left community "{community.name}"!')
        
        return redirect('community_detail', pk=community.pk)


class CreatePostView(LoginRequiredMixin, View):
    """Create a new community post"""
    template_name = 'community/create_post.html'
    form_class = CommunityPostForm
    login_url = 'login'
    
    def get(self, request, community_pk):
        community = get_object_or_404(Community, pk=community_pk)
        
        # Check if user is member
        if request.user not in community.members.all():
            messages.error(request, 'You must be a member of this community to post.')
            return redirect('community_detail', pk=community_pk)
        
        form = self.form_class()
        return render(request, self.template_name, {
            'form': form,
            'community': community
        })
    
    def post(self, request, community_pk):
        community = get_object_or_404(Community, pk=community_pk)
        
        # Check if user is member
        if request.user not in community.members.all():
            messages.error(request, 'You must be a member of this community to post.')
            return redirect('community_detail', pk=community_pk)
        
        form = self.form_class(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.community = community
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('community_detail', pk=community_pk)
        
        return render(request, self.template_name, {
            'form': form,
            'community': community
        })


class EditPostView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Edit a community post"""
    template_name = 'community/edit_post.html'
    form_class = CommunityPostForm
    login_url = 'login'
    
    def test_func(self):
        post = get_object_or_404(CommunityPost, pk=self.kwargs['pk'])
        return post.author == self.request.user or self.request.user.is_admin_user()
    
    def get(self, request, pk):
        post = get_object_or_404(CommunityPost, pk=pk)
        form = self.form_class(instance=post)
        return render(request, self.template_name, {
            'form': form,
            'post': post,
            'community': post.community
        })
    
    def post(self, request, pk):
        post = get_object_or_404(CommunityPost, pk=pk)
        form = self.form_class(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('community_detail', pk=post.community.pk)
        
        return render(request, self.template_name, {
            'form': form,
            'post': post,
            'community': post.community
        })


class DeletePostView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Delete a community post"""
    login_url = 'login'
    
    def test_func(self):
        post = get_object_or_404(CommunityPost, pk=self.kwargs['pk'])
        return post.author == self.request.user or self.request.user.is_admin_user()
    
    def post(self, request, pk):
        post = get_object_or_404(CommunityPost, pk=pk)
        community_pk = post.community.pk
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('community_detail', pk=community_pk)


class CommentHistoryView(LoginRequiredMixin, View):
    """View user's comment history"""
    template_name = 'community/comment_history.html'
    login_url = 'login'
    paginate_by = 20
    
    def get(self, request):
        comments = Comment.objects.filter(author=request.user).order_by('-created_at')
        
        # Paginate comments
        paginator = Paginator(comments, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'comments': page_obj.object_list,
        }
        return render(request, self.template_name, context)


class EditCommentView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Edit a comment"""
    template_name = 'community/edit_comment.html'
    form_class = CommentForm
    login_url = 'login'
    
    def test_func(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        return comment.author == self.request.user or self.request.user.is_admin_user()
    
    def get(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        form = self.form_class(instance=comment)
        return render(request, self.template_name, {
            'form': form,
            'comment': comment
        })
    
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        form = self.form_class(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated successfully!')
            return redirect('post_detail', pk=comment.post.pk)
        
        return render(request, self.template_name, {
            'form': form,
            'comment': comment
        })


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Delete a comment"""
    login_url = 'login'
    
    def test_func(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        return comment.author == self.request.user or self.request.user.is_admin_user()
    
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        post_pk = comment.post.pk
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('post_detail', pk=post_pk)


class PostDetailView(LoginRequiredMixin, View):
    """View a specific post with comments"""
    template_name = 'community/post_detail.html'
    login_url = 'login'
    form_class = CommentForm
    
    def get(self, request, pk):
        post = get_object_or_404(CommunityPost, pk=pk)
        comments = post.comments.all()
        form = self.form_class()
        
        context = {
            'post': post,
            'comments': comments,
            'form': form,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        post = get_object_or_404(CommunityPost, pk=pk)
        form = self.form_class(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Comment posted successfully!')
            return redirect('post_detail', pk=post.pk)
        
        comments = post.comments.all()
        context = {
            'post': post,
            'comments': comments,
            'form': form,
        }
        return render(request, self.template_name, context)
