from django.contrib import admin
from .models import Invoice, Payment, UserBalance, User
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('id', 'username', 'password', 'role', 'email')}),
        ('Персональные данные', {
            'fields': ('first_name', 'last_name'),
            'classes': ('collapse',),
        })
    )

    add_fieldsets = (
        (None, {'fields': ('id', 'username', 'password1', 'password2', 'role', 'email')}),
        ('Персональные данные', {
            'fields': ('first_name', 'last_name'),
            'classes': ('collapse',),
        }),
    )

    list_display = (
        'username', 'first_name', 'last_name', 'role', 'email',
    )
    readonly_fields = ('id',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "amount", "currency", "status", "created_at")
    search_fields = ("id", "user__username", "user__email")
    list_filter = ("status", "currency")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "invoice", "amount", "status", "attempts", "provider_transaction_id", "created_at")
    search_fields = ("id", "provider_transaction_id")


@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "reserved", "updated_at")
    search_fields = ("user__username", "user__email")