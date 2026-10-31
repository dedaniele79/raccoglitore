# Raccoglitore TCG – web app per iPhone

Versione 1.4 del 31 ottobre 2026. La guida completa è nel file `guida.html` (si apre anche dall'app, con il pulsante ? in alto a destra) e nel manuale PDF.

Web app per archiviare la collezione di carte Pokémon. Si apre da Safari e si aggiunge alla schermata Home: si comporta come un'app, non scade e non va reinstallata. Gli aggiornamenti arrivano da soli quando carichi i nuovi file su GitHub sopra i vecchi.

## Cosa fa

- **Scansiona** (1.4): legge il numero, riconosce la lingua della carta (italiano, inglese, francese, tedesco, spagnolo, portoghese, giapponese, coreano, cinese), controlla il nome e salva la foto di ogni carta. Pulsante bianco per scattare quando la carta non viene riconosciuta da sola.
- **Scansione, dettagli**: tieni le carte una dopo l'altra davanti alla fotocamera, senza toccare nulla. L'app legge il numero stampato (es. 025/165) e, se la carta è unica, la aggiunge da sola con edizione, variante e condizione scelte una volta per tutta la sessione. Se più carte hanno lo stesso numero, la scegli con un tocco; ogni aggiunta si può annullare o correggere dalla lista della sessione. Dal raccoglitore di un'espansione puoi scansionare solo le sue carte, così non ci sono dubbi.
- **Collezione**: come nei negozi, per edizione (IT, EN, JP, KR, CN), serie ed espansione con data d'uscita. Ogni espansione si apre come un raccoglitore a pagine da 9 tasche, con le mancanti in grigio.
- **Valore**: trend Cardmarket in euro (via TCGdex), aggiornato da solo una volta al giorno, con coefficiente per lingua e valore personale per copia.
- **Scambi**: una copia per carta, edizione e variante resta in collezione; le altre sono doppioni, esportabili in CSV.
- **Cerca**: per nome, in 12 lingue.
- **Copia di sicurezza**: salva e ripristina in un file tutte le carte, le impostazioni e le foto; promemoria dopo ogni sessione; versioni automatiche sul telefono (una all'ora, le ultime 30).

## Metterla online con GitHub Pages (gratis, una volta sola)

1. Crea un account su github.com, se non ce l'hai.
2. In alto a destra: **+ › New repository**. Nome: `raccoglitore`. Visibilità: **Public** (GitHub Pages gratuito lo richiede; i tuoi dati non finiscono lì, restano sull'iPhone). Crea.
3. Nella pagina del repository: **Add file › Upload files**. Trascina tutto il contenuto di questa cartella: i file (`index.html`, `guida.html`, `manifest.webmanifest`, `sw.js`, le due icone) e le cartelle `ocr` e `fonts`. **Commit changes**.
4. **Settings › Pages**: in *Source* scegli **Deploy from a branch**, branch **main**, cartella **/ (root)**, **Save**.
5. Dopo uno o due minuti l'indirizzo è `https://<tuo-utente>.github.io/raccoglitore/`.

## Installarla sull'iPhone

1. Apri l'indirizzo con **Safari**.
2. Tocca **Condividi › Aggiungi alla schermata Home › Aggiungi**.
3. Apri l'app dall'icona e consenti la fotocamera quando lo chiede.

## Sicurezza

- Nessun account e nessun server: la collezione resta sull'iPhone, le immagini della fotocamera non escono dal telefono.
- Il lettore (cartella `ocr`, Tesseract.js con inglese, giapponese e coreano) e i caratteri (cartella `fonts`) sono dentro l'app: nessun codice da altri siti, nessuna richiesta a Google. Il riconoscimento delle carte avviene tutto sul telefono.
- La pagina ha una Content-Security-Policy: può collegarsi solo al catalogo TCGdex ed eseguire solo il proprio codice.
- Le copie di sicurezza vengono controllate prima del ripristino; il ripristino si può annullare per qualche secondo.

## Da sapere

- I dati sono salvati sull'iPhone, dentro l'app. Se cancelli l'app dalla schermata Home si cancellano anche loro: salva ogni tanto la copia di sicurezza (⚙︎ Impostazioni › Salva copia).
- La lettura del numero scarica la prima volta alcuni MB; serve la connessione. Con poca luce o riflessi forti scrivi il numero a mano.
- Il trend Cardmarket mescola lingue e condizioni: usa i coefficienti per lingua o il valore personale per correggerlo.
- La variante (normale, reverse, holo) non si riconosce dalla foto: separa prima le pile e scegli la variante della sessione, oppure correggila con un tocco nella lista.

Catalogo, immagini e prezzi da TCGdex (fonte Cardmarket). App per uso personale, non affiliata a The Pokémon Company né a Cardmarket.
