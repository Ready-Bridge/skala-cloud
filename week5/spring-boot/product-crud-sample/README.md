# H2 → PostgreSQL DB 마이그레이션 트러블슈팅

## 📋 개요
- **작업일**: 2026-01-27
- **목적**: Spring Boot 애플리케이션의 DB를 H2 인메모리에서 PostgreSQL로 변경
- **환경**: WSL2 (Spring Boot) ↔ Windows (PostgreSQL Server)

---

## 🎯 최종 구성

### 환경 구조
```
┌─────────────────┐         ┌──────────────────┐
│   WSL2 Ubuntu   │         │   Windows 11     │
│                 │         │                  │
│  Spring Boot    │  ────→  │  PostgreSQL      │
│  (localhost)    │         │  (5432)          │
│  Port: 8080     │         │                  │
└─────────────────┘         └──────────────────┘
        ↑
        │
   host.docker.internal
```

---

## 📝 변경 파일 목록

### 1. application-postgres.yml (신규 생성)
**위치**: `src/main/resources/application-postgres.yml`

```yaml
spring:
  datasource:
    url: jdbc:postgresql://${DB_HOST:localhost}:${DB_PORT:5432}/${DB_NAME:productdb}
    username: ${DB_USERNAME:postgres}
    password: ${DB_PASSWORD:}
    driver-class-name: org.postgresql.Driver
  sql:
    init:
      mode: always
```

**주요 변경사항**:
- H2 JDBC URL에서 PostgreSQL JDBC URL로 변경
- 환경변수를 통한 동적 설정 지원
- `mode: always`로 설정하여 schema.sql/data.sql 자동 실행

---

### 2. postgres.sh (신규 생성)
**위치**: `product-crud-sample/postgres.sh`

```bash
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
```

**주요 기능**:
- .env 파일 자동 로드
- WSL 환경에 맞춘 기본 호스트 설정 (`host.docker.internal`)
- 환경변수 기반 설정 오버라이드
- JAR/Gradle 실행 모드 자동 선택

---

### 3. .env (신규 생성)
**위치**: `product-crud-sample/.env`

```env
# PostgreSQL 데이터베이스 환경변수 설정
# WSL → Windows PostgreSQL 접속 (host.docker.internal 사용)
DB_HOST=host.docker.internal
DB_PORT=5432
DB_NAME=productdb
DB_USERNAME=postgres
DB_PASSWORD=~
```

**보안 주의사항**:
- `.gitignore`에 추가 필수
- 프로덕션 환경에서는 시크릿 관리 도구 사용 권장

---

### 4. schema.sql 수정
**위치**: `src/main/resources/schema.sql`

**변경사항**: H2 문법 → PostgreSQL 문법

| 항목 | 변경 전 (H2) | 변경 후 (PostgreSQL) |
|------|-------------|---------------------|
| Auto Increment | `BIGINT AUTO_INCREMENT` | `BIGSERIAL` |

**수정 예시**:
```sql
-- 변경 전
CREATE TABLE products(
 id BIGINT AUTO_INCREMENT PRIMARY KEY,
 ...
);

-- 변경 후
CREATE TABLE products(
 id BIGSERIAL PRIMARY KEY,
 ...
);
```

---

## 🔧 트러블슈팅 과정

### Issue 1: MyBatis 설정 누락
**증상**:
```
UnsatisfiedDependencyException: Cannot resolve reference to bean 'sqlSessionTemplate'
```

**원인**: application-postgres.yml에 MyBatis 설정 누락

**해결**: 
- 초기에는 MyBatis 설정을 중복으로 추가하려 했으나, Spring Boot Profile 메커니즘 이해 후 제거
- `application.yml`의 MyBatis 설정이 자동 상속됨을 확인
- 최종적으로 datasource만 오버라이드하는 방식으로 정리

---

### Issue 2: WSL ↔ Windows 네트워크 연결 실패
**증상**:
```
Connection refused: localhost:5432
PSQLException: pg_hba.conf에 일치 항목 없음 (10.250.175.177)
```

**원인**:
1. WSL의 `localhost`는 WSL 자체를 가리켜 Windows PostgreSQL에 접근 불가
2. Windows PostgreSQL의 `pg_hba.conf`에서 WSL IP 대역 미허용

**해결**:
1. DB_HOST를 `host.docker.internal`로 변경 (WSL → Windows 호스트 접근)
2. Windows PostgreSQL 설정 변경:
   ```
   # C:\Program Files\PostgreSQL\15\data\pg_hba.conf
   host    all    all    10.0.0.0/8    scram-sha-256
   ```
3. PostgreSQL 서비스 재시작:
   ```powershell
   net stop postgresql-x64-15
   net start postgresql-x64-15
   ```

---

### Issue 3: schema.sql 문법 오류
**증상**:
```
PSQLException: 오류: 구문 오류, "AUTO_INCREMENT" 부근
Position: 34
```

**원인**: H2와 PostgreSQL의 Auto Increment 문법 차이

**해결**: 
```sql
-- H2 문법
BIGINT AUTO_INCREMENT

-- PostgreSQL 문법
BIGSERIAL
```

3개 테이블(products, members, purchases) 모두 수정

---

### Issue 4: 환경변수 로드 우선순위 이슈
**증상**: .env 파일의 `DB_HOST` 값이 무시되고 postgres.sh의 기본값 `localhost` 사용

**원인**: Bash 파라미터 확장 `${VAR:=default}`가 빈 문자열도 기본값으로 대체

**해결**: postgres.sh의 기본값을 `host.docker.internal`로 변경
```bash
DB_HOST=${DB_HOST:=host.docker.internal}
```

---

## ✅ 검증 단계

### 1. 빌드 확인
```bash
./gradlew clean bootJar -x test
```

### 2. 애플리케이션 실행
```bash
./postgres.sh
```

### 3. API 테스트
```bash
curl http://localhost:8080/api/members
curl http://localhost:8080/actuator/health
```

### 4. 로그 확인 포인트
- ✅ `HikariPool-1 - Start completed`: DB 연결 성공
- ✅ `Started ProductApplication in X seconds`: 애플리케이션 시작 완료
- ✅ `Tomcat started on port 8080`: 웹 서버 정상 구동

---

## 📚 추가 설정 (Windows)

### PostgreSQL 데이터베이스 생성
```sql
-- pgAdmin 또는 psql에서 실행
CREATE DATABASE productdb OWNER postgres;
```

### pg_hba.conf 전체 설정 예시
```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
# IPv4 local connections:
host    all             all             127.0.0.1/32            scram-sha-256
# IPv6 local connections:
host    all             all             ::1/128                 scram-sha-256
# WSL2 connections (추가):
host    all             all             10.0.0.0/8              scram-sha-256
```

---

## 🎓 학습 포인트

### 1. Spring Boot Profile 메커니즘
- `application.yml`: 공통 설정
- `application-{profile}.yml`: 프로파일별 설정
- 같은 key는 프로파일 설정이 오버라이드
- 다른 key는 자동 상속

### 2. WSL2 네트워크 아키텍처
- WSL2는 별도 가상 네트워크에서 동작
- `localhost`는 WSL 자체를 가리킴
- Windows 호스트 접근: `host.docker.internal` 또는 `/etc/resolv.conf`의 nameserver IP

### 3. PostgreSQL vs H2 주요 차이
| 항목 | H2 | PostgreSQL |
|------|-----|-----------|
| Auto Increment | `AUTO_INCREMENT` | `SERIAL` / `BIGSERIAL` |
| 타입 호환성 | 느슨함 | 엄격함 |
| 기본 포트 | 임베디드 | 5432 |

### 4. 환경변수 관리 모범 사례
- `.env` 파일로 로컬 개발 설정 관리
- `.gitignore`에 반드시 추가
- 프로덕션: AWS Secrets Manager, HashiCorp Vault 등 사용

---

## 🚀 실행 방법

### 일반 실행
```bash
cd product-crud-sample
./postgres.sh
```

### 환경변수 오버라이드
```bash
DB_HOST=192.168.1.100 DB_PASSWORD=custom_pwd ./postgres.sh
```

### 백그라운드 실행
```bash
nohup ./postgres.sh > app.log 2>&1 &
```

---

## 📌 체크리스트

- [x] application-postgres.yml 생성
- [x] postgres.sh 생성 및 실행 권한 부여
- [x] .env 파일 생성 및 비밀번호 설정
- [x] schema.sql PostgreSQL 문법 수정
- [x] Windows PostgreSQL 설치 확인
- [x] productdb 데이터베이스 생성
- [x] pg_hba.conf WSL IP 허용 설정
- [x] PostgreSQL 서비스 재시작
- [x] .gitignore에 .env 추가
- [x] API 응답 정상 확인

---

## 🔗 참고 자료

- [Spring Boot Profile Documentation](https://docs.spring.io/spring-boot/reference/features/profiles.html)
- [PostgreSQL pg_hba.conf Guide](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)
- [WSL2 Networking](https://learn.microsoft.com/en-us/windows/wsl/networking)
- [MyBatis Spring Boot Starter](https://mybatis.org/spring-boot-starter/mybatis-spring-boot-autoconfigure/)
