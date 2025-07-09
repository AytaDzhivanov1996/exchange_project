from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from ads.models import Ad, ExchangeProposal
from ads.serializers import AdSerializer, ExchangeProposalSerializer

class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'condition']
    
    def get_queryset(self):
        queryset = Ad.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def exchange_proposal(self, request, pk=None):
        """Создание предложения обмена через API"""
        ad_receiver = self.get_object()
        ad_sender_id = request.data.get('ad_sender_id')
        comment = request.data.get('comment')
        
        if not ad_sender_id or not comment:
            return Response({'error': 'Требуются ad_sender_id и comment'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            ad_sender = Ad.objects.get(pk=ad_sender_id, user=request.user)
        except Ad.DoesNotExist:
            return Response({'error': 'Объявление отправителя не найдено'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        proposal = ExchangeProposal.objects.create(
            ad_sender=ad_sender,
            ad_receiver=ad_receiver,
            comment=comment
        )
        
        serializer = ExchangeProposalSerializer(proposal)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ExchangeProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ExchangeProposalSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return ExchangeProposal.objects.filter(
            Q(ad_sender__user=self.request.user) | 
            Q(ad_receiver__user=self.request.user)
        )
        