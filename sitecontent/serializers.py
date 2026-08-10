from pathlib import Path
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageOps, UnidentifiedImageError
from rest_framework import serializers

from .models import CallToAction, MediaAsset, NavigationItem, PageSection, RequestFormOptionSet, SiteSetting, SocialLink


def is_image_upload(file_obj):
    content_type = getattr(file_obj, "content_type", "")
    return content_type.startswith("image/")


DANGEROUS_UPLOAD_EXTENSIONS = (".svg", ".html", ".htm", ".xhtml", ".mhtml", ".js", ".mjs", ".php", ".phtml")
DANGEROUS_UPLOAD_CONTENT_TYPES = (
    "text/html",
    "application/xhtml+xml",
    "image/svg+xml",
    "application/javascript",
    "text/javascript",
)


def reject_dangerous_upload(file_obj):
    """Block script-capable file types (SVG, HTML, JS, ...) regardless of the
    asset type the upload is attached to. The client-supplied content type is
    not trustworthy on its own, so this also checks the filename extension."""
    if not file_obj:
        return
    name = str(getattr(file_obj, "name", "")).lower()
    content_type = getattr(file_obj, "content_type", "").lower()
    if name.endswith(DANGEROUS_UPLOAD_EXTENSIONS) or content_type in DANGEROUS_UPLOAD_CONTENT_TYPES:
        raise serializers.ValidationError("This file type is not allowed for security reasons.")


def optimize_image_upload(file_obj):
    if not file_obj or not is_image_upload(file_obj):
        return file_obj

    try:
        file_obj.seek(0)
        image = Image.open(file_obj)
        image = ImageOps.exif_transpose(image)
    except (UnidentifiedImageError, OSError):
        file_obj.seek(0)
        return file_obj

    if getattr(image, "is_animated", False):
        file_obj.seek(0)
        return file_obj

    image.thumbnail((settings.MEDIA_IMAGE_MAX_WIDTH, settings.MEDIA_IMAGE_MAX_HEIGHT), Image.Resampling.LANCZOS)

    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA" if "A" in image.getbands() else "RGB")

    output = BytesIO()
    image.save(output, format="WEBP", quality=settings.MEDIA_IMAGE_QUALITY, method=6)
    output.seek(0)

    original_name = Path(getattr(file_obj, "name", "upload")).stem or "upload"
    return ContentFile(output.read(), name=f"{original_name}.webp")


def media_public_url(file_name):
    public_root = getattr(settings, "SUPABASE_STORAGE_PUBLIC_URL", "")
    if public_root and file_name:
        return f"{public_root}/{str(file_name).lstrip('/')}"
    return ""


class NavigationItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = NavigationItem
        fields = "__all__"

    def get_children(self, obj):
        children = obj.children.filter(is_visible=True)
        return NavigationItemSerializer(children, many=True, context=self.context).data


class PageSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageSection
        fields = "__all__"


class CallToActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallToAction
        fields = "__all__"


class MediaAssetSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = "__all__"

    def validate_file(self, value):
        if not value:
            return value
        reject_dangerous_upload(value)
        if value.size > settings.MEDIA_UPLOAD_MAX_BYTES:
            raise serializers.ValidationError(f"Upload must be {settings.MEDIA_UPLOAD_MAX_MB}MB or smaller.")
        return optimize_image_upload(value)

    def get_file_url(self, obj):
        if not obj.file:
            return ""
        public_url = media_public_url(obj.file.name)
        if public_url:
            return public_url
        request = self.context.get("request")
        url = obj.file.url
        return request.build_absolute_uri(url) if request else url


class SiteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSetting
        fields = "__all__"


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = "__all__"


class RequestFormOptionSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestFormOptionSet
        fields = "__all__"
