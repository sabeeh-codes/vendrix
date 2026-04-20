from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, ColorViewSet

router = DefaultRouter()
router.register(r'colors',     ColorViewSet,    basename='color')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products',   ProductViewSet,  basename='product')

urlpatterns = router.urls