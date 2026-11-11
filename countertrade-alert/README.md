# Countertrade-alarm til Teams

Tjekker hvert 5. minut Energinets datasæt [Countertrade Procured in Intraday](https://www.energidataservice.dk/tso-electricity/CountertradeIntraday_v2). Når der er publiceret ny countertrade, sendes en kort Teams-besked med antal timer og et link til data.

## Opsætning

1. **Teams-webhook**
   Åbn appen **Workflows** i Teams → vælg skabelonen **"Send webhook alerts to a chat"** → vælg den chat/bruger, der skal have beskeden → gem og kopiér webhook-URL'en.

2. **GitHub-repo**
   Opret et nyt **offentligt** repo og push indholdet af denne mappe til det.
   (Offentlige repos har ubegrænsede gratis Actions-minutter. Private repos har kun 2.000 min/md., som en kørsel hvert 5. minut overskrider. Webhook-URL'en er stadig hemmelig, fordi den ligger som secret.)
   Gå til *Settings → Secrets and variables → Actions → New repository secret* og opret:
   - Navn: `TEAMS_WEBHOOK_URL`
   - Værdi: URL'en fra trin 1

3. **Test**
   Gå til fanen *Actions* → *Countertrade alert* → **Run workflow**. Første kørsel sender en besked om den seneste publicering.

## Lokal test

```
python check_countertrade.py --dry-run
```

Viser beskeden uden at sende den.
