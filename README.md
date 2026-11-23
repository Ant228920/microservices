# Helm-чарт `microservices`

Helm-чарт застосунку з лабораторної роботи №3: три FastAPI-сервіси (`gateway`, `user`, `payment`), PostgreSQL та RabbitMQ. Чарт створює той самий набір об'єктів Kubernetes, що й маніфести з каталогу `k8s/`, окрім `Namespace` (його задають під час встановлення через `-n ... --create-namespace`).

## Структура

```
chart/microservices/
├── Chart.yaml
├── values.yaml            # значення за замовчуванням (середовище розробки)
├── values-dev.yaml        # dev
├── values-prod.yaml       # prod
└── templates/
    ├── _helpers.tpl       # fullname, labels, selectorLabels
    ├── NOTES.txt
    ├── configmap.yaml
    ├── secret.yaml
    ├── database.yaml      # PVC (за прапорцем) + Deployment + Service PostgreSQL
    ├── rabbitmq.yaml
    ├── user.yaml
    ├── payment.yaml
    ├── gateway.yaml
    ├── ingress.yaml       # лише якщо ingress.enabled=true
    ├── hooks/pre-upgrade-job.yaml
    └── tests/test-connection.yaml
```

## `version` і `appVersion`

- `version` (`0.1.0`) це версія самого чарта, тобто пакування: шаблонів, значень, структури. Вона змінюється, коли змінюється чарт, навіть якщо код застосунку лишився тим самим. Дотримуємося SemVer.
- `appVersion` (`865266f`) це версія застосунку, який розгортає чарт. У цьому проєкті це короткий хеш коміту, з якого CI збирає образи (`sha-865266f`). Вона змінюється, коли виходить новий образ.

Приклад: CI зібрав нові образи, тоді змінюється `appVersion`. Додали прапорець `persistence.enabled` у чарт, тоді збільшується `version`.

## Встановлення

### dev (значення за замовчуванням збігаються з `values-dev.yaml`)

```bash
helm install dev chart/microservices -f chart/microservices/values-dev.yaml -n dev --create-namespace
```

### prod

Паролі у файлах значень не зберігаються. Для prod вони обов'язково передаються через `--set` (інакше шаблон завершиться помилкою через `required`):

```bash
helm install prod chart/microservices -f chart/microservices/values-prod.yaml \
  -n prod --create-namespace \
  --set secret.postgresPassword='<пароль>' \
  --set secret.secretKey='<ключ>'
```

Відкрити застосунок (dev):

```bash
kubectl port-forward svc/dev-microservices-gateway 8080:8000 -n dev
# http://localhost:8080/docs
```

## Параметри

| Параметр | За замовчуванням | Опис |
|---|---|---|
| `config.rabbitmqQueue` | `main_queue` | Назва черги RabbitMQ (ConfigMap) |
| `secret.postgresPassword` | `postgres` | Пароль PostgreSQL. **Лише dev-заглушка**, у prod передається через `--set` |
| `secret.secretKey` | `dev-only-secret-key` | Ключ підпису JWT. **Лише dev-заглушка**, у prod через `--set` |
| `ingress.enabled` | `false` | Створювати Ingress |
| `ingress.className` | `""` | `ingressClassName` (порожнє: клас за замовчуванням) |
| `ingress.host` | `""` | Хост у правилі Ingress (порожнє: будь-який) |
| `postgres.image.repository` | `postgres` | Образ PostgreSQL |
| `postgres.image.tag` | `15-alpine` | Тег образу PostgreSQL |
| `postgres.database` | `lab_db` | Назва бази даних |
| `postgres.user` | `postgres` | Користувач бази даних |
| `postgres.service.port` | `5432` | Порт сервісу PostgreSQL |
| `postgres.persistence.enabled` | `true` | Створювати PersistentVolumeClaim (інакше `emptyDir`) |
| `postgres.persistence.size` | `1Gi` | Розмір PVC |
| `rabbitmq.image.repository` | `rabbitmq` | Образ RabbitMQ |
| `rabbitmq.image.tag` | `3-management-alpine` | Тег образу RabbitMQ |
| `rabbitmq.service.amqpPort` | `5672` | Порт AMQP |
| `rabbitmq.service.managementPort` | `15672` | Порт панелі керування |
| `<svc>.replicaCount` | `1` | Кількість реплік |
| `<svc>.image.repository` | `ghcr.io/ant228920/microservices-<svc>_service` | Репозиторій образу |
| `<svc>.image.tag` | `sha-865266f` | Тег образу |
| `<svc>.image.pullPolicy` | `IfNotPresent` | Політика завантаження образу |
| `<svc>.service.type` | `ClusterIP` | Тип сервісу |
| `<svc>.service.port` | `8000` | Порт сервісу |
| `<svc>.resources` | requests `100m`/`64Mi`, limits `250m`/`128Mi` | Ресурси контейнера |

`<svc>` це `gateway`, `user` або `payment`.

### Різниця між середовищами

| | dev | prod |
|---|---|---|
| Репліки (gateway / user / payment) | 1 / 1 / 1 | 3 / 2 / 2 |
| Ресурси (requests / limits) | 100m, 64Mi / 250m, 128Mi | 200m, 128Mi / 500m, 256Mi |
| Тег образу | `sha-865266f` | `latest` (`pullPolicy: Always`) |
| Ingress | вимкнено | увімкнено |
| Розмір PVC | 1Gi | 5Gi |
| Паролі | dev-заглушки | порожні, через `--set` |

## Пріоритет значень

Від найнижчого до найвищого:

1. `values.yaml` чарта;
2. файли `-f` (кілька файлів накладаються зліва направо, останній виграє);
3. прапорці `--set` (найвищий пріоритет; з кількох `--set` виграє останній).

Значення зливаються по ключах: якщо файл `-f` задає лише `user.replicaCount`, решта параметрів лишається зі значень нижчого рівня.

Показати різницю без встановлення в кластер:

```bash
helm template demo chart/microservices -f chart/microservices/values-dev.yaml  > dev.yaml
helm template demo chart/microservices -f chart/microservices/values-prod.yaml \
  --set secret.postgresPassword=x --set secret.secretKey=y > prod.yaml
git diff --no-index dev.yaml prod.yaml
```

## Життєвий цикл релізу

```bash
helm lint chart/microservices
helm install lab4 chart/microservices -f chart/microservices/values-dev.yaml -n olianiuk-helm --create-namespace
helm list -n olianiuk-helm
helm status lab4 -n olianiuk-helm
helm get values lab4 -n olianiuk-helm
helm upgrade lab4 chart/microservices -f chart/microservices/values-dev.yaml -n olianiuk-helm --set gateway.image.tag=latest
helm history lab4 -n olianiuk-helm
helm rollback lab4 1 -n olianiuk-helm
helm uninstall lab4 -n olianiuk-helm
```

Helm 3 зберігає кожну ревізію релізу як Secret типу `helm.sh/release.v1` у namespace релізу (`sh.helm.release.v1.<реліз>.v<N>`).

## Хук і тест (завдання 9b)

- `templates/hooks/pre-upgrade-job.yaml`: Job з анотацією `helm.sh/hook: pre-upgrade`. Перед кожним `helm upgrade` перевіряє, що PostgreSQL доступний (`nc -z`). Якщо ні, оновлення переривається.
- `templates/tests/test-connection.yaml`: Pod з анотацією `helm.sh/hook: test`. Команда `helm test <реліз> -n <namespace>` перевіряє, що gateway відповідає на `/docs`.

```bash
helm test lab4 -n olianiuk-helm
kubectl get jobs -n olianiuk-helm
kubectl logs job/lab4-microservices-pre-upgrade -n olianiuk-helm
```

## Примітки

- Namespace чарт не створює: його задають через `-n <ns> --create-namespace`.
- Імена об'єктів будуються як `<реліз>-microservices-<компонент>`, тому чарт можна встановити кілька разів в один кластер.
- Під час `helm upgrade` не змінюйте `postgres.persistence.size` на більший для класу сховища, який не підтримує розширення (наприклад, `standard` у minikube): оновлення завершиться помилкою.
- Пароль PostgreSQL ініціалізується під час першого запуску бази. Змінна `POSTGRES_PASSWORD` після цього не змінює пароль у наявних даних, тому під час оновлення релізу з наявним PVC передавайте той самий пароль.
