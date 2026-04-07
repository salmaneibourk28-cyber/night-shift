# Night Shift – Emergency Decision System

Serious game médical en **2D** : vous dirigez les urgences pendant une garde de nuit. Analysez les symptômes, prescrivez des examens, posez un diagnostic, puis traitez ou déléguez. Chaque décision impacte **budget**, **réputation** et **survie des patients**.

## Prérequis

- **Python 3.9+**
- [Pygame](https://www.pygame.org/) 2.x

## Installation

```bash
pip install pygame
```

## Lancer le jeu

```bash
python night_shift.py
```

- Résolution : **1280 × 720**
- Dépendance : uniquement `pygame` (aucun asset externe : sons et interface générés en code)

## Contrôles (rappel)

| Action | Input |
|--------|--------|
| Pause | Bouton *Pause* ou **Échap** |
| Panneau droit | **Molette** pour faire défiler le contenu (diagnostics, journal, etc.) |
| Quitter (menu) | *Quitter le jeu* puis confirmation |

## Dépannage audio (Windows)

Si la fenêtre se ferme au premier clic, mettez à jour Pygame ou lancez sans audio :

```bash
set NIGHT_SHIFT_NO_AUDIO=1
python night_shift.py
```

(PowerShell : `$env:NIGHT_SHIFT_NO_AUDIO=1` puis `python night_shift.py`.)

## Structure du projet

- `night_shift.py` — jeu complet (logique, UI, audio procédural, données médicales)
- `.gitignore` — ignore caches Python et fichiers de log locaux

## Licence

Indiquez ici la licence de votre choix (MIT, GPL, etc.) si vous publiez le dépôt.
