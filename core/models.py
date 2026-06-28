from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal


class Korisnik(AbstractUser):
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = "Korisnik"
        verbose_name_plural = "Korisnici"

    def __str__(self):
        return self.username


# zaposlenici

class Pozicija(models.Model):
    naziv = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["naziv"]
        verbose_name = "Pozicija"
        verbose_name_plural = "Pozicije"

    def __str__(self):
        return self.naziv


class Zaposlenik(models.Model):
    ime              = models.CharField(max_length=100)
    prezime          = models.CharField(max_length=100)
    oib              = models.CharField(max_length=11, unique=True)
    email            = models.EmailField(unique=True)
    telefon          = models.CharField(max_length=20, blank=True)
    pozicija         = models.ForeignKey(Pozicija, on_delete=models.PROTECT, related_name="zaposlenici")
    datum_zaposlenja = models.DateField()
    aktivan          = models.BooleanField(default=True)

    class Meta:
        ordering = ["prezime", "ime"]
        verbose_name = "Zaposlenik"
        verbose_name_plural = "Zaposlenici"

    def __str__(self):
        return f"{self.prezime} {self.ime}"

  
class Ugovor(models.Model):
    STUDENTSKI = "STUDENTSKI"
    STALNI     = "STALNI"
    TIP_CHOICES = [
        (STUDENTSKI, "Studentski ugovor"),
        (STALNI,     "Stalni radni odnos"),
    ]

    zaposlenik = models.ForeignKey(Zaposlenik, on_delete=models.CASCADE, related_name='ugovori')
    tip           = models.CharField(max_length=20, choices=TIP_CHOICES)
    satnica       = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    fiksna_placa  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    aktivan       = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Ugovor"
        verbose_name_plural = "Ugovori"

    def __str__(self):
        return f"{self.zaposlenik} — {self.get_tip_display()}"
class EvidencijaRada(models.Model):
    zaposlenik = models.ForeignKey(Zaposlenik, on_delete=models.CASCADE, related_name="evidencije")
    datum      = models.DateField()
    sati       = models.DecimalField(max_digits=4, decimal_places=2)
    napomena   = models.TextField(blank=True)

    class Meta:
        unique_together = ["zaposlenik", "datum"]
        ordering = ["-datum"]
        verbose_name = "Evidencija rada"
        verbose_name_plural = "Evidencije rada"

    def __str__(self):
        return f"{self.zaposlenik} — {self.datum}: {self.sati}h"

class BonusOdbitak(models.Model):
    BONUS   = "BONUS"
    ODBITAK = "ODBITAK"
    TIP_CHOICES = [
        (BONUS,   "Bonus"),
        (ODBITAK, "Odbitak"),
    ]

    zaposlenik = models.ForeignKey(Zaposlenik, on_delete=models.CASCADE, related_name="bonusi_odbitci")
    mjesec     = models.PositiveSmallIntegerField()
    godina     = models.PositiveIntegerField()
    tip        = models.CharField(max_length=10, choices=TIP_CHOICES)
    iznos      = models.DecimalField(max_digits=10, decimal_places=2)
    opis       = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Bonus / odbitak"
        verbose_name_plural = "Bonusi i odbitci"

    def __str__(self):
        return f"{self.get_tip_display()}: {self.iznos} € — {self.opis}"

class ObracunPlace(models.Model):
    zaposlenik     = models.ForeignKey(Zaposlenik, on_delete=models.CASCADE, related_name="obracuni")
    mjesec         = models.PositiveSmallIntegerField()
    godina         = models.PositiveIntegerField()
    ukupni_sati    = models.DecimalField(max_digits=6, decimal_places=2)
    osnovna_placa  = models.DecimalField(max_digits=10, decimal_places=2)
    ukupni_dodaci  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ukupni_odbitci = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    za_isplatu     = models.DecimalField(max_digits=10, decimal_places=2)
    datum_obracuna = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["zaposlenik", "mjesec", "godina"]
        verbose_name = "Obračun plaće"
        verbose_name_plural = "Obračuni plaća"

    def __str__(self):
        return f"Obračun — {self.zaposlenik} {self.mjesec}/{self.godina}: {self.za_isplatu} €"
# inventar

class Kategorija(models.Model):
    ARTIKL = "ARTIKL"
    TROSAK = "TROSAK"
    TIP_CHOICES = [
        (ARTIKL, "Kategorija artikla"),
        (TROSAK, "Kategorija troška"),
    ]

    naziv = models.CharField(max_length=100)
    tip   = models.CharField(max_length=10, choices=TIP_CHOICES)

    class Meta:
        unique_together = ["naziv", "tip"]
        ordering = ["naziv"]
        verbose_name = "Kategorija"
        verbose_name_plural = "Kategorije"

    def __str__(self):
        return f"{self.naziv} ({self.get_tip_display()})"


class JedinicaMjere(models.Model):
    naziv = models.CharField(max_length=20, unique=True)  

    class Meta:
        ordering = ["naziv"]
        verbose_name = "Jedinica mjere"
        verbose_name_plural = "Jedinice mjere"

    def __str__(self):
        return self.naziv


class Artikl(models.Model):
    kategorija       = models.ForeignKey(Kategorija, on_delete=models.PROTECT, related_name="artikli")
    jedinica_mjere   = models.ForeignKey(JedinicaMjere, on_delete=models.PROTECT, related_name="artikli")
    naziv            = models.CharField(max_length=150)
    minimalna_razina = models.DecimalField(max_digits=10, decimal_places=3)
    aktivan          = models.BooleanField(default=True)

    class Meta:
        ordering = ["naziv"]
        verbose_name = "Artikl"
        verbose_name_plural = "Artikli"

    def __str__(self):
        return f"{self.naziv} ({self.jedinica_mjere})"

    def trenutno_stanje(self):
        zadnje = self.dnevna_stanja.order_by("-datum").first()
        return zadnje.kolicina if zadnje else Decimal("0")

    def ispod_minimuma(self):
        return self.trenutno_stanje() < self.minimalna_razina


class DnevnoStanje(models.Model):
    artikl    = models.ForeignKey(Artikl, on_delete=models.CASCADE, related_name="dnevna_stanja")
    datum     = models.DateField()
    kolicina  = models.DecimalField(max_digits=10, decimal_places=3)
    potrosnja = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    class Meta:
        unique_together = ["artikl", "datum"]
        ordering = ["-datum"]
        verbose_name = "Dnevno stanje"
        verbose_name_plural = "Dnevna stanja"

    def save(self, *args, **kwargs):
        prethodno = DnevnoStanje.objects.filter(
            artikl=self.artikl, datum__lt=self.datum
        ).order_by("-datum").first()

        if prethodno:
            razlika = prethodno.kolicina - self.kolicina
            self.potrosnja = razlika if razlika >= 0 else Decimal("0")
        else:
            self.potrosnja = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.artikl} — {self.datum}: {self.kolicina}"
# ─dobavljaci i racuni

class Dobavljac(models.Model):
    naziv         = models.CharField(max_length=200)
    oib           = models.CharField(max_length=11, blank=True)
    kontakt_osoba = models.CharField(max_length=150, blank=True)
    email         = models.EmailField(blank=True)
    telefon       = models.CharField(max_length=20, blank=True)
    adresa        = models.TextField(blank=True)
    aktivan       = models.BooleanField(default=True)

    class Meta:
        ordering = ["naziv"]
        verbose_name = "Dobavljač"
        verbose_name_plural = "Dobavljači"

    def __str__(self):
        return self.naziv


class Racun(models.Model):
    NEPLACENO = "NEPLACENO"
    PLACENO   = "PLACENO"
    STATUS_CHOICES = [
        (NEPLACENO, "Neplaćeno"),
        (PLACENO,   "Plaćeno"),
    ]

    dobavljac       = models.ForeignKey(Dobavljac, on_delete=models.PROTECT, related_name="racuni")
    broj_racuna     = models.CharField(max_length=100)
    datum_racuna    = models.DateField()
    datum_dospijeca = models.DateField(null=True, blank=True)
    ukupni_iznos    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NEPLACENO)
    napomena        = models.TextField(blank=True)

    class Meta:
        ordering = ["-datum_racuna"]
        verbose_name = "Račun"
        verbose_name_plural = "Računi"

    def __str__(self):
        return f"Račun {self.broj_racuna} — {self.dobavljac}"

class StavkaRacuna(models.Model):
    racun              = models.ForeignKey(Racun, on_delete=models.CASCADE, related_name="stavke")
    artikl             = models.ForeignKey(Artikl, on_delete=models.PROTECT, related_name="stavke_racuna")
    kolicina           = models.DecimalField(max_digits=10, decimal_places=3)
    cijena_po_jedinici = models.DecimalField(max_digits=10, decimal_places=2)
    ukupno             = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.ukupno = self.kolicina * self.cijena_po_jedinici
        super().save(*args, **kwargs)
   
        ukupno_racuna = sum(s.ukupno for s in self.racun.stavke.all())
        Racun.objects.filter(pk=self.racun.pk).update(ukupni_iznos=ukupno_racuna)
    
        stanje = DnevnoStanje.objects.filter(
            artikl=self.artikl, datum=self.racun.datum_racuna
        ).first()
        if stanje:
            stanje.kolicina += self.kolicina
            stanje.save()
        else:
            DnevnoStanje.objects.create(
                artikl=self.artikl,
                datum=self.racun.datum_racuna,
                kolicina=self.kolicina
        )

class Trosak(models.Model):
    kategorija = models.ForeignKey(Kategorija, on_delete=models.PROTECT, related_name="troskovi")
    naziv      = models.CharField(max_length=200)
    iznos      = models.DecimalField(max_digits=12, decimal_places=2)
    datum      = models.DateField()
    opis       = models.TextField(blank=True)

    class Meta:
        ordering = ["-datum"]
        verbose_name = "Trošak"
        verbose_name_plural = "Troškovi"

    def __str__(self):
        return f"{self.naziv} — {self.iznos} €"