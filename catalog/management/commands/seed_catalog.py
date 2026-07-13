from decimal import Decimal

from django.core.management.base import BaseCommand

from catalog.models import Brand, Category, Course, PortfolioProject, Product, Review, Service
from sitecontent.models import MediaAsset, RequestFormOptionSet, SiteSetting, SocialLink


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


BRANDS = [
    {"slug": "danajet-booklab", "name": "BookLab", "code": "DL", "summary": "Book design, formatting & publishing", "href": "/request-project", "icon": "book-open"},
    {"slug": "danajet-media", "name": "Media", "code": "DM", "summary": "Storytelling, YouTube & content", "href": "/request-project", "icon": "play"},
    {"slug": "danajet-academy", "name": "Academy", "code": "DA", "summary": "Courses & learning resources", "href": "/courses", "icon": "layers"},
    {"slug": "danajet-transport", "name": "Transport", "code": "DT", "summary": "A future-facing transport vision", "href": "/transport", "icon": "plane"},
]


SERVICES = [
    {"slug": "print-book-formatting", "title": "Print Book Formatting", "summary": "Beautiful, readable interiors ready for print.", "icon": "file-text"},
    {"slug": "kindle-epub-formatting", "title": "Kindle EPUB Formatting", "summary": "Responsive ebooks built for smooth reading.", "icon": "book-copy"},
    {"slug": "childrens-book-design", "title": "Children's Book Design", "summary": "Playful layouts that support every illustration.", "icon": "palette"},
    {"slug": "workbook-design", "title": "Workbook Design", "summary": "Clear, engaging pages made for active learning.", "icon": "layers"},
    {"slug": "kdp-upload-support", "title": "KDP Upload Support", "summary": "Careful checks and guidance through publishing.", "icon": "package-check"},
    {"slug": "full-book-creation-support", "title": "Full Book Creation Support", "summary": "Joined-up support from your first idea onward.", "icon": "sparkles"},
]


PORTFOLIO_PROJECTS = [
    ("children", "The Ultimate Tanzania Activity Book", "03"),
    ("children", "Mindfulness Coloring Book", "04"),
    ("children", "The Ultimate Senegal Activity Book", "05"),
    ("children", "Pawtastic Dog Breed Word Search", "06"),
    ("children", "The Ultimate Ghana Activity Book", "07"),
    ("children", "Anxiety Relief Coloring Book", "08"),
    ("children", "Adulting Coloring Book", "09"),
    ("children", "The Ultimate South Africa Activity Book", "10"),
    ("children", "Super Cool Facts for Smart Kids", "11"),
    ("covers", "Children's Book Cover Collection", "13"),
    ("covers", "Wellness & Lifestyle Cover Collection", "14"),
    ("covers", "Contemporary Romance Cover Collection", "15"),
    ("covers", "Thriller & Mystery Cover Collection", "16"),
    ("covers", "Activity Book Cover Collection", "17"),
    ("covers", "Romance Cover Collection", "18"),
    ("covers", "Educational Cover Collection", "19"),
    ("epub", "Kindle Fire E-reader Preview", "21"),
    ("epub", "Kindle Tablet EPUB Preview", "22"),
    ("epub", "Kindle Mobile EPUB Preview", "23"),
    ("workbooks", "The Voice of Forgiveness Journal", "25"),
    ("workbooks", "Manifest Your Dream Life Workbook", "26"),
    ("workbooks", "Social Emotional Learning Workbook", "27"),
    ("workbooks", "Journey Better Workbook", "28"),
    ("aplus", "Start Growing Gracefully", "30"),
    ("aplus", "Gods, Monsters, and Heroes", "31"),
    ("aplus", "The Ultimate Ghana Activity Book", "32"),
    ("aplus", "A Perfect Wedding", "33"),
    ("aplus", "Pawtastic Dog Breed", "34"),
    ("aplus", "Anxiety Relief Coloring Book", "35"),
    ("aplus", "Unlocking the Heavens", "36"),
    ("aplus", "The Ultimate Tanzania Activity Book", "37"),
    ("interiors", "Why We Get Cancer", "39"),
    ("interiors", "The Rise of Revenge", "40"),
    ("interiors", "Inspiring Soccer Stories for Kids", "41"),
    ("interiors", "Interesting Facts & Myths", "42"),
    ("interiors", "3D: The Power of Your Spirit", "43"),
    ("pdf", "Dubai Real Estate Guide", "45"),
    ("pdf", "Construction Company Profile", "46"),
]


REVIEWS = [
    {
        "slug": "richard-bass",
        "name": "Richard Bass",
        "role": "Amazon Bestselling Educational Author",
        "service": "amazon",
        "project": "Educational book project",
        "cta_label": "View on Amazon",
        "cta_url": "https://a.co/d/0bznxH3L",
        "image": "/assets/reviews/richard-bass.jpg",
    },
    {
        "slug": "jesi-washington",
        "name": "Jesi Washington",
        "role": "Education Professional",
        "service": "canva",
        "project": "Education design project",
        "cta_label": "View on Canva",
        "cta_url": "https://canva.link/3oggxou00to7ds8",
        "image": "/assets/reviews/jesi-washington.jpg",
    },
    {
        "slug": "crystal-jones",
        "name": "Crystal Jones",
        "role": "Recipe Books Author",
        "service": "amazon",
        "project": "Recipe book project",
        "cta_label": "View on Amazon",
        "cta_url": "https://a.co/d/0aVn71TB",
        "image": "/assets/reviews/crystal-jones.jpg",
    },
    {
        "slug": "jimmy-sweeney",
        "name": "Jimmy Sweeney",
        "role": "Author",
        "service": "amazon",
        "project": "Book project",
        "cta_label": "View on Amazon",
        "cta_url": "",
        "image": "",
    },
    {
        "slug": "natasha-noel",
        "name": "Natasha Noel",
        "role": "Founder, Faith Work Production",
        "service": "amazon",
        "project": "Book project",
        "cta_label": "View on Amazon",
        "cta_url": "",
        "image": "/assets/reviews/natasha-noel.jpg",
    },
    {
        "slug": "tangie-cokes",
        "name": "Tangie Cokes",
        "role": "Children's Book Author",
        "service": "amazon",
        "project": "Children's book project",
        "cta_label": "View on Amazon",
        "cta_url": "https://a.co/d/04GeWzMr",
        "image": "/assets/reviews/tangie-cokes.jpg",
    },
]


REVIEW_QUOTE = (
    "He is very skilled. I had a very pleased experience working with him, and as long you convey your idea to him "
    "and send him examples of what you are looking for, he will do an awesome job."
)


FEATURED_WORK_HIGHLIGHTS = [
    {"id": "featured-highlight-0", "title": "MISA Educational Series", "imageUrl": ""},
    {"id": "featured-highlight-1", "title": "Tangie's Children's Books", "imageUrl": ""},
    {"id": "featured-highlight-2", "title": "Ricardo's Amazon Bestselling Educational Books", "imageUrl": ""},
    {"id": "featured-highlight-3", "title": "Jimmy's Sports Betting Book", "imageUrl": ""},
    {"id": "featured-highlight-4", "title": "NLS Rwanda Educational Materials", "imageUrl": ""},
]


ABOUT_SETTINGS = {
    "founderRole": "Founder and Creative Lead",
    "founderName": "Daniel - Ajetunmobi",
    "founderTagline": "Helping authors, learners, and creative brands turn ideas into polished work.",
    "intro": "I'm Daniel, the founder and creative mind behind Danajet. My work brings together book design, publishing support, storytelling, education, and long-term innovation under one clear creative vision.",
    "journey": "My journey started with a passion for creativity, storytelling, and helping ideas come to life. The name \"Danajet\" was born by combining \"Dan\" from my first name, Daniel, and \"Ajet\" from my surname, Ajetunmobi. More than just a name, it represents my belief that great ideas deserve the opportunity to take flight. What began as a love for designing and creating has grown into a brand dedicated to helping authors transform their manuscripts into professional, publish-ready books.",
    "ecosystem": "Danajet is more than one service. It is a growing ecosystem for creativity, education, media, and future innovation, with each part created to help people present their work with more confidence and clarity.",
    "beliefTitle": "Core belief",
    "beliefText": "Great ideas deserve to be seen, experienced, and shared with the world.",
    "invitation": "Whether you're an author with a manuscript waiting to become a beautiful book, a learner seeking new skills, or a reader exploring my creations, I invite you to be part of the Danajet journey.",
    "video": "/assets/about-brand-intro.mp4",
}


CONTACT_SETTINGS = {
    "email": "hello@danajet.com",
    "whatsapp": "+1 000 000 0000",
    "businessHours": "Monday - Friday, 9:00 AM - 5:00 PM",
    "location": "Remote, serving authors worldwide",
    "youtube": "#youtube",
    "instagram": "#instagram",
    "tiktok": "#tiktok",
    "linkedin": "#linkedin",
    "footerCopy": "Helping authors create, publish, and share professional books while building educational resources, creative media, and future innovations.",
}


REQUEST_FORM_OPTIONS = {
    "services": [
        "Interior Book Formatting", "Children's Book Design", "Book Cover Design", "Front & Back Cover Design",
        "PDF Design & Layout", "Kindle eBook Formatting", "Hardcover Formatting", "Paperback Formatting",
        "Workbook Design", "A+ Content Design", "Promotional Book Trailer", "Publishing Assistance",
        "Full Book Creation", "Other (Please specify)",
    ],
    "stages": [
        "I only have an idea", "My manuscript is in progress", "My manuscript is complete",
        "My book has already been published and needs updates", "I need help publishing my book",
    ],
    "sizes": ["5 x 8 inches", "5.5 x 8.5 inches", "6 x 9 inches", "8 x 10 inches", "8.5 x 8.5 inches", "8.5 x 11 inches", "Other (Please specify)"],
    "budgets": ["Under $1,000", "$1,000 - $5,000", "$5,000 - $10,000", "Above $10,000"],
    "timelines": ["ASAP", "Within 1 week", "Within 2-4 weeks", "1-3 months", "Flexible"],
    "referrals": ["Google Search", "Amazon Books", "YouTube", "Tiktok", "Facebook", "Referral", "Previous Client", "Other"],
    "successMessage": ["Your Book Is Ready for Takeoff!", "", "Welcome aboard the Danajet BookLab journey.", "", "Thank you for submitting your project request. I will personally review your details and contact you through your preferred method shortly.", "", "Let's make your book soar!"],
    "confidentiality": ["Your manuscript and project details will be treated with complete confidentiality and will never be shared with third parties."],
}


MEDIA_ASSETS = [
    {"slug": "hero-cutout", "title": "Hero cutout", "asset_type": "image", "external_url": "/assets/hero-books-cutout.png", "usage": "Homepage hero"},
    {"slug": "danajet-about-intro-video", "title": "Danajet about intro video", "asset_type": "video", "external_url": "/assets/about-brand-intro.mp4", "usage": "About page video placeholder"},
    {"slug": "sticker-tile", "title": "Sticker tile", "asset_type": "image", "external_url": "/assets/sticker.png", "usage": "Brand section background"},
    {"slug": "reviewer-headshots", "title": "Reviewer headshots", "asset_type": "folder", "external_url": "/assets/reviews/", "usage": "Reviews"},
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

    def add_arguments(self, parser):
        parser.add_argument(
            "--only-empty",
            action="store_true",
            help="Only seed a content area when its database table is empty.",
        )

    def handle(self, *args, **options):
        only_empty = options["only_empty"]
        categories = {}
        if self.should_seed(Category, only_empty):
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
        else:
            categories = {category.slug: category for category in Category.objects.all()}

        if self.should_seed(Product, only_empty):
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

        if self.should_seed(Course, only_empty):
            course_order = 0
            for category_title, category_slug, titles in COURSE_GROUPS:
                category_ref = categories.get(category_slug)
                for raw_title in titles:
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

        if self.should_seed(Brand, only_empty):
            for index, item in enumerate(BRANDS):
                Brand.objects.update_or_create(
                    slug=item["slug"],
                    defaults={
                        "name": item["name"],
                        "code": item["code"],
                        "summary": item["summary"],
                        "href": item["href"],
                        "icon": item["icon"],
                        "display_order": index,
                        "is_published": True,
                    },
                )

        if self.should_seed(Service, only_empty):
            for index, item in enumerate(SERVICES):
                Service.objects.update_or_create(
                    slug=item["slug"],
                    defaults={
                        "title": item["title"],
                        "summary": item["summary"],
                        "icon": item["icon"],
                        "display_order": index,
                        "is_published": True,
                    },
                )

        if self.should_seed(PortfolioProject, only_empty):
            for index, (category, title, image) in enumerate(PORTFOLIO_PROJECTS):
                PortfolioProject.objects.update_or_create(
                    slug=self.slug_from_title(title),
                    defaults={
                        "title": title,
                        "summary": f"{title} portfolio presentation.",
                        "category": category,
                        "featured": index < 5,
                        "display_order": index,
                        "is_published": True,
                        "images": [f"/assets/portfolio/page-{image}.jpg"],
                        "metadata": {"image": image, "imageUrl": f"/assets/portfolio/page-{image}.jpg"},
                    },
                )

        if self.should_seed(Review, only_empty):
            for index, item in enumerate(REVIEWS):
                Review.objects.update_or_create(
                    slug=item["slug"],
                    defaults={
                        "title": item["name"],
                        "reviewer_name": item["name"],
                        "reviewer_role": item["role"],
                        "quote": REVIEW_QUOTE if item["name"] != "Tangie Cokes" else "He's my go-to guy! Thank you so much for always helping me bring out the best in my books. Thank you for supporting me from beginning to end!",
                        "rating": 5,
                        "project": item["project"],
                        "service": item["service"],
                        "source": item["service"],
                        "cta_label": item["cta_label"],
                        "cta_url": item["cta_url"],
                        "featured": index < 3,
                        "display_order": index,
                        "is_published": True,
                        "metadata": {"image": item["image"]},
                    },
                )

        if self.should_seed(MediaAsset, only_empty):
            for item in MEDIA_ASSETS:
                MediaAsset.objects.update_or_create(slug=item["slug"], defaults=item)

        if self.should_seed(SocialLink, only_empty):
            for index, platform in enumerate(["youtube", "instagram", "facebook", "linkedin", "tiktok"]):
                SocialLink.objects.update_or_create(
                    platform=platform,
                    defaults={"url": f"#{platform}", "icon": platform, "display_order": index, "is_visible": True},
                )

        if self.should_seed(SiteSetting, only_empty):
            for key, value in ABOUT_SETTINGS.items():
                self.save_setting(f"about-page-{key}", value, f"About page: {key}", "about-page")
            for key, value in CONTACT_SETTINGS.items():
                self.save_setting(f"contact-footer-{key}", value, f"Contact footer: {key}", "contact-footer")
            for key, values in REQUEST_FORM_OPTIONS.items():
                self.save_setting(f"request-form-{key}", "\n".join(values), f"Request form: {key}", "request-form")
            self.save_setting(
                "collection-featured-highlights",
                "",
                "Featured work highlights collection",
                "collection",
                FEATURED_WORK_HIGHLIGHTS,
            )

        if self.should_seed(RequestFormOptionSet, only_empty):
            for index, (key, values) in enumerate(REQUEST_FORM_OPTIONS.items()):
                RequestFormOptionSet.objects.update_or_create(
                    key=key,
                    defaults={
                        "label": key.replace("-", " ").replace("_", " ").title(),
                        "options": values,
                        "display_order": index,
                        "is_active": True,
                    },
                )

        self.stdout.write(self.style.SUCCESS("Seeded Danajet starter backend content."))

    def should_seed(self, model, only_empty):
        return not only_empty or not model.objects.exists()

    def slug_from_title(self, title):
        slug = title.lower().replace("&", "and")
        slug = "".join(char if char.isalnum() else "-" for char in slug)
        return "-".join(part for part in slug.split("-") if part)

    def save_setting(self, key, value, label, group, value_json=None):
        SiteSetting.objects.update_or_create(
            key=key,
            defaults={
                "label": label,
                "value": value,
                "value_json": value_json if value_json is not None else {},
                "group": group,
                "is_public": True,
            },
        )
