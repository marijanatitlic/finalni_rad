from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal
from datetime import date

from .models import (
    Pozicija, Zaposlenik, Ugovor, EvidencijaRada, BonusOdbitak, ObracunPlace,
    Kategorija, JedinicaMjere, Artikl, DnevnoStanje,
    Dobavljac, Racun, Trosak
)
from .forms import (
    ZaposlenikForma, UgovorForma, EvidencijaRadaForma, BonusOdbitakForma,
    ArtiklForma, DnevnoStanjeForma, DobavljacForma, RacunForma,
    TrosakForma, PozicijaForma, KategorijaForma, JedinicaMjereForma, StavkaRacuna, StavkaRacunaForma
)


#dasbord

@login_required
def dashboard(request):
    danas = date.today()
    mjesec = int(request.GET.get('mjesec', danas.month))
    godina = int(request.GET.get('godina', danas.year))


    artikli_alarm= [a for a in Artikl.objects.filter(aktivan=True) if a.ispod_minimuma()]

    
    zaposlenici = Zaposlenik.objects.filter(aktivan=True).select_related('pozicija').prefetch_related('ugovori', 'evidencije', 'obracuni')

    artikli = Artikl.objects.filter(aktivan=True).select_related('jedinica_mjere')
    potrosnja_artikala = []
    for artikl in artikli:
        dnevno = artikl.dnevna_stanja.order_by('-datum').first()
        mjesecna = artikl.dnevna_stanja.filter(
            datum__month=mjesec, datum__year=godina
        ).aggregate(ukupno=Sum('potrosnja'))['ukupno'] or Decimal('0')
        potrosnja_artikala.append({
            'artikl':          artikl,
            'dnevna_potrosnja': dnevno.potrosnja if dnevno and dnevno.potrosnja else Decimal('0'),
            'mjesecna_potrosnja': mjesecna,
        })

    
    troskovi_mjesec = Trosak.objects.filter(
        datum__month=mjesec, datum__year=godina
    ).aggregate(ukupno=Sum('iznos'))['ukupno'] or Decimal('0')

    racuni_mjesec = Racun.objects.filter(
        datum_racuna__month=mjesec, datum_racuna__year=godina
    ).aggregate(ukupno=Sum('ukupni_iznos'))['ukupno'] or Decimal('0')

    place_mjesec = ObracunPlace.objects.filter(
    mjesec=mjesec, godina=godina
    ).aggregate(ukupno=Sum('za_isplatu'))['ukupno'] or Decimal('0')
    
    ukupni_troskovi = troskovi_mjesec + racuni_mjesec + place_mjesec
    top_artikli = StavkaRacuna.objects.filter(
       racun__datum_racuna__month=mjesec,
        racun__datum_racuna__year=godina
    ).values('artikl__naziv', 'artikl__jedinica_mjere__naziv').annotate(
        ukupna_kolicina=Sum('kolicina')
    ).order_by('-ukupna_kolicina')[:5]

    return render(request, 'core/dashboard.html', {
        'artikli_alarm':        artikli_alarm,
        'zaposlenici':          zaposlenici,
        'potrosnja_artikala':   potrosnja_artikala,
        'troskovi_mjesec':      troskovi_mjesec,
        'racuni_mjesec':        racuni_mjesec,
        'place_mjesec':         place_mjesec,
        'ukupni_troskovi':      ukupni_troskovi,
        'mjesec':               mjesec,
        'godina':               godina,
        'top_artikli': top_artikli,
    })


# zaposlenici

@login_required
def zaposlenici(request):
    lista = Zaposlenik.objects.select_related('pozicija').prefetch_related('ugovori').all()
    return render(request, 'core/zaposlenici.html', {'zaposlenici': lista})
@login_required
def zaposlenik_forma(request, pk=None):
    zaposlenik = get_object_or_404(Zaposlenik, pk=pk) if pk else None
    ugovor = Ugovor.objects.filter(zaposlenik=zaposlenik).first() if zaposlenik else None

    if request.method == 'POST':
        z_forma = ZaposlenikForma(request.POST, instance=zaposlenik)
        u_forma = UgovorForma(request.POST, instance=ugovor)
        if z_forma.is_valid() and u_forma.is_valid():
            zaposlenik        = z_forma.save()
            ugovor            = u_forma.save(commit=False)
            ugovor.zaposlenik = zaposlenik
            ugovor.aktivan    = True
            ugovor.save()
            messages.success(request, 'Zaposlenik uspješno spremljen.')
            return redirect('zaposlenici')
    else:
        z_forma = ZaposlenikForma(instance=zaposlenik)
        u_forma = UgovorForma(instance=ugovor)

    return render(request, 'core/zaposlenik_forma.html', {
        'z_forma':    z_forma,
        'u_forma':    u_forma,
        'zaposlenik': zaposlenik,
    })


@login_required
def zaposlenik_obrisi(request, pk):
    zaposlenik = get_object_or_404(Zaposlenik, pk=pk)
    if request.method == 'POST':
        zaposlenik.delete()
        messages.success(request, 'Zaposlenik obrisan.')
    return redirect('zaposlenici')


#evidencija

@login_required
def evidencija(request):
    mjesec = int(request.GET.get('mjesec', date.today().month))
    godina = int(request.GET.get('godina', date.today().year))
    lista  = EvidencijaRada.objects.filter(
        datum__month=mjesec, datum__year=godina
    ).select_related('zaposlenik').order_by('zaposlenik', 'datum')
    return render(request, 'core/evidencija.html', {
        'evidencije': lista,
        'mjesec':     mjesec,
        'godina':     godina,
    })


@login_required
def evidencija_forma(request, pk=None):
    evidencija = get_object_or_404(EvidencijaRada, pk=pk) if pk else None

    if request.method == 'POST':
        forma = EvidencijaRadaForma(request.POST, instance=evidencija)
        if forma.is_valid():
            forma.save()
            messages.success(request, 'Evidencija rada uspješno spremljena.')
            return redirect('evidencija')
    else:
        forma = EvidencijaRadaForma(instance=evidencija)

    return render(request, 'core/evidencija_forma.html', {
        'forma':      forma,
        'evidencija': evidencija,
    })


@login_required
def evidencija_obrisi(request, pk):
    evidencija = get_object_or_404(EvidencijaRada, pk=pk)
    if request.method == 'POST':
        evidencija.delete()
        messages.success(request, 'Evidencija obrisana.')
    return redirect('evidencija')


@login_required
def bonus_forma(request, zaposlenik_pk, mjesec, godina):
    zaposlenik = get_object_or_404(Zaposlenik, pk=zaposlenik_pk)
    bonusi     = BonusOdbitak.objects.filter(
        zaposlenik=zaposlenik, mjesec=mjesec, godina=godina
    )

    if request.method == 'POST':
        forma = BonusOdbitakForma(request.POST)
        if forma.is_valid():
            bonus = forma.save(commit=False)
            bonus.zaposlenik = zaposlenik
            bonus.mjesec     = mjesec
            bonus.godina     = godina
            bonus.save()
            messages.success(request, 'Bonus/odbitak dodan.')
            return redirect('bonus_dodaj', zaposlenik_pk=zaposlenik_pk, mjesec=mjesec, godina=godina)
    else:
        forma = BonusOdbitakForma()

    return render(request, 'core/evidencija_forma.html', {
        'forma':       forma,
        'zaposlenik':  zaposlenik,
        'bonusi':      bonusi,
        'bonus_mod':   True,
        'mjesec':      mjesec,
        'godina':      godina,
    })


@login_required
def obracun(request, zaposlenik_pk, miesec, godina):
    zaposlenik = get_object_or_404(Zaposlenik, pk=zaposlenik_pk)
    postojeci  = ObracunPlace.objects.filter(
        zaposlenik=zaposlenik, miesec=miesec, godina=godina
    ).first()

    if request.method == 'POST' and not postojeci:
        # Dohvati sve evidencije za taj mjesec
        evidencije = EvidencijaRada.objects.filter(
            zaposlenik=zaposlenik,
            datum__month=miesec,
            datum__year=godina
        )
        ukupni_sati = sum(ev.sati for ev in evidencije)

        # Dohvati ugovor
        ugovor = Ugovor.objects.filter(zaposlenik=zaposlenik).first()

        # Izračunaj osnovnu plaću
        if ugovor.tip == Ugovor.STUDENTSKI:
            osnovna = ukupni_sati * ugovor.satnica
        else:
            osnovna = ugovor.fiksna_placa

        # Bonusi i odbitci
        stavke  = BonusOdbitak.objects.filter(
            zaposlenik=zaposlenik, miesec=miesec, godina=godina
        )
        dodaci  = sum(s.iznos for s in stavke if s.tip == BonusOdbitak.BONUS) or Decimal('0')
        odbitci = sum(s.iznos for s in stavke if s.tip == BonusOdbitak.ODBITAK) or Decimal('0')

        postojeci = ObracunPlace.objects.create(
            zaposlenik     = zaposlenik,
            miesec         = miesec,
            godina         = godina,
            ukupni_sati    = ukupni_sati,
            osnovna_placa  = osnovna,
            ukupni_dodaci  = dodaci,
            ukupni_odbitci = odbitci,
            za_isplatu     = max(osnovna + dodaci - odbitci, Decimal('0')),
        )
        messages.success(request, 'Obračun uspješno generiran.')

    return render(request, 'core/obracun.html', {
        'zaposlenik': zaposlenik,
        'obracun':    postojeci,
        'miesec':     miesec,
        'godina':     godina,
    })

# inventar

@login_required
def inventar(request):
    artikli = Artikl.objects.select_related('kategorija', 'jedinica_mjere').filter(aktivan=True)
    return render(request, 'core/inventar.html', {'artikli': artikli})


@login_required
def artikl_forma(request, pk=None):
    artikl = get_object_or_404(Artikl, pk=pk) if pk else None

    if request.method == 'POST':
        forma = ArtiklForma(request.POST, instance=artikl)
        if forma.is_valid():
            forma.save()
            messages.success(request, 'Artikl uspješno spremljen.')
            return redirect('inventar')
    else:
        forma = ArtiklForma(instance=artikl)

    return render(request, 'core/artikl_forma.html', {'forma': forma, 'artikl': artikl})


@login_required
def artikl_obrisi(request, pk):
    artikl         = get_object_or_404(Artikl, pk=pk)
    artikl.aktivan = False
    artikl.save()
    messages.success(request, 'Artikl deaktiviran.')
    return redirect('inventar')


@login_required
def dnevno_stanje_forma(request):
    artikli = Artikl.objects.filter(aktivan=True).select_related('jedinica_mjere')

    if request.method == 'POST':
        datum = request.POST.get('datum')
        for artikl in artikli:
            kolicina = request.POST.get(f'kolicina_{artikl.pk}')
            if kolicina:
                DnevnoStanje.objects.update_or_create(
                    artikl=artikl,
                    datum=datum,
                    defaults={
                        'kolicina': Decimal(kolicina),
                        
                    }
                )
        messages.success(request, 'Dnevno stanje uspješno uneseno.')
        return redirect('inventar')

    return render(request, 'core/dnevno_stanje.html', {'artikli': artikli})

@login_required
def dobavljaci(request):
    lista = Dobavljac.objects.filter(aktivan=True)
    return render(request, 'core/dobavljaci.html', {'dobavljaci': lista})


@login_required
def dobavljac_forma(request, pk=None):
    dobavljac = get_object_or_404(Dobavljac, pk=pk) if pk else None

    if request.method == 'POST':
        forma = DobavljacForma(request.POST, instance=dobavljac)
        if forma.is_valid():
            forma.save()
            messages.success(request, 'Dobavljač uspješno spremljen.')
            return redirect('dobavljaci')
    else:
        forma = DobavljacForma(instance=dobavljac)

    return render(request, 'core/dobavljac_forma.html', {'forma': forma, 'dobavljac': dobavljac})


@login_required
def dobavljac_obrisi(request, pk):
    dobavljac         = get_object_or_404(Dobavljac, pk=pk)
    dobavljac.aktivan = False
    dobavljac.save()
    messages.success(request, 'Dobavljač deaktiviran.')
    return redirect('dobavljaci')


#racuni

@login_required
def racuni(request):
    lista = Racun.objects.select_related('dobavljac').all()
    return render(request, 'core/racuni.html', {'racuni': lista})


@login_required
def racun_forma(request, pk=None):
    racun = get_object_or_404(Racun, pk=pk) if pk else None

    if request.method == 'POST':
        forma = RacunForma(request.POST, instance=racun)
        if forma.is_valid():
            forma.save()
            messages.success(request, 'Račun uspješno spremljen.')
            return redirect('racuni')
    else:
        forma = RacunForma(instance=racun)

    return render(request, 'core/racun_forma.html', {'forma': forma, 'racun': racun})


@login_required
def racun_obrisi(request, pk):
    racun = get_object_or_404(Racun, pk=pk)
    racun.delete()
    messages.success(request, 'Račun obrisan.')
    return redirect('racuni')


@login_required
def racun_plati(request, pk):
    racun        = get_object_or_404(Racun, pk=pk)
    racun.status = Racun.PLACENO
    racun.save()
    messages.success(request, 'Račun označen kao plaćen.')
    return redirect('racuni')

@login_required
def racun_stavke(request, pk):
    racun  = get_object_or_404(Racun, pk=pk)
    stavke = racun.stavke.all()

    if request.method == 'POST':
        forma = StavkaRacunaForma(request.POST)
        if forma.is_valid():
            stavka       = forma.save(commit=False)
            stavka.racun = racun
            stavka.save()
            messages.success(request, 'Stavka dodana.')
            return redirect('racun_stavke', pk=pk)
    else:
        forma = StavkaRacunaForma()

    return render(request, 'core/racun_stavke.html', {
        'racun':  racun,
        'stavke': stavke,
        'forma':  forma,
    })

# troskovi

@login_required
def troskovi(request):
    mjesec = int(request.GET.get('mjesec', date.today().month))
    godina = int(request.GET.get('godina', date.today().year))
    lista  = Trosak.objects.filter(
        datum__month=mjesec, datum__year=godina
    ).select_related('kategorija')
    ukupno = lista.aggregate(ukupno=Sum('iznos'))['ukupno'] or Decimal('0')
    return render(request, 'core/troskovi.html', {
        'troskovi': lista,
        'ukupno':   ukupno,
        'mjesec':   mjesec,
        'godina':   godina,
    })


@login_required
def trosak_forma(request, pk=None):
    trosak = get_object_or_404(Trosak, pk=pk) if pk else None

    if request.method == 'POST':
        forma = TrosakForma(request.POST, instance=trosak)
        if forma.is_valid():
            forma.save()
            messages.success(request, 'Trošak uspješno spremljen.')
            return redirect('troskovi')
    else:
        forma = TrosakForma(instance=trosak)

    return render(request, 'core/trosak_forma.html', {'forma': forma, 'trosak': trosak})


@login_required
def trosak_obrisi(request, pk):
    trosak = get_object_or_404(Trosak, pk=pk)
    trosak.delete()
    messages.success(request, 'Trošak obrisan.')
    return redirect('troskovi')


# postavke za dodat kategorije il jedinicu mjere i poziciju

@login_required
def postavke(request):
    pozicije   = Pozicija.objects.all()
    kategorije = Kategorija.objects.all()
    jedinice   = JedinicaMjere.objects.all()
    return render(request, 'core/postavke.html', {
        'pozicije':   pozicije,
        'kategorije': kategorije,
        'jedinice':   jedinice,
    })


@login_required
def pozicija_forma(request, pk=None):
    pozicija = get_object_or_404(Pozicija, pk=pk) if pk else None
    if request.method == 'POST':
        forma = PozicijaForma(request.POST, instance=pozicija)
        if forma.is_valid():
            forma.save()
            messages.success(request, 'Pozicija uspješno spremljena.')
            return redirect('postavke')
    else:
        forma = PozicijaForma(instance=pozicija)
    return render(request, 'core/postavke.html', {'forma': forma, 'aktivan_tab': 'pozicije'})


@login_required
def pozicija_obrisi(request, pk):
    pozicija = get_object_or_404(Pozicija, pk=pk)
    if request.method == 'POST':
        pozicija.delete()
        messages.success(request, 'Pozicija obrisana.')
    return redirect('postavke')


@login_required
def kategorija_forma(request, pk=None):
    kategorija = get_object_or_404(Kategorija, pk=pk) if pk else None
    if request.method == 'POST':
        forma = KategorijaForma(request.POST, instance=kategorija)
        if forma.is_valid():
            forma.save()
            messages.success(request, 'Kategorija uspješno spremljena.')
            return redirect('postavke')
    else:
        forma = KategorijaForma(instance=kategorija)
    return render(request, 'core/postavke.html', {'forma': forma, 'aktivan_tab': 'kategorije'})


@login_required
def kategorija_obrisi(request, pk):
    kategorija = get_object_or_404(Kategorija, pk=pk)
    if request.method == 'POST':
        kategorija.delete()
        messages.success(request, 'Kategorija obrisana.')
    return redirect('postavke')


@login_required
def jedinica_forma(request, pk=None):
    jedinica = get_object_or_404(JedinicaMjere, pk=pk) if pk else None
    if request.method == 'POST':
        forma = JedinicaMjereForma(request.POST, instance=jedinica)
        if forma.is_valid():
            forma.save()
            messages.success(request, 'Jedinica mjere uspješno spremljena.')
            return redirect('postavke')
    else:
        forma = JedinicaMjereForma(instance=jedinica)
    return render(request, 'core/postavke.html', {'forma': forma, 'aktivan_tab': 'jedinice'})


@login_required
def jedinica_obrisi(request, pk):
    jedinica = get_object_or_404(JedinicaMjere, pk=pk)
    if request.method == 'POST':
        jedinica.delete()
        messages.success(request, 'Jedinica mjere obrisana.')
    return redirect('postavke')