# Kafka — Consumer lag élevé

## Symptômes

Le consumer lag mesure l’écart entre le dernier offset écrit dans une partition et l’offset traité par un groupe de consommateurs. Une hausse durable indique que le groupe ne suit plus le rythme de production.

## Vérifications en lecture seule

1. Confirmer que le retard concerne toutes les partitions ou seulement certaines.
2. Vérifier la stabilité du groupe et les rééquilibrages récents.
3. Comparer le débit entrant avec le débit de traitement.
4. Examiner les erreurs applicatives, timeouts et dépendances lentes.

```bash
kafka-consumer-groups.sh --bootstrap-server <broker> --describe --group <group>
kafka-consumer-groups.sh --bootstrap-server <broker> --state --group <group>
```

## Causes fréquentes

- Traitement unitaire devenu plus lent.
- Nombre de consommateurs inférieur au nombre de partitions actives.
- Rééquilibrages répétés du groupe.
- Partition chaude recevant une part disproportionnée du trafic.
- Dépendance externe lente ou indisponible.

## Escalade

Ne réinitialisez jamais les offsets sans validation explicite du propriétaire des données. Documentez les partitions touchées, la tendance du lag et l’heure de début avant l’escalade.
