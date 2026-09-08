from django.contrib import admin
from django.db import models
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action, display
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RelatedDropdownFilter, RangeDateFilter
from unfold.contrib.forms.widgets import WysiwygWidget

from .models import (
    BlogPost, Category, ProductCategory, Product, ProductVariant,
    ProductImage, Tag, TeamMember, Certification,
    ContactMessage, SiteConfiguration
)
from .widgets import DragDropImageWidget


# =====================================================================
# DASHBOARD CALLBACK (for Unfold modern admin)
# =====================================================================
def dashboard_callback(request, context):
    """
    Custom dashboard data for Unfold admin.
    Adds statistics and recent messages to the dashboard.
    """
    total_products = Product.objects.count()
    total_categories = ProductCategory.objects.count()
    total_variants = ProductVariant.objects.count()
    total_messages_last_30d = ContactMessage.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()

    certified_count = Product.objects.filter(certification_status='full').count()
    in_progress_count = Product.objects.filter(certification_status='in_progress').count()
    pre_certified_count = Product.objects.filter(certification_status='pre').count()

    context.update({
        'total_products': total_products,
        'total_categories': total_categories,
        'total_variants': total_variants,
        'total_messages': total_messages_last_30d,
        'recent_messages': ContactMessage.objects.order_by('-created_at')[:5],
        'certified_count': certified_count,
        'in_progress_count': in_progress_count,
        'pre_certified_count': pre_certified_count,
        'team_size': TeamMember.objects.count(),
        'blog_posts': BlogPost.objects.count(),
        'certifications': Certification.objects.count(),
    })
    return context


def environment_callback(request):
    """
    Small colored label shown top-right of the admin header, so nobody
    accidentally edits production thinking they're in dev.
    Returns [text, color] where color is one of: info, danger, warning, success.
    """
    from django.conf import settings
    if settings.DEBUG:
        return ["Development", "warning"]
    return ["Production", "danger"]


# =====================================================================
# BASE ADMIN — shared modern-UX defaults for every model below
# =====================================================================
class BaseModelAdmin(ModelAdmin):
    compressed_fields = True      # tighter, cleaner form layout
    warn_unsaved_form = True      # confirm before navigating away with unsaved edits
    list_filter_submit = True     # "Apply" button on filters instead of instant-reload per click


# ---------- Inline Admin Classes ----------
class ProductVariantInline(TabularInline):
    model = ProductVariant
    extra = 1
    tab = True
    fields = ['name', 'weight', 'price', 'stock_quantity', 'sku']
    verbose_name = "Product Variant"
    verbose_name_plural = "Product Variants"


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    tab = True
    fields = ['image', 'caption', 'is_primary', 'display_order']
    formfield_overrides = {
        models.ImageField: {'widget': DragDropImageWidget},
    }


# ---------- Custom Admin Classes ----------
@admin.register(ProductCategory)
class ProductCategoryAdmin(BaseModelAdmin):
    list_display = ['name', 'slug', 'display_order', 'product_count']
    list_editable = ['display_order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    ordering = ['display_order']

    @display(description="Products")
    def product_count(self, obj):
        return obj.products.count()


@admin.register(Product)
class ProductAdmin(BaseModelAdmin):
    list_display = ['name', 'category', 'status_badge', 'featured_badge', 'created_at']
    list_filter = [
        ('category', RelatedDropdownFilter),
        ('certification_status', ChoicesDropdownFilter),
        'is_featured',
        'is_organic',
    ]
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline, ProductImageInline]
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    actions_row = ['preview_on_site']

    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},
    }

    fieldsets = (
        (_("General"), {
            'classes': ['tab'],
            'fields': ('name', 'slug', 'category'),
        }),
        (_("Content"), {
            'classes': ['tab'],
            'fields': ('description', 'detailed_description'),
        }),
        (_("Certification & Status"), {
            'classes': ['tab'],
            'fields': ('certification_status', 'is_organic', 'is_featured'),
        }),
        (_("Metadata"), {
            'classes': ['tab'],
            'fields': ('display_order', 'created_at', 'updated_at'),
        }),
    )

    @display(description="Status", label={
        'full': 'success',
        'pre': 'info',
        'in_progress': 'warning',
        'not_applicable': 'danger',
    })
    def status_badge(self, obj):
        return obj.certification_status

    @display(description="Featured", boolean=True)
    def featured_badge(self, obj):
        return obj.is_featured

    @action(description="View on site", icon="visibility", url_path="view-on-site",
            attrs={"target": "_blank"})
    def preview_on_site(self, request, object_id):
        product = self.get_object(request, object_id)
        return redirect(reverse('product_detail', args=[product.slug]))

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('images', 'product_variants')


@admin.register(ProductVariant)
class ProductVariantAdmin(BaseModelAdmin):
    list_display = ['name', 'product', 'weight', 'price', 'stock_status']
    list_filter = ['product__category']
    search_fields = ['name', 'product__name', 'sku']
    list_select_related = ['product']

    @display(description="Status", label={
        'In Stock': 'success',
        'Low Stock': 'warning',
        'Out of Stock': 'danger',
    })
    def stock_status(self, obj):
        if obj.stock_quantity > 50:
            return 'In Stock'
        elif obj.stock_quantity > 0:
            return 'Low Stock'
        return 'Out of Stock'


@admin.register(ProductImage)
class ProductImageAdmin(BaseModelAdmin):
    list_display = ['product', 'thumbnail', 'is_primary', 'display_order']
    list_editable = ['is_primary', 'display_order']
    list_filter = [('product', RelatedDropdownFilter)]
    search_fields = ['product__name', 'caption']
    formfield_overrides = {
        models.ImageField: {'widget': DragDropImageWidget},
    }

    @display(description="Preview")
    def thumbnail(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" style="width:44px;height:44px;'
                f'object-fit:cover;border-radius:8px;" />'
            )
        return '—'


@admin.register(TeamMember)
class TeamMemberAdmin(BaseModelAdmin):
    list_display = ['name', 'position', 'thumbnail']
    search_fields = ['name', 'position']
    formfield_overrides = {
        models.ImageField: {'widget': DragDropImageWidget},
        models.TextField: {'widget': WysiwygWidget},
    }
    fieldsets = (
        (_("Personal Info"), {
            'classes': ['tab'],
            'fields': ('name', 'position', 'bio'),
        }),
        (_("Social Media"), {
            'classes': ['tab'],
            'fields': ('twitter', 'facebook', 'instagram', 'linkedin'),
        }),
        (_("Photo"), {
            'classes': ['tab'],
            'fields': ('image',),
        }),
    )

    @display(description="Photo")
    def thumbnail(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" style="width:36px;height:36px;'
                f'object-fit:cover;border-radius:50%;" />'
            )
        return '—'


@admin.register(Certification)
class CertificationAdmin(BaseModelAdmin):
    list_display = ['name', 'thumbnail']
    search_fields = ['name']
    ordering = ['name']
    formfield_overrides = {
        models.ImageField: {'widget': DragDropImageWidget},
        models.TextField: {'widget': WysiwygWidget},
    }

    @display(description="Logo")
    def thumbnail(self, obj):
        if obj.logo:
            return mark_safe(
                f'<img src="{obj.logo.url}" style="width:36px;height:36px;'
                f'object-fit:contain;border-radius:6px;" />'
            )
        return '—'


@admin.register(ContactMessage)
class ContactMessageAdmin(BaseModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at']
    list_filter = [('created_at', RangeDateFilter)]
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        (_("Message Details"), {
            'fields': ('name', 'email', 'subject', 'message')
        }),
        (_("Metadata"), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(BlogPost)
class BlogPostAdmin(BaseModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = [
        ('categories', RelatedDropdownFilter),
        ('tags', RelatedDropdownFilter),
    ]
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories', 'tags')
    formfield_overrides = {
        models.ImageField: {'widget': DragDropImageWidget},
        models.TextField: {'widget': WysiwygWidget},
    }


@admin.register(Category)
class CategoryAdmin(BaseModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(BaseModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


# =====================================================================
# SITE CONFIGURATION (Singleton)
# =====================================================================
@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(BaseModelAdmin):
    def has_add_permission(self, request):
        return not SiteConfiguration.objects.exists()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # Only give the long-form prose fields the rich text editor —
        # one-line hero subtitles etc. stay as plain inputs.
        if db_field.name in ('about_description', 'about_closing'):
            kwargs['widget'] = WysiwygWidget
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (
        (_("Site Identity"), {
            'classes': ['tab'],
            'fields': ('site_name',),
        }),
        (_("Hero Slides"), {
            'classes': ['tab'],
            'fields': (
                'hero_slide1_title', 'hero_slide1_subtitle', 'hero_slide1_image',
                'hero_slide1_button_text', 'hero_slide1_button_link',
                'hero_slide2_title', 'hero_slide2_subtitle', 'hero_slide2_image',
                'hero_slide2_button_text', 'hero_slide2_button_link',
                'hero_slide3_title', 'hero_slide3_subtitle', 'hero_slide3_image',
                'hero_slide3_button_text', 'hero_slide3_button_link',
            ),
        }),
        (_("About Section"), {
            'classes': ['tab'],
            'fields': ('about_title', 'about_subtitle', 'about_description',
                       'about_bullet1', 'about_bullet2', 'about_bullet3',
                       'about_closing'),
        }),
        (_("Section Visibility"), {
            'classes': ['tab'],
            'fields': ('show_about_section', 'show_products_section',
                       'show_certifications_section'),
        }),
        (_("Products & Certifications"), {
            'classes': ['tab'],
            'fields': ('products_section_title', 'products_section_subtitle',
                       'certifications_section_title', 'certifications_section_subtitle'),
        }),
        (_("Contact & Maps"), {
            'classes': ['tab'],
            'fields': ('contact_address_line1', 'contact_address_line2',
                       'contact_city', 'contact_postal',
                       'contact_phone1', 'contact_phone2',
                       'contact_email1', 'contact_email2',
                       'google_maps_embed_url'),
        }),
        (_("WhatsApp & Social"), {
            'classes': ['tab'],
            'fields': ('whatsapp_number', 'whatsapp_message',
                       'facebook_url', 'instagram_url', 'linkedin_url', 'twitter_url'),
        }),
        (_("Footer"), {
            'classes': ['tab'],
            'fields': ('footer_developer_text', 'footer_developer_url'),
        }),
    )

# Admin Site Customization
admin.site.site_header = "MAME Foods Administration"
admin.site.site_title = "MAME Foods Admin Portal"
admin.site.index_title = "Welcome to MAME Foods Administration"
