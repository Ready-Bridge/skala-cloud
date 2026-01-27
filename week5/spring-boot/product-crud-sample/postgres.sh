#!/bin/bash

# PostgreSQL 환경 실행 스크립트
# 포트: 8080

# .env 파일에서 환경변수 로드
if [ -f ".env" ]; then
    export $(cat .env | grep -v '#' | xargs)
    echo ".env 파일에서 설정을 로드했습니다."
fi

PROFILE="postgres"
PORT=8080

# PostgreSQL 데이터베이스 설정 (기본값 적용)
DB_HOST=${DB_HOST:=host.docker.internal}
DB_PORT=${DB_PORT:=5432}
DB_NAME=${DB_NAME:=productdb}
DB_USERNAME=${DB_USERNAME:=postgres}
DB_PASSWORD=${DB_PASSWORD:=}

echo "=========================================="
echo "  Product CRUD Application - PostgreSQL"
echo "=========================================="
echo "프로파일: $PROFILE"
echo "포트: $PORT"
echo "=========================================="
echo "데이터베이스 설정:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  Username: $DB_USERNAME"
echo "=========================================="
echo ""

# JAR 파일이 있으면 JAR로 실행, 없으면 Gradle로 실행
if [ -f "build/libs/product-crud-0.0.1-SNAPSHOT.jar" ]; then
    echo "JAR 파일로 실행합니다..."
    java \
      -Dspring.profiles.active=$PROFILE \
      -Dserver.port=$PORT \
      -Dspring.datasource.url=jdbc:postgresql://$DB_HOST:$DB_PORT/$DB_NAME \
      -Dspring.datasource.username=$DB_USERNAME \
      -Dspring.datasource.password=$DB_PASSWORD \
      -Dspring.datasource.driver-class-name=org.postgresql.Driver \
      -jar build/libs/product-crud-0.0.1-SNAPSHOT.jar
else
    echo "Gradle로 실행합니다..."
    ./gradlew bootRun \
      --args="--spring.profiles.active=$PROFILE --server.port=$PORT \
        --spring.datasource.url=jdbc:postgresql://$DB_HOST:$DB_PORT/$DB_NAME \
        --spring.datasource.username=$DB_USERNAME \
        --spring.datasource.password=$DB_PASSWORD \
        --spring.datasource.driver-class-name=org.postgresql.Driver"
fi
