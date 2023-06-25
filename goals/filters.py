from django_filters import rest_framework

from goals.models import Goal, GoalCategory


class GoalFilter(rest_framework.FilterSet):
    class Meta:
        model = Goal
        fields = {
            'due_date': ['lte', 'gte'],
            'category': ['in'],
            'status': ['in'],
            'priority': ['in']
        }


class GoalCategoryFilter(rest_framework.FilterSet):
    class Meta:
        model = GoalCategory
        fields = {
            'board': ['exact']
        }
