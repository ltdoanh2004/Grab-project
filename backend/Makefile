DB_URL=mysql://root:88889999@tcp(localhost:3306)/mydb
DB_NAME=mydb

server:
	go run cmd/main.go

mysql:
	docker run --name grab-bootcamp-db -e MYSQL_ROOT_PASSWORD=88889999 -e MYSQL_DATABASE=${DB_NAME} -p 3306:3306 -d mysql:9-oraclelinux9

createdb:
	docker exec -i grab-bootcamp-db mysql -uroot -p88889999 -e "CREATE DATABASE ${DB_NAME};"

dropdb:
	docker exec -i grab-bootcamp-db mysql -uroot -p88889999 -e "DROP DATABASE ${DB_NAME};"

.PHONY: server mysql createdb dropdb migrateup migratedown