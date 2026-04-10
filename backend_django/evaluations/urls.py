from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.views import (
    EmployeeViewSet,
    EvaluationViewSet,
    BonoViewSet,
    ApprovalRequestViewSet
)
from .views.auth_views import (
    LoginView,
    LogoutView,
    CurrentUserView,
    RefreshTokenView,
    UserListView
)

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employees')
router.register(r'evaluations', EvaluationViewSet, basename='evaluations')
router.register(r'bonos', BonoViewSet, basename='bonos')
router.register(r'approvals', ApprovalRequestViewSet, basename='approvals')

urlpatterns = [
    path('', include(router.urls)),
    
    # Auth endpoints
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', CurrentUserView.as_view(), name='current_user'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh_token'),
    
    # Users endpoint
    path('users/', UserListView.as_view(), name='user_list'),
]