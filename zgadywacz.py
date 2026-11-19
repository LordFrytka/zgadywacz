import json
import os
import random

plik_zapisu = "zapis.json"
ogolne_mmr = 200
ogolne_pkt = 0.0
dolary = 1000
ranga = "Brąz"
nierank_gry = 0
nierank_proby = 0
rank_gry = 0
rank_proby = 0
najwieksza_wygrana = 0
lacznie_wygrane = 0

def wczytaj_dane():
    global ogolne_mmr, ogolne_pkt, dolary, nierank_gry, nierank_proby, rank_gry, rank_proby, najwieksza_wygrana, lacznie_wygrane
    if os.path.exists(plik_zapisu):
        try:
            with open(plik_zapisu, "r", encoding="utf-8") as plik:
                dane = json.load(plik)
                ogolne_mmr = dane.get("ogolne_mmr", 200)
                ogolne_pkt = dane.get("ogolne_pkt", 0.0)
                dolary = dane.get("dolary", 1000)
                nierank_gry = dane.get("nierank_gry", 0)
                nierank_proby = dane.get("nierank_proby", 0)
                rank_gry = dane.get("rank_gry", 0)
                rank_proby = dane.get("rank_proby", 0)
                najwieksza_wygrana = dane.get("najwieksza_wygrana", 0)
                lacznie_wygrane = dane.get("lacznie_wygrane", 0)
        except Exception:
            pass

def zapisz_dane():
    dane = {
        "ogolne_mmr": ogolne_mmr,
        "ogolne_pkt": ogolne_pkt,
        "dolary": dolary,
        "nierank_gry": nierank_gry,
        "nierank_proby": nierank_proby,
        "rank_gry": rank_gry,
        "rank_proby": rank_proby,
        "najwieksza_wygrana": najwieksza_wygrana,
        "lacznie_wygrane": lacznie_wygrane
    }
    with open(plik_zapisu, "w", encoding="utf-8") as plik:
        json.dump(dane, plik, ensure_ascii=False, indent=4)

def menu():
    while True:
        print("\033c", end="")
        print(
            "---------------------\n"
            "      ZGADYWACZ      \n"
            "---------------------\n"
            "1. Start gry\n"
            "2. Ustawienia\n"
            "3. Dodatkowe opcje\n"
            "4. Wyjdź z gry\n"
            "---------------------\n"
        )
        try:
            opcja = int(input("Wybierz opcję (1-4): "))
        except ValueError:
            print("Wpisz cyfrę od 1 do 4!")
            input("Kliknij cokolwiek aby spróbować jeszcze raz...")
            continue
        if opcja == 1:
            tryby()
        elif opcja == 2:
            ustawienia()
        elif opcja == 3:
            dodatkowe()
        elif opcja == 4:
            zapisz_dane()
            print("Papa!")
            quit()

def tryby():
    while True:
        print("\033c", end="")
        print(
            "---------------------\n"
            "        TRYBY        \n"
            "---------------------\n"
            "1. Tryb nierankingowy\n"
            "2. Tryb rankingowy\n"
            "3. Tryb zakładowy\n"
            "4. Powrót do menu\n"
            "---------------------\n"
        )
        try:
            tryb = int(input("Wybierz opcję (1-4): "))
        except ValueError:
            print("Wpisz cyfrę od 1 do 4!")
            input("Kliknij cokolwiek aby spróbować jeszcze raz...")
            continue
        if tryb == 1:
            start(mode="unranked")
        elif tryb == 2:
            start(mode="ranked")
        elif tryb == 3:
            start(mode="wager")
        elif tryb == 4:
            menu()

def ustawienia():
    global ogolne_mmr, ogolne_pkt, dolary, nierank_gry, nierank_proby, rank_gry, rank_proby, najwieksza_wygrana, lacznie_wygrane
    while True:
        print("\033c", end="")
        print(
            "-------------------------------------\n"
            "              USTAWIENIA\n"
            "-------------------------------------\n"
            "1. Reset statystyk\n"
            "2. Powrót do menu\n"
            "-------------------------------------"
        )
        try:
            ustawienie = int(input("Wybierz opcję (1-2): "))
        except ValueError:
            print("Wpisz cyfrę od 1 do 2!")
            input("Kliknij cokolwiek aby spróbować jeszcze raz...")
            continue
        if ustawienie == 1:
            while True:
                potwierdzenie = input("Czy na pewno chcesz zresetować statystyki? (Napisz T aby zatwierdzić): ")
                if potwierdzenie == "T" or potwierdzenie == "t":
                    ogolne_mmr = 200
                    ogolne_pkt = 0.0
                    dolary = 1000
                    nierank_gry = 0
                    nierank_proby = 0
                    rank_gry = 0
                    rank_proby = 0
                    zapisz_dane()
                    print("Statystyki zostały zresetowane!")
                    input("Kliknij cokolwiek aby wrócić do menu...")
                    wczytaj_dane()
                    menu()
                else:
                    print("Anulowano reset statystyk!")
                    input("Kliknij cokolwiek aby wrócić do menu...")
                    menu()
        elif ustawienie == 2:
            menu()

def dodatkowe():
    while True:
        print("\033c", end="")
        print(
            "---------------------\n"
            "   OPCJE DODATKOWE\n"
            "---------------------\n"
            "1. Statystyki\n"
            "2. Informacje\n"
            "3. Nowości\n"
            "4. Powrót do menu\n"
            "---------------------\n"
        )
        try:
            wybor = int(input("Wybierz opcję (1-4): "))
        except ValueError:
            print("Wpisz cyfrę od 1 do 4!")
            input("Kliknij cokolwiek aby spróbować jeszcze raz...")
            continue
        if wybor == 1:
            statystyki()
        elif wybor == 2:
            informacje()
        elif wybor == 3:
            nowosci()
        elif wybor == 4:
            menu()

def start(mode):
    print("\033c", end="")
    global ogolne_pkt, ogolne_mmr, dolary, nierank_gry, nierank_proby, rank_gry, rank_proby, najwieksza_wygrana, lacznie_wygrane
    dzielnik = 1
    pkt = 100.0
    mmr = 0
    if mode == "unranked":
        min = int(input("Podaj minimalną liczbę do zgadywania (min 5): "))
        max = int(input("Podaj maksymalną liczbę do zgadywania (min 10): "))
        if min < 5 or max < 10 or min >= max:
            print("Źle wprowadzone dane!")
            input("Kliknij cokolwiek aby spróbować jeszcze raz...")
            start(mode="unranked")
    else:
        if mode == "wager":
            obstawione = int(input("Podaj ile chcesz obstawić dolarów (min 100): "))
            if obstawione < 100 or obstawione > dolary:
                print("Źle wprowadzone dane!")
                input("Kliknij cokolwiek aby spróbować jeszcze raz...")
                start(mode="wager")
            print("Twoja waluta zostanie podwojona jeżeli zgadniesz do 5 próby. Inaczej ją stracisz!")
        min = 10
        max = 100
    losowa = random.randint(min, max)
    liczba = 0
    print(f"Wylosowano liczbę z przedziału <{min};{max}>. Spróbuj zgadnąć!")

    if mode == "unranked" or mode == "ranked":
        while liczba != losowa:
            try:
                liczba = int(input("Twoja liczba: "))
            except ValueError:
                print("To musi być liczba!")
                continue
            if liczba == losowa:
                print("Gratulacje! Udało ci się zgadnąć!")
                if mode == "unranked":
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
    else:
        while dzielnik <= 5:
            try:
                liczba = int(input("Twoja liczba: "))
            except ValueError:
                print("To musi być liczba!")
                continue
            if liczba == losowa:
                print("Gratulacje! Udało ci się zgadnąć!")
                dolary += (obstawione * 2)
                lacznie_wygrane += (obstawione * 2)
                if najwieksza_wygrana < (obstawione * 2):
                    najwieksza_wygrana = obstawione * 2
                print(
                    f"Wygrywasz {obstawione * 2}$\n"
                    f"Łącznie masz {dolary}$"
                )
                input("\nKliknij cokolwiek aby wrócić do menu...")
                menu()
            else:
                dzielnik += 1
                if liczba == (losowa - 1) or liczba == (losowa + 1):
                    print("Jesteś bardzo blisko!")
                elif liczba < losowa:
                    print("Za mało!")
                elif liczba > losowa:
                    print("Za dużo!")
        dolary -= obstawione
        print(
            f"Skończyły ci się próby! Wylosowana liczba to: {losowa}\n"
            f"Przegrywasz {obstawione}$\n"
            f"Łącznie masz {dolary}$"
        )
        input("\nKliknij cokolwiek aby wrócić do menu...")
        menu()

def informacje():
    print("\033c", end="")
    print(
        "-------------------------------------------\n"
        "                INFORMACJE\n"
        "-------------------------------------------\n"
        "Zgadywacz to gra, w której musisz\n"
        "zgadnąć liczbę z danego przedziału.\n"
        "W trybie nierankingowym możesz ustalić\n"
        "przedział i zdobywać punkty ogólne.\n"
        "W trybie rankingowym jest ustalony\n"
        "na stałe przedział między 10, a 100.\n"
        "Dodatkowo w trybie rankingowym dostajesz\n"
        "punkty rankingowe, dzięki którym możesz\n"
        "zdobywać rangi, np. srebro za 1000 punktów.\n"
        "Możesz również zagrać w tryb zakładowy,\n"
        "gdzie obstawiasz dolary, że do 5 próby \n"
        "zgadniesz liczbę. Jeżeli przegrasz, tracisz\n"
        "walutę, a jeżeli wygrasz, to dostaniesz\n"
        "w nagrodę podwojoną wartość obstawioną.\n"
        "-------------------------------------------"
    )
    input("Kliknij cokolwiek aby wrócić do menu...")
    menu()

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
        "--------------------------\n"
        "        STATYSTYKI\n"
        "--------------------------\n"
        "NIERANKINGOWE:\n"
        f"Zdobyte punkty: {ogolne_pkt:.2f}\n"
        f"Średnia ilość prób: {srednia_nierank:.2f}\n\n"
        "RANKINGOWE:\n"
        f"Aktualna ranga: {zaladuj_range()}\n"
        f"Punkty rankingowe: {ogolne_mmr}\n"
        f"Średnia ilość prób: {srednia_rank:.2f}\n\n"
        "ZAKŁADY:\n"
        f"Saldo: {dolary}$\n"
        f"Największa wygrana: {najwieksza_wygrana}$\n"
        f"Łącznie wygrane: {lacznie_wygrane}$\n"
        "--------------------------"
    )
    input("Kliknij cokolwiek aby wrócić do menu...")
    menu()

def nowosci():
    print("\033c", end="")
    print(
        "-----------------------------------------------\n"
        "                   NOWOŚCI\n"
        "-----------------------------------------------\n"
        "WERSJA 1.1:\n"
        "- Dodano tryb zakładów i walutę do trybu\n"
        "- Dodano zakładkę z dodatkowymi opcjami\n"
        "- Dodano resetowanie statystyk w ustawieniach\n"
        "- Naprawiono błędy z brakiem powrotu do menu\n"
        "-----------------------------------------------"
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
