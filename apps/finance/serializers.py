from rest_framework import serializers
from .models import Account, Category, Transaction, Budget

class AccountSerializer(serializers.ModelSerializer):
    current_balance = serializers.DecimalField(max_digits=15, decimal_places=0, read_only=True)
    class Meta:
        model = Account
        fields = ['id', 'name', 'type', 'currency', 'initial_balance', 'current_balance', 'is_active']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'parent', 'is_active']

class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    account_name = serializers.ReadOnlyField(source='account.name')
    dest_account_name = serializers.ReadOnlyField(source='destination_account.name')

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['user']

    def validate(self, data):
        # Logic: Nếu là chuyển khoản thì bắt buộc phải có ví đích và khác ví nguồn
        if data.get('type') == 'transfer':
            if not data.get('destination_account'):
                raise serializers.ValidationError({"destination_account": "Required for transfers."})
            if data['account'] == data['destination_account']:
                raise serializers.ValidationError({"destination_account": "Cannot transfer to same account."})
        return data

class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ['user']