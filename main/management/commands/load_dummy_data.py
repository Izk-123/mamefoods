from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from main.models import (
    ProductCategory, Product, ProductVariant, ProductImage,
    TeamMember, Certification, BlogPost, Category, Tag,
    SiteConfiguration
)
from django.utils import timezone
import requests
from io import BytesIO

class Command(BaseCommand):
    help = 'Load dummy data for demonstration of all features'

    def handle(self, *args, **options):
        self.stdout.write('Loading dummy data...')

        # --- Site Configuration ---
        config, _ = SiteConfiguration.objects.get_or_create(pk=1)
        config.site_name = "MAME Foods"
        config.hero_slide1_title = "Welcome to MAME Foods"
        config.hero_slide1_subtitle = "Malawi's finest aromatic long grain rice, flour & produce"
        config.hero_slide1_button_text = "Discover More"
        config.hero_slide1_button_link = "#about-us"
        config.hero_slide2_title = "Organic & Authentic"
        config.hero_slide2_subtitle = "The original kumudzi taste, straight from our fields"
        config.hero_slide2_button_text = "Our Products"
        config.hero_slide2_button_link = "#products"
        config.hero_slide3_title = "Quality Certified"
        config.hero_slide3_subtitle = "Pre-certified by Malawi Bureau of Standards"
        config.hero_slide3_button_text = "Our Certifications"
        config.hero_slide3_button_link = "#certifications"
        config.about_title = "About MAME Foods"
        config.about_subtitle = "Trusted indigenous brand providing authentic kumudzi taste"
        config.about_description = "MAME Foods is a producer and supplier of food stuffs in Malawi. We produce and pack one of the finest and most aromatic long grained rice in Malawi, flour, and different agricultural produce."
        config.about_bullet1 = "Pre-certified by the Malawi Bureau of Standards"
        config.about_bullet2 = "Substantial progress towards full certification"
        config.about_bullet3 = "All products in different phases of certification"
        config.about_closing = "Our drive is to give you quality organic food stuffs that maintain their original kumudzi taste at a good price."
        config.show_about_section = True
        config.show_products_section = True
        config.show_certifications_section = True
        config.products_section_title = "Our Products"
        config.products_section_subtitle = "Premium quality food products made with care"
        config.certifications_section_title = "Our Certifications"
        config.certifications_section_subtitle = "Quality assurance and standards compliance"
        config.contact_address_line1 = "MAME House"
        config.contact_address_line2 = "Plot 10/069, Luther Street"
        config.contact_city = "Area 10, Lilongwe"
        config.contact_postal = "P.O. Box 30632, Capital City, Lilongwe 3"
        config.contact_phone1 = "+265 999 950 489"
        config.contact_phone2 = "+265 888 123 456"
        config.contact_email1 = "info@mamefoods.mw"
        config.contact_email2 = "sales@mamefoods.mw"
        config.google_maps_embed_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3770.755798307342!2d33.76824441490085!3d-13.983324959861402!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMTPCsDU4JzU5LjkiUyAzM8KwNDYnMTUuNSJF!5e0!3m2!1sen!2smw!4v1651234567890!5m2!1sen!2smw"
        config.whatsapp_number = "+265999950489"
        config.whatsapp_message = "Hello MAME Foods! I'd like to know more about your products."
        config.facebook_url = "https://facebook.com/mamefoods"
        config.instagram_url = "https://instagram.com/mamefoods"
        config.linkedin_url = "https://linkedin.com/company/mamefoods"
        config.twitter_url = "https://twitter.com/mamefoods"
        config.footer_developer_text = "Developed by Pritech"
        config.footer_developer_url = "https://pritech.co.mw"
        config.save()
        self.stdout.write('Site configuration set.')

        # --- Product Categories ---
        rice_cat, _ = ProductCategory.objects.get_or_create(
            name="Premium Rice",
            defaults={"slug": "premium-rice", "icon_class": "bx bxs-bowl-rice", "display_order": 1}
        )
        flour_cat, _ = ProductCategory.objects.get_or_create(
            name="Quality Flour",
            defaults={"slug": "quality-flour", "icon_class": "bx bxs-baguette", "display_order": 2}
        )
        produce_cat, _ = ProductCategory.objects.get_or_create(
            name="Agricultural Produce",
            defaults={"slug": "agricultural-produce", "icon_class": "bx bxs-leaf", "display_order": 3}
        )
        self.stdout.write('Categories created.')

        # --- Products ---
        # Helper to download a placeholder image
        def get_placeholder_img(name, width=800, height=600):
            url = f"https://placehold.co/{width}x{height}?text={name.replace(' ', '+')}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    return ContentFile(response.content)
                else:
                    return None
            except Exception:
                return None

        # Rice product
        rice, created = Product.objects.get_or_create(
            slug="mame-super-aromatic-rice",
            defaults={
                "name": "MAME Super Aromatic Rice",
                "category": rice_cat,
                "description": "Our flagship long-grain rice, naturally aromatic with a distinct nutty flavour. Grown in the fertile wetlands of Malawi and hand-sorted for quality.",
                "detailed_description": "Experience the true taste of Malawi with MAME Super Aromatic Rice. Each grain is carefully processed to preserve its natural aroma and texture. Perfect for pilau, biryani, or simply steamed as a side.",
                "certification_status": "pre",
                "is_organic": True,
                "is_featured": True,
                "display_order": 1,
            }
        )
        if created:
            img = get_placeholder_img("Super Aromatic Rice")
            if img:
                ProductImage.objects.create(product=rice, image=ContentFile(img.read(), name="rice1.jpg"), is_primary=True, caption="Premium aromatic rice")
            ProductVariant.objects.create(product=rice, name="Small Pack", weight="1kg", price=2500.00, stock_quantity=100, sku="SAR-1KG")
            ProductVariant.objects.create(product=rice, name="Family Pack", weight="5kg", price=11000.00, stock_quantity=50, sku="SAR-5KG")
            ProductVariant.objects.create(product=rice, name="Bulk", weight="25kg", price=50000.00, stock_quantity=20, sku="SAR-25KG")
            self.stdout.write(f'Created product: {rice.name}')

        # Flour product
        flour, created = Product.objects.get_or_create(
            slug="mame-wholemeal-maize-flour",
            defaults={
                "name": "MAME Wholemeal Maize Flour",
                "category": flour_cat,
                "description": "Stone-ground maize flour, retaining all the natural goodness and fibre. Ideal for nsima, porridge, and baking.",
                "detailed_description": "Our maize is sourced from smallholder farmers in central Malawi, milled using traditional stone grinders to keep nutrients intact. No additives or preservatives.",
                "certification_status": "in_progress",
                "is_organic": True,
                "is_featured": True,
                "display_order": 2,
            }
        )
        if created:
            img = get_placeholder_img("Maize Flour")
            if img:
                ProductImage.objects.create(product=flour, image=ContentFile(img.read(), name="flour1.jpg"), is_primary=True, caption="Stone-ground maize flour")
            ProductVariant.objects.create(product=flour, name="Standard", weight="2kg", price=1800.00, stock_quantity=200, sku="WMF-2KG")
            ProductVariant.objects.create(product=flour, name="Large", weight="10kg", price=8000.00, stock_quantity=80, sku="WMF-10KG")
            self.stdout.write(f'Created product: {flour.name}')

        # Produce item
        produce, created = Product.objects.get_or_create(
            slug="mame-soya-beans",
            defaults={
                "name": "MAME Soya Beans",
                "category": produce_cat,
                "description": "High-protein soya beans, perfect for making soya milk, flour, or as a nutritious addition to meals.",
                "detailed_description": "Non-GMO soya beans grown in rotation with our rice paddies to enrich the soil. Rich in protein and essential amino acids.",
                "certification_status": "pre",
                "is_organic": True,
                "is_featured": True,
                "display_order": 3,
            }
        )
        if created:
            img = get_placeholder_img("Soya Beans")
            if img:
                ProductImage.objects.create(product=produce, image=ContentFile(img.read(), name="soya1.jpg"), is_primary=True, caption="High-protein soya beans")
            ProductVariant.objects.create(product=produce, name="Sack", weight="50kg", price=35000.00, stock_quantity=30, sku="SB-50KG")
            self.stdout.write(f'Created product: {produce.name}')

        # --- Team Members ---
        team_data = [
            {"name": "Grace Banda", "position": "Managing Director", "bio": "20 years in agribusiness, passionate about Malawian produce.", "image": get_placeholder_img("Grace", 300, 300)},
            {"name": "Peter Chirwa", "position": "Operations Manager", "bio": "Ensures quality from field to packaging.", "image": get_placeholder_img("Peter", 300, 300)},
            {"name": "Tiwo Mkandawire", "position": "Sales & Marketing Lead", "bio": "Connecting MAME products with families across Malawi.", "image": get_placeholder_img("Tiwo", 300, 300)},
            {"name": "Chifundo Phiri", "position": "Head of Quality Assurance", "bio": "Making sure every grain meets our high standards.", "image": get_placeholder_img("Chifundo", 300, 300)},
        ]
        for member in team_data:
            tm, created = TeamMember.objects.get_or_create(name=member["name"], defaults={"position": member["position"], "bio": member["bio"]})
            if created and member["image"]:
                tm.image.save(f'{member["name"].replace(" ", "_").lower()}.jpg', member["image"])
                tm.save()
        self.stdout.write('Team members created.')

        # --- Certifications ---
        cert_data = [
            {"name": "Malawi Bureau of Standards (MBS)", "logo": get_placeholder_img("MBS", 200, 100)},
            {"name": "Organic Certification (in progress)", "logo": get_placeholder_img("Organic", 200, 100)},
            {"name": "HACCP Compliant", "logo": get_placeholder_img("HACCP", 200, 100)},
            {"name": "ISO 22000 (pending)", "logo": get_placeholder_img("ISO", 200, 100)},
        ]
        for cert in cert_data:
            c, created = Certification.objects.get_or_create(name=cert["name"])
            if created and cert["logo"]:
                c.logo.save(f'{cert["name"].replace(" ", "_").lower()}.png', cert["logo"])
                c.save()
        self.stdout.write('Certifications added.')

        # --- Blog Categories & Tags ---
        blog_cat, _ = Category.objects.get_or_create(name="Company News", slug="company-news")
        tag1, _ = Tag.objects.get_or_create(name="Rice Farming", slug="rice-farming")
        tag2, _ = Tag.objects.get_or_create(name="Organic", slug="organic")
        tag3, _ = Tag.objects.get_or_create(name="Malawi", slug="malawi")

        # --- Blog Posts ---
        post1, created = BlogPost.objects.get_or_create(
            slug="the-journey-of-mame-foods",
            defaults={
                "title": "The Journey of MAME Foods: From Field to Fork",
                "content": "<p>Founded in 2015, MAME Foods started with a simple mission: bring quality Malawian produce to every household. Today we supply over 500 retailers nationwide.</p><p>Our rice is grown in the fertile soils of Karonga, where the unique climate gives it an exceptional aroma.</p>",
                "excerpt": "From humble beginnings to a trusted brand, discover how MAME Foods became a household name in Malawi.",
                "created_at": timezone.now(),
            }
        )
        if created:
            img = get_placeholder_img("Blog 1", 800, 400)
            if img:
                post1.featured_image.save("blog1.jpg", img)
            post1.categories.add(blog_cat)
            post1.tags.add(tag1, tag3)
            self.stdout.write(f'Created blog post: {post1.title}')

        post2, created = BlogPost.objects.get_or_create(
            slug="benefits-of-organic-rice",
            defaults={
                "title": "5 Reasons to Choose Organic Rice",
                "content": "<p>Organic rice is not just healthier, it supports sustainable farming. Here’s why you should make the switch.</p><ul><li>No chemical pesticides</li><li>Richer in nutrients</li><li>Better taste</li><li>Supports local farmers</li><li>Environmentally friendly</li></ul>",
                "excerpt": "Why organic rice is the smarter choice for your health and the planet.",
                "created_at": timezone.now(),
            }
        )
        if created:
            img = get_placeholder_img("Blog 2", 800, 400)
            if img:
                post2.featured_image.save("blog2.jpg", img)
            post2.categories.add(blog_cat)
            post2.tags.add(tag2)
            self.stdout.write(f'Created blog post: {post2.title}')

        self.stdout.write(self.style.SUCCESS('Dummy data loaded successfully!'))