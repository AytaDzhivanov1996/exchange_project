from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login

from ads.models import Ad, ExchangeProposal
from ads.forms import AdForm, ExchangeProposalForm, AdSearchForm, SignUpForm

def ad_list(request):
    """Список объявлений с поиском и фильтрацией"""
    ads = Ad.objects.all()
    form = AdSearchForm(request.GET)
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        condition = form.cleaned_data.get('condition')
        
        if query:
            ads = ads.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if category:
            ads = ads.filter(category=category)
        if condition:
            ads = ads.filter(condition=condition)
    
    paginator = Paginator(ads, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'ads/ad_list.html', {
        'page_obj': page_obj,
        'form': form,
        'ads': page_obj.object_list
    })

def ad_detail(request, pk):
    """Детальная страница объявления"""
    ad = get_object_or_404(Ad, pk=pk)
    user_ads = []
    
    if request.user.is_authenticated and request.user != ad.user:
        user_ads = Ad.objects.filter(user=request.user)
    
    return render(request, 'ads/ad_detail.html', {
        'ad': ad,
        'user_ads': user_ads
    })

@login_required
def ad_create(request):
    """Создание нового объявления"""
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            messages.success(request, 'Объявление успешно создано!')
            return redirect('ad_detail', pk=ad.pk)
    else:
        form = AdForm()
    
    return render(request, 'ads/ad_form.html', {
        'form': form,
        'title': 'Создать объявление'
    })

@login_required
def ad_edit(request, pk):
    """Редактирование объявления"""
    ad = get_object_or_404(Ad, pk=pk)
    
    if ad.user != request.user:
        messages.error(request, 'Вы можете редактировать только свои объявления!')
        return redirect('ad_detail', pk=pk)
    
    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Объявление успешно обновлено!')
            return redirect('ad_detail', pk=pk)
    else:
        form = AdForm(instance=ad)
    
    return render(request, 'ads/ad_form.html', {
        'form': form,
        'title': 'Редактировать объявление',
        'ad': ad
    })

@login_required
def ad_delete(request, pk):
    """Удаление объявления"""
    ad = get_object_or_404(Ad, pk=pk)
    
    if ad.user != request.user:
        messages.error(request, 'Вы можете удалять только свои объявления!')
        return redirect('ad_detail', pk=pk)
    
    if request.method == 'POST':
        ad.delete()
        messages.success(request, 'Объявление успешно удалено!')
        return redirect('ad_list')
    
    return render(request, 'ads/ad_confirm_delete.html', {'ad': ad})

@login_required
def create_exchange_proposal(request, ad_id):
    """Создание предложения обмена"""
    ad_receiver = get_object_or_404(Ad, pk=ad_id)
    
    if ad_receiver.user == request.user:
        messages.error(request, 'Вы не можете предложить обмен на свое объявление!')
        return redirect('ad_detail', pk=ad_id)
    
    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST)
        ad_sender_id = request.POST.get('ad_sender')
        
        if form.is_valid() and ad_sender_id:
            ad_sender = get_object_or_404(Ad, pk=ad_sender_id, user=request.user)
            
            existing_proposal = ExchangeProposal.objects.filter(
                ad_sender=ad_sender,
                ad_receiver=ad_receiver
            ).first()
            
            if existing_proposal:
                messages.error(request, 'Предложение обмена уже существует!')
                return redirect('ad_detail', pk=ad_id)
            
            proposal = form.save(commit=False)
            proposal.ad_sender = ad_sender
            proposal.ad_receiver = ad_receiver
            proposal.save()
            
            messages.success(request, 'Предложение обмена отправлено!')
            return redirect('ad_detail', pk=ad_id)
    else:
        form = ExchangeProposalForm()
    
    user_ads = Ad.objects.filter(user=request.user)
    
    return render(request, 'ads/create_exchange_proposal.html', {
        'form': form,
        'ad_receiver': ad_receiver,
        'user_ads': user_ads
    })

@login_required
def proposal_list(request):
    """Список предложений обмена"""
    received_proposals = ExchangeProposal.objects.filter(
        ad_receiver__user=request.user
    )
    sent_proposals = ExchangeProposal.objects.filter(
        ad_sender__user=request.user
    )
    
    return render(request, 'ads/proposal_list.html', {
        'received_proposals': received_proposals,
        'sent_proposals': sent_proposals
    })

@login_required
@require_http_methods(["POST"])
def update_proposal_status(request, proposal_id):
    """Обновление статуса предложения"""
    proposal = get_object_or_404(ExchangeProposal, pk=proposal_id)
    
    if proposal.ad_receiver.user != request.user:
        messages.error(request, 'Вы можете изменять статус только своих предложений!')
        return redirect('proposal_list')
    
    new_status = request.POST.get('status')
    if new_status in ['accepted', 'rejected']:
        proposal.status = new_status
        proposal.save()
        
        status_text = 'принято' if new_status == 'accepted' else 'отклонено'
        messages.success(request, f'Предложение {status_text}!')
    
    return redirect('proposal_list')

@login_required
def my_ads(request):
    """Мои объявления"""
    ads = Ad.objects.filter(user=request.user)
    paginator = Paginator(ads, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'ads/my_ads.html', {
        'page_obj': page_obj,
        'ads': page_obj.object_list
    })

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
