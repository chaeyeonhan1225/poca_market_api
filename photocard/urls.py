from django.urls import path

from photocard import views

urlpatterns = [
    path("", views.PhotoCardListCreateView.as_view(), name="photocard-list"),
    path("<int:pk>/", views.PhotoCardDetailView.as_view(), name="photocard-list"),
    path("sales/", views.PhotoCardSaleListView.as_view(), name="photocard-sales-list"),
    path("<int:pk>/sales/<uuid:sale_id>/", views.PhotoCardSaleDetailView.as_view(), name="photocard-sale-purchase"),
    path("<int:pk>/sales/", views.PhotoCardSaleListCreateView.as_view(), name="photocard-sales-list-create"),
    path(
        "<int:pk>/sales/<uuid:sale_id>/purchase/",
        views.PhotoCardSalePurchaseView.as_view(),
        name="photocard-sale-purchase",
    ),
]
