from decimal import Decimal

from django.core.management.base import BaseCommand

from catalog.models import Category, Course, Product


SHOP_CATEGORIES = [
    {"name": "Adult Books", "slug": "adult", "category_type": "product", "description": "Books, journals, guides, and workbooks for adult readers."},
    {"name": "Children's Book", "slug": "childrens", "category_type": "product", "description": "Children's stories and learning resources."},
    {"name": "Storytelling", "slug": "storytelling", "category_type": "product", "description": "Story-rich books and creative guides."},
    {"name": "Book Design & Publishing", "slug": "book-design-publishing", "category_type": "course"},
    {"name": "Masterclasses", "slug": "masterclasses", "category_type": "course"},
    {"name": "Content & Marketing", "slug": "content-marketing", "category_type": "course"},
    {"name": "Premium Services", "slug": "premium-services", "category_type": "course"},
    {"name": "Templates & Resources", "slug": "templates-resources", "category_type": "course"},
]


PRODUCTS = [
    {
        "slug": "little-wings-big-dreams",
        "title": "Little Wings, Big Dreams",
        "subtitle": "A bright story about finding your own way",
        "category": "childrens",
        "filter_categories": ["childrens", "storytelling"],
        "category_label": "Children's book",
        "author": "Dana A.",
        "price": "14.99",
        "rating": "4.9",
        "review_count": 18,
        "inventory": 24,
        "badge": "Bestseller",
        "cover": "sky",
        "accent": "#ef5b4f",
        "featured": True,
        "summary": "A warm, encouraging picture book for young readers learning to trust their ideas, use their voice, and take brave first steps.",
        "features": ["32 full-color pages", "Ages 4-8", "8.5 x 8.5 inch paperback", "Printed on premium matte paper"],
    },
    {
        "slug": "a-better-week",
        "title": "A Better Week",
        "subtitle": "A practical workbook for calmer, clearer days",
        "category": "workbooks",
        "filter_categories": ["adult"],
        "category_label": "Workbook",
        "author": "Danajet BookLab",
        "price": "18.00",
        "compare_at_price": "22.00",
        "rating": "4.8",
        "review_count": 12,
        "inventory": 16,
        "badge": "Sale",
        "cover": "cream",
        "accent": "#0c7777",
        "featured": True,
        "summary": "A guided weekly planning workbook that turns priorities, reflection, and realistic routines into a calmer rhythm you can keep.",
        "features": ["12 weeks of guided planning", "Weekly reflection pages", "Undated format", "Large 8 x 10 inch pages"],
    },
    {
        "slug": "beyond-the-horizon",
        "title": "Beyond the Horizon",
        "subtitle": "A practical guide to courageous new beginnings",
        "category": "guides",
        "filter_categories": ["adult"],
        "category_label": "Personal growth",
        "author": "Dana A.",
        "price": "16.50",
        "rating": "5.0",
        "review_count": 9,
        "inventory": 30,
        "badge": "New",
        "cover": "orange",
        "accent": "#000000",
        "featured": True,
        "summary": "A clear, grounded guide for moving through uncertainty, rebuilding confidence, and making meaningful progress one decision at a time.",
        "features": ["Practical reflection prompts", "Action-focused chapters", "Reader exercises", "6 x 9 inch paperback"],
    },
    {
        "slug": "the-quiet-idea",
        "title": "The Quiet Idea",
        "subtitle": "How small thoughts become meaningful work",
        "category": "guides",
        "filter_categories": ["adult", "storytelling"],
        "category_label": "Creative guide",
        "author": "M. Cole",
        "price": "15.00",
        "rating": "4.7",
        "review_count": 7,
        "inventory": 11,
        "cover": "teal",
        "accent": "#f5c84c",
        "summary": "An inviting guide for creatives who want to protect fragile ideas, build a steady practice, and finish work that matters.",
        "features": ["Creative prompts", "Project planning pages", "Gentle productivity tools", "6 x 9 inch paperback"],
    },
    {
        "slug": "built-to-bloom",
        "title": "Built to Bloom",
        "subtitle": "A workbook for purposeful personal growth",
        "category": "workbooks",
        "filter_categories": ["adult"],
        "category_label": "Workbook",
        "author": "R. James",
        "price": "19.50",
        "rating": "4.9",
        "review_count": 21,
        "inventory": 20,
        "badge": "Popular",
        "cover": "coral",
        "accent": "#111111",
        "featured": True,
        "summary": "A thoughtful workbook for understanding where you are, defining what matters, and growing with more intention.",
        "features": ["Guided self-assessments", "Goal mapping exercises", "Monthly checkpoints", "Premium workbook paper"],
    },
    {
        "slug": "notes-to-my-future-self",
        "title": "Notes to My Future Self",
        "subtitle": "A journal for honest reflection and hopeful plans",
        "category": "journals",
        "filter_categories": ["adult"],
        "category_label": "Guided journal",
        "author": "Danajet BookLab",
        "price": "13.99",
        "rating": "4.8",
        "review_count": 14,
        "inventory": 28,
        "cover": "black",
        "accent": "#ff8200",
        "summary": "A spacious guided journal filled with meaningful prompts for recording lessons, hopes, and letters to the person you are becoming.",
        "features": ["120 guided pages", "Lay-flat binding", "Reflection prompts", "Gift-ready paperback"],
    },
    {
        "slug": "milo-finds-his-voice",
        "title": "Milo Finds His Voice",
        "subtitle": "A playful story about courage and belonging",
        "category": "childrens",
        "filter_categories": ["childrens", "storytelling"],
        "category_label": "Children's book",
        "author": "T. Green",
        "price": "14.50",
        "rating": "5.0",
        "review_count": 16,
        "inventory": 18,
        "badge": "Staff pick",
        "cover": "yellow",
        "accent": "#dc503d",
        "featured": True,
        "summary": "Milo has plenty to say, but the words disappear when everyone is listening. A kind story about confidence, friendship, and being heard.",
        "features": ["36 illustrated pages", "Ages 5-9", "Discussion prompts", "8.5 x 8.5 inch paperback"],
    },
    {
        "slug": "leading-light",
        "title": "Leading Light",
        "subtitle": "Create impact with clarity and confidence",
        "category": "guides",
        "filter_categories": ["adult"],
        "category_label": "Leadership",
        "author": "N. Okafor",
        "price": "17.99",
        "rating": "4.8",
        "review_count": 11,
        "inventory": 14,
        "cover": "navy",
        "accent": "#ff8200",
        "summary": "A practical leadership book for communicating clearly, making grounded decisions, and building trust without losing your voice.",
        "features": ["Leadership frameworks", "Real-world exercises", "Team reflection prompts", "6 x 9 inch paperback"],
    },
]


COURSE_GROUPS = [
    ("Book Design & Publishing", "book-design-publishing", [
        "Book Idea Blueprint (How I Generate Winning Book Ideas)",
        "EPUB Made Easy (Convert Any Book into a Clickable EPUB)",
        "ChatGPT for Book Creators (Getting Better Results for Design & Publishing)",
        "A+ Content Secrets (Designing High-Converting Amazon A+ Content)",
        "KDP Error Fixer (Solving Common Amazon Publishing Problems)",
        "KDP Compliance Guide (Understanding Amazon's Publishing Requirements)",
        "Perfect Margins (Preparing Books for Print & Publication)",
        "Book Design in Canva (Creating Professional Book Interiors)",
        "The Danajet Design Process (My Complete Book Creation Workflow)",
        "Children's Book Blueprint (From Idea to Published Book)",
    ]),
    ("Masterclasses", "masterclasses", [
        "Paperback & Kindle Formatting Masterclass",
        "Canva Book Design Masterclass",
        "Amazon KDP Publishing Masterclass",
    ]),
    ("Content & Marketing", "content-marketing", [
        "Book Trailer Studio (Creating Promotional Book Trailers)",
        "Storytelling Video Editing (TikTok & YouTube for Authors)",
        "Flyer Design System (My Method for Designing Social Media Graphics)",
        "Cover Design Masterclass (Designing Front & Back Covers That Sell)",
    ]),
    ("Premium Services", "premium-services", [
        "Publish With Me (Live Book Formatting & Publishing Support)",
    ]),
    ("Templates & Resources", "templates-resources", [
        "Book Interior Layout Templates",
        "KDP Publishing Checklist",
        "A+ Content Planning Template",
        "Book Launch Planner",
        "Children's Book Planning Workbook",
    ]),
]


def split_course_title(raw_title):
    if "(" not in raw_title or not raw_title.endswith(")"):
        return raw_title, ""
    title, subtitle = raw_title.rsplit("(", 1)
    return title.strip(), subtitle[:-1].strip()


class Command(BaseCommand):
    help = "Seed Danajet starter shop products and academy courses."

    def handle(self, *args, **options):
        categories = {}
        for index, item in enumerate(SHOP_CATEGORIES):
            category, _ = Category.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "name": item["name"],
                    "category_type": item["category_type"],
                    "description": item.get("description", ""),
                    "display_order": index,
                    "is_visible": True,
                },
            )
            categories[item["slug"]] = category

        for index, item in enumerate(PRODUCTS):
            category_ref = categories.get(item["filter_categories"][0])
            Product.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "subtitle": item["subtitle"],
                    "summary": item["summary"],
                    "category": item["category"],
                    "category_ref": category_ref,
                    "author": item["author"],
                    "price": Decimal(item["price"]),
                    "compare_at_price": Decimal(item["compare_at_price"]) if item.get("compare_at_price") else None,
                    "rating": Decimal(item["rating"]),
                    "review_count": item["review_count"],
                    "inventory": item["inventory"],
                    "featured": item.get("featured", False),
                    "features": item["features"],
                    "display_order": index,
                    "is_published": True,
                    "metadata": {
                        "badge": item.get("badge"),
                        "cover": item["cover"],
                        "accent": item["accent"],
                        "filter_categories": item["filter_categories"],
                        "category_label": item["category_label"],
                        "currency": "USD",
                    },
                },
            )

        course_order = 0
        for category_title, category_slug, titles in COURSE_GROUPS:
            category_ref = categories[category_slug]
            for item_index, raw_title in enumerate(titles):
                title, subtitle = split_course_title(raw_title)
                slug = raw_title.lower().replace("&", "and")
                slug = "".join(char if char.isalnum() else "-" for char in slug)
                slug = "-".join(part for part in slug.split("-") if part)
                price = Decimal("9.00") if "chatgpt" in raw_title.lower() else Decimal("7.00")
                Course.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "title": title,
                        "subtitle": subtitle or category_title,
                        "summary": subtitle or f"{category_title} course from Danajet Academy.",
                        "category": category_title,
                        "category_ref": category_ref,
                        "price": price,
                        "status": "Coming Soon",
                        "video_url": "/assets/Course_one.mp4" if course_order == 0 else "",
                        "featured": course_order < 6,
                        "display_order": course_order,
                        "is_published": True,
                        "metadata": {
                            "raw_title": raw_title,
                            "rating": "5.0" if "chatgpt" in raw_title.lower() else "4.9",
                            "compare_at_price": "49.00",
                            "category_icon": category_slug,
                        },
                    },
                )
                course_order += 1

        self.stdout.write(self.style.SUCCESS("Seeded Danajet catalog products and courses."))
