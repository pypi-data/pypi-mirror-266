from django.urls import (
    path,
)

from . import (
    const,
    views,
)


urlpatterns = [
    path(
        'search/place/', views.PlaceSearchView.as_view(),
        name=const.SEARCH_PLACE_NAME
    ),
    path(
        'search/street/', views.StreetSearchView.as_view(),
        name=const.SEARCH_STREET_NAME
    ),
    path(
        'search/house/', views.HouseSearchView.as_view(),
        name=const.SEARCH_HOUSE_NAME
    ),
    path(
        'search/house-or-stead/', views.HouseOrSteadSearchView.as_view(),
        name=const.SEARCH_HOUSE_OR_STEAD_NAME
    ),
    path(
        'search/apartment/', views.ApartmentSearchView.as_view(),
        name=const.SEARCH_APARTMENT
    ),
]
