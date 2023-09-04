from rest_framework import serializers
from .models import *


class SwimmingSpotSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = SwimmingSpot
        fields = '__all__'

    def create(self, validated_data):
        image_data = self.context['request'].FILES.get('image')  # Use 'FILES' for image upload

        # Create the SwimmingSpot instance
        instance = SwimmingSpot.objects.create(**validated_data)

        if image_data:
            # Handle image upload and associate it with the spot
            image = Image.objects.create(swimming_spot=instance, image=image_data)

        # Create a feed item for the new swimming spot
        request = self.context['request']
        user = request.user
        FeedItem.objects.create(user=user, content_object=instance)

        return instance
