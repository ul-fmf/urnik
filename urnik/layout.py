def razdeli_srecanja_po_dneh(srecanja):
    dnevi = {}
    for srecanje in srecanja:
        dnevi.setdefault(srecanje.dan, []).append(srecanje)
    return dnevi.values()


def razdeli_dan_na_skupine(srecanja):
    skupina, konec_zadnjega_srecanja = [], None

    for srecanje in srecanja:
        # Če se naslednje srečanje začne za koncem vseh prejšnjih, zaključimo
        # skupino.
        if konec_zadnjega_srecanja is not None and srecanje.ura >= konec_zadnjega_srecanja:
            yield skupina
            skupina, konec_zadnjega_srecanja = [], None

        # Vstavimo v prvi stolpec, kjer je prostor. Če ga ni, dodamo novega.
        for stolpec in skupina:
            if stolpec[-1].ura + stolpec[-1].trajanje <= srecanje.ura:
                stolpec.append(srecanje)
                break
        else:
            skupina.append([srecanje])

        # Popravimo konec zadnjega srečanja.
        konec = srecanje.ura + srecanje.trajanje
        if konec_zadnjega_srecanja is None or konec > konec_zadnjega_srecanja:
            konec_zadnjega_srecanja = konec

    if skupina:
        yield skupina


def nastavi_sirine_srecanj(srecanja):
    for srecanja_dneva in razdeli_srecanja_po_dneh(srecanja):
        for skupina in razdeli_dan_na_skupine(srecanja_dneva):
            for i, stolpec in enumerate(skupina):
                for srecanje in stolpec:
                    srecanje.sirina = 1 / len(skupina)
                    srecanje.zamik = i / len(skupina)
    return srecanja
