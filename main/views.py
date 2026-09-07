from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, TemplateView, FormView, View
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from .models import ProductCategory, Product, Tag, TeamMember, Certification, BlogPost, Category
from .forms import ContactForm


# ─────────────────────────────────────────────
#  Home Page
# ─────────────────────────────────────────────
class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(is_featured=True)[:3]
        context['certifications'] = Certification.objects.all()
        return context


# ─────────────────────────────────────────────
#  Products (category listing)
# ─────────────────────────────────────────────
class ProductListView(ListView):
    template_name = 'main/products.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return ProductCategory.objects.prefetch_related('products').order_by('display_order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if any products exist across all categories
        context['has_products'] = any(cat.products.exists() for cat in context['categories'])
        return context


# ─────────────────────────────────────────────
#  Product Detail
# ─────────────────────────────────────────────
class ProductDetailView(DetailView):
    model = Product
    template_name = 'main/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.prefetch_related('images', 'product_variants')


# ─────────────────────────────────────────────
#  About Page
# ─────────────────────────────────────────────
class AboutView(TemplateView):
    template_name = 'main/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team_members'] = TeamMember.objects.all()
        context['certifications'] = Certification.objects.all()
        return context


# ─────────────────────────────────────────────
#  Contact Form (with AJAX support)
# ─────────────────────────────────────────────
class ContactView(FormView):
    template_name = 'main/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact_success')

    def form_valid(self, form):
        form.save()
        # If AJAX request, return JSON response
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Your message has been sent. Thank you!'
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        # If AJAX request, return JSON errors
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Please correct the errors below',
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)


# ─────────────────────────────────────────────
#  Contact Success Page
# ─────────────────────────────────────────────
class ContactSuccessView(TemplateView):
    template_name = 'main/contact_success.html'


# ─────────────────────────────────────────────
#  Blog Listing
# ─────────────────────────────────────────────
class BlogListView(ListView):
    model = BlogPost
    template_name = 'main/blog.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['recent_posts'] = BlogPost.objects.all().order_by('-created_at')[:5]
        context['tags'] = Tag.objects.all()
        return context


# ─────────────────────────────────────────────
#  Blog Detail
# ─────────────────────────────────────────────
class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'main/blog-single.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


# ─────────────────────────────────────────────
#  HTMX Product List (partial)
# ─────────────────────────────────────────────
class HTMXProductListView(View):
    """
    Returns a partial HTML list of products filtered by category.
    Used for HTMX dynamic filtering (e.g., in admin or front-end).
    """
    def get(self, request, *args, **kwargs):
        category_id = request.GET.get('category')
        products = Product.objects.all()
        if category_id:
            products = products.filter(category_id=category_id)

        html = render_to_string('partials/product_list.html', {'products': products})
        return HttpResponse(html)