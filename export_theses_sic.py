"""Extrait d'un export theses.fr (data.gouv) les theses en Sciences de l'information
et de la communication (SIC), avec les variantes d'intitule, les disciplines voisines,
les STIC et "Image, information, hypermedia".

Usage :
    python3 export_theses_sic.py data/2026-11-17-02-00-01-datagouv-results.csv thesesSIC.csv

Affiche le nombre de theses retenues et le detail par intitule de discipline.
"""
import csv, sys, collections, re
csv.field_size_limit(sys.maxsize)
norm=lambda s: re.sub(r'\s+',' ',s.replace('’',"'").strip().lower())
core=re.compile(r"information,? (et )?(de la )?communication|information[- ]communication|information de la documentation|information et de la documentation")
core_ex=re.compile(r"technologies? de l|techniques de l|technologie de l|réseaux|stic|ingénierie|énergétique|biostat|télécom|électron")
other=re.compile(r"communication|médias|medias|hypermédia")
other_ex=re.compile(r"technolog|stic|télécom|telecom|électron|electron|réseau|signal|optique|micro|radio|endocrin|neuro|cellul|moléculaire|biostat|énerg|ingéni|systèmes? (de|et) communication|système de communication|systèmes de télécom|informatique|computer|processeurs|lasers|cognition|communications numériques|génie|fréquences|matériaux|physique|sciences appliquées")
fp=re.compile(r"^signaux|énergétique|laser|acoustique|technologiesde|quantique|robotique|systèmes d'information communicants|radiocommunication|^information, communications$|^image, information")
# Ajouts explicites : STIC, Telecommunications (STIC), Sciences et techniques de l'information et de la communication, Sciences et technologies de l'information et de la communication,
# Image, information, hypermedia
force=re.compile(r"^stic\b|^télécommunications \(stic\)|sciences? et (technologies?|techniques?) ?de l' ?information,? et de la communication|^image, information,? (et )?hypermédia")
def keep(d):
    n=norm(d)
    if force.search(n): return True
    if fp.search(n): return False
    if core.search(n): return not core_ex.search(n)
    return bool(other.search(n)) and not other_ex.search(n)
c=collections.Counter(); kept=0
with open(sys.argv[1],newline='',encoding='utf-8-sig') as f, open(sys.argv[2],'w',newline='',encoding='utf-8-sig') as o:
    r=csv.DictReader(f); w=csv.DictWriter(o,fieldnames=r.fieldnames,quoting=csv.QUOTE_ALL); w.writeheader()
    for row in r:
        d=row['discipline'] or ''
        if keep(d): w.writerow(row); kept+=1; c[d]+=1
print('kept',kept)
for k,v in c.most_common(): print(v,'\t',k)
