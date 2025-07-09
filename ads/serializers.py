from rest_framework import serializers

from ads.models import Ad, ExchangeProposal

class AdSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Ad
        fields = ['id', 'user', 'title', 'description', 'image_url', 'category', 'condition', 'created_at']
        read_only_fields = ['created_at']

class ExchangeProposalSerializer(serializers.ModelSerializer):
    ad_sender = AdSerializer(read_only=True)
    ad_receiver = AdSerializer(read_only=True)
    
    class Meta:
        model = ExchangeProposal
        fields = ['id', 'ad_sender', 'ad_receiver', 'comment', 'status', 'created_at']
        read_only_fields = ['created_at']