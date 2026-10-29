# Pump maintenu — 16 fenêtres restantes (round 2, 2026-10-29)

## Résumé exécutif

**Fenêtres gagnées : 0. Fenêtres perdues : 0.** Aucun patch source n'est proposé : la preuve
binaire ne permet pas de trancher les formes source restantes, et les règles interdisent un
changement non prouvé.

Ce round établit trois choses :

1. **La baseline est reproduite exactement** contre l'artefact publié : `scripts/window_measure.py`
   → **1 019 / 1 035 matched, 188 raw**, et les **16 non appariées sont exactement les cibles**.
2. **Le build publié n'est pas reproductible octet pour octet sous Linux/WSL** : le paquet
   exige le *cohorte natif macOS v1.44* (hash des binaires `rustc`/`cargo`), absent ici.
   Le même source compilé avec le v1.44 Linux donne un binaire différent, mais **le même set
   de 1 019 fenêtres appariées** (183 raw au lieu de 188 : 7 perdues / 2 gagnées, toutes des
   fonctions std/alloc/metaplex, pas des 16).
3. **Analyse des 16 recalculée contre le candidat maintenu** : les écarts sont désormais fins.
   La fenêtre `0x14f4e0` est à **4 instructions** (polarités de branche complémentaires) et
   8 régions de placement de blocs d'un match complet ; les 15 autres sont classées par
   cause (ordre de blocs intra-corps, décomposition en helpers, tuple de ligne différent).
4. **Tentative ciblée sur `0x14f4e0`** (5 variantes source, builds mesurés) : les inversions
   de condition fidèles déplacent bien la polarité et réduisent les régions de 8 à 5, mais
   **aucune ne matche** ; `matched` reste 1 019 et `raw` 183 pour toutes (zéro régression).
   Détail et preuves par micro-changement en §3bis.

| Mesure | Publié (`0f50faa8…`) | Linux avant (`linux01`) | Linux après (`linux02`) |
|---|---:|---:|---:|
| Fenêtres appariées | **1 019 / 1 035** | **1 019 / 1 035** | **1 019 / 1 035** |
| Exactes (`raw`) | **188** | **183** | **183** |
| Non appariées | 16 | 16 (les mêmes) | 16 (les mêmes) |

Sets `matched` **bit-identiques** entre publié, linux01 et linux02
(`sha256(JSON)=9bcaaca813bf87b19551505bfa345c886c189719301ef2a4bc46502c8a59867d`).
Sets `raw` linux01 = linux02 (`ad082bf8…`), sous-ensemble du publié à 7 près et sur-ensemble à 2 près.

## 1. Réconciliation d'environnement

### 1.1 Checkout

- `pumpfun-source-maintained`, `HEAD = 5bc20fe59624b533a63f6c94bb4ce16a6ff7935d`.
- Sparse checkout contient bien `research/pump-program-creator-notice-qualification-20261028/`
  et `repro/status.json` (pas `repro/` en entier).
- **Piège CRLF** : le checkout Windows a converti les fins de ligne. Le wrapper du paquet
  vaut `4f33f35f…` sur disque mais `d959fe00…` (valeur publiée) après normalisation LF.
  Après normalisation LF en mémoire, **les 65/65 entrées de `source_inputs` et le wrapper
  correspondent exactement** à `build-inputs.json` (`artifacts/source-lf-check.txt`).
  Le contenu source est donc authentique ; seuls les octets CRLF diffèrent.

### 1.2 Tentative de reproduction du build publié

`build.py` a été lancé avec la commande documentée :

```
python3 -B research/pump-program-creator-notice-qualification-20261028/build.py \
  --source-directory .../source \
  --sdk ~/.cache/solana/v1.44/platform-tools \
  --cargo-home ~/pumpwork/netcargo \
  --target-library-profile linux-v1.44-sbpf \
  --target-libraries ~/.cache/solana/v1.44/platform-tools/rust/lib/rustlib/sbpf-solana-solana/lib \
  --wrapper .../tools/pump_physical_source_wrapper.py \
  --output work/build-attempt-01 --jobs 2
```

Il s'arrête avant compilation sur `assert sha(wrapper)==expected['source_wrapper_sha256']`
(conséquence CRLF). Après normalisation LF, le prochain verrou est
`pump_target_library_profile.prepare()` : `spec["native_tools"]` exige
`rust/bin/rustc = 1f26338c…` et `rust/bin/cargo = cd27e411…`, c'est-à-dire les binaires
**macOS**. Le SDK Linux fournit `rustc = c8807b7e…`, `cargo = e7…` différents. Aucun SDK
Linux ne peut satisfaire ce verrou ; le profil lui-même est décrit comme
« unchanged native macOS v1.44 compiler/host libraries with official Linux x86_64 v1.44
SBPF target libraries ».

**Les 25 bibliothèques cibles SBPF, elles, sont identiques** : `check_libs.py` → 25/25 hashes
OK (`artifacts/target-libs-check.txt`). Seuls les outils hôtes diffèrent.

### 1.3 Build Linux du même source

`scripts/linux_build.py` reproduit le staging de `build.py` (workspace, LF, wrapper,
`-Zremap-cwd-prefix`, `--locked --offline`) mais avec le v1.44 Linux et les 25 libs admises :

| | SHA-256 |
|---|---|
| publié `unstripped.so` | `0f50faa8c325104dc77898ed84866dec2ad1eec475b6abba72c475cf7bf9bab6` |
| publié `candidate.so` | `d0377d7cef5b7378063f8bfabac5dc9c08d29eeaaaaa14022d36909688ff5e1b` |
| linux01/02 `unstripped.so` | `297ef41e784ca5db96e6813345e7f6342b554efd46ccab47be4b26f63cbe47d9` |
| linux01/02 `candidate.so` | `aa5b10d7e40bbb6a87d7055ca26aae85177d10dc00b9a55dc517aefa47624cf6` |

Deux builds Linux dans des **targets neufs distincts** donnent des fichiers **byte-identiques**
(déterminisme). L'écart d'identité avec le publié est donc bien un écart d'hôte de compilation.

Fenêtres `raw` perdues par l'hôte Linux (7) : `0x188d30`, `0x188fe0`, `0x1891d8`, `0x189340`,
`0x18de90`, `0x18e568`, `0x1a7b00` — `String::write_char`, `String::write_str`, deux
`RawVec::do_reserve_and_handle`, `mpl_token_metadata::CollectionDetails::serialize`,
`Uses::serialize`, `Debug::fmt`. Gagnées (2) : `0x199af0`, `0x199b18` (`Display::fmt`,
`Debug::fmt`). Aucune n'est parmi les 16.

## 2. Les 16 fenêtres contre le candidat maintenu

Mesure : `matched` = même taille + mêmes octets normalisés (immédiat d'appel et pointeur
relogé masqués) + même motif de relocations ; `raw` = octets identiques.
« Squelette » = séquence `opcode.dst.src` alignée (immediates et déplacements ignorés).
« Callees = » = multiensemble des signatures normalisées des fonctions appelées (alias-free).

| Adresse | Taille | Fonction candidate | Δ | Tuples = | Squelette = | Régions | Callees = |
|---|---:|---|---:|---|---:|---:|---|
| `0x1e7c0` | 15 576 | `create_v2::execute` | −728 | oui | 898/1947 | 90 | non |
| `0x22a10` | 27 400 | `admin_cto::execute` | −7 496 | **non** | 594/3425 | 72 | non |
| `0x4c158` | 8 368 | `migrate_v2::create_token_account_v2` | +56 | oui | 764/1046 | 67 | **oui** |
| `0x5b3b0` | 18 584 | `multi_hop_curve::swap_hop` | −48 | **non** | 846/2323 | 138 | non |
| `0x6cd78` | 8 544 | `legacy_sell::process_cashback_inner` | +272 | oui | 921/1068 | 63 | non |
| `0x72810` | 7 832 | `sweep::execute` | +952 | oui | 554/979 | 70 | non |
| `0x77940` | 8 832 | `token_incentives::claim_token_incentives::cashback::claim_v2` | −368 | oui | 598/1104 | 90 | non |
| `0x80df8` | 2 120 | `trade::v3_buy_costs` | −64 | oui | 205/265 | 28 | **oui** |
| `0x83c00` | 3 440 | `trade::v3_execute_buy` | −32 | oui | 352/430 | 33 | **oui** |
| `0x13b9b8` | 15 480 | `buy_v2::buy_handler` | −56 | oui | 1236/1935 | 168 | **oui** |
| `0x13f630` | 20 184 | `buy_v2::buy_exact_quote_in_handler` | −88 | oui | 1782/2523 | 231 | **oui** |
| `0x144508` | 13 976 | `sell_v2::execute` | +128 | oui | 1328/1747 | 173 | **oui** |
| `0x147ba0` | 3 672 | `trade::buy` | +128 | oui | 354/459 | 59 | non |
| `0x1489f8` | 7 856 | `trade::buy_exact_quote` | −56 | oui | 694/982 | 80 | non |
| `0x14a8a8` | 6 032 | `trade::sell` | +24 | oui | 552/754 | 98 | **oui** |
| `0x14f4e0` | 13 224 | `buy_exact_sol_in` | **0** | oui | **1627/1653** | **8** | **oui** |

Les triplets `(path,line,code)` correspondent déjà **exactement** pour 14/16 fenêtres : le
placement de lignes du source maintenu est donc déjà correct sur ces corps. Les exceptions :

- `0x22a10` : déployé `admin_cto.rs:2006` (sans code) ; candidat `admin_cto.rs:648`.
  Le corps déployé fait 7 496 octets de plus : la forme `Accounts`/handler diffère encore.
- `0x5b3b0` : le candidat possède un site d'erreur **supplémentaire**
  `multi_hop_curve_swap.rs:581 / 6024` absent du déployé ; les 5 autres tuples concordent.

## 3. Cause par fenêtre et raison de l'absence de patch

### 3.1 `0x14f4e0` — la plus proche (cause localisée, non corrigée)

Même taille (13 224 B), mêmes triplets, mêmes callees. 1 627/1 653 instructions identiques
en squelette, **8 régions** de différence. Le multiensemble de squelettes ne diffère que par
**4 instructions**, et ce sont des **polarités de branche complémentaires** :

| Déployé | Candidat | Interprétation |
|---|---|---|
| `0x150008  jge r3, r0, +0x29` | `0x14F1A8  jlt r3, r0, +0x2e` | comparaison inversée |
| `0x150160  jne r3, 0, +0x20` | `0x14F1B8  jeq r3, 0, +0x3d` | comparaison inversée |

Les régions restantes sont des permutations de blocs froids (construction d'erreur propriétaire
`buy.rs` lignes 59/92/110, ancrées par les triplets) : le bloc « erreur ligne 110 » est inline
à `0x150158` chez le déployé, tandis que le candidat place un autre bloc à `0x14F320` et
décale l'ensemble (`D[399:401] → C[404:421]`, `D[429:449] → ∅`). C'est exactement le mur
`jne` vs `jeq;ja` documenté par le projet, qui se traite par **réordonnancement de blocs
LLVM-IR**, pas par une retouche de ligne. Aucun changement de source n'a été fait : aucune
forme source n'est prouvée par le binaire pour produire cet ordre.

### 3.2 Huit fenêtres à callees identiques (codegen intra-corps)

`0x4c158`, `0x80df8`, `0x83c00`, `0x13b9b8`, `0x13f630`, `0x144508`, `0x14a8a8`, `0x14f4e0` :
la décomposition en helpers est **la bonne** (mêmes signatures de callees). Les écarts sont
internes (ordre de blocs, allocation de registres, polarités), donc du même type que 3.1.

Résultat négatif utile : pour `0x13b9b8`/`0x13f630` le déployé appelle
`transfer_from_user` et le candidat `transfer_from_user_recipient` ; pour `0x144508`,
`transfer_to_user` vs `transfer_to_recipient`. **Ces variantes ont des octets normalisés
identiques** (`transfer_to_user` et `transfer_to_recipient` : 944 B, même
`normalized_sha256` ; idem `transfer_from_user`/`..._recipient` : 704 B). Le choix de variante
est donc **invisible pour la métrique** (l'immédiat d'appel est masqué) : ce n'est pas un levier.

### 3.3 Huit fenêtres à callees différents (vraie décomposition)

- `0x147ba0` et `0x1489f8` : leur multiensemble de callees diffère **uniquement parce qu'ils
  appellent `0x80df8` et `0x83c00`**, deux autres fenêtres cibles non appariées (leurs
  contreparties candidates sont `trade::v3_buy_costs` et `trade::v3_execute_buy`). Ce n'est
  pas une décomposition indépendante : corriger les deux petits helpers fermerait
  potentiellement quatre fenêtres. Le graphe d'appel induit sur les 16 est minimal :
  seuls `0x147ba0 → {0x80df8, 0x83c00}` et `0x1489f8 → {0x80df8, 0x83c00}` existent.
- `0x5b3b0` (`multi_hop_curve::swap_hop`) : 32 callees déployés absents / 23 ajoutés, plus un
  tuple d'erreur en trop côté candidat → corps encore différent.
- `0x72810` (`sweep`) : le déployé utilise `Rent::minimum_balance`, `legacy_buy::native_payments::transfer`,
  `quote_payments::transfer_to_owned`, `memcmp` ; le candidat `ensure_rent_exempt`,
  `Lamports::add_lamports`, `transfer_quote_tokens`.
- `0x77940` (`claim`/cashback) : le déployé manipule les `AccountInfo`/lamports directement,
  le candidat passe par `Lamports::add_lamports`.
- `0x6cd78` (`process_cashback_inner`) : `Account::try_from_unchecked` + `rust_begin_unwind`
  côté déployé vs `Account::try_from` + panic de slice côté candidat.
- `0x1e7c0` (`create_v2::execute`) : même décomposition à une instanciation
  `Error::with_values` près, mais 728 octets et 90 régions d'écart.
- `0x22a10` (`admin_cto::execute`) : le plus éloigné (Δ −7 496 B, tuple de ligne différent).

## 3bis. Round 3 — tentative ciblée sur `0x14f4e0` (variantes mesurées)

Le source maintenu a été copié dans un répertoire de travail `work2/` (recréé par `stage2.py`,
jamais dans le checkout), `buy.rs` seul modifié.
Chaque variante est un build Linux complet, mesuré avec `scripts/window_measure.py` contre
`evidence/original/pump/deployed.so` et l'`unstripped.so` de la variante.

| Variante | Édition (ligne 110 / 92) | Taille | Δ | Squelette | Régions | Multiset D/C | `0x14f4e0` | matched / raw |
|---|---|---:|---:|---:|---:|---:|---|---|
| `v0` | aucune (référence) | 13 224 | 0 | 1 627/1 653 | 8 | 2 / 2 | non | 1 019 / 183 |
| `v1` | 110 → `if quote==0 { return Err(PumpError::…into()) }` | 13 024 | −200 | 1 610 | 6 | 18 / 4 | non | 1 019 / 183 |
| `v1c` | 110 → `if quote>0 {} else { return Err(error!(…).with_values((quote,0))) }` | 13 224 | **0** | **1 629** | **5** | 3 / 3 | non | 1 019 / 183 |
| `v1d` | 110 → `if quote==0 { return Err(error!(…).with_values((quote,0))) }` | 13 224 | 0 | 1 629 | 5 | 3 / 3 | non | 1 019 / 183 |
| `v2c` | 92 → inversion fidèle (`raw_quote`) | 13 216 | −8 | 1 594 | 8 | 3 / 2 | non | 1 019 / 183 |
| `v3c` | 92 + 110 inversions fidèles | 13 216 | −8 | 1 594 | 7 | 4 / 3 | non | 1 019 / 183 |

Enseignements prouvés par les binaires :

1. **`v1` est rejetée** : `require_gt!` ajoute `.with_values((value,0))` (macro Anchor 0.31.1,
   `lib.rs:679-681`). L'écrire avec `into()` seul retire la charge utile (−200 B) : non fidèle.
2. **`v1c` et `v1d` compilent au même binaire** (`0680fcf1…`) : LLVM canonicalise
   `if cond {} else {…}` et `if !cond {…}`. L'inversion *source* de la ligne 110 ne contrôle
   donc pas la polarité de `jne`/`jeq` ; elle déplace la polarité sur un autre test
   (`r1` au lieu de `r3`) et améliore le squelette (+2) sans matcher.
3. **`v2c`/`v3c` changent la taille (−8 B)** : la forme inversée de la ligne 92 n'est pas
   canonisée vers la macro et éloigne (1 594). Rejetées.
4. **Aucune variante ne perd de fenêtre** : `matched_set` inchangé (1 019, hash `9bcaaca8…`)
   et `raw` 183 partout. Le diff source final reste **vide** : aucune variante n'est retenue.

Conclusion : la polarité observée n'est pas une simple condition écrite à l'envers ; c'est
l'ordre de placement des blocs froids (construction d'erreur ligne 110 inline chez le déployé,
`0x150158`, vs bloc déplacé chez le candidat) que seul un travail IR/`llc` peut fixer. Le
prochain levier prouvé est donc l'émission LLVM-IR de `buy_exact_sol_in`, pas une retouche
de condition.

## 4. Pourquoi aucun patch

Cinq variantes ciblées (§3bis) ont testé les leviers source sur `0x14f4e0` ; aucune ne matche.
Aucune des causes identifiées ne se corrige par un changement de source **prouvé** :

- les écarts majoritaires sont des **ordres de blocs LLVM** (polarités `jge/jlt`, `jne/jeq`,
  permutations de blocs froids) ; la méthode documentée est l'émission d'IR + réordonnancement
  `llc`, hors de portée d'un patch source ponctuel et interdit en sweep ;
- les écarts de décomposition (`0x147ba0`/`0x1489f8`) demandent de réécrire les corps
  `trade_v3` puis de re-prouver chaque ligne, pas une substitution de nom ;
- les variantes de helpers interchangeées sont **métriquement neutres** (3.2), donc les
  modifier n'apporterait rien ;
- toute retouche non prouvée violerait « mesuré ou ça n'existe pas » et « une ligne = un
  triplet prouvé ».

Le diff source est donc **vide** (`source-diff.patch`, 0 octet) et les ensembles `matched`
et `raw` sont identiques avant/après (builds linux01/linux02).

## 5. Reproductibilité

```powershell
# 1. vérifier la source et les bibliothèques cibles
wsl -d kali-linux -- bash -lc 'python3 /mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained/scripts/check_source_lf.py'
wsl -d kali-linux -- bash -lc 'python3 /mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained/scripts/check_libs.py'

# 2. mesurer l'artefact publié (doit donner 1019/188)
wsl -d kali-linux -- bash /mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained/scripts/baseline.sh

# 3. build Linux (target neuf) + mesure
wsl -d kali-linux -- bash -lc 'python3 /mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained/scripts/linux_build.py linux03'

# 4. analyse des 16
wsl -d kali-linux -- bash -lc 'python3 /mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained/scripts/analyze16.py'

# 5. variantes ciblées 0x14f4e0 (recrée work2/, puis build + évaluation)
wsl -d kali-linux -- bash -lc 'cd /mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained && python3 scripts/stage2.py && python3 scripts/apply_variant.py v1c && bash scripts/build_variant.sh v1c && python3 scripts/eval_variant.py work2/out/v1c-unstripped.so'
```

Tentative `build.py` publiée : `scripts/build_attempt.sh` (s'arrête au hash wrapper à cause
du CRLF ; après LF, au verrou macOS).

## 6. Toolchain

| Élément | Valeur |
|---|---|
| Hôte | WSL2 `kali-linux`, Linux 6.6.87.2-microsoft-standard-WSL2 x86_64 |
| rustc v1.44 | `rustc 1.79.0-dev`, sha256 `c8807b7ebede8578ac5a257ea333780f9d89bd356064fd8184af7e996cb71a97` |
| cargo v1.44 | `cargo 1.79.0 (804e32543 2025-01-29)` |
| clang v1.44 | `18.1.7-rust-dev`, sha256 `b6541efe3e5662c1e1679c8a819535da574823b68da32522164dbcdb6ef8b3d9` |
| objcopy v1.52 | sha256 `673b3b86f0b1b8eadd755e29e2f66a7582248ef3bda7a267fbb370b733c1cb69` |
| Cohortes publiées exigées | rustc `1f26338c…`, cargo `cd27e411…` (macOS) → indisponibles ici |
| Bibliothèques cibles | 25/25 hashes SBPF v1.44 Linux conformes au profil |

## 7. Limitations explicites

- Le build publié (`d0377d7c…` / `0f50faa8…`) **n'est pas reproduit** ici : le paquet verrouille
  des outils hôtes macOS. Le build Linux est un **substitut mesuré** (même set apparié,
  5 raw de moins), pas une preuve d'identité.
- Les 7/2 fenêtres raw d'écart sont des fonctions std/alloc/metaplex : effet d'hôte, non
  analysé plus avant.
- Les paires déployé→candidat sont choisies par module/taille/triplets ; pour `0x22a10`,
  `0x5b3b0` et `0x77940` la correspondance de corps n'est pas certaine (le candidat peut
  fusionner ou scinder des fonctions, et le symbole `claim_token_incentives::cashback::claim_v2`
  ne couvre que 8 464 B contre 8 832 B déployés).
- L'analyse « squelette » ignore immediates et déplacements : elle mesure la forme, pas
  l'égalité d'octets.
- Aucun test runtime, aucune comparaison différentielle : hors périmètre.
- Les formes source ne sont pas prouvées pour les écarts de blocs ; aucune coordonnée
  historique n'a été fabriquée, aucun padding binaire.

## 8. Contenu du paquet

```
packet-maintained/
  RESULT.md, source-diff.patch (0 octet), SHA256SUMS
  artifacts/
    baseline.json                 mesure de l'artefact publié (1019/188)
    before.json, after.json       mesures linux01 / linux02 (1019/183)
    published-vs-linux.json       écarts raw (7 perdus, 2 gagnés), matched identiques
    analysis16.json               table machine des 16 (tuples, squelette, régions, callees)
    variants-0x14f4e0.json        les 5 variantes : taille, squelette, régions, multiset, matched
    measure-v0.json … v3c.json    mesures complètes de chaque variante (matched/raw/sets)
    experiment-v1.patch … v3c.patch  diffs exacts des 5 variantes (v1, v1c, v1d, v2c, v3c ; aucune retenue)
    table16.md                    table Markdown
    callee-signatures.json        comparaison alias-free des callees
    candidate-match.json          meilleures contreparties par fenêtre
    pairs.json                    paires et tuples déployé/candidat
    environment.txt, source-lf-check.txt, target-libs-check.txt
    build-linux01.json, build-linux02.json
  scripts/                        mesureur, build Linux, staging/variantes, analyses, vérificateurs
```

Attribution : construit sur `lalalune/pumpfun-source` (MIT). `deployed.so` n'est jamais une
entrée de build ; il sert uniquement à la mesure et à l'analyse.
