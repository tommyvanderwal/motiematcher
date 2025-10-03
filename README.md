# MotieeMatcher

Website die moties matched - partij wijzer op basis van stem geschiedenis van de Tweede Kamer.

## Over het project

MotieeMatcher helpt gebruikers om te ontdekken welke politieke partij het beste aansluit bij hun standpunten. Door vragen te beantwoorden over actuele moties uit de Tweede Kamer, vergelijken we de antwoorden met het daadwerkelijke stemgedrag van politieke partijen.

## Functionaliteiten

- ✅ Interactieve stemtest met 10 actuele moties
- ✅ Matching algoritme dat gebruikersvoorkeuren vergelijkt met historisch stemgedrag
- ✅ Resultaten met percentage match per partij
- ✅ Responsive design voor mobile en desktop
- ✅ Deel functionaliteit voor resultaten
- ✅ Eenvoudig te deployen naar AWS (S3 + CloudFront)

## Technologie

Pure HTML, CSS en JavaScript - geen frameworks nodig. Dit maakt de site:
- Snel te laden
- Makkelijk te hosten
- Eenvoudig te onderhouden
- Geschikt voor static hosting op AWS S3

## Deployment

De website kan gehost worden op:
- AWS S3 + CloudFront (aanbevolen voor beta.motiematcher.nl)
- Netlify
- Vercel
- Elke andere static hosting service

Zie [DEPLOYMENT.md](DEPLOYMENT.md) voor gedetailleerde instructies.

## Lokaal draaien

Open gewoon `index.html` in je browser. Geen build stap of dependencies nodig!

## Data

De motie data in `data.js` bevat voorbeelden van stemgedrag. Voor productie gebruik kunnen deze vervangen worden door echte data van de Tweede Kamer API of andere bronnen.
