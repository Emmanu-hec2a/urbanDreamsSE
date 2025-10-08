from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import MenuItem, Sale, SaleItem
from .forms import MenuItemForm, SaleForm, SaleItemForm, UserRegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.http import JsonResponse, HttpResponse
import json
import csv

# Authentication Views
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

# Dashboard View
@login_required
def dashboard(request):
    if not request.user.is_staff:
        return redirect('sales_entry')

    # Today's sales
    today = timezone.now().date()
    today_sales = Sale.objects.filter(sale_date__date=today).aggregate(
        total=Sum('total_amount'),
        count=Count('id')
    )

    # Weekly sales
    week_ago = today - timedelta(days=7)
    weekly_sales = Sale.objects.filter(sale_date__date__gte=week_ago).aggregate(
        total=Sum('total_amount'),
        count=Count('id')
    )

    # Top selling items
    top_items = SaleItem.objects.values('menu_item__name').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]

    # Payment method distribution
    payment_methods = Sale.objects.values('payment_method').annotate(
        count=Count('id')
    )

    # Dynamic chart data for the last 7 days
    chart_data = []
    chart_labels = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        sales_sum = Sale.objects.filter(sale_date__date=date).aggregate(total=Sum('total_amount'))['total'] or 0
        chart_labels.append(date.strftime('%a'))
        chart_data.append(float(sales_sum))

    context = {
        'today_sales': today_sales,
        'weekly_sales': weekly_sales,
        'top_items': top_items,
        'payment_methods': payment_methods,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'dashboard.html', context)

# Sales Entry View
@login_required
def sales_entry(request):
    if request.method == 'POST':
        sale_form = SaleForm(request.POST)
        if sale_form.is_valid():
            sale = sale_form.save(commit=False)
            sale.created_by = request.user
            sale.total_amount = 0  # Will calculate from items
            sale.save()

            # Process cart items from POST data
            cart_data_raw = request.POST.get('cart_data', '')
            if cart_data_raw:
                try:
                    cart_data = json.loads(cart_data_raw)
                except json.JSONDecodeError:
                    cart_data = []
            else:
                cart_data = []

            total = 0
            for item in cart_data:
                menu_item = get_object_or_404(MenuItem, id=item['id'])
                quantity = item['quantity']
                unit_price = menu_item.unit_price
                subtotal = quantity * unit_price
                SaleItem.objects.create(
                    sale=sale,
                    menu_item=menu_item,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal
                )
                total += subtotal

            sale.total_amount = total
            sale.save()

            messages.success(request, 'Sale recorded successfully!')
            return redirect('sales_entry')
    else:
        sale_form = SaleForm(initial={'sale_date': timezone.now()})

    menu_items = MenuItem.objects.filter(is_available=True)
    context = {
        'sale_form': sale_form,
        'menu_items': menu_items,
    }
    return render(request, 'sales_entry.html', context)

# Menu Management Views
class MenuItemListView(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = 'menu_list.html'
    context_object_name = 'menu_items'

    def get_queryset(self):
        return MenuItem.objects.all().order_by('category', 'name')

class MenuItemCreateView(LoginRequiredMixin, CreateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'menu_form.html'
    success_url = reverse_lazy('menu_list')

    def form_valid(self, form):
        messages.success(self.request, 'Menu item created successfully!')
        return super().form_valid(form)

class MenuItemUpdateView(LoginRequiredMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'menu_form.html'
    success_url = reverse_lazy('menu_list')

    def form_valid(self, form):
        messages.success(self.request, 'Menu item updated successfully!')
        return super().form_valid(form)

class MenuItemDeleteView(LoginRequiredMixin, DeleteView):
    model = MenuItem
    template_name = 'menu_confirm_delete.html'
    success_url = reverse_lazy('menu_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Menu item deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Sales History View
@login_required
def sales_history(request):
    if request.user.is_staff:
        sales = Sale.objects.all().order_by('-sale_date')
    else:
        sales = Sale.objects.filter(created_by=request.user).order_by('-sale_date')

    context = {
        'sales': sales,
    }
    return render(request, 'sales_history.html', context)

# Sale Management Views
class SaleUpdateView(LoginRequiredMixin, UpdateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sale_form.html'
    success_url = reverse_lazy('sales_history')

    def get_queryset(self):
        if self.request.user.is_staff:
            return Sale.objects.all()
        return Sale.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Sale updated successfully!')
        return super().form_valid(form)

class SaleDeleteView(LoginRequiredMixin, DeleteView):
    model = Sale
    template_name = 'sale_confirm_delete.html'
    success_url = reverse_lazy('sales_history')

    def get_queryset(self):
        if self.request.user.is_staff:
            return Sale.objects.all()
        return Sale.objects.filter(created_by=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Sale deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Reports View
@login_required
def reports(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    sales_report = None
    if request.GET.get('start_date') and request.GET.get('end_date'):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        sales_report = Sale.objects.filter(
            sale_date__date__gte=start_date,
            sale_date__date__lte=end_date
        ).order_by('-sale_date')

    context = {
        'sales_report': sales_report,
    }
    return render(request, 'reports.html', context)

# Export CSV View
@login_required
def export_csv(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        messages.error(request, 'Please provide start and end dates.')
        return redirect('reports')

    sales = Sale.objects.filter(
        sale_date__date__gte=start_date,
        sale_date__date__lte=end_date
    ).order_by('-sale_date')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date}_to_{end_date}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Total Amount (KES)', 'Payment Method', 'Notes', 'Created By'])

    for sale in sales:
        writer.writerow([
            sale.sale_date.strftime('%Y-%m-%d %H:%M'),
            sale.total_amount,
            sale.payment_method,
            sale.notes or '',
            sale.created_by.get_full_name() or sale.created_by.username
        ])

    return response

# AJAX Views for dynamic functionality
def get_menu_item_price(request, item_id):
    try:
        item = MenuItem.objects.get(id=item_id)
        return JsonResponse({'price': float(item.unit_price), 'name': item.name})
    except MenuItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
