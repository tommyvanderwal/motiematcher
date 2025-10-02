# MotieeMatcher - Quick Start

## 🚀 Snelle Start

### Lokaal testen
```bash
# Open gewoon index.html in je browser, of:
python3 -m http.server 8080
# Open http://localhost:8080
```

## ☁️ AWS Deployment (Aanbevolen)

### Optie 1: AWS CLI (Snelst)
```bash
# Maak S3 bucket
aws s3 mb s3://beta.motiematcher.nl

# Upload bestanden
aws s3 sync . s3://beta.motiematcher.nl \
  --exclude ".git/*" \
  --exclude "*.md" \
  --exclude ".gitignore"

# Zet static website hosting aan
aws s3 website s3://beta.motiematcher.nl \
  --index-document index.html \
  --error-document index.html
```

### Optie 2: AWS Console
1. Log in op AWS Console
2. Ga naar S3 → Create bucket → `beta.motiematcher.nl`
3. Upload: `index.html`, `styles.css`, `app.js`, `data.js`
4. Properties → Static website hosting → Enable
5. Permissions → Block public access → Off
6. Bucket policy → Voeg toe (zie DEPLOYMENT.md)

### CloudFront (Voor HTTPS en snelheid)
1. CloudFront → Create distribution
2. Origin: S3 bucket
3. Alternate domain: `beta.motiematcher.nl`
4. SSL certificate: Request via ACM
5. Route 53: A-record → CloudFront

## 🌐 Alternatieve Deployment (Nog makkelijker)

### Netlify (Gratis, 1 minuut)
1. Push naar GitHub (✓ al gedaan!)
2. [netlify.com](https://netlify.com) → New site from Git
3. Select repository → Deploy
4. Custom domain: `beta.motiematcher.nl`

### Vercel (Gratis, 1 minuut)
1. Push naar GitHub (✓ al gedaan!)
2. [vercel.com](https://vercel.com) → New Project
3. Import repository → Deploy
4. Custom domain: `beta.motiematcher.nl`

## 📊 Belangrijke Notities

- **Geen build stap nodig** - Pure HTML/CSS/JS
- **Geen dependencies** - Alles werkt direct
- **Geen database nodig** - Data zit in data.js
- **SSL/HTTPS** - Gebruik CloudFront of Netlify/Vercel
- **DNS** - Wijs beta.motiematcher.nl naar je hosting

## 🔄 Updates Deployen

```bash
# AWS
aws s3 sync . s3://beta.motiematcher.nl --exclude ".git/*"
aws cloudfront create-invalidation --distribution-id XXX --paths "/*"

# Netlify/Vercel
git push  # Automatisch deployed!
```

## 📝 Data Aanpassen

Bewerk `data.js` om:
- Nieuwe moties toe te voegen
- Stemgedrag aan te passen
- Partijen toe te voegen/verwijderen

Formaat:
```javascript
{
    id: 1,
    title: "Motie titel",
    description: "Beschrijving...",
    votes: {
        "VVD": "voor",
        "PVV": "tegen",
        // etc.
    }
}
```

## 🎨 Styling Aanpassen

- **Kleuren**: Bewerk CSS variables in `styles.css` (`:root`)
- **Logo**: Vervang 🗳️ emoji in `index.html`
- **Teksten**: Bewerk `index.html`

## ✅ Checklist voor Productie

- [ ] Test alle 10 vragen
- [ ] Test op mobile (Chrome DevTools)
- [ ] Controleer resultaten accuracy
- [ ] Update data.js met echte stemdata (indien beschikbaar)
- [ ] Configureer custom domain
- [ ] Enable HTTPS
- [ ] Test share functie
- [ ] Voeg Google Analytics toe (optioneel)

## 🆘 Problemen?

**Site laadt niet:**
- Check S3 bucket permissions
- Verify static website hosting enabled

**Share werkt niet:**
- Normaal! Alleen op HTTPS domains met share API support

**Verkeerde resultaten:**
- Check data.js formatting
- Verify all parties have votes for all questions

## 📞 Support

Zie [DEPLOYMENT.md](DEPLOYMENT.md) voor gedetailleerde instructies.
