# Kubernetes — CrashLoopBackOff

## Symptômes

Un pod en état `CrashLoopBackOff` démarre, échoue, puis Kubernetes augmente progressivement le délai avant le prochain redémarrage. Cet état décrit une boucle de redémarrage, pas sa cause racine.

## Vérifications en lecture seule

1. Identifier le conteneur en échec et son nombre de redémarrages.
2. Lire les événements récents du pod.
3. Comparer les logs courants avec ceux de l’instance précédente.
4. Vérifier les probes, les variables d’environnement et les ressources demandées.

```bash
kubectl get pod -n <namespace> <pod> -o wide
kubectl describe pod -n <namespace> <pod>
kubectl logs -n <namespace> <pod> --all-containers
kubectl logs -n <namespace> <pod> --previous
```

## Causes fréquentes

- Le processus principal se termine immédiatement.
- Une liveness probe est trop stricte ou vise le mauvais chemin.
- Une variable, un secret ou un fichier de configuration manque.
- Le conteneur est tué pour dépassement mémoire (`OOMKilled`).
- Une dépendance n’est pas joignable au démarrage.

## Escalade

Ne redémarrez pas aveuglément le déploiement. Conservez les événements et logs précédents, puis impliquez l’équipe propriétaire si la modification de configuration ou un rollback est nécessaire.
