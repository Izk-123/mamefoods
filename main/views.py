from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import ProductCategory, Product, Tag, TeamMember, Certification, BlogPost, Category
from .forms import ContactForm

def index(request):
    featured_products = Product.objects.filter(is_featured=True)[:3]
    certifications = Certification.objects.all()  # Added certifications
    
    return render(request, 'main/index.html', {
        'featured_products': featured_products,
        'certifications': certifications  # Pass certifications to template
    })

def products(request):
    categories = ProductCategory.objects.prefetch_related(
        'products'
    ).order_by('display_order')
    
    # Check if any products exist across all categories
    has_products = any(category.products.exists() for category in categories)
    
    return render(request, 'main/products.html', {
        'categories': categories,
        'has_products': has_products  # Pass flag to template
    })

def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related('images', 'product_variants'),
        slug=slug
    )
    return render(request, 'main/product_detail.html', {
        'product': product
    })

def about(request):
    team_members = TeamMember.objects.all()
    certifications = Certification.objects.all()
    return render(request, 'main/about.html', {
        'team_members': team_members,
        'certifications': certifications
    })

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            
            # Handle AJAX response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Your message has been sent. Thank you!'
                })
            else:
                return redirect('contact_success')
        else:
            # Handle form errors for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please correct the errors below',
                    'errors': form.errors
                }, status=400)
    else:
        form = ContactForm()
    
    # Handle GET requests and non-AJAX POST with errors
    return render(request, 'main/contact.html', {'form': form})

def contact_success(request):
    return render(request, 'main/contact_success.html')

def blog_list(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    recent_posts = BlogPost.objects.all().order_by('-created_at')[:5]
    tags = Tag.objects.all()  # Add tags to context
    
    return render(request, 'main/blog.html', {
        'posts': posts,
        'categories': categories,
        'recent_posts': recent_posts,
        'tags': tags  # Add this line
    })

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'main/blog-single.html', {'post': post})