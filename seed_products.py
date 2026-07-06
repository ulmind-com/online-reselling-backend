import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from urllib.parse import urlparse
import random

from app.core.config import settings
from app.models.product import Product, ProductFile
from app.models.category import Category

async def seed_data():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    parsed_uri = urlparse(settings.MONGODB_URI)
    db_name = parsed_uri.path.lstrip('/') or "lumina"
    
    await init_beanie(database=client[db_name], document_models=[Product, Category])
    
    print("Clearing existing products and categories...")
    await Product.delete_all()
    await Category.delete_all()
    
    print("Creating Categories...")
    cats = [
        Category(name="Courses", slug="courses", description="High quality video courses"),
        Category(name="Templates", slug="templates", description="Premium editing templates"),
        Category(name="Digital Products", slug="digital-products", description="E-books and guides")
    ]
    await Category.insert_many(cats)
    
    courses_id = cats[0].id
    templates_id = cats[1].id
    digital_id = cats[2].id

    print("Creating Products...")
    products = [
        Product(
            title="Make Money Online for Editors",
            slug="make-money-online-editors",
            short_description="The ultimate blueprint to scaling your editing business.",
            full_description="<p>Stop editing for peanuts on Fiverr. Learn the exact systems to land high-paying clients...</p>",
            price=199.0,
            sale_price=99.0,
            category_id=courses_id,
            status="published",
            is_featured=True,
            is_bestseller=True,
            tags=["business", "editing", "freelance"],
            affiliate_enabled=True,
            commission_percentage=20.0,
            thumbnail_url="https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=800&q=80",
            features=["10+ Hours of Video", "Client Outreach Templates", "Discord Access"]
        ),
        Product(
            title="Beginner Editing Masterclass",
            slug="beginner-editing-masterclass",
            short_description="Start your video editing journey here.",
            full_description="<p>A complete beginner guide to Premiere Pro and DaVinci Resolve.</p>",
            price=49.0,
            category_id=courses_id,
            status="published",
            is_new=True,
            thumbnail_url="https://images.unsplash.com/photo-1601506521937-0121a7fc2a6b?w=800&q=80"
        ),
        Product(
            title="Premium Editing Templates Pack",
            slug="premium-editing-templates-pack",
            short_description="100+ drag and drop templates for faster editing.",
            full_description="<p>Save hours of time with these pre-made transitions, LUTs, and sound effects.</p>",
            price=29.0,
            category_id=templates_id,
            status="published",
            is_bestseller=True,
            thumbnail_url="https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&q=80"
        ),
        Product(
            title="Viral Reels Editing Course",
            slug="viral-reels-editing",
            short_description="Master the art of short-form content.",
            full_description="<p>Learn exactly how to edit TikToks, Shorts, and Reels that get millions of views.</p>",
            price=149.0,
            category_id=courses_id,
            status="published",
            thumbnail_url="https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=800&q=80"
        ),
        Product(
            title="AI Video Editing Toolkit",
            slug="ai-video-editing",
            short_description="Leverage AI to edit 10x faster.",
            full_description="<p>Discover the secret AI tools top editors use to automate the boring stuff.</p>",
            price=79.0,
            category_id=digital_id,
            status="published",
            is_new=True,
            thumbnail_url="https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80"
        ),
        Product(
            title="Freelancing Blueprint",
            slug="freelancing-blueprint",
            short_description="How to price your work and get paid.",
            full_description="<p>Contracts, invoicing, and negotiation tactics for freelancers.</p>",
            price=59.0,
            category_id=digital_id,
            status="published",
            thumbnail_url="https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80"
        ),
        Product(
            title="Social Media Growth Course",
            slug="social-media-growth",
            short_description="Grow your own personal brand.",
            full_description="<p>How editors can leverage Twitter and Instagram to get inbound leads.</p>",
            price=99.0,
            category_id=courses_id,
            status="published",
            thumbnail_url="https://images.unsplash.com/photo-1611926653458-09294b3142bf?w=800&q=80"
        ),
        Product(
            title="Content Creator Bundle",
            slug="content-creator-bundle",
            short_description="Everything you need in one pack.",
            full_description="<p>Templates, overlays, LUTs, and SFX.</p>",
            price=199.0,
            sale_price=149.0,
            category_id=templates_id,
            status="published",
            thumbnail_url="https://images.unsplash.com/photo-1536240478700-b869070f9279?w=800&q=80"
        ),
        Product(
            title="CapCut Pro Workflow",
            slug="capcut-pro-workflow",
            short_description="Master the mobile and desktop app.",
            full_description="<p>Advanced techniques for CapCut.</p>",
            price=39.0,
            category_id=courses_id,
            status="published",
            thumbnail_url="https://images.unsplash.com/photo-1526628953301-3e589a6a8b74?w=800&q=80"
        ),
        Product(
            title="Advanced Client Acquisition Guide",
            slug="advanced-client-acquisition",
            short_description="Cold email and DMs that convert.",
            full_description="<p>Scripts and strategies to sign $5k/mo retainers.</p>",
            price=89.0,
            category_id=digital_id,
            status="published",
            thumbnail_url="https://images.unsplash.com/photo-1553877522-43269d4ea984?w=800&q=80"
        )
    ]
    
    await Product.insert_many(products)
    print("Database seeded successfully with 10 products and 3 categories!")

if __name__ == "__main__":
    asyncio.run(seed_data())
