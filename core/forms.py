from django import forms
from .models import (
    Pozicija, Zaposlenik, Ugovor, EvidencijaRada, BonusOdbitak,
    Artikl, DnevnoStanje, Dobavljac, Racun,
    Trosak, Kategorija, JedinicaMjere
)
from datetime import date

class ZaposlenikForma(forms.ModelForm):
    class Meta:
        model  = Zaposlenik
        fields = ['ime', 'prezime', 'oib', 'email', 'telefon', 'pozicija', 'datum_zaposlenja']
        widgets = {
            'datum_zaposlenja': forms.DateInput(attrs={'type': 'date'}),
        }


class UgovorForma(forms.ModelForm):
    class Meta:
        model  = Ugovor
        fields = ['tip', 'satnica', 'fiksna_placa']



class EvidencijaRadaForma(forms.ModelForm):
    class Meta:
        model  = EvidencijaRada
        fields = ['zaposlenik', 'mjesec', 'godina', 'ostvareni_sati', 'napomena']

    def clean(self):
        cleaned_data = super().clean()
        mjesec = cleaned_data.get('mjesec')
        godina = cleaned_data.get('godina')
        danas  = date.today()

        if godina and (godina < 2000 or godina > danas.year):
            self.add_error('godina', f'Godina mora biti između 2000 i {danas.year}.')
        if mjesec and (mjesec < 1 or mjesec > 12):
            self.add_error('mjesec', 'Mjesec mora biti između 1 i 12.')

        return cleaned_data

class BonusOdbitakForma(forms.ModelForm):
    class Meta:
        model  = BonusOdbitak
        fields = ['tip', 'iznos', 'opis']


class ArtiklForma(forms.ModelForm):
    class Meta:
        model  = Artikl
        fields = ['naziv', 'kategorija', 'jedinica_mjere', 'minimalna_razina']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kategorija'].queryset = Kategorija.objects.filter(tip=Kategorija.ARTIKL)

class DnevnoStanjeForma(forms.ModelForm):
    class Meta:
        model  = DnevnoStanje
        fields = ['artikl', 'datum', 'kolicina']
        widgets = {
            'datum': forms.DateInput(attrs={'type': 'date'}),
        }


class DobavljacForma(forms.ModelForm):
    class Meta:
        model  = Dobavljac
        fields = ['naziv', 'oib', 'kontakt_osoba', 'email', 'telefon', 'adresa']
        widgets = {
            'adresa': forms.Textarea(attrs={'rows': 3}),
        }


class RacunForma(forms.ModelForm):
    class Meta:
        model  = Racun
        fields = ['dobavljac', 'broj_racuna', 'datum_racuna', 'datum_dospijeca','ukupni_iznos', 'status', 'napomena']
        widgets = {
            'datum_racuna':    forms.DateInput(attrs={'type': 'date'}),
            'datum_dospijeca': forms.DateInput(attrs={'type': 'date'}),
            'napomena':        forms.Textarea(attrs={'rows': 3}),
        }




class TrosakForma(forms.ModelForm):
    class Meta:
        model  = Trosak
        fields = ['naziv', 'kategorija', 'iznos', 'datum', 'opis']
        widgets = {
            'datum': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'opis':  forms.Textarea(attrs={'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kategorija'].queryset = Kategorija.objects.filter(tip=Kategorija.TROSAK)


class KategorijaForma(forms.ModelForm):
    class Meta:
        model  = Kategorija
        fields = ['naziv', 'tip']


class JedinicaMjereForma(forms.ModelForm):
    class Meta:
        model  = JedinicaMjere
        fields = ['naziv']


class PozicijaForma(forms.ModelForm):
    class Meta:
        from .models import Pozicija
        model  = Pozicija
        fields = ['naziv']


# botstrap klase na ova polja
for forma_klasa in [ZaposlenikForma, UgovorForma, EvidencijaRadaForma, 
                     BonusOdbitakForma, ArtiklForma, DnevnoStanjeForma,
                     DobavljacForma, RacunForma, TrosakForma, 
                     KategorijaForma, JedinicaMjereForma, PozicijaForma]:
    for field in forma_klasa.base_fields.values():
        if hasattr(field.widget, 'attrs'):
            field.widget.attrs.update({'class': 'form-control'})