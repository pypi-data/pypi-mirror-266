from django.urls import path
from .views import MyTerritoriesView, MemberOfCommunitiesView
from djangoldp_community.models import Community

urlpatterns = [
    path('myterritories/', MyTerritoriesView.as_view({'get': 'list'}, model=Community), name='myterritories'),
    path('memberofcommunities/', MemberOfCommunitiesView.as_view({'get': 'list'}, model=Community), name='memberofcommunities'),
]