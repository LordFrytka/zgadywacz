import json
import os
import random

plik_zapisu = "zapis.json"
ogolne_mmr = 200
ogolne_pkt = 0.0
ranga = "Brąz"
nierank_gry = 0
nierank_proby = 0
rank_gry = 0
rank_proby = 0

def wczytaj_dane():
    global ogolne_mmr, ogolne_pkt, nierank_gry, nierank_proby, rank_gry, rank_proby
    if os.path.exists(plik_zapisu):
        try:
            with open(plik_zapisu, "r", encoding="utf-8") as plik:
                dane = json.load(plik)
                ogolne_mmr = dane.get("ogolne_mmr", 200)
                ogolne_pkt = dane.get("ogolne_pkt", 0.0)
                nierank_gry = dane.get("nierank_gry", 0)
                nierank_proby = dane.get("nierank_proby", 0)
                rank_gry = dane.get("rank_gry", 0)
                rank_proby = dane.get("rank_proby", 0)
        except Exception:
            pass

def zapisz_dane():
    dane = {
        "ogolne_mmr": ogolne_mmr,
        "ogolne_pkt": ogolne_pkt,
        "nierank_gry": nierank_gry,
        "nierank_proby": nierank_proby,
        "rank_gry": rank_gry,
        "rank_proby": rank_proby,
    }
    with open(plik_zapisu, "w", encoding="utf-8") as plik:
        json.dump(dane, plik, ensure_ascii=False, indent=4)

def menu():
    while True:
        print("\033c", end="")
        print(
            "----------------------\n"
            "1. Tryb nierankingowy\n"
            "2. Tryb rankingowy\n"
            "3. Informacje o grze\n"
            "4. Statystyki\n"
            "5. Wyjdź z gry\n"
            "----------------------\n"
        )
        try:
            opcja = int(input("Wybierz opcję (1-5): "))
        except ValueError:
            print("Wpisz cyfrę od 1 do 5!")
            input("Kliknij cokolwiek aby spróbować jeszcze raz...")
            continue
        if opcja == 1:
            start(ranked=False)
        elif opcja == 2:
            start(ranked=True)
        elif opcja == 3:
            informacje()
        elif opcja == 4:
            statystyki()
        elif opcja == 5:
            zapisz_dane()
            print("Papa!")
            break

def start(ranked):
    print("\033c", end="")
    global ogolne_pkt, ogolne_mmr, nierank_gry, nierank_proby, rank_gry, rank_proby
    dzielnik = 1
    pkt = 100.0
    mmr = 0
    if ranked == False:
        min = int(input("Podaj minimalną liczbę do zgadywania (min 5): "))
        max = int(input("Podaj maksymalną liczbę do zgadywania (min 10): "))
        if min < 5 or max < 10 or min >= max:
            print("Źle wprowadzone dane!")
            input("Kliknij cokolwiek aby spróbować jeszcze raz...")
            return
    else:
        min = 10
        max = 100
    losowa = random.randint(min, max)
    liczba = 0
    print(f"Wylosowano liczbę z przedziału <{min};{max}>. Spróbuj zgadnąć!")

    while liczba != losowa:
        try:
            liczba = int(input("Twoja liczba: "))
        except ValueError:
            print("To musi być liczba!")
            continue
        if liczba == losowa:
            print("Gratulacje! Udało ci się zgadnąć!")
            if ranked == False:
                pkt = pkt / dzielnik
                ogolne_pkt += pkt
                nierank_gry += 1
                nierank_proby += dzielnik
                print(f"Zdobywasz {pkt:.2f} punktów!")
            else:
                mmr = 30 - (5 * dzielnik)
                ogolne_mmr += mmr
                rank_gry += 1
                rank_proby += dzielnik
                print(
                    f"Zdobywasz {mmr} punktów rankingowych!\n"
                    f"Twoja aktualna ranga: {zaladuj_range()}"
                )
                zapisz_dane()
        else:
            dzielnik += 1
            if liczba == (losowa - 1) or liczba == (losowa + 1):
                print("Jesteś bardzo blisko!")
            elif liczba < losowa:
                print("Za mało!")
            elif liczba > losowa:
                print("Za dużo!")
    input("\nKliknij cokolwiek aby wrócić do menu...")
    menu()

def informacje():
    print("\033c", end="")
    print(
        "-----------------------------------------------\n"
        "Zgadywacz to gra, w której musisz\n"
        "zgadnąć liczbę z danego przedziału.\n"
        "W trybie nierankingowym możesz ustalić\n"
        "przedział i zdobywać punkty ogólne.\n"
        "W trybie rankingowym jest ustalony\n"
        "na stałe przedział między 10, a 100.\n"
        "Dodatkowo w trybie rankingowym dostajesz\n"
        "punkty rankingowe, dzięki którym możesz\n"
        "zdobywać rangi, np. srebro za 1000 punktów.\n"
        "-----------------------------------------------"
    )
    input("Kliknij cokolwiek aby wrócić do menu...")


def statystyki():
    if nierank_gry > 0:
        srednia_nierank = nierank_proby / nierank_gry
    else:
        srednia_nierank = 0
    if rank_gry > 0:
        srednia_rank = rank_proby / rank_gry
    else:
        srednia_rank = 0
    print("\033c", end="")
    print(
        "----------------------\n"
        "NIERANKINGOWE:\n"
        f"Zdobyte punkty: {ogolne_pkt:.2f}\n"
        f"Średnia ilość prób: {srednia_nierank:.2f}\n\n"
        "RANKINGOWE:\n"
        f"Aktualna ranga: {zaladuj_range()}\n"
        f"Punkty rankingowe: {ogolne_mmr}\n"
        f"Średnia ilość prób: {srednia_rank:.2f}\n"
        "----------------------"
    )
    input("Kliknij cokolwiek aby wrócić do menu...")
    menu()

def zaladuj_range():
    global ogolne_mmr
    if ogolne_mmr <= 0:
        ogolne_mmr = 0
        return "Stracono"
    elif ogolne_mmr < 500:
        return "Brąz"
    elif 500 <= ogolne_mmr < 1000:
        return "Srebro"
    elif 1000 <= ogolne_mmr < 1500:
        return "Złoto"
    elif 1500 <= ogolne_mmr < 2000:
        return "Platyna"
    elif 2000 <= ogolne_mmr < 2500:
        return "Diament"
    else:
        return "Master Zgadywacz"

wczytaj_dane()
menu()

# MADE BY FRYTA