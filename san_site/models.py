from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Prefetch
from django.db import connection

# connection.queries

class SectionManager(models.Manager):
    pass


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.PROTECT)
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    sort = models.IntegerField(default=500)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class Person(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, null=True, db_index=True, on_delete=models.PROTECT)
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    sort = models.IntegerField(default=500)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    change_password = models.BooleanField(default=False)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class Section(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    sort = models.IntegerField(default=500)
    parent_guid = models.CharField(max_length=50, db_index=True)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    objects = SectionManager()

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name

    def list_with_children(self, list_sections):
        list_sections.append(self)
        children = Section.objects.filter(parent_guid=self.guid)
        for child in children:
            list_sections.append(child)
            child.list_with_children(list_sections)

    def get_goods_list(self, user):

        list_sections = []
        self.list_with_children(list_sections)

        list_res_ = []

        currency_dict = {elem_.id: elem_.name for elem_ in Currency.objects.all()}

        if user.is_authenticated:

            current_customer = get_customer(user)
            if current_customer is None:
                return list_res_

            products = Product.objects.filter(section__in=list_sections).order_by('code') \
                .prefetch_related(
                Prefetch('product_inventories',
                    queryset=Inventories.objects.all()),
                Prefetch('product_customers_prices',
                    queryset=CustomersPrices.objects.filter(customer=current_customer)))
            for value_product in products:
                quantity_sum = 0
                for product_inventories in value_product.product_inventories.all():
                    quantity_sum += product_inventories.quantity
                price_value, price_discount, price_percent = (0, 0, 0)
                currency_name = ''
                for product_prices in value_product.product_customers_prices.all():
                    price_value = product_prices.value
                    price_discount = product_prices.discount
                    price_percent = product_prices.percent
                    currency_name = currency_dict.get(product_prices.currency_id, '')
                list_res_.append({'product': value_product,
                                'guid': value_product.guid,
                                'code': value_product.code,
                                'name': value_product.name,
                                'quantity': '>10' if quantity_sum > 10 else '' if quantity_sum == 0 else quantity_sum,
                                'price': '' if price_discount == 0 else price_discount,
                                'discount': '' if price_value == 0 else price_value,
                                'currency': currency_name,
                                'percent': '' if price_percent == 0 else price_percent,
                                'url_tr_good': 'tr_good' + value_product.guid})

        else:
            products = Product.objects.filter(section__in=list_sections).order_by('code') \
                .prefetch_related('product_inventories', 'product_prices')
            for value_product in products:
                quantity_sum = 0
                for product_inventories in value_product.product_inventories.all():
                    quantity_sum += product_inventories.quantity
                price_value = 0
                currency_name = ''
                for product_prices in value_product.product_prices.all():
                    price_value = product_prices.value
                    currency_name = currency_dict.get(product_prices.currency_id, '')
                list_res_.append({'product': value_product,
                                'guid': value_product.guid,
                                'code': value_product.code,
                                'name': value_product.name,
                                'quantity': '>10' if quantity_sum > 10 else '' if quantity_sum == 0 else quantity_sum,
                                'price': '' if price_value == 0 else price_value,
                                'discount': '',
                                'currency': currency_name,
                                'percent': ''})

        return list_res_


class Product(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30)
    sort = models.IntegerField(default=500)
    section = models.ForeignKey(Section, null=True, db_index=True, on_delete=models.PROTECT)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name

    def url_add_cart(self):
        return 'cart/add/?product=' + self.guid

    def get_price(self, user):

        current_customer = get_customer(user)
        if current_customer is None:
            return dict(price=0, price_ruble=0, currency='')

        query_set_price = CustomersPrices.objects.\
            filter(customer=current_customer, product=self).select_related('currency')
        if len(query_set_price):
            currency = query_set_price[0].currency
            currency_name = query_set_price[0].currency.name
            price = query_set_price[0].discount
            price_ruble = currency.change_ruble(price)
            return dict(price=price, price_ruble=price_ruble, currency=currency_name)
        return dict(price=0, price_ruble=0, currency='')


class Store(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    sort = models.IntegerField(default=500)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class Price(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    sort = models.IntegerField(default=500)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class Currency(models.Model):
    guid = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    sort = models.IntegerField(default=500)
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name

    def get_today_course(self):
        from django.db.models import Max
        dict_max_date = Courses.objects.filter(currency=self).aggregate(max_date=Max('date'))
        if not dict_max_date['max_date'] is None:
            set_course = Courses.objects.filter(currency=self).filter(date=dict_max_date['max_date'])
            if len(set_course) > 0:
                return {'course': set_course[0].course, 'multiplicity': set_course[0].multiplicity}
        return {'course': 1, 'multiplicity': 1}

    def change_ruble(self, value):
        course = self.get_today_course()
        return round(value * course['course'] / course['multiplicity'], 2)


class Inventories(models.Model):
    product = models.ForeignKey(Product, related_name='product_inventories', null=True, db_index=True, on_delete=models.DO_NOTHING)
    store = models.ForeignKey(Store, null=True, unique=False, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(null=False, default=0)

class Prices(models.Model):
    product = models.ForeignKey(Product, related_name='product_prices', null=True, db_index=True, on_delete=models.DO_NOTHING)
    price = models.ForeignKey(Price, null=True, unique=False, on_delete=models.DO_NOTHING)
    currency = models.ForeignKey(Currency, null=True, unique=False, on_delete=models.DO_NOTHING)
    value = models.FloatField(null=False, default=0)

class CustomersPrices(models.Model):
    customer = models.ForeignKey(Customer, null=True, db_index=True, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, related_name='product_customers_prices', null=True, db_index=True, on_delete=models.DO_NOTHING)
    currency = models.ForeignKey(Currency, null=True, on_delete=models.DO_NOTHING)
    value = models.FloatField(null=False, default=0)
    discount = models.FloatField(null=False, default=0)
    percent = models.FloatField(null=False, default=0)


class Courses(models.Model):
    date = models.DateField(db_index=True)
    currency = models.ForeignKey(Currency, null=False, db_index=True, on_delete=models.DO_NOTHING)
    course = models.FloatField(null=False, default=0)
    multiplicity = models.IntegerField(null=False, default=1)


def get_customer(user):
    set_person = Person.objects.filter(user=user).select_related('customer').only('customer')
    if len(set_person) > 0:
        return set_person[0].customer
