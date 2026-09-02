from django.contrib import admin
from .models import (
    BlogPost, Category, ProductCategory, Product, ProductVariant,
    ProductImage, Tag, TeamMember, Certification,
    ContactMessage, SiteConfiguration
)

# Inline Admin Classes
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['name', 'weight', 'price', 'stock_quantity', 'sku']
    classes = ['collapse']
    verbose_name = "Product Variant"
    verbose_name_plural = "Product Variants"

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'caption', 'is_primary', 'display_order']
    classes = ['collapse']

# Custom Admin Classes
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'display_order', 'product_count']
    list_editable = ['display_order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    ordering = ['display_order']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Products"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'certification_status', 'is_featured', 'created_at']
    list_filter = ['category', 'certification_status', 'is_featured', 'is_organic']
    list_editable = ['is_featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline, ProductImageInline]
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'detailed_description')
        }),
        ('Certification & Status', {
            'fields': ('certification_status', 'is_organic', 'is_featured')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'display_order'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('images', 'product_variants')

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'weight', 'price', 'stock_status']
    list_filter = ['product__category']
    search_fields = ['name', 'product__name', 'sku']
    list_select_related = ['product']

    def stock_status(self, obj):
        if obj.stock_quantity > 50:
            return 'In Stock'
        elif obj.stock_quantity > 0:
            return 'Low Stock'
        return 'Out of Stock'
    stock_status.short_description = 'Status'
    stock_status.admin_order_field = 'stock_quantity'

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'thumbnail', 'is_primary', 'display_order']
    list_editable = ['is_primary', 'display_order']
    list_filter = ['product']
    search_fields = ['product__name', 'caption']

    def thumbnail(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" />'
        return '-'
    thumbnail.allow_tags = True
    thumbnail.short_description = 'Preview'

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'thumbnail']
    search_fields = ['name', 'position']
    fieldsets = (
        ('Personal Info', {
            'fields': ('name', 'position', 'bio')
        }),
        ('Social Media', {
            'fields': ('twitter', 'facebook', 'instagram', 'linkedin'),
            'classes': ('collapse',)
        }),
        ('Image', {
            'fields': ('image',)
        }),
    )

    def thumbnail(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" />'
        return '-'
    thumbnail.allow_tags = True
    thumbnail.short_description = 'Photo'

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'thumbnail']
    search_fields = ['name']
    ordering = ['name']

    def thumbnail(self, obj):
        if obj.logo:
            return f'<img src="{obj.logo.url}" width="50" height="50" />'
        return '-'
    thumbnail.allow_tags = True
    thumbnail.short_description = 'Logo'

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Message Details', {
            'fields': ('name', 'email', 'subject', 'message')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories', 'tags')

admin.site.register(Category)
admin.site.register(Tag)


# =====================================================================
# SITE CONFIGURATION (Singleton) – control all dynamic content from here
# =====================================================================
@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only one instance allowed
        return not SiteConfiguration.objects.exists()

    fieldsets = (
        ('Site Identity', {
            'fields': ('site_name',)
        }),
        ('Hero Slides', {
            'fields': (
                'hero_slide1_title', 'hero_slide1_subtitle', 'hero_slide1_image',
                'hero_slide1_button_text', 'hero_slide1_button_link',
                'hero_slide2_title', 'hero_slide2_subtitle', 'hero_slide2_image',
                'hero_slide2_button_text', 'hero_slide2_button_link',
                'hero_slide3_title', 'hero_slide3_subtitle', 'hero_slide3_image',
                'hero_slide3_button_text', 'hero_slide3_button_link',
            ),
            'classes': ('collapse',)
        }),
        ('About Section', {
            'fields': ('about_title', 'about_subtitle', 'about_description',
                       'about_bullet1', 'about_bullet2', 'about_bullet3',
                       'about_closing'),
            'classes': ('collapse',)
        }),
        ('Section Visibility', {
            'fields': ('show_about_section', 'show_products_section',
                       'show_certifications_section'),
        }),
        ('Products Section', {
            'fields': ('products_section_title', 'products_section_subtitle'),
            'classes': ('collapse',)
        }),
        ('Certifications Section', {
            'fields': ('certifications_section_title', 'certifications_section_subtitle'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('contact_address_line1', 'contact_address_line2',
                       'contact_city', 'contact_postal',
                       'contact_phone1', 'contact_phone2',
                       'contact_email1', 'contact_email2'),
            'classes': ('collapse',)
        }),
        ('Google Maps', {
            'fields': ('google_maps_embed_url',),
            'classes': ('collapse',)
        }),
        ('WhatsApp Integration', {
            'fields': ('whatsapp_number', 'whatsapp_message'),
        }),
        ('Social Media Links', {
            'fields': ('facebook_url', 'instagram_url', 'linkedin_url', 'twitter_url'),
            'classes': ('collapse',)
        }),
        ('Footer', {
            'fields': ('footer_developer_text', 'footer_developer_url'),
        }),
    )


# Admin Site Customization
admin.site.site_header = "MAME Foods Administration"
admin.site.site_title = "MAME Foods Admin Portal"
admin.site.index_title = "Welcome to MAME Foods Administration"