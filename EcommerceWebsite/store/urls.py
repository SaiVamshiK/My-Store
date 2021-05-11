from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.store,name='store'),
    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('update_item/',views.updateitem,name='update_item'),
    path('process_order/',views.processOrder,name='process_order'),
    path('register/',views.register,name='register'),
    path('login/',auth_views.LoginView.as_view(template_name='store/login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='store/logout.html'),name='logout'),
    path('reset_password/',auth_views.PasswordResetView.as_view(
        template_name='store/PassWordReset.html'
    ),name='reset_password'),
    path('reset_password_sent/',auth_views.PasswordResetDoneView.as_view(
        template_name='store/PassWordResetSent.html'
    ),name='password_reset_done'),
    path('reset/<uidb64>>/<token>/',auth_views.PasswordResetConfirmView.as_view(
        template_name='store/PassWordResetForm.html'
    ),name='password_reset_confirm'),
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(
        template_name='store/PassWordResetdone.html'
    ),name='password_reset_complete'),
    path('previous_orders/',views.previousOrders,name='previous_orders'),
    path('pdf_view/',views.ViewPDF.as_view(),name='pdf_view'),
    path('cur_pdf_view/',views.ViewCurPDF.as_view(),name='cur_pdf_view'),
    path('product/<int:pk>/review/',views.createReview,name='each_product_review'),
    path('product/<int:pk>/see_rating/',views.see_rating,name='see_rating'),
    path('product/<int:pk>/review/classify/',views.call_model.as_view(),name='result')
]



