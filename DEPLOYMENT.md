# Deployment Handleiding

## AWS S3 + CloudFront Deployment

Deze website is een statische site en kan eenvoudig gehost worden op AWS.

### Stap 1: S3 Bucket aanmaken

1. Log in op AWS Console
2. Ga naar S3
3. Maak een nieuwe bucket aan (bijv. `beta.motiematcher.nl`)
4. Schakel "Block all public access" uit
5. Enable "Static website hosting" in bucket properties

### Stap 2: Bestanden uploaden

Upload de volgende bestanden naar de bucket:
- `index.html`
- `styles.css`
- `app.js`
- `data.js`

### Stap 3: Bucket Policy instellen

Voeg deze bucket policy toe voor publieke toegang:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::beta.motiematcher.nl/*"
        }
    ]
}
```

### Stap 4: CloudFront Distribution (Optioneel maar aanbevolen)

1. Ga naar CloudFront in AWS Console
2. Maak een nieuwe distribution
3. Selecteer je S3 bucket als origin
4. Configureer SSL certificaat voor HTTPS
5. Voeg alternate domain name toe: `beta.motiematcher.nl`

### Stap 5: DNS configureren

1. Ga naar Route 53 (of je DNS provider)
2. Maak een A-record of CNAME voor `beta.motiematcher.nl`
3. Wijs deze naar je CloudFront distribution

### Deployment commando's (AWS CLI)

```bash
# Sync bestanden naar S3
aws s3 sync . s3://beta.motiematcher.nl --exclude ".git/*" --exclude "*.md"

# Invalidate CloudFront cache (na updates)
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

## Alternatieve Deployment Opties

### Netlify (Makkelijkste optie)
1. Push code naar GitHub
2. Koppel repository aan Netlify
3. Deploy gebeurt automatisch bij elke push

### Vercel
1. Push code naar GitHub
2. Koppel repository aan Vercel
3. Deploy gebeurt automatisch bij elke push

## Productie (zonder beta)

Voor de productie versie op `motiematcher.nl`:
1. Volg dezelfde stappen als hierboven
2. Vervang `beta.motiematcher.nl` door `motiematcher.nl`
3. Update de DNS records
