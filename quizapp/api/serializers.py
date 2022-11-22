from rest_framework import serializers
from main_app.models import *


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'


class CreateTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ('name', 'description', 'is_public', 'access_by_link', 'show_results', 'category')


class UpdateTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = (
            'name', 'description', 'time_create', 'time_update', 'is_public', 'access_by_link', 'show_results',
            'category', 'owner')
        read_only_fields = ('owner',)


class QuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = '__all__'

