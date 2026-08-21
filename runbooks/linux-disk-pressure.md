# Linux — Pression disque

## Symptômes

Un filesystem proche de 100 % peut provoquer des erreurs d’écriture, des bases indisponibles et des services incapables de créer leurs fichiers temporaires. Les inodes peuvent aussi être épuisés alors que de l’espace reste disponible.

## Vérifications en lecture seule

1. Mesurer l’espace et les inodes par filesystem.
2. Identifier les répertoires volumineux sans traverser d’autres montages.
3. Vérifier les fichiers supprimés qui restent ouverts par un processus.
4. Contrôler la rotation des journaux et la croissance des données applicatives.

```bash
df -h
df -i
du -xhd 1 /var 2>/dev/null | sort -h
lsof +L1
```

## Causes fréquentes

- Journaux non soumis à rotation.
- Fichier supprimé mais encore ouvert.
- Cache ou fichiers temporaires en croissance.
- Rétention de sauvegardes incorrecte.
- Épuisement des inodes par de nombreux petits fichiers.

## Escalade

Ne supprimez aucun fichier sur la seule base de sa taille. Identifiez son propriétaire, sa politique de rétention et une méthode de nettoyage supportée avant toute action.
