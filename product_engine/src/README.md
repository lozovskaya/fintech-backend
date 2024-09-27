## To run Docker:

```bash
docker build -t product-engine .
docker run -d --network="fintech-network" --name product-engine -p 80:80 product-engine
```

to re-run it, do not forget to do this before running a container
```bash
docker stop product-engine
docker rm product-engine 
```

## To test the fuctionality:

### Product API endpoints:

**Get requests: **

```bash
curl http://localhost:80/product/
curl http://localhost:80/product/CL_1.0    
```

**Post requests: **

```bash
curl -X POST "http://localhost:80/product/" \
     -H "Content-Type: application/json" \
     -d '{  "client_friendly_name": "Cash Loan",
            "internal_code": "CL_2.0",
            "min_loan_term": 12,
            "max_loan_term": 60,
            "min_principal_amount": 1000.00,
            "max_principal_amount": 50000.00,
            "min_interest_rate": 5.0,
            "max_interest_rate": 15.0,
            "min_origination_amount": 50.00,
            "max_origination_amount": 500.00
          }' 
```

**Delete requests: **

```bash
curl -X DELETE http://localhost:80/product/CL_2.0
```

### Agreement API endpoints:

**Post requests:**

```bash
curl -X POST "http://localhost:80/agreement" \
     -H "Content-Type: application/json" \
     -d '{   
        "product_code": "CL_1.0",
        "client" : {
                "first_name": "Ivan",
                "second_name": "Ivanov",
                "third_name": "Ivanovich",
                "birthday": "01.01.1990",
                "passport_number": "1234567890",
                "email": "ivan@gmail.com",
                "phone": "00000",
                "salary": 1000.0
           },
        "term": 6,
        "interest": 10.0,
        "disbursment_amount": 20000.0
        }'
```

## Troubleshooter:

"Is the server running on that host and accepting TCP/IP connections?
2024-05-24 13:05:00 connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused
2024-05-24 13:05:00     Is the server running on that host and accepting TCP/IP connections?"

If the postgres server is running for whatever reason even without you running to, do this:

```bash
psql
SHOW data_directory;
\q

pg_ctl stop -D {insert_path}
```