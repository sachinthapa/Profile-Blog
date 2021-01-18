from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post
from django.db.models import Q, Count
from django.contrib.auth.models import User
import psycopg2

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)

class PostListView(ListView):

    con = psycopg2.connect(database="blog", 
    user="sachin", 
    password="sachin",
    host="localhost", port="5432")
    
    print("Database opened successfully")
    cur = con.cursor()

    cur.execute("SELECT * FROM blog_post")
    rows = cur.fetchall()
    for row in rows:
        print(rows)
    

    
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    
    paginate_by = 5

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5
    
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

class PostDetailView(DetailView):
    model = Post

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

def FilterView(request):
    qs=Post.objects.all()

    title_author_query=request.GET.get('title_contains')
    title_exact_query=request.GET.get('id_exact')
    title_or_author_query=request.GET.get('title_or_author')

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    print("date_min date_max", date_min,date_max)

    if is_valid_queryparam(title_author_query):
        qs = qs.filter(title__icontains=title_author_query)
    elif is_valid_queryparam(title_or_author_query):
        qs = qs.filter(Q(title__icontains=title_or_author_query)
                       | Q(author__username__icontains=title_or_author_query)
                       ).distinct()

    if is_valid_queryparam(date_min):
        qs = qs.filter(date_posted=date_min)

    if is_valid_queryparam(date_max):
        qs = qs.filter(date_posted=date_max)

    context = {
        'queryset' : qs
    }

    return render(request,'blog/blog_search.html',context)


def is_valid_queryparam(param):
    return param != '' and param is not None
