from django.contrib import admin
from .models import (
    Korisnik, Pozicija, StavkaRacuna, Zaposlenik, Ugovor,
    EvidencijaRada, BonusOdbitak, ObracunPlace,
    Kategorija, JedinicaMjere, Artikl, DnevnoStanje,
    Dobavljac, Racun, Trosak
)

admin.site.register(Korisnik)
admin.site.register(Pozicija)
admin.site.register(Zaposlenik)
admin.site.register(Ugovor)
admin.site.register(EvidencijaRada)
admin.site.register(BonusOdbitak)
admin.site.register(ObracunPlace)
admin.site.register(Kategorija)
admin.site.register(JedinicaMjere)
admin.site.register(Artikl)
admin.site.register(DnevnoStanje)
admin.site.register(Dobavljac)
admin.site.register(StavkaRacuna)
admin.site.register(Racun)
admin.site.register(Trosak)