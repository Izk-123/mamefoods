from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    featured_image = models.ImageField(upload_to='blog/')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    icon_class = models.CharField(
        max_length=50, 
        default='bx bxs-leaf',
        help_text="Icon class from Boxicons (e.g. 'bx bxs-leaf')"
    )
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    CERT_STATUS_CHOICES = [
        ('pre', 'Pre-Certified'),
        ('full', 'Fully Certified'),
        ('in_progress', 'In Progress'),
        ('not_applicable', 'Not Applicable'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, related_name='products')
    description = models.TextField()
    detailed_description = models.TextField(blank=True)
    certification_status = models.CharField(max_length=20, choices=CERT_STATUS_CHOICES, default='in_progress')
    is_organic = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Product variations
    variants = models.ManyToManyField('ProductVariant', blank=True, related_name='main_products')

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ProductVariant(models.Model):
    name = models.CharField(max_length=100)
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='product_variants'
    )
    weight = models.CharField(
        max_length=50, 
        blank=True,
        help_text="e.g., 1kg, 5kg, 10kg"
    )
    price = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        blank=True,
        null=True
    )
    image = models.ImageField(
        upload_to='products/variants/',
        blank=True,
        null=True
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    sku = models.CharField(
        max_length=50, 
        unique=True,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.product.name} - {self.name} ({self.weight})"

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='team/', blank=True, null=True)
    twitter = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.position}"

class Certification(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='certifications/')
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)

    def __str__(self):
        return self.name

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.name}"
    
class SiteConfiguration(models.Model):
    """
    Singleton model for global site settings.
    Use SiteConfiguration.load() to access the single instance.
    """
    # Site identity
    site_name = models.CharField(max_length=100, default="MAME Foods")

    # Hero Slide 1
    hero_slide1_title = models.CharField(max_length=200, blank=True,
                                         default="Welcome to MAME Foods")
    hero_slide1_subtitle = models.TextField(blank=True,
        default="Producer of Malawi's finest aromatic long grain rice, flour, and agricultural products")
    hero_slide1_image = models.ImageField(upload_to='hero/', blank=True, null=True,
        help_text="Leave empty to use static fallback (img/slide/slide-1.jpg)")
    hero_slide1_button_text = models.CharField(max_length=50, blank=True, default="Discover More")
    hero_slide1_button_link = models.CharField(max_length=200, blank=True, default="#about-us")

    # Hero Slide 2
    hero_slide2_title = models.CharField(max_length=200, blank=True,
                                         default="Organic & Authentic Taste")
    hero_slide2_subtitle = models.TextField(blank=True,
        default='Experience the original "kumudzi" taste in every product we create')
    hero_slide2_image = models.ImageField(upload_to='hero/', blank=True, null=True)
    hero_slide2_button_text = models.CharField(max_length=50, blank=True, default="Our Products")
    hero_slide2_button_link = models.CharField(max_length=200, blank=True, default="#products")

    # Hero Slide 3
    hero_slide3_title = models.CharField(max_length=200, blank=True,
                                         default="Quality Certified")
    hero_slide3_subtitle = models.TextField(blank=True,
        default="Pre-certified by Malawi Bureau of Standards with full certification underway")
    hero_slide3_image = models.ImageField(upload_to='hero/', blank=True, null=True)
    hero_slide3_button_text = models.CharField(max_length=50, blank=True, default="Our Certifications")
    hero_slide3_button_link = models.CharField(max_length=200, blank=True, default="#certifications")

    # About section
    about_title = models.CharField(max_length=200, blank=True, default="About MAME Foods")
    about_subtitle = models.CharField(max_length=200, blank=True,
                                      default="Trusted indigenous brand providing authentic \"kumudzi\" taste")
    about_description = models.TextField(blank=True,
        default="MAME Foods is a producer and supplier of food stuffs in Malawi...")
    about_bullet1 = models.CharField(max_length=200, blank=True,
                                     default="Our rice is pre-certified by the Malawi Bureau of Standards")
    about_bullet2 = models.CharField(max_length=200, blank=True,
                                     default="Substantial progress towards full certification")
    about_bullet3 = models.CharField(max_length=200, blank=True,
                                     default="All products in different phases of certification process")
    about_closing = models.TextField(blank=True,
        default="Our drive is to give you quality organic food stuffs that maintain their original \"kumudzi\" taste at a good price.")

    # Section visibility toggles
    show_about_section = models.BooleanField(default=True)
    show_products_section = models.BooleanField(default=True)
    show_certifications_section = models.BooleanField(default=True)

    # Products section
    products_section_title = models.CharField(max_length=200, blank=True, default="Our Products")
    products_section_subtitle = models.CharField(max_length=200, blank=True,
                                                 default="Premium quality food products made with care")

    # Certifications section
    certifications_section_title = models.CharField(max_length=200, blank=True, default="Our Certifications")
    certifications_section_subtitle = models.CharField(max_length=200, blank=True,
                                                       default="Quality assurance and standards compliance")

    # Contact information
    contact_address_line1 = models.CharField(max_length=200, blank=True, default="MAME House")
    contact_address_line2 = models.CharField(max_length=200, blank=True,
                                             default="Plot 10/069, Luther Street")
    contact_city = models.CharField(max_length=100, blank=True, default="Area 10, Lilongwe")
    contact_postal = models.CharField(max_length=100, blank=True,
                                      default="P.O. Box 30632, Capital City, Lilongwe 3")
    contact_phone1 = models.CharField(max_length=20, blank=True, default="+265 999 950 489")
    contact_phone2 = models.CharField(max_length=20, blank=True)
    contact_email1 = models.EmailField(blank=True, default="info@mamefoods.mw")
    contact_email2 = models.EmailField(blank=True)

    google_maps_embed_url = models.URLField(
        max_length=1000,
        blank=True,
        default="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3770.755798307342!2d33.76824441490085!3d-13.983324959861402!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMTPCsDU4JzU5LjkiUyAzM8KwNDYnMTUuNSJF!5e0!3m2!1sen!2smw!4v1651234567890!5m2!1sen!2smw")

    # WhatsApp integration
    whatsapp_number = models.CharField(max_length=20, blank=True,
                                       help_text="Full international number, e.g. +265999950489")
    whatsapp_message = models.TextField(blank=True,
                                        default="Hello MAME Foods! I'd like to know more about your products.")

    # Social links
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)

    # Footer
    footer_developer_text = models.CharField(max_length=200,
                                             default="Developed by Pritech",
                                             help_text="Appears in the copyright line")
    footer_developer_url = models.URLField(blank=True, help_text="Optional link for the developer")

    def save(self, *args, **kwargs):
        # Ensure only one instance exists (pk=1)
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Site Configuration"