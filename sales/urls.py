from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Sales Entry
    path('sales/entry/', views.sales_entry, name='sales_entry'),

    # Menu Management
    path('menu/', views.MenuItemListView.as_view(), name='menu_list'),
    path('menu/add/', views.MenuItemCreateView.as_view(), name='menu_add'),
    path('menu/<int:pk>/edit/', views.MenuItemUpdateView.as_view(), name='menu_edit'),
    path('menu/<int:pk>/delete/', views.MenuItemDeleteView.as_view(), name='menu_delete'),

    # Sales History
    path('sales/history/', views.sales_history, name='sales_history'),
    path('sales/<int:pk>/edit/', views.SaleUpdateView.as_view(), name='sale_update'),
    path('sales/<int:pk>/delete/', views.SaleDeleteView.as_view(), name='sale_delete'),

    # Reports
    path('reports/', views.reports, name='reports'),
    path('reports/export/', views.export_csv, name='export_csv'),

    # AJAX
    path('api/menu-item/<int:item_id>/price/', views.get_menu_item_price, name='menu_item_price'),
]
