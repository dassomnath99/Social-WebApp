from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from .models import Post, Comment, Profile, Conversation, Message
from .forms import SignUpForm, PostForm, CommentForm, ProfileForm
from django.views.decorators.http import require_POST

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect("core:feed")
    else:
        form = SignUpForm()
        return render(request, 'core/signup.html',{
            'form':form,
        })
    return render(request, 'core/signup.html',{
        'form':form,
    })

def feed(request):
    if request.user.is_authenticated is False:
        return redirect('core:signup')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('core:feed')
    else:
        form = PostForm()
    
    following_users = request.user.profile.following.all()
    following_ids = [u.user.id for u in following_users]
    posts = Post.objects.filter(
        Q(author__in = following_ids) | Q(author=request.user)
    ).select_related('author').prefetch_related('likes','comments')
    return render(request, 'core/feed.html',{
        'form':form,
        'posts':posts
    })


def logout_view(request):
    # Ensure the user is logged out and an HttpResponse (redirect) is always returned.
    logout(request)
    return redirect('core:signup')



@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post,pk=pk)
    comments = post.comments.all()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail',pk=pk)
    else:
        form = CommentForm()
        return render(request, 'core/post_detail.html',{
            'post':post, 'comments':comments, 'form':form
        })

    return render(request, 'core/post_detail.html',{
        'post':post, 'comments':comments, 'form':form
    })

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Optional: Check if user can interact with this post
    # (e.g., not blocked, post is visible, etc.)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'total_likes': post.total_likes(),
    })


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    posts = user.posts.all()
    is_following = request.user.profile.following.filter(user=user).exists()

    

    return render(request,'core/profile.html',{
        'profile_user':user,
        'profile':profile,
        'posts':posts,
        'is_following':is_following
    })

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('core:profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'core/edit_profile.html',{
        'form':form
    })

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow != request.user:
        profile_to_follow = user_to_follow.profile
        if request.user.profile.following.filter(user=user_to_follow).exists():
            request.user.profile.following.remove(profile_to_follow)
            following = False
        else:
            request.user.profile.following.add(profile_to_follow)
            following = True
        return JsonResponse({'following':following})
    return JsonResponse({'error':'Cannot follow yourself'}, status=400)

@login_required
def message_list(request):
    conversations = Conversation.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related('user1','user2').prefetch_related('messages')

    # Build conversation list with metadata
    conversation_data = []
    for conv in conversations:
        other_user = conv.get_other_user(request.user)
        last_message = conv.messages.last()
        unread_count = conv.messages.filter(
            is_read=False
        ).exclude(sender=request.user).count

        conversation_data.append({
            'conversation':conv,
            'other_user':other_user,
            'last_message':last_message,
            'unread_count':unread_count
        })
    all_users = User.objects.exclude(id=request.user.id).select_related('profile')

    return render(request, 'core/messages_list.html',{
        'conversations':conversation_data,
        'all_users':all_users,
    })

@login_required
def chat_view(request, username):
    #one to one chat view
    other_user = get_object_or_404(User, username=username)

    if other_user == request.user:
        return redirect('message_list')
    
    conversation = Conversation.get_or_create_conversation(request.user, other_user)
    messages = conversation.messages.select_related('sender').all()

    unread_messages = messages.filter(is_read=False).exclude(sender=request.user)
    for message in unread_messages:
        @require_POST
        @login_required
        def like_post(request, pk):
            post = get_object_or_404(Post, pk=pk)
            if request.user in post.likes.all():
                post.likes.remove(request.user)
                liked = False
            else:
                post.likes.add(request.user)
                liked = True
            return JsonResponse({'liked': liked, 'total_likes': post.total_likes()})
    return render(request, 'core/chat.html',{
        'other_user':other_user,
        'conversation':conversation,
        'messages':messages
    })

@login_required
def search_users(request):
    query = request.GET.get('q','')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).exclude(id=request.user.id).select_related('profile')[:10]
    else:
        users = []

    return JsonResponse({
        'users': [{
            'id':user.id,
            'username':user.username,
            'full_name':user.get_full_name() or user.username,
            'is_online':user.profile.is_online
        }for user in users]
    })
