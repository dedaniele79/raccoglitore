# Raccoglitore TCG – web app per iPhone e Android

Versione 2.0 dell'8 novembre 2026. La guida completa è nel file `guida.html` (si apre anche dall'app, con il pulsante ? in alto a destra) e nel manuale PDF.

Web app per archiviare la collezione di carte Pokémon. Si apre da Safari (iPhone) o da Chrome/Samsung Internet (Android) e si aggiunge alla schermata Home: si comporta come un'app, non scade e non va reinstallata. Gli aggiornamenti arrivano da soli quando carichi i nuovi file su GitHub sopra i vecchi.

## Cosa fa

- **Scansione veloce come PokéCardex** (2.0): la carta si riconosce dall'illustrazione in meno di un secondo. Un'azione GitHub (`.github/workflows/impronte.yml`, script `tools/impronte.py`) calcola ogni settimana l'impronta dell'illustrazione di tutte le carte del catalogo TCGdex (circa 19.600) e la pubblica sul ramo `impronte`; l'app la scarica una volta (circa 1 MB), la tiene sul telefono e confronta la carta inquadrata in pochi millesimi di secondo. Se la lingua è nota la carta si aggiunge subito; foto e variante si salvano in background.
- **Android** (2.0): ottimizzata per Samsung Galaxy S24 e gli altri Android: pulsante Installa, icona adattiva, scorciatoie Scansiona e Valore (tieni premuta l'icona), tasto Indietro che chiude schede e pannelli, messa a fuoco continua e pulsante Luce nella scansione.
- **Scansiona** (1.4): legge il numero, riconosce la lingua della carta (italiano, inglese, francese, tedesco, spagnolo, portoghese, giapponese, coreano, cinese), controlla il nome e salva la foto di ogni carta. Pulsante bianco per scattare quando la carta non viene riconosciuta da sola.
- **Scansione, dettagli**: tieni le carte una dopo l'altra davanti alla fotocamera, senza toccare nulla. L'app legge il numero stampato (es. 025/165) e, se la carta è unica, la aggiunge da sola con edizione, variante e condizione scelte una volta per tutta la sessione. Se più carte hanno lo stesso numero, la scegli con un tocco; ogni aggiunta si può annullare o correggere dalla lista della sessione. Dal raccoglitore di un'espansione puoi scansionare solo le sue carte, così non ci sono dubbi.
- **Collezione**: come nei negozi, per edizione (IT, EN, JP, KR, CN), serie ed espansione con data d'uscita. Ogni espansione si apre come un raccoglitore a pagine da 9 tasche, con le mancanti in grigio.
- **Valore**: trend Cardmarket in euro (via TCGdex), aggiornato da solo una volta al giorno, con coefficiente per lingua e valore personale per copia.
- **Scambi**: una copia per carta, edizione e variante resta in collezione; le altre sono doppioni, esportabili in CSV.
- **Cerca**: per nome, in 12 lingue.
- **Collezioni di famiglia** (1.5): ognuno condivide la sua collezione come file e vede quelle degli altri, in sola lettura.
- **Carte fuori catalogo** (1.5): le carte che TCGdex non ha (per esempio molte buste speciali cinesi) si archiviano lo stesso con foto, nome, numero ed espansione.
- **Cardmarket diretto** (1.6): un'azione GitHub (`.github/workflows/cardmarket.yml`, script `tools/cardmarket.py`) scarica ogni notte il listino pubblico Cardmarket dei Pokémon e lo pubblica sul ramo `dati`; l'app lo legge per collegare le carte fuori catalogo e aggiornarne il prezzo.
- **Carte cinesi fuori catalogo** (1.9): nome cinese letto (lettori `chi_sim` e `chi_tra` in `ocr/`) e tradotto con `nomi-pokemon.json` (nomi per numero di Pokédex, dal pacchetto MIT «pokemon»), poi cercato su Cardmarket.
- **Carte solo su Cardmarket** (1.8): se il catalogo non ha la carta (es. Pokémon Trading Card Game Classic), l'app la cerca per nome nel listino Cardmarket e la propone con il prezzo.
- **Carte promo e Federicstore** (1.7): l'app legge i codici delle promo (MEP, SVP…) e completa il catalogo italiano con quello inglese; ogni carta ha il link a Federicstore per comprarla o confrontarne il prezzo. Il valore resta Cardmarket.
- **Copia di sicurezza**: salva e ripristina in un file tutte le carte, le impostazioni e le foto; promemoria dopo ogni sessione; versioni automatiche sul telefono (una all'ora, le ultime 30).

## Metterla online con GitHub Pages (gratis, una volta sola)

1. Crea un account su github.com, se non ce l'hai.
2. In alto a destra: **+ › New repository**. Nome: `raccoglitore`. Visibilità: **Public** (GitHub Pages gratuito lo richiede; i tuoi dati non finiscono lì, restano sul telefono). Crea.
3. Nella pagina del repository: **Add file › Upload files**. Trascina tutto il contenuto di questa cartella: i file (`index.html`, `guida.html`, `manifest.webmanifest`, `sw.js`, `nomi-pokemon.json`, le icone `icon-*.png`, le schermate `schermata-*.webp`) e le cartelle `ocr` e `fonts`. **Commit changes**.
4. **Settings › Pages**: in *Source* scegli **Deploy from a branch**, branch **main**, cartella **/ (root)**, **Save**.
5. Dopo uno o due minuti l'indirizzo è `https://<tuo-utente>.github.io/raccoglitore/`.

## Installarla sull'iPhone

1. Apri l'indirizzo con **Safari**.
2. Tocca **Condividi › Aggiungi alla schermata Home › Aggiungi**.
3. Apri l'app dall'icona e consenti la fotocamera quando lo chiede.

## Installarla su Android (es. Samsung Galaxy S24)

1. Apri l'indirizzo con **Chrome** (o Samsung Internet).
2. Chrome: tocca **Installa** nel riquadro in cima alla collezione, oppure **⋮ › Installa app**. Samsung Internet: **≡ › Aggiungi pagina a › Schermata Home**.
3. Apri l'app dall'icona e consenti la fotocamera quando lo chiede.

## Sicurezza

- Nessun account e nessun server: la collezione resta sul telefono, le immagini della fotocamera non escono dal telefono.
- Il lettore (cartella `ocr`, Tesseract.js con inglese, giapponese e coreano) e i caratteri (cartella `fonts`) sono dentro l'app: nessun codice da altri siti, nessuna richiesta a Google. Il riconoscimento delle carte avviene tutto sul telefono.
- La pagina ha una Content-Security-Policy: può collegarsi solo al catalogo TCGdex e al proprio GitHub (listino Cardmarket e impronte, in sola lettura) ed eseguire solo il proprio codice.
- Le copie di sicurezza vengono controllate prima del ripristino; il ripristino si può annullare per qualche secondo.

## Da sapere

- I dati sono salvati sul telefono, dentro l'app. Se cancelli l'app dalla schermata Home si cancellano anche loro: salva ogni tanto la copia di sicurezza (⚙︎ Impostazioni › Salva copia).
- La lettura del numero scarica la prima volta alcuni MB; serve la connessione. Con poca luce o riflessi forti scrivi il numero a mano.
- Il trend Cardmarket mescola lingue e condizioni: usa i coefficienti per lingua o il valore personale per correggerlo.
- La variante (normale, reverse, holo) si riconosce solo in modo approssimativo: se hai separato le pile, scegli la variante della sessione; altrimenti correggila con un tocco nella lista.
- Il riconoscimento dall'illustrazione vale per le edizioni occidentali (IT, EN, FR, DE, ES, PT); le carte giapponesi, coreane e cinesi si riconoscono dal numero.

Catalogo, immagini e prezzi da TCGdex (fonte Cardmarket). App per uso personale, non affiliata a The Pokémon Company né a Cardmarket.
