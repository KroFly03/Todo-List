from django.urls import path

from goals import views

urlpatterns = [
    path('goal_category/create', views.GoalCategoryCreateView.as_view(), name='create_category'),
    path('goal_category/list', views.GoalCategoryListView.as_view(), name='list_category'),
    path('goal_category/<pk>', views.GoalCategoryView.as_view(), name='detail_category'),
    path('goal/create', views.GoalCreateView.as_view(), name='create_goal'),
    path('goal/list', views.GoalListView.as_view(), name='list_goal'),
    path('goal/<pk>', views.GoalView.as_view(), name='detail_goal'),
    path('goal_comment/create', views.GoalCommentCreateView.as_view(), name='create_comment'),
    path('goal_comment/list', views.GoalCommentListView.as_view(), name='list_comment'),
    path('goal_comment/<pk>', views.GoalCommentView.as_view(), name='detail_comment'),
]
