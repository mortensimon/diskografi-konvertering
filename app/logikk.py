
# Filtreringsmuligheter på label, artistnavn og opphavsmenn (author) (også deler av disse)

# 2023 / 2025 Tore Simonsen

import pandas as pd
import InDesign_C as C
import InDesign_RLC as RLC
import InDesign_MXC as MXC
import DiscoFunc
import numpy as np
import os
from os import path

# Windows GUI
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

# globale variable
fil = ""
ext = ""
label = ""
artname = ""
authname = ""
tell = ""

def get_rightmost_numeric_element(s):
    # Split the string into words
    words = s.split()

    # Reverse the list to start from the right
    words.reverse()

    # Iterate over the reversed list
    for word in words:
        # Check if the word is numeric
        if word.isdigit():
            # Return the numeric word
            return word

    # If no numeric element is found, return 0
    return 0

# Denne rutinen leser en csv-eksport fra DiscoM og skriver en tagged txt kompakt Indesign-format i release-rekkefølge
def runRL():

    global fil
    global ext
    global tell

    # øker størrelse på celler og antall kolonner
    pd.options.display.max_columns = None
    pd.options.display.max_colwidth = 200

    # webadresse for labelfotos
    web = "https\:\/\/www.historisklyd.no\/labels\/"

    # filnavn
    discofile = fil + ext
    outputfile = fil + " RL tag.txt"

    # leser en CSV-fil til en DataFrame, gjør blanke celler om til tomme strenger, leser "RelMedium" og "CatNo1" som tekststreng
    disco = pd.read_csv(discofile, keep_default_na=False, dtype={"RelMedium": str, "CatNo1": str})

    # les inn søkestrenger, blank betyr velg alt
    label = ""
    artname = ""
    authname = ""

    # filtrerer på label-/artist-/authornavn og lager en ny dataframe ("takes") av kun de aktuelle radene
    takes = disco.loc[disco['Label'].str.contains(label, case=False)].copy()
    # og, logisk AND
    takes = takes.loc[disco['Artists'].str.contains(artname, case = False)].copy()
    # og, logisk AND
    takes = takes.loc[disco['Authors'].str.contains(authname, case = False)].copy()

    # lager en ny kolonne for den numeriske delen av CatNo1 for å bruken den til sortering
    takes["CatNo1sort"] = takes["CatNo1"].apply(get_rightmost_numeric_element)
    takes["CatNo1sort"] = takes["CatNo1sort"].astype(int)

    # fjerner alle rader uten Label
    takes["Label"].replace("", np.nan, inplace = True)
    takes = takes.dropna()

    # takes sorteres i releaserekkefølge
    takes.sort_values(["Label","CatNo1sort","Mx1"], axis = 0, ascending=True, inplace=True, na_position='first')

    # legger på en ekstra rad med blank Label slik at løkken nedenfor ikke stopper for tidlig
    new_row = pd.DataFrame({"Label": [""]}, index = [len(takes)])
    takes = pd.concat([takes, new_row], ignore_index = True)

    # setter startverdier fra den første raden i det sorterte settet
    oldlabel = takes.iloc[0]["Label"]
    oldrelease = takes.iloc[0]["CatNo1"]

    # åpner fil for utskrift til InDesign tagged txt format

    with open(outputfile, "w", encoding="utf-16") as f:

        # skriv definisjoner
        print(C.Code, file = f)
        print(C.Intro, file = f)
        print(C.CharStyleLight, file = f)
        print(C.CharStyleLightItalic, file = f)
        print(C.CharStyleRegular, file = f)
        print(C.CharStyleBold, file = f)
        print(C.HyperLink, file = f)
        print(C.FontNorm, file = f)

        print(RLC.FontRelease, file = f)
        print(RLC.FontRecording, file = f)
        print(RLC.FontWork, file = f)
        print(RLC.FontAuthors, file = f)
        print(RLC.FontArtists, file = f)
        print(RLC.TableDef, file = f)

        # loop gjennom takes i sortert rekkefølge

        for ind in takes.index:
            thislabel = takes["Label"][ind]
            thisrelease = takes["CatNo1"][ind]
            thisaltrelease = takes["CatNo2"][ind]
            thismedium = takes["RelMedium"][ind]

            # nytt katalognummer?
            if thisrelease != oldrelease:

                # da skal de foregående rader (med CatNo1 = oldrelease) gjøres klar for output
                # lag en ny dataframe (release) med kun disse og merk antall rader
                release = takes.loc[takes['CatNo1'] == oldrelease]
                rows = len(release)

                # kolonne 1 i InDesign-tabellen (med oldrelease) genereres
                col1 = RLC.Release + RLC.TableStart1 + str(rows) + RLC.TableStart2 + RLC.CellStart + str(rows) + ",1>" + RLC.Release + oldlabel + "\n" + oldrelease + "\n" + C.CharLight + oldmedium + C.CellEnd

                # InDesign radskille og kolonne 2/3 nullstilles
                skille = ""
                col23 = ""

                # loop gjennom release
                for ind in release.index:

                    # kolonne 2 lages

                    matrix = release["Mx1"][ind]
                    if matrix == "":
                        matrix = C.CharBold + "UKJENT MATRISE" + C.CharLight

                    # beregner lenke til labelbilde
                    link = ""
                    linkstart = "Side " + release["SideNo"][ind] # blir lenkestart i InDesign
                    linklen = len(linkstart)

                    # bytter sære matrisetegn ut med tillatte tegn
                    if "¼" in takes["Mx1"][ind]:
                        mxpic = takes["Mx1"][ind].replace("¼", "x1")
                    elif "½" in takes["Mx1"][ind]:
                        mxpic = takes["Mx1"][ind].replace("½", "x2")
                    elif "¾" in takes["Mx1"][ind]:
                        mxpic = takes["Mx1"][ind].replace("¾", "x3")
                    else:
                        mxpic = takes["Mx1"][ind]

                    # bytter "/"" ut med "&"" i katalognummer
                    if "/" in takes["CatNo1"][ind]:
                        catnopic = takes["CatNo1"][ind].replace("/", "&")
                    else:
                        catnopic = takes["CatNo1"][ind]

                    labelpic = takes["Label"][ind] + "\/" + takes["Label"][ind] + "\_" + catnopic + "\_" + mxpic
                    labelpic = labelpic.replace(" ","")
                    link = C.LinkStart + linkstart + C.LinkName + web + labelpic + C.LinkEndStart + str(linklen) + C.LinkEnd + linkstart + C.CharEnd + C.LinkDef + web + labelpic + C.LinkDestURL + web + labelpic + C.LinkDefEnd

                    placedate = release["Place"][ind] + " " + release["DateSource"][ind]
                    if placedate.isspace() == True:
                        col2 = RLC.Cell + RLC.Recording + matrix + "\n" + link + C.CellEnd
                    else:
                        col2 = RLC.Cell + RLC.Recording + matrix + "\n" + link + "\n" + placedate + C.CellEnd

                    # kolonne 3 lages

                    if takes["SourceForm"][ind] == "":
                        line1 = takes["SourceWork"][ind]
                    else:
                        line1 = takes["SourceWork"][ind] + C.CharLight + " (" + takes["SourceForm"][ind] + ") "

                    work = takes["Work"][ind]
                    if takes["Work"][ind] != "":
                        work = work + " "

                    part = "(" + takes["PartOf"][ind] + ")"
                    if takes["PartOf"][ind] != "":
                        part = part + " "

                    if takes["PartOf"][ind] == "" and takes["Seq"][ind] == "":
                        line2 = work
                    elif takes["PartOf"][ind] != "" and takes["Seq"][ind] == "":
                        line2 = work + part
                    elif takes["PartOf"][ind] == "" and takes["Seq"][ind] != "":
                        line2 = work + "[del " + takes["Seq"][ind] + "]"
                    elif takes["PartOf"][ind] != "" and takes["Seq"][ind] != "":
                        line2 = work + part + "[del " + takes["Seq"][ind] + "]"
                    if line2 != "" and line1 != "":
                        line2 = "\n" + line2

                    line3 = DiscoFunc.nameformat(takes["Authors"][ind])
                    if line3 != "":
                        line3 = "\n" + C.CharLightItalic + line3

                    line4 = DiscoFunc.nameformat(takes["Artists"][ind])
                    if line4 != "":
                        line4 = "\n" + C.CharLight + line4

                    # lagrer den nye navne-/verktabellen for å kunne evt. bruke den i neste løkke
                    col3 = RLC.Cell + RLC.Work + line1 + C.CharRegular + line2 + line3 + line4  + C.CellEnd


                    # -----------------------------


                    col23 = col23 + skille + col2 + col3
                    skille = RLC.NewRow + RLC.Cell + C.CellEnd

                col23 = col23 + C.TableEnd

                # skriv InDesign-tabell for oldrelease
                f.write(col1 + col23)

            oldlabel = thislabel
            oldrelease = thisrelease
            oldaltrelease = thisaltrelease
            oldmedium = thismedium
            tell = ind + 1

            update_run()

# Denne rutinen leser en csv-eksport fra DiscoM og skriver en tagged txt Indesign-format i matrise-rekkefølge
def runMX():

    global fil
    global ext
    global tell

    # øker størrelse på celler og antall kolonner
    pd.options.display.max_columns = None
    pd.options.display.max_colwidth = 200

    # webadresse for labelfotos
    web = "https\:\/\/www.historisklyd.no\/labels\/"

    # filnavn
    discofile = fil + ext
    outputfile = fil + " MX tag.txt"

    # leser en CSV-fil til en DataFrame, neglisjerer blanke celler, leser "RelMedium" og "CatNo1" som tekststreng
    disco = pd.read_csv(discofile, keep_default_na=False, dtype=str)

    # leser inn søkestrenger, blank betyr velg alt
    label = ""
    artname = ""
    authname = ""

    # filtrerer på label-/artist-/authornavn og lager en ny dataframe ("takes") av kun de aktuelle radene
    takes = disco.loc[disco['Label'].str.contains(label, case=False)].copy()
    # og, logisk AND
    takes = takes.loc[disco['Artists'].str.contains(artname, case = False)].copy()
    # og, logisk AND
    takes = takes.loc[disco['Authors'].str.contains(authname, case = False)].copy()

    # lager en ny kolonne for den numeriske delen av Mx1 for å bruken den til sortering
    takes["Mx1sort"] = takes["Mx1"].apply(get_rightmost_numeric_element)
    takes["Mx1sort"] = takes["Mx1sort"].astype(int)

    # det nye datasettet sorteres på matrisenr
    takes.sort_values(["Mx1sort"],axis=0, ascending=True,inplace=True,na_position='first')

    # evt på sorteringsdato og matrisenr
    #takes.sort_values(["DateSort","Mx1sort"],axis=0, ascending=True,inplace=True,na_position='first')

    # startverdier
    oldmatrix = ""
    table = ""

    # åpner fil for utskrift til InDesign tagged txt format
    with open(outputfile, "w", encoding="utf-16") as f:

        # skriv InDesign-definisjoner
        print(C.Code, file = f)
        print(C.Intro, file = f)
        print(C.CharStyleLight, file = f)
        print(C.CharStyleLightItalic, file = f)
        print(C.CharStyleRegular, file = f)
        print(C.CharStyleBold, file = f)
        print(C.HyperLink, file = f)
        print(C.FontNorm, file = f)

        print(MXC.FontRelease, file = f)
        print(MXC.FontRecording, file = f)
        print(MXC.FontWork, file = f)
        print(MXC.FontAuthors, file = f)
        print(MXC.FontArtists, file = f)
        print(MXC.TableDef, file = f)

        # loop gjennom takes i sortert rekkefølge
        for ind in takes.index:
            thismatrix = takes["Mx1"][ind]

            # ny matrise?
            if oldmatrix != thismatrix:

                # skriv forrige rads navne-/verktabell
                if table != "":
                    print(table, file = f) # men ikke ved første linje

                # matrisenummer etc. for den nye matrisen
                if takes["Place"][ind] != "":
                    if takes["DateSource"][ind] != "":
                        print(MXC.Recording + takes["Mx1"][ind] + C.CharLight + " (" + takes["Place"][ind] + " " + takes["DateSource"][ind] + ")", file=f)
                    else:
                        print(MXC.Recording + takes["Mx1"][ind] + C.CharLight + " (" + takes["Place"][ind] + ")", file=f)
                else:
                    if takes["DateSource"][ind] != "":
                        print(MXC.Recording + takes["Mx1"][ind] + C.CharLight + " (" + takes["DateSource"][ind] + ")", file=f)
                    else:
                        print(MXC.Recording + takes["Mx1"][ind] + C.CharLight, file=f)

                # Bygger opp ny navne-/verktabell:
                # line1: sourcework (sourceform)
                # line2: work (partof) [seq]
                # line3: authors
                # line4: artists

                if takes["SourceForm"][ind] == "":
                    line1 = takes["SourceWork"][ind]
                else:
                    line1 = takes["SourceWork"][ind] + C.CharLight + " (" + takes["SourceForm"][ind] + ") "

                work = takes["Work"][ind]
                if takes["Work"][ind] != "":
                    work = work + " "

                part = "(" + takes["PartOf"][ind] + ")"
                if takes["PartOf"][ind] != "":
                    part = part + " "

                if takes["PartOf"][ind] == "" and takes["Seq"][ind] == "":
                    line2 = work
                elif takes["PartOf"][ind] != "" and takes["Seq"][ind] == "":
                    line2 = work + part
                elif takes["PartOf"][ind] == "" and takes["Seq"][ind] != "":
                    line2 = work + "[del " + takes["Seq"][ind] + "]"
                elif takes["PartOf"][ind] != "" and takes["Seq"][ind] != "":
                    line2 = work + part + "[del " + takes["Seq"][ind] + "]"
                if line2 != "" and line1 != "":
                    line2 = "\n" + line2

                line3 = DiscoFunc.nameformat(takes["Authors"][ind])
                if line3 != "":
                    line3 = "\n" + MXC.Authors + line3

                line4 = DiscoFunc.nameformat(takes["Artists"][ind])
                if line4 != "":
                    line4 = "\n" + MXC.Artists + line4

                # lagrer den nye navne-/verktabellen for å kunne evt. bruke den i neste løkke
                table = MXC.Work + line1 + C.CharRegular + line2 + line3 + line4

            link = ""
            linkstart = "Side " + takes["SideNo"][ind] # blir lenkestart i InDesign
            linklen = len(linkstart)

            # bytter sære matrisetegn ut med tillatte tegn
            if "¼" in takes["Mx1"][ind]:
                mxpic = takes["Mx1"][ind].replace("¼", "x1")
            elif "½" in takes["Mx1"][ind]:
                mxpic = takes["Mx1"][ind].replace("½", "x2")
            elif "¾" in takes["Mx1"][ind]:
                mxpic = takes["Mx1"][ind].replace("¾", "x3")
            else:
                mxpic = takes["Mx1"][ind]

            # bytter "/"" ut med "&"" i katalognummer
            if "/" in takes["CatNo1"][ind]:
                catnopic = takes["CatNo1"][ind].replace("/", "&")
            else:
                catnopic = takes["CatNo1"][ind]

            labelpic = takes["Label"][ind] + "\/" + takes["Label"][ind] + "\_" + catnopic + "\_" + mxpic
            labelpic = labelpic.replace(" ","")
            link = C.LinkStart + linkstart + C.LinkName + web + labelpic + C.LinkEndStart + str(linklen) + C.LinkEnd + linkstart + C.CharEnd + C.LinkDef + web + labelpic + C.LinkDestURL + web + labelpic + C.LinkDefEnd

            if takes["CatNo1"][ind] == "":
                print(MXC.Release + "Ingen utgivelse registrert" + C.CharEnd, file = f)
            else:
                if takes["CatNo2"][ind] != "":
                    print(MXC.Release + takes["Label"][ind] + " " + takes["CatNo1"][ind] + C.CharLight + " (" + takes["CatNo2"][ind] + ") [" + takes["RelMedium"][ind] + "] " + link + C.CharEnd, file = f)
                else:
                    print(MXC.Release + takes["Label"][ind] + " " + takes["CatNo1"][ind] + C.CharLight + " [" + takes["RelMedium"][ind] + "] " + link + C.CharEnd, file = f)

            # gjør klar for ny løkke
            oldmatrix = thismatrix

            tell = ind + 1
            update_run()

        # skriver ut den siste navne-/verktabellen
        print(table, file = f)

def AllNames():

    # Denne rutinen leser en csv-eksport fra DiscoM
    # og skriver en sortert liste over samtlige navn (artister og opphavsmenn) til en kolonne i en Excel-fil
    # Programmet generert av GPT_5

    global fil
    global ext
    global tell

    # filnavn
    discofile = fil + ext
    outputfile = fil + " AllNames.xlsx"

    import pandas as pd

    # Read CSV
    disco = pd.read_csv(discofile, keep_default_na=False)

    # Combine both columns and split by semicolon
    allnames = (disco["Artists"] + ";" + disco["Authors"]).str.split(";")

    # Flatten the list and clean whitespace
    names = pd.Series([name.strip() for sublist in allnames for name in sublist if name.strip()])

    # Count and sort names alphabetically
    namelist = names.value_counts().reset_index()
    namelist.columns = ["Name", "Count"]
    namelist = namelist.sort_values("Name")

    # Save to Excel only
    namelist.to_excel(outputfile, header=False, index=False)

def select_file():
    global fil
    global ext
    filetypes = (('csv files', '*.csv'), ('tsv files', '*.tsv'))

    infile = fd.askopenfilename(
        title = 'Open a file',
        initialdir = 'C:\\Users\\tore\\OneDrive\\PyPro\\kurs',
        filetypes = filetypes)
    infile = os.path.basename(infile)
    fil, ext = os.path.splitext(infile)
    update_label()

def update_label():
    global fil
    out_label.config(text = f"Inputfil: {fil}{ext}")

def update_run():
    global tell
    run_label.config(text = f"Antall rader lest: {tell}")

if __name__ == "__main__":

    # window
    window = tk.Tk()
    window.title("Norsk Forening for Historisk Lyd")
    window.geometry("500x150")

    # title
    title_label = ttk.Label(master = window, text = "csv til InDesign tagged txt", font = "Lato 18 bold")
    title_label.pack()

    # input fields
    input_frame = ttk.Frame(master = window)
    input_frame.pack(pady = 20)

    # labels
    run_label = ttk.Label(master = input_frame, text = "")
    run_label.pack(side = "bottom")
    out_label = ttk.Label(master = input_frame, text = "")
    out_label.pack(side = "bottom")

    # buttons
    buttonselect = ttk.Button(master = input_frame, text = "Select file", command = select_file)
    buttonselect.pack(side = "right")

    buttonrunRL = ttk.Button(master = input_frame, text = "Run RL", command = runRL)
    buttonrunRL.pack(side = "left")

    buttonrunMX = ttk.Button(master = input_frame, text = "Run MX", command = runMX)
    buttonrunMX.pack(side = "left")

    buttonrunMX = ttk.Button(master = input_frame, text = "Check names", command = AllNames)
    buttonrunMX.pack(side = "left")

    window.mainloop()
