from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

   
    path('zaposlenici/', views.zaposlenici, name='zaposlenici'),
    path('zaposlenici/dodaj/', views.zaposlenik_forma, name='zaposlenik_dodaj'),
    path('zaposlenici/<int:pk>/uredi/', views.zaposlenik_forma, name='zaposlenik_uredi'),
    path('zaposlenici/<int:pk>/obrisi/', views.zaposlenik_obrisi, name='zaposlenik_obrisi'),

   
    path('evidencija/', views.evidencija, name='evidencija'),
    path('evidencija/dodaj/', views.evidencija_forma, name='evidencija_dodaj'),
    path('evidencija/<int:pk>/uredi/', views.evidencija_forma, name='evidencija_uredi'),
    path('evidencija/<int:pk>/obrisi/', views.evidencija_obrisi, name='evidencija_obrisi'),
    path('evidencija/<int:zaposlenik_pk>/<int:mjesec>/<int:godina>/bonus/', views.bonus_forma, name='bonus_dodaj'),
    path('evidencija/<int:zaposlenik_pk>/<int:mjesec>/<int:godina>/obracun/', views.obracun, name='obracun'),


    path('inventar/', views.inventar, name='inventar'),
    path('inventar/dodaj/', views.artikl_forma, name='artikl_dodaj'),
    path('inventar/<int:pk>/uredi/', views.artikl_forma, name='artikl_uredi'),
    path('inventar/<int:pk>/obrisi/', views.artikl_obrisi, name='artikl_obrisi'),
    path('inventar/stanje/dodaj/', views.dnevno_stanje_forma, name='dnevno_stanje_dodaj'),


    path('dobavljaci/', views.dobavljaci, name='dobavljaci'),
    path('dobavljaci/dodaj/', views.dobavljac_forma, name='dobavljac_dodaj'),
    path('dobavljaci/<int:pk>/uredi/', views.dobavljac_forma, name='dobavljac_uredi'),
    path('dobavljaci/<int:pk>/obrisi/', views.dobavljac_obrisi, name='dobavljac_obrisi'),

    
    path('racuni/', views.racuni, name='racuni'),
    path('racuni/dodaj/', views.racun_forma, name='racun_dodaj'),
    path('racuni/<int:pk>/uredi/', views.racun_forma, name='racun_uredi'),
    path('racuni/<int:pk>/obrisi/', views.racun_obrisi, name='racun_obrisi'),
    path('racuni/<int:pk>/plati/', views.racun_plati, name='racun_plati'),
    path('racuni/<int:pk>/stavke/', views.racun_stavke, name='racun_stavke'),

    path('troskovi/', views.troskovi, name='troskovi'),
    path('troskovi/dodaj/', views.trosak_forma, name='trosak_dodaj'),
    path('troskovi/<int:pk>/uredi/', views.trosak_forma, name='trosak_uredi'),
    path('troskovi/<int:pk>/obrisi/', views.trosak_obrisi, name='trosak_obrisi'),

    path('postavke/', views.postavke, name='postavke'),
    path('postavke/pozicija/dodaj/', views.pozicija_forma, name='pozicija_dodaj'),
    path('postavke/pozicija/<int:pk>/uredi/', views.pozicija_forma, name='pozicija_uredi'),
    path('postavke/pozicija/<int:pk>/obrisi/', views.pozicija_obrisi, name='pozicija_obrisi'),
    path('postavke/kategorija/dodaj/', views.kategorija_forma, name='kategorija_dodaj'),
    path('postavke/kategorija/<int:pk>/uredi/', views.kategorija_forma, name='kategorija_uredi'),
    path('postavke/kategorija/<int:pk>/obrisi/', views.kategorija_obrisi, name='kategorija_obrisi'),
    path('postavke/jedinica/dodaj/', views.jedinica_forma, name='jedinica_dodaj'),
    path('postavke/jedinica/<int:pk>/uredi/', views.jedinica_forma, name='jedinica_uredi'),
    path('postavke/jedinica/<int:pk>/obrisi/', views.jedinica_obrisi, name='jedinica_obrisi'),
]