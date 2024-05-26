1.
```bash
docker compose up -d
```

2. Запустим миграции (из корня):
    **Product engine:**
    ```bash
    docker run --rm --network="fintech-network" -v ./product_engine/migrations:/app liquibase/liquibase:4.19.0 --log-level ERROR --defaultsFile=/app/dev.properties update
    ```

    ```bash
    docker run --rm --network="fintech-network" -v ./product_engine/migrations:/app liquibase/liquibase:4.19.0 --defaultsFile=/app/dev.properties update
    ```
    **Origination:**
    ```bash
    docker run --rm --network="fintech-network" -v ./origination/migrations:/app liquibase/liquibase:4.19.0 --log-level ERROR --defaultsFile=/app/dev.properties update
    ```

    ```bash
    docker run --rm --network="fintech-network" -v ./origination/migrations:/app liquibase/liquibase:4.19.0 --defaultsFile=/app/dev.properties update
    ```