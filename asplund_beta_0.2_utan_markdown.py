import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import hashlib

# Läs in dataset
ath = pd.read_csv("assets/athlete_events.csv")
noc = pd.read_csv("assets/noc_regions.csv")

ath.head()

# Slå ihop de två datamängderna för att få med landnamn
df = ath.merge(noc, on="NOC", how="left")
df.head()

# Hur många länder (unika NOC-koder)?
antal_lander = df['NOC'].nunique()
print("Antal länder:", antal_lander)

# Vilka länder (endast förkortningar)?
lander_lista = np.array(sorted(df['NOC'].unique()))
print(lander_lista)

# Vilka sporter finns i datan?
sporter_lista = np.array(sorted(df['Sport'].unique()))
print(sporter_lista)

# Vilka olika medaljer finns representerade?
medaljer = df['Medal'].dropna().unique()

ordning = ["Gold", "Silver", "Bronze"]
medaljer_sorterade = sorted(medaljer, key=lambda x: ordning.index(x))

print(medaljer_sorterade)

# Hur ser åldersfördelningenfördelningen av atleter ut?
mean_age = round(df['Age'].mean())
median_age = round(df['Age'].median())
min_age = round(df['Age'].min())
max_age = round(df['Age'].max())
std_age = round(df['Age'].std())

print("Åldersfördelning på deltagande atleter:")
print("-----------------------------")
print(f"Medelålder:             {mean_age} år")
print(f"Medianålder:            {median_age} år")
print(f"Yngsta deltagare:       {min_age} år")
print(f"Äldsta deltagare:       {max_age} år")
print(f"Standardavvikelse:      {std_age} år")

# Topp 10 vanligaste sporterna och antal deltagare
top10_sporter = df['Sport'].value_counts().head(10)
top10_sporter_sorted = top10_sporter.sort_index()

print("Sport")
print("-------------------------------")

for sport, antal in top10_sporter_sorted.items():
    print(f"{sport:<25} {antal:>5}")

# Länder i storleksordning, börja med flest antal deltagande atleter
lander = df['region'].value_counts().head(10)

print("Land")
print("-------------------------------")

for land, antal in lander.items():
    print(f"{land:<25} {antal:>5}")

# Genomsnittlig ålder per sport i bokstavsordning
genomsnitt_alder = (
    df.groupby('Sport')['Age']
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

# sortera i bokstavsordning
genomsnitt_alder_sorted = genomsnitt_alder.sort_index()

print("Sport")
print("-------------------------------------")

for sport, alder in genomsnitt_alder_sorted.items():
    print(f"{sport:<25} {round(alder):>5}")

# Fördelning man / kvinna bland deltagande atleter
df['Sex'].value_counts().plot(kind='bar', zorder=3)
plt.title("Könsfördelning")
plt.xlabel("Kön")
plt.ylabel("Antal")
plt.grid(True, zorder=0)
plt.xticks(rotation=0)
plt.show()

# Topp 10 länder med flest vunna medaljer
medals = df.dropna(subset=['Medal'])
top10_medal = medals['region'].value_counts().head(10)

top10_medal.plot(kind='bar', zorder=3)
plt.title("Topp 10 länder med flest medaljer")
plt.xlabel("Land")
plt.ylabel("Antal medaljer")
plt.xticks(rotation=75)
plt.grid(True, zorder=0)
plt.show()

# Åldersfördelning ovasett kön bland atleterna
plt.hist(df['Age'].dropna(), bins=40, zorder=3)
plt.title("Åldersfördelning")
plt.ylabel("Antal")
plt.xlabel("Ålder")
plt.grid(True, zorder=0)
plt.show()

# Fördelning av medaljtyper
medals['Medal'].value_counts().plot(kind='bar', zorder=3)
plt.title("Fördelning av medaljtyper")
plt.ylabel("Antal")
plt.xlabel("Medaljtyp")
plt.xticks(rotation=0)
plt.grid(True, zorder=0)
plt.show()

# Topp 15 vanligaste sporterna i OS
df['Sport'].value_counts().head(15).plot(kind='bar', zorder=3)
plt.title("Topp 15 vanligaste sporterna")
plt.xticks(rotation=75)
plt.grid(True, zorder=0)
plt.show()

# Funktion som hashar en sträng med SHA-256
def sha256_hash(text):
    if pd.isna(text):
        return None
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

# Skapa en ny kolumn med de hashade namnen
df['Name_hash'] = df['Name'].apply(sha256_hash)

# Visa resultatet
df[['Name', 'Name_hash']].head()

# Ta bort namnet på deltagande atleter
df = df.drop(columns=['Name'])
df.head()

# Sortera ut så att svaren endast är kopplade till Japans prestationer
japan_df = df[df['region'] == "Japan"].copy()
japan_df.head()

# Filtrera datan för att endast visa hur Japanska atleter har presterat i OS
japan = df[df['region'] == "Japan"].copy()
japan.head()

# Filtrera japanska medaljer
japan_medals = japan.dropna(subset=['Medal'])

# Räkna japanska medaljer per sport
medals_per_sport = japan_medals['Sport'].value_counts().head(15)

medals_per_sport.plot(kind='bar', zorder=3)
plt.title("Japan - Topp 15 sporter med flest medaljer")
plt.xlabel("Sport")
plt.ylabel("Antal medaljer")
plt.xticks(rotation=75)
plt.grid(True, zorder=0)
plt.show()

# Visa totalt antal japanska medaljer per OS
medals_per_year = japan_medals['Year'].value_counts().sort_index()
medals_per_year.plot(kind='bar', zorder=3)

plt.title("Japan - Medaljer per OS")
plt.xlabel("År")
plt.ylabel("Antal medaljer")
plt.xticks(rotation=75)
plt.grid(True, zorder=0)
plt.show()

# Visa japanska atleters åldrar/åldersfördelning
plt.hist(japan['Age'].dropna(), bins=40, zorder=3)
plt.title("Japan - Åldersfördelning hos OS-deltagare")
plt.xlabel("Ålder")
plt.ylabel("Antal")
plt.grid(True, zorder=0)
plt.show()

# Visa hur många medaljer av de olika valörerna Japan tagit
counts = japan_medals['Medal'].value_counts()
order = ["Gold", "Silver", "Bronze"]
counts_ordered = counts.reindex(order)
counts_ordered.plot(kind='bar', zorder=3)

plt.title("Japan - Antal medaljer utifrån pallplacering i OS")
plt.xlabel("Medaljtyp")
plt.ylabel("Antal")
plt.grid(True, zorder=0)
plt.xticks(rotation=75)
plt.show()

# Könsfördelning på japanska atleter i OS totalt
japan['Sex'].value_counts().plot(kind='bar', zorder=3)
plt.title("Japan - Könsfördelning av deltagare")
plt.xlabel("Kön")
plt.ylabel("Antal")
plt.grid(True, zorder=0)
plt.xticks(rotation=0)
plt.show()

# Visa genomsnittlig ålder för japanska atleter utifrån år
age_per_year = japan.groupby('Year')['Age'].mean().plot(kind='bar', zorder=3)

plt.title("Japan - Genomsnittlig ålder per OS")
plt.xlabel("År")
plt.ylabel("Medelålder")
plt.grid(True, zorder=0)
plt.xticks(rotation=75)
plt.show()

#Vanligaste OS-grenar där flest japanska atleter deltagit
japan['Sport'].value_counts().head(15).plot(kind='bar', zorder=3)
plt.title("Japan - Topp 15 populäraste sporterna")
plt.xlabel("Sport")
plt.ylabel("Antal deltagare")
plt.xticks(rotation=75)
plt.grid(True, zorder=0)
plt.show()

# Längd och vikt för alla de deltagande japanska atleterna
plt.figure()

# Filtrera efter kön
men = japan[japan['Sex'] == 'M']
women = japan[japan['Sex'] == 'F']

# Män (blå plupp)
plt.scatter(
    men['Height'],
    men['Weight'],
    color='tab:blue',
    s=10,
    label='Män',
    zorder=3
)

# Kvinnor (orange plupp)
plt.scatter(
    women['Height'],
    women['Weight'],
    color='tab:orange',
    s=10,
    label='Kvinnor',
    zorder=3
)

plt.title("Japan - Förhållande mellan längd och vikt för deltagande atleter")
plt.xlabel("Längd (cm)")
plt.ylabel("Vikt (kg)")
plt.legend()
plt.grid(True, zorder=0)
plt.show()

# Medaljer per sport uppdelat på kön för japanska atleter i OS
pivot = japan_medals.pivot_table(index='Sport', columns='Sex', values='Medal', aggfunc='count')
pivot.columns.name = "Kön"
pivot.sort_values(by=['M', 'F'], ascending=False).head(10).plot(kind='bar', stacked=True, zorder=3)

plt.title("Japan - Medaljer per sport och kön")
plt.xlabel("Sport")
plt.ylabel("Antal medaljer")
plt.grid(True, zorder=0)
plt.xticks(rotation=75)
plt.show()

# Japanska medaljer över tid sorterat utifrån valör
medals_by_year_type = japan_medals.groupby(['Year', 'Medal']).size().unstack()
order = ["Gold", "Silver", "Bronze"]
medals_by_year_type = medals_by_year_type[order]
medals_by_year_type.plot(
    kind='bar',
    zorder=3
)

plt.title("Japan - Medaljer i OS över tid listat utifrån medaljtyp")
plt.xlabel("År")
plt.ylabel("Antal medaljer")
plt.grid(True, axis='y', zorder=0)
plt.xticks(rotation=75)
plt.show()

# Filtrera data och analysera utifrån sport
sports = ["Athletics", "Gymnastics", "Judo", "Swimming"]
sports_df = df[df['Sport'].isin(sports)].copy() 

sports_df['Sport'] = pd.Categorical(sports_df['Sport'], categories=sports, ordered=True)
sports_df = sports_df.sort_values("Sport")

sports_df.head()

# Medaljfördelning utifrån land och sport
sports_medals = sports_df.dropna(subset=['Medal'])
medals_by_country_sport = sports_medals.groupby(['Sport', 'region'], observed=True).size().unstack(fill_value=0)

# Visa de 10 länder som tagit flest medaljer totalt inom de valda sporterna
top_countries = medals_by_country_sport.sum(axis=0).sort_values(ascending=False).head(10).index

medals_by_country_sport[top_countries].T.plot(kind='bar', zorder=3)
plt.title("Medaljfördelning mellan länder inom valda sporter")
plt.xlabel("Land")
plt.ylabel("Antal medaljer")
plt.grid(True, axis='y', zorder=0)
plt.xticks(rotation=75)
plt.show()

# Åldersfördelning utifrån sport
plt.figure(figsize=(10,6))
for sport in sports:
    sns.kdeplot(sports_df[sports_df['Sport'] == sport]['Age'].dropna(), label=sport, fill=False)

plt.title("Åldersfördelning per sport")
plt.xlabel("Ålder")
plt.ylabel("Vanligt förekommande")
plt.legend()
plt.grid(True, axis='y')
plt.show()

# Fördelning Män / Kvinnor utifrån valda sporter
sex_counts = sports_df.groupby(['Sport', 'Sex'], observed=True).size().unstack(fill_value=0)
sex_counts.columns.name = "Kön"
sex_counts.plot(kind='bar', stacked=True, zorder=3)

plt.title("Könsfördelning per sport")
plt.xlabel("Sport")
plt.ylabel("Antal deltagare")
plt.xticks(rotation=0)
plt.grid(True, axis='y', zorder=0)
plt.show()

# Medaljer som delats ut i OS över tid sorterade utifrån sport
medals_per_year_sport = sports_medals.groupby(['Year', 'Sport'], observed=True).size().unstack(fill_value=0)

medals_per_year_sport.plot(figsize=(12,6), marker='o')
plt.title("Utdelade medaljer över tid per sport")
plt.xlabel("År")
plt.ylabel("Antal medaljer")
plt.xticks(ticks=medals_per_year_sport.index, rotation=75)
plt.grid(True, zorder=0)
plt.show()

# Längd kontra vikt i utvalda sporter
plt.figure(figsize=(10,6))
sns.scatterplot(data=sports_df, x='Height', y='Weight', hue='Sport', alpha=0.6)
plt.title("Längd vs Vikt i utvalda sporter")
plt.xlabel("Längd (cm)")
plt.ylabel("Vikt (kg)")
plt.grid(True, zorder=0)
plt.show()

for sport in sports:
    subset = sports_medals[sports_medals['Sport'] == sport]
    top5 = subset['region'].value_counts().head(5)

    top5.plot(kind='bar', zorder=3)
    plt.title(f"Topp 5 medaljländer i {sport}")
    plt.xlabel("Land")
    plt.ylabel("Antal medaljer")
    plt.xticks(rotation=45)
    plt.grid(True, axis='y', zorder=0)
    plt.show()

# Genomsnittlig ålder per OS och sport uppdelat per år
age_per_year_sport = sports_df.groupby(['Year', 'Sport'])['Age'].mean().unstack()

age_per_year_sport.plot(figsize=(12,6), marker='o')
plt.title("Genomsnittlig ålder per OS och sport")
plt.xlabel("År")
plt.ylabel("Medelålder")
plt.xticks(ticks=medals_per_year_sport.index, rotation=75)
plt.grid(True, zorder=0)

plt.show()
