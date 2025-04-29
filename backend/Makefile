DB_URL=mysql://root:88889999@tcp(localhost:3306)/mydb?charset=utf8mb4&parseTime=True&loc=Local
DB_NAME=mydb

server:
	go run cmd/main.go

mysql:
	docker run --name grab-bootcamp-db -e MYSQL_ROOT_PASSWORD=88889999 -e MYSQL_DATABASE=${DB_NAME} -p 3306:3306 -d mysql:9-oraclelinux9

createdb:
	docker exec -i grab-bootcamp-db mysql -uroot -p88889999 -e "CREATE DATABASE ${DB_NAME};"

dropdb:
	docker exec -i grab-bootcamp-db mysql -uroot -p88889999 -e "DROP DATABASE ${DB_NAME};"

swag:
	swag init -g cmd/main.go

mockdata:
	docker exec -i grab-bootcamp-db mysql -uroot -p88889999 ${DB_NAME} < mockdata/mock_data.sql

.PHONY: server mysql createdb dropdb swag mockdata