from django.db import models
from django.contrib.auth.models import AbstractUser


# =========================
# =========================
# 1. CUSTOM USER MODEL
# =========================

class User(AbstractUser):

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=15)

    address = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


# =========================
# 2. CATEGORY MODEL
# =========================
# =========================

class Category(models.Model):

    name = models.CharField(max_length=200)

    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


# =========================
# 3. PRODUCT MODEL
# =========================

class Product(models.Model):
    name = models.CharField(max_length=300)

    price = models.FloatField()

    quantity = models.IntegerField(default=0)

    description = models.CharField(max_length=200)

    class Meta:
        db_table = "api_product"

    def __str__(self):
        return self.name


# =========================
# 4. CART MODEL
# =========================

class Cart(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


# =========================
# 5. CART ITEM MODEL
# =========================

class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.product.name


# =========================
# 6. ORDER MODEL
# =========================

class Order(models.Model):

    STATUS = (
        ('pending','Pending'),
        ('confirmed','Confirmed'),
        ('shipped','Shipped'),
        ('delivered','Delivered'),
        ('cancelled','Cancelled')
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    total_price = models.FloatField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='pending'
    )

    address = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


# =========================
# 7. ORDER ITEM MODEL
# =========================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField()

    price = models.FloatField()

    def __str__(self):
        return self.product.name


# =========================
# 8. PAYMENT MODEL
# =========================

class Payment(models.Model):

    METHOD = (
        ('cod','Cash On Delivery'),
        ('card','Card'),
        ('jazzcash','JazzCash'),
        ('easypaisa','EasyPaisa')
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    payment_method = models.CharField(
        max_length=20,
        choices=METHOD
    )

    amount = models.FloatField()

    payment_status = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.order.id)


# =========================
# 9. CHAT MODEL (AI Agent)
# =========================

class ChatMessage(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    response = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email
