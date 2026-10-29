# PumpSwap maintenu — fenêtre `0x4c750` : reproduction du build et cause exacte du dernier écart

Paquet séparé (`packet-maintained/`). Aucune écriture git, aucun accès GitHub, aucun
téléchargement. Le `.so` déployé n'est jamais un input de build. Attribution :
lalalune/pumpfun-source (MIT) ; métrique = `scripts/window_measure.py` du checkout.

---

## 0. Résultat en une ligne

- **Phase 1 : le build maintenu est reproduit à l'octet** (sans podman) —
  `candidate.so = 86dbc2c64e81…`, `symbols.so = 7271aaf8…`, y compris en rebuild à
  target neuf.
- **Phase 2 : l'écart de `0x4c750` est entièrement localisé** — même adresse, même
  taille (9 024 o), même nombre d'instructions (1 075), même multiset d'instructions
  **à une seule encoding près**, 47/47 lignes de relocation appariables, **21 lignes
  d'offset décalées** (le chiffre du README). Les 10 tuples `file!()/line!()` sont
  déjà identiques.
- **Phase 3 : aucune correction source n'a été trouvée qui gagne la fenêtre.**
  10 variantes de forme source ont été testées ; 8 produisent un binaire
  **byte-identique** au build maintenu, 1 est rejetée (changement global), 1 contrôle
  positif prouve que la boucle rebuild bien. Zéro régression (784/784 conservés).
- **Phase 3bis (attributs) : résultat négatif prouvé.** `#[cold] #[inline(never)]`
  *sort* le bras 467 de la fenêtre (cashback 8 864 o, helper de 520 o hors fenêtre) —
  l'inverse du déployé, qui le garde intra-fonction à `0x4e718`. `#[inline(always)]`
  et le helper de check donnent un binaire **identique**. `#[cold]` sur `cashback`
  régresse (783/785). Aucun attribut ne produit un bloc froid intra-fonction.
  `0x4c750` reste non appariée ; la cause est identifiée et prouvée au niveau IR/bloc.

---

## 1. Phase 1 — reproduction du build maintenu

### 1.1 Environnement

- Checkout : `pumpfun-source-maintained` (HEAD `5bc20fe5`).
- Source : `research/amm-layout-closure-20261028/` (`build.py`, `ordered.ld`,
  `rustc_wrapper.py`, `linker_wrapper.py`, `workspace_recipe.py`).
- Le builder scellé utilise `podman` + image `solanafoundation/solana-verifiable-build`
  — **podman absent dans WSL kali**. J'ai donc exécuté la **même recette en natif** :
  staging identique via `workspace_recipe.py stage`, mêmes flags rustc, même
  `ordered.ld`, même `rust-lld` ; seule adaptation : le point de montage `/out` du
  conteneur devient `$AMM_OUT` dans les deux wrappers (aucun autre changement : le
  hash du script de link par défaut est vérifié, `ordered.ld` est substitué tel quel).
- `ordered.ld` du checkout est en **CRLF** (hash `e16a4a42…`) ; après `tr -d '\r'` il
  donne exactement le hash enregistré `b8a35889…`. Le linker l'accepte tel quel et le
  binaire reproduit est identique.

### 1.2 Résultats

| build | target dir | candidate.so | symbols.so |
|---|---|---|---|
| build-a (référence enregistrée) | — | `86dbc2c64e81988dead173039b61fa01ba5f68a00fbb6f6dd49f2cda0afec37f` | `7271aaf8afe13b6c8f13a6cf0e9534896a66650dda13a2aa1b32e41edd46426d` |
| reproduction native `base` | `target-m-base` | **identique** | **identique** |
| rebuild froid `cold` | `target-m-cold` (neuf) | **identique** | **identique** |

Mesure (métrique du dépôt, `measure(deployed, symbols.so)`) :

```
total 785 | matched 784 | raw 784 | unmatched [[313168, 9024]]
```

`0x4c750` = 313 168 = la seule fenêtre non appariée, taille 9 024 o. C'est bien la
cible. (Mesurer le `candidate.so` strippé donnerait 2/785 : la métrique indexe les
fonctions candidat par la table de symboles, donc on mesure `symbols.so`.)

---

## 2. Phase 2 — anatomie exacte de l'écart

### 2.1 Le cadre

| | déployé | candidat maintenu |
|---|---:|---:|
| adresse | `0x4c750` | `0x4c750` |
| taille | **9 024 o** | **9 024 o** |
| instructions | **1 075** | **1 075** |
| lignes de relocation | **47** | **47** |
| tuples `sell.rs` | 10 (dont 2× ligne 502) | 10 (mêmes lignes, mêmes codes : 378, 383, 392, 395, 444, 448, 464, 467, 502, 502) |

Tout le reste du binaire est identique : le désaccord n'est ni la taille, ni les
lignes, ni les cibles de relocation. Les 8 tuples « réguliers » sont extraits par
`errsites2.py` ; les deux sites `stw …, 502` sont vérifiés dans les deux binaires par
`find_line_store.py` (aux adresses `0x4e6b8`/`0x4e8e0` déployé et
`0x4e798`/`0x4e8e8` candidat).

### 2.2 Les instructions sont identiques à une encoding près

Multiset des instructions (cibles d'appel, adresses `lddw` et déplacements de branche
masqués) :

```
only in deployed : 1 × jeqr r2, r3, <OFF>
only in candidate: 1 × jner r2, r3, <OFF>
```

C'est l'unique différence d'instruction de toute la fenêtre. Elle est à `0x4d450`,
sur le `?` de `user_volume_accumulator.try_borrow_data()` (source ligne 445) :
le déployé encode `jeq +1; ja far` (2 instructions), le candidat `jne far`
(1 instruction) ; le compte total reste 1 075 des deux côtés.

### 2.3 Une seule décision de placement de bloc

Inventaire de blocs de base (fin de bloc = `ja`/saut conditionnel/`exit`, tokens
masqués) :

```
blocs déployé = 171   blocs candidat = 170
blocs à tuple de tokens identique : 169/171 (déployé) et 168/170 (candidat)
```

Le diff de séquence de blocs (`analysis/block-sequence-diff.txt`) montre **un seul
déplacement structurel** : le bloc d'erreur de la ligne 467
(`InvalidCashbackAccumulatorAta`, `require!(ata.is_writable, …)`).

| | déployé | candidat |
|---|---|---|
| bloc d'erreur 467 | `0x4e718` (queue froide, après le corps) | `0x4e2a0` (inline, juste après le test) |
| ordre create / join | create (clones `0x4e258`) **puis** join (`0x4e3e0`) | join (`0x4e248`) **puis** create (trampoline `0x4e378`, clones `0x4e390`) |
| saut `is_writable` | `jeq r2,0,+0x9b` (vers la queue) | `jeq r2,0,+0xd` (inline) |

Autrement dit : le compilateur a choisi, pour le déployé, de poser le bloc `then`
(create ATA) en fallthrough et le bloc d'erreur 467 dans la queue froide ; pour le
candidat, c'est le bloc de jointure (`try_from_unchecked`) qui est en fallthrough.

### 2.4 Preuve IR de la cause

IR émis (`--emit=llvm-ir`, mêmes flags) : la fonction
`instructions::swap::sell::cashback` a 74 blocs. Le test `is_writable` est en `bb54` :

```
bb54: %_166.not = icmp eq i8 %190, 0
      br i1 %_166.not, label %bb60, label %bb59     ; bb60 = erreur 467, bb59 = suite
bb60: … store i32 467 … call Error::from … br label %bb76
bb59: %_176 = call AccountInfo::data_is_empty
      br i1 %_176, label %bb65, label %bb68          ; bb65 = create, bb68 = join
```

Dans l'IR **candidat**, l'ordre d'émission est `… bb59, bb68 (join), bb65 (create) …` :
le join précède le create, et `MachineBlockPlacement` conserve cet ordre (join en
fallthrough). Pour obtenir le layout déployé il faudrait un IR où `bb65` précède
`bb68`. Les 10 tuples d'erreur étant identiques par ailleurs, la reconstruction
maintenue est sémantiquement exacte ; **seul l'ordre de blocs IR/MIR diffère**.

### 2.5 Relocations : 47/47, 21 offsets décalés

Ledger complet dans `analysis/reloc-deployed.json`, `reloc-candidate.json`,
`reloc-pairing.txt` :

- **47 lignes** de chaque côté, toutes type 8 (`R_BPF_64_64`) sur des `lddw` ;
- **47/47 appariables par payload** (10 chemins `sell.rs`, 18 chaînes `.rodata`,
  4 `;`, 8 `<`, 4 `=`, 1 message `Display`, 2 seed `user_volume_accumulator`) ;
- **0 ligne sans contrepartie** de part et d'autre ;
- **26 lignes à offset identique, 21 lignes à offset décalé** — exactement le
  « 21 relocation-offset rows » du README. La comparaison ensembliste
  `(offset,type,symbol)` de `window_gap.py` donne bien **21 offsets seulement-déployé
  et 21 seulement-candidat** (mêmes payloads, offsets décalés). Décalages observés :
  `-0x478, -0x340, -0x58, -0x8, 0, +0x8, +0xe0` (les 21 lignes sont listées dans
  `reloc-pairing.txt`).

Les 26 offsets identiques sont avant la divergence ou après reconvergence ; les 21
autres suivent le bloc déplacé / le fold de branche. Il n'y a **aucun écart de
relocation de nature sémantique** : uniquement des offsets, dus au layout.

### 2.6 Ce qui reste pour gagner la fenêtre

Une seule chose : reproduire l'ordre de blocs IR du déployé autour de
`if ata.data_is_empty() { create }` (create avant join) et de son erreur 467
(queue froide). Tant que cet ordre n'est pas reproduit, la taille et les
instructions restent justes mais les déplacements de branche diffèrent, donc le
hash normalisé et les 21 offsets de relocation diffèrent.

---

## 3. Phase 3 — variantes source testées (mesurées)

Toutes les variantes ne touchent que `legacy…/sell.rs` (cashback), conservent les
lignes 378/383/392/395/444/448/464/467/502 et la sémantique. Boucle :
`build-maintained.sh` (target chaud) + `verify_baseline_cand.py` (métrique dépôt).

| variante | changement | candidate.so | matched | raw |
|---|---|---|---:|---:|
| base | — | `86dbc2c6…` | 784 | 784 |
| v1 | `if !ata.is_writable { return err!(…) }` au lieu de `require!` | `86dbc2c6…` | 784 | 784 |
| v2 | `else {}` vide sur le `if ata.data_is_empty()` | `86dbc2c6…` | 784 | 784 |
| v4 | `if !ata.data_is_empty() {} else { create }` | `86dbc2c6…` | 784 | 784 |
| v5 | `match ata.data_is_empty() { true => create, false => {} }` | `86dbc2c6…` | 784 | 784 |
| v7 | `match ata.is_writable { false => return err!, true => {} }` | `86dbc2c6…` | 784 | 784 |
| v8 | `if ata.is_writable == false { return err! }` | `86dbc2c6…` | 784 | 784 |
| v9 | `match ata.data_is_empty() { false => {}, true => create }` | `86dbc2c6…` | 784 | 784 |
| v10 | `if ata.is_writable { } else { return err! }` | `86dbc2c6…` | 784 | 784 |
| v12 | `match try_borrow_data() { Ok/Err }` au lieu de `?` | `21062eb2…` | 784 | **257** |
| ctl | contrôle : code d'erreur 467 changé | `09542d5d…` | 784 | 784 |

Conclusions :

- **8 variantes de forme produisent un binaire strictement identique** au build
  maintenu (même sha256). Le frontend canonicalise ces écritures : elles ne changent
  ni l'IR ni le layout. Elles ne peuvent donc pas gagner la fenêtre.
- **v12** change bien le binaire, mais globalement (`.text` −24 o, 445 039 octets
  décalés, raw 784→257) : c'est un changement de layout global, rejeté.
- **ctl** (changement sémantique volontaire) change le binaire : la boucle rebuild
  bien, les résultats ci-dessus ne sont pas des faux négatifs de cache.
- **Zéro régression** : aucune variante retenue ne modifie le binaire ; toutes les
  mesures restent 784/784 avec `0x4c750` seule non appariée.

Aucun patch n'est donc proposé pour intégration. Les diffs des variantes sont
fournis dans `variants/` à titre de preuve (ils s'appliquent au source maintenu et
sont tous non-gagnants).

---

## 3bis. Mission « attributs de fonction » — variantes testées et mesurées

Hypothèse testée : demander au compilateur l'outlining du bras d'erreur 467 en zone
froide (`#[cold] #[inline(never)]`) ou son contraire (`#[inline(always)]`), puis
cibler l'encodage de `0x4d450`. Toutes les variantes conservent la sémantique et les
lignes d'erreur 378/383/392/395/444/448/464/467/502 (vérifié par `errsites2`/`all_tuples`).

| variante | changement (source) | cashback | insns | sha256 | matched | raw | verdict |
|---|---|---:|---:|---|---:|---:|---|
| base | — | 9 024 | 1 075 | `86dbc2c6…` | 784 | 784 | référence |
| **a1** | `#[cold] #[inline(never)] fn cold_467()` imbriqué (error! ligne 467) + `if !ata.is_writable { return cold_467(); }` | **8 864** | 1 058 | `4e6df695…` | 784 | 257 | **outline** : `cashback::cold_467` = 520 o à `0x11bbb8`, hors fenêtre → taille ≠ 9 024 |
| **a2** | même helper avec `#[inline(always)]` | 9 024 | 1 075 | `86dbc2c6…` | 784 | 784 | **byte-identique** (inliné) |
| **a3** | `#[cold] #[inline(never)] fn check_467(ata)` (check + bras) | 9 024 | 1 075 | `86dbc2c6…` | 784 | 784 | **byte-identique** (le helper local est inliné malgré l'attribut) |
| **a4** | `#[cold]` sur `fn cashback` elle-même | 9 024 | 1 075 | `dddabfd3…` | **783** | 257 | **régression** : cashback déplacé à `0x119928`, fenêtre 0x49b50 perdue → rejeté |
| **c1** | `match try_borrow_data() { Ok(d)=>d, Err(e)=>return Err(Error::from(e)) }` au lieu de `?` | **9 000** | 1 072 | `21062eb2…` | 784 | 257 | n'atteint pas l'encodage `jeqr+ja` (émet toujours `jne` à `0x4d440`) ; taille ≠ 9 024 |
| **c2** | `.map_err(|e| Error::from(e))?` | 9 000 | 1 072 | `21062eb2…` | 784 | 257 | identique à c1 |
| **a1c1** | a1 + c1 | **8 840** | 1 055 | `a1359f1f…` | 784 | 257 | outline + conversion explicite → taille ≠ 9 024 |

### Ce que ces expériences prouvent

1. **L'outlining froid est le contraire du layout déployé.** Chez le déployé, le bras
   `sell.rs:467` est *dans* la fenêtre de 9 024 o (bloc à `0x4e718`, tuple à `0x4e768`).
   `#[cold] #[inline(never)]` le sort dans une fonction séparée : le tuple reste bien
   à la ligne 467 (preuve : `0x11bd30` dans `cashback::cold_467`), mais `cashback`
   tombe à 8 864 o et le helper (520 o) est placé en fin de binaire. **Aucun attribut
   d'outlining ne peut donc produire un bloc froid intra-fonction** ; la taille cible
   de 9 024 o l'exclut structurellement.
2. **`#[inline(always)]` et le helper de check sont des no-ops** : binaire
   strictement identique à la référence (`86dbc2c6…`). Ils ne changent ni l'ordre
   create/join ni le placement du bloc 467.
3. **`#[cold]` sur la fonction elle-même est une régression** : le linker déplace
   `cashback` (`0x119928`), la fenêtre appelante `0x49b50` (9 184 o) est perdue
   (matched 783). Rejeté sans ambiguïté.
4. **L'encodage `0x4d450` n'est pas une cible indépendante** : `c1`/`c2` (conversion
   explicite du `?`) changent bien le code (9 000 o, 1 072 insns) mais émettent
   toujours `jne r2, r1, +0xcb` — jamais le `jeqr r2, r3, +1; ja` du déployé. Cet
   encodage est une conséquence de l'ordre de blocs (create→join, queue froide),
   pas une forme de contrôle de flux à réécrire.
5. **Zéro régression nette** : toutes les variantes non identiques laissent
   `matched = 784` sauf a4 (783, rejeté) ; aucune n'est proposée pour intégration.

**Conclusion de la mission attributs : résultat négatif documenté.** Le levier
attributs ne peut pas produire un bloc froid *à l'intérieur* d'une fonction ; il ne
reste donc que la reproduction de l'ordre IR create→join (bloc de jointure émis
après le bloc `then`), qui n'a été obtenue par aucune forme source ni attribut testé.

---

## 4. Commandes exactes

Staging :

```sh
python3 research/amm-layout-closure-20261028/workspace_recipe.py stage \
  --source-root <checkout> --output <ws>
```

Build natif (recette scellée, `/out` → `$AMM_OUT`) :

```sh
P=$HOME/.cache/solana/v1.44/platform-tools
export RUSTC=$P/rust/bin/rustc CC=$P/llvm/bin/clang AR=$P/llvm/bin/llvm-ar
export CARGO_HOME=$HOME/pumpwork/netcargo CARGO_TARGET_DIR=<target>
export RUSTC_WRAPPER=<out>/rustc_wrapper.py AMM_OUT=<out>
export CARGO_TARGET_SBPF_SOLANA_SOLANA_RUSTFLAGS=" -Zremap-cwd-prefix="
export CARGO_NET_OFFLINE=true
cd <ws> && $P/rust/bin/cargo build --release --target sbpf-solana-solana \
  --locked --offline --verbose
$HOME/.cache/solana/v1.52/platform-tools/llvm/bin/llvm-objcopy --strip-all \
  <target>/sbpf-solana-solana/release/pump_amm_recovered.so <out>/candidate.so
```

Mesure : `python3 packet-maintained/transform/verify_baseline_cand.py <symbols.so> out.json`.
Analyse : `window_gap.py`, `block_seq.py`, `multiset_diff.py`, `reloc_ledger.py`,
`reloc_pair.py` (dans `transform/`).

Toolchain : rustc `1.79.0-dev` (v1.44, sha `c8807b7e…`), cargo `1.79.0`
(`d2844457…`), clang `18.1.7-rust-dev` (`b6541efe…`), `llvm-objcopy` v1.52
(`673b3b86…`), `rust-lld` (`f28db364…` — identique au SDK enregistré), anchor-lang
`0.31.1`, flags `-C opt-level=3 -C panic=abort -C embed-bitcode=no -C codegen-units=1
-C overflow-checks=on -C metadata=bb5f628ba4a31e11 -C strip=debuginfo`.

---

## 5. Limites explicites

1. Le build scellé passe par podman (absent) ; la reproduction est une **adaptation
   hôte** de la même recette (`/out` → `$AMM_OUT`), avec les mêmes objets, flags,
   SDK, `ordered.ld` et `rust-lld`. Les hashes identiques (deux fois, dont un target
   froid) sont la preuve que l'adaptation ne change rien.
2. `0x4c750` **n'est pas gagnée**. La cause est prouvée au niveau IR/bloc
   (ordre create/join + queue froide du bloc 467), mais la forme source exacte qui
   produit cet ordre n'a pas été trouvée ; 8 formes candidates canonicalisent.
3. La méthode « reorder IR puis llc » n'a pas pu être menée : `llc` du SDK émet un
   `.text` monolithique (+ `.text.unlikely`) alors que le backend rustc émet des
   sections par fonction utilisées par `ordered.ld` ; un round-trip fidèle exigerait
   le backend de rustc, pas llc nu. Piste restante documentée.
4. Aucun test runtime (pas de CLI Solana/localnet) : aucune equivalence
   comportementale n'est revendiquée au-delà de l'identité quasi-totale du binaire.
5. Les 21 offsets de relocation sont mesurés et classés ; aucun n'est « corrigé »
   par patch binaire.

---

## 6. Fichiers

```
packet-maintained/
  RESULT.md
  measurements/base.json          mesure 784/784 (sets matched/raw)
  measurements/variants.json      hashes + mesures des 10 variantes de forme
  measurements/attr-variants.json hashes + tailles/insns des 7 variantes attributs
  analysis/attr-a1-outlined.txt   fonction cashback::cold_467 (a1)
  analysis/attr-a1-tuples.txt     tuple 467 préservé dans le helper (0x11bd30)
  analysis/attr-a4-functions.txt  cashback déplacé à 0x119928 (a4)
  analysis/attr-c1-tryborrow.txt  c1 : toujours `jne`, pas `jeqr+ja`
  analysis/window-gap.txt         gap normalisé + reloc rows seulement-déployé/candidat
  analysis/block-sequence-diff.txt  déplacement du bloc 467 (preuve)
  analysis/block-inventory.txt    inventaire des blocs
  analysis/instruction-multiset.txt  l'unique encoding jeqr/ja vs jner
  analysis/reloc-deployed.json    47 lignes déployées
  analysis/reloc-candidate.json   47 lignes candidat
  analysis/reloc-pairing.txt      appariement + 21 offsets décalés
  analysis/error-tuples-candidate.txt  tuples sell.rs du candidat (liste binaire)
  analysis/line-502-stw-deployed.txt   sites `stw 502` déployé
  analysis/line-502-stw-candidate.txt  sites `stw 502` candidat
  analysis/ir-blocks.txt          ordre des blocs IR (bb54/bb59/bb65/bb68)
  analysis/rustc-link-invocations.txt  flags et inputs réels
  analysis/toolchain-and-recipe.json
  analysis/verification.txt      vérification finale indépendante (baseline, hashes,
                                 mesure, multiset, relocations, 8 variants)
  variants/*.patch                diffs des 10 variantes (toutes non-gagnantes)
  transform/*.py|*.sh             staging/build/mesure/analyse (avec asserts)
  SHA256SUMS
```
