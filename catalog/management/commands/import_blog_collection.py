from datetime import timedelta
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.text import slugify

from catalog.models import BlogPost, Category


POSTS = [
    ("Claude vs. Codex: Which AI Tool Is Better for Automated Video Creation?", "AI & Creative Technology"),
    ("Adobe InDesign vs. Canva: Which Is Better for Professional Book Formatting?", "Book Design"),
    ("Adobe Illustrator vs. Canva: Which Is Better for Book Covers and Illustrations?", "Book Design"),
    ("Amazon KDP vs. IngramSpark: Which Publishing Platform Is Better for Independent Authors?", "Publishing"),
    ("AI-Generated Illustrations vs. Human Illustrators: Which Should Authors Choose?", "AI & Creative Technology"),
    ("Paperback, Hardcover, or Kindle: Which Book Format Should You Publish First?", "Publishing"),
    ("7 Book Formatting Mistakes That Can Ruin Your Amazon KDP Print Quality", "Book Formatting"),
]


class Command(BaseCommand):
    help = "Import the Danajet blog content collection from a UTF-8 text file."

    def add_arguments(self, parser):
        parser.add_argument("source", help="Path to the Danajet blog collection text file")

    def handle(self, *args, **options):
        source = Path(options["source"])
        if not source.exists():
            raise CommandError(f"Blog collection not found: {source}")

        text = source.read_text(encoding="utf-8").replace("\r\n", "\n")
        markers = []
        for index, (title, category_name) in enumerate(POSTS, start=1):
            marker = f"\n{index}. {title.upper()}\n"
            position = text.find(marker)
            if position < 0:
                raise CommandError(f"Could not locate article heading: {title}")
            markers.append((position, len(marker), title, category_name))

        created_count = 0
        updated_count = 0
        for index, (position, marker_length, title, category_name) in enumerate(markers):
            end = markers[index + 1][0] if index + 1 < len(markers) else len(text)
            content = text[position + marker_length:end].strip()
            first_paragraph = content.split("\n\n", 1)[0].strip()
            excerpt = first_paragraph[:420].rsplit(" ", 1)[0] + ("…" if len(first_paragraph) > 420 else "")
            category, _ = Category.objects.get_or_create(
                slug=slugify(category_name),
                defaults={"name": category_name, "category_type": "blog", "is_visible": True, "display_order": index},
            )
            word_count = len(content.split())
            post, created = BlogPost.objects.update_or_create(
                slug=slugify(title),
                defaults={
                    "title": title,
                    "summary": excerpt,
                    "excerpt": excerpt,
                    "author": "Danajet",
                    "published_at": timezone.now() - timedelta(days=index),
                    "content": content,
                    "tags": category_name,
                    "category_ref": category,
                    "read_time": f"{max(4, round(word_count / 200))} min read",
                    "display_order": index,
                    "is_published": True,
                    "metadata": {"source": "Danajet Blog Content Collection", "research_checked": "July 2026"},
                },
            )
            created_count += int(created)
            updated_count += int(not created)
            self.stdout.write(f"{'Created' if created else 'Updated'}: {post.title}")

        self.stdout.write(self.style.SUCCESS(f"Imported {created_count} new and updated {updated_count} existing blog posts."))
