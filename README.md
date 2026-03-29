A german GUI to use Mastodon with C64 Ultimate.
It tooks the code https://github.com/Havoc6502/MOStodon 

The zip-File contains all you need.

Just for Linux


Diese Anleitng ist auch AI-generiert

# MOStodon GUI – Anleitung

MOStodon ist ein Mastodon-Client für den Commodore 64. Er besteht aus zwei Teilen: einem Python-Proxy-Server, der auf dem PC läuft, und einem Terminalprogramm auf dem C64. Diese Anleitung erklärt, wie man den Server mit der GUI startet.

---

## Was du brauchst

- Einen PC oder Laptop mit **Ubuntu** (oder einer anderen Linux-Distribution)
- Einen **Commodore 64** mit WLAN-Modem (z.B. 1541 Ultimate II+) oder ein Emulator wie VICE mit TCPser
- Ein **Mastodon-Konto** (auf einer beliebigen Instanz, z.B. norden.social, mastodon.social usw.)
- Eine funktionierende **Netzwerkverbindung** (PC und C64 müssen im selben WLAN/LAN sein)

---

## Schritt 1: MOStodon herunterladen

Öffne ein Terminal und gib ein:

```bash
cd ~/Downloads
wget https://github.com/Havoc6502/MOStodon/archive/refs/heads/main.zip
unzip main.zip
```

Oder lade die ZIP-Datei manuell von https://github.com/Havoc6502/MOStodon herunter und entpacke sie.

---

## Schritt 2: Voraussetzungen installieren

Öffne ein Terminal und installiere die nötigen Pakete:

```bash
sudo apt install python3 python3-venv python3-tk
```

Das sind die einzigen Pakete, die du systemweit brauchst. Alles andere erledigt die GUI automatisch.

---

## Schritt 3: Mastodon-App erstellen und Token holen

1. Öffne deinen Browser und gehe zu deiner Mastodon-Instanz (z.B. https://norden.social)
2. Einloggen → **Einstellungen** → **Entwicklung** → **Neue Anwendung**
3. Name: `MOStodon` — Berechtigungen: read, write, follow (Standard ist meistens richtig)
4. Speichern → auf die neue App klicken → **Zugriffstoken** kopieren

Den Zugriffstoken brauchst du gleich in der GUI.

---

## Schritt 4: GUI-Launcher herunterladen und starten

Speichere die Datei `mostodon_gui.py` irgendwo auf deinem PC, z.B. in deinem Home-Verzeichnis oder im MOStodon-Ordner. Dann im Terminal:

```bash
python3 ~/mostodon_gui.py
```

Beim ersten Start macht die GUI folgendes automatisch:
- Sie sucht nach `MOStodon.py` auf deinem System
- Sie erstellt eine Python-Umgebung (venv) im MOStodon-Ordner
- Sie installiert alle benötigten Python-Pakete
- Sie speichert deine Einstellungen in `~/.mostodon_config.json`

---

## Schritt 5: GUI ausfüllen und Server starten

Beim ersten Start musst du drei Dinge eintragen:

| Feld | Beispiel |
|---|---|
| Pfad zu MOStodon.py | `/home/frank/Downloads/MOStodon-main/MOStodon.py` |
| Mastodon-Instanz | `https://norden.social` |
| Access Token | (der Token aus Schritt 3) |

Beim nächsten Start sind alle Felder bereits ausgefüllt — einfach auf **SERVER STARTEN** klicken.

Die GUI zeigt dir auch direkt die **AT-Befehle** an, die du auf dem C64 eingeben musst:

```
atdt192.168.18.117:6502
```

---

## Schritt 6: Vom C64 verbinden

1. Starte auf dem C64 dein Terminalprogramm (z.B. **UltimateTerm** oder **CCGMS**)
2. Wähle **BBS** als Verbindungstyp
3. Gib den AT-Befehl ein, der in der GUI angezeigt wird (z.B. `atdt192.168.18.117:6502`)
4. Drücke Enter — du solltest das MOStodon-Menü sehen

---

## Fehlerbehebung

**"No such file or directory: venv/bin/pip"**
Das venv wurde nicht korrekt erstellt. Lösche es und starte neu:
```bash
rm -rf /pfad/zu/MOStodon-main/venv
```
Dann erneut auf SERVER STARTEN klicken.

**"The access token is invalid"**
Gehe in Mastodon → Einstellungen → Entwicklung → MOStodon → Token regenerieren. Neuen Token in der GUI eintragen.

**"This action is outside the authorized scopes"**
Die Mastodon-App hat nicht die richtigen Berechtigungen. Gehe in Mastodon → Einstellungen → Entwicklung → MOStodon und stelle sicher dass read, write und follow aktiviert sind.

**C64 verbindet sich, aber nichts passiert**
Prüfe ob PC und C64 im selben Netzwerk sind. Die IP-Adresse in der GUI muss erreichbar sein.

**tkinter nicht gefunden**
```bash
sudo apt install python3-tk
```

---

## Konfiguration ändern

Alle Einstellungen werden in `~/.mostodon_config.json` gespeichert. Du kannst diese Datei mit einem Texteditor öffnen, falls du etwas manuell ändern möchtest. Normalerweise reicht es, die Felder in der GUI zu ändern und neu zu starten.

---

## Hinweise

- Der Token ist wie ein Passwort — teile ihn nicht mit anderen.
- Wenn sich deine IP-Adresse ändert (z.B. nach einem Router-Neustart), zeigt die GUI beim nächsten Start die neue Adresse an.
- Der Server läuft nur solange die GUI offen ist. Schließt du die GUI, trennt sich auch der C64.
