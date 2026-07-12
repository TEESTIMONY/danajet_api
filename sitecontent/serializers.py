from rest_framework import serializers

from .models import CallToAction, MediaAsset, NavigationItem, PageSection, RequestFormOptionSet, SiteSetting, SocialLink


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

    def get_file_url(self, obj):
        if not obj.file:
            return ""
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
