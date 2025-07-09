import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client
from django.conf import settings

from ads.models import Ad, ExchangeProposal

@pytest.fixture(autouse=True, scope="session")
def set_test_settings():
    settings.FORMS_URLFIELD_ASSUME_HTTPS = True

@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass123')

@pytest.fixture
def client_user(user):
    client = Client()
    client.login(username='testuser', password='testpass123')
    return client

@pytest.fixture
def ad(user):
    return Ad.objects.create(
        user=user,
        title='Test Ad',
        description='Test Description',
        category='electronics',
        condition='new'
    )

@pytest.fixture
def users(db):
    user1 = User.objects.create_user(username='user1', password='pass123')
    user2 = User.objects.create_user(username='user2', password='pass123')
    return user1, user2

@pytest.fixture
def ads(users):
    user1, user2 = users
    ad1 = Ad.objects.create(
        user=user1,
        title='Ad 1',
        description='Description 1',
        category='electronics',
        condition='new'
    )
    ad2 = Ad.objects.create(
        user=user2,
        title='Ad 2',
        description='Description 2',
        category='books',
        condition='used'
    )
    return ad1, ad2

def test_ad_creation(ad, user):
    assert ad.title == 'Test Ad'
    assert ad.user == user
    assert str(ad) == 'Test Ad - testuser'

def test_ad_list_view(client, ad):
    response = client.get(reverse('ad_list'))
    assert response.status_code == 200
    assert 'Test Ad' in response.content.decode()

def test_ad_detail_view(client, ad):
    response = client.get(reverse('ad_detail', kwargs={'pk': ad.pk}))
    assert response.status_code == 200
    assert 'Test Ad' in response.content.decode()

def test_ad_create_requires_login(client):
    response = client.get(reverse('ad_create'))
    assert response.status_code == 302

def test_ad_create_authenticated(client_user):
    response = client_user.post(reverse('ad_create'), {
        'title': 'New Ad',
        'description': 'New Description',
        'category': 'books',
        'condition': 'used'
    })
    assert response.status_code == 302
    assert Ad.objects.filter(title='New Ad').exists()

def test_exchange_proposal_creation(ads, users):
    ad1, ad2 = ads
    user1, user2 = users
    
    proposal = ExchangeProposal.objects.create(
        ad_sender=ad1,
        ad_receiver=ad2,
        comment='Test exchange proposal'
    )
    
    assert proposal.status == 'pending'
    assert proposal.comment == 'Test exchange proposal'
    assert proposal.sender_user == user1
    assert proposal.receiver_user == user2
    