# Stock Trading Application

Spring Boot 3.2.0 기반 주식 거래 플랫폼 애플리케이션입니다.

## 📋 목차
- [빠른 시작](#빠른-시작)
- [프로젝트 구조](#프로젝트-구조)
- [주요 기능](#주요-기능)
- [Docker 배포 가이드](#docker-배포-가이드)
- [API 문서](#api-문서)

---

## 🚀 빠른 시작

### 로컬 실행

```bash
# 프로젝트 폴더 진입
cd StockTrading2

# 애플리케이션 실행
./gradlew bootRun

# 또는 JAR 파일로 실행
./gradlew clean build
java -jar build/libs/StockTrading2-0.0.1-SNAPSHOT.jar
```

**접속 URL:**
- Swagger UI: http://localhost:8080/swagger-ui.html
- H2 Console: http://localhost:8080/h2-console
- Actuator Health: http://localhost:8080/actuator/health

---

## 📁 프로젝트 구조

```
src/
├── main/
│   ├── java/com/skala/stock/
│   │   ├── controller/          # REST API 컨트롤러
│   │   ├── service/             # 비즈니스 로직
│   │   ├── repository/          # JPA 리포지토리
│   │   ├── entity/              # JPA 엔티티
│   │   ├── dto/                 # 데이터 전송 객체
│   │   └── aop/                 # AOP (실행 시간 로깅)
│   └── resources/
│       ├── application.yml      # 설정 파일
│       └── data.sql             # 초기 데이터
└── test/
    └── java/                    # 단위 테스트
```

---

## ✨ 주요 기능

### 1. User Management (사용자 관리)
- 사용자 등록, 조회, 수정, 삭제
- 잔액 관리

### 2. Stock Management (주식 관리)
- 주식 등록, 조회, 수정, 삭제
- 실시간 가격 업데이트

### 3. Trading (주식 거래)
- 주식 매수/매도
- 거래 내역 조회
- 포트폴리오 관리

### 4. Analysis (분석)
- 포트폴리오 평가 손익 조회
- 거래 내역 상세 분석
- 총 자산 및 수익률 계산
- 일별 거래 통계

### 5. Monitoring (모니터링)
- AOP 기반 실행 시간 로깅
- Spring Boot Actuator (Health, Metrics)

---

## 🐳 Docker 배포 가이드

### 1️⃣ Docker 이미지 빌드

```bash
docker build -t stock-trading-app:v1 .
```

**명령어 설명:**
- `docker build`: Docker 이미지를 빌드
- `-t stock-trading-app:v1`: 이미지 이름 및 버전 태그
- `.`: 현재 디렉토리의 Dockerfile 사용

**Dockerfile 구조:**
```dockerfile
# 1단계: 빌드 스테이지 (gradle:8.5-jdk21)
- 소스 코드 컴파일
- JAR 파일 생성

# 2단계: 런타임 스테이지 (eclipse-temurin:21-jre)
- 빌드된 JAR만 복사
- 최종 이미지 크기 최소화
```

### 2️⃣ 컨테이너 실행

```bash
docker run -d \
  -p 8080:8080 \
  --name stock-service \
  stock-trading-app:v1
```

**옵션 설명:**
- `-d`: 백그라운드 실행 (detached mode)
- `-p 8080:8080`: 포트 매핑 (호스트포트:컨테이너포트)
- `--name stock-service`: 컨테이너 이름 지정

### 3️⃣ 컨테이너 관리

#### 실행 중인 컨테이너 확인
```bash
docker ps
```

**출력 예시:**
```
CONTAINER ID   IMAGE                    PORTS                    NAMES
a1b2c3d4e5f6   stock-trading-app:v1   0.0.0.0:8080->8080/tcp   stock-service
```

#### 실시간 로그 확인
```bash
# 최근 100줄부터 실시간 확인
docker logs -f --tail 100 stock-service

# 타임스탐프와 함께 보기
docker logs -f -t stock-service

# 특정 시간 이후의 로그만 보기
docker logs -f --since 10m stock-service
```

**로그 보기 종료:** `Ctrl + C`

#### 컨테이너 중지 및 재시작
```bash
# 컨테이너 중지
docker stop stock-service

# 컨테이너 재시작
docker restart stock-service

# 컨테이너 강제 삭제 (재시작 전 필수)
docker rm -f stock-service
```

#### 모든 컨테이너 확인
```bash
# 실행 중인 것만
docker ps

# 모두 (중지된 것 포함)
docker ps -a

# 이미지 확인
docker images
```

---

## WSL2에서 Windows Docker 사용 가능한 이유

**WSL2 (Windows Subsystem for Linux 2) 아키텍처:**

```
┌──────────────────────────────────────────────────────┐
│              Hyper-V 하이퍼바이저                     │
│         (Windows와 WSL2를 물리적으로 분리)            │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────┐   ┌──────────────────┐       │
│  │  Windows(Host)   │   │  WSL2(Guest)     │       │
│  │  OS              │   │  Linux Kernel    │       │
│  │                  │   │                  │       │
│  │ ┌──────────────┐ │   │ ┌──────────────┐│       │
│  │ │Docker        │ │   │ │docker        ││       │
│  │ │Desktop       │◄────►│ │CLI           ││       │
│  │ │(Engine)      │ │   │ │              ││       │
│  │ └──────────────┘ │   │ └──────────────┘│       │
│  │ Named Pipe:      │   │ Unix Socket:    │       │
│  │ \\.\pipe\        │◄─►│ /var/run/      │       │
│  │ docker_engine    │   │ docker.sock     │       │
│  │                  │   │                 │       │
│  └──────────────────┘   └──────────────────┘       │
│         ▲                        ▲                   │
│         │ Named Pipe            │ Unix Socket       │
│         │ (Windows IPC)         │ (Linux IPC)       │
│         └────────┬──────────────┘                   │
│                  │                                   │
│         Docker Desktop Proxy                        │
│         (Relay Agent)                               │
│         VMBus/AF_VSOCK (Hyper-V)                    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

#### 📡 통신 메커니즘: 3단계 릴레이

**① WSL2에서 명령어 실행**
```bash
$ docker ps
```
➜ WSL2의 리눅스 커널에서 `docker` 명령어가 실행됨

**② Unix Socket을 통해 로컬 에이전트로 전달**
```
docker ps → /var/run/docker.sock → WSL2 내부 Docker Agent
```
WSL2 내부에 Docker Desktop이 심어둔 **작은 대리인(Agent)**이 요청을 받음

**③ Hyper-V 하이퍼콜로 Windows의 Docker Engine으로 전달**
```
WSL2 Agent ──(VMBus/AF_VSOCK)──> Windows Docker Engine
           (Hyper-V 전용 채널)
```
WSL2 에이전트가 **Windows Named Pipe**를 통해 실제 Docker Engine과 통신

```
\\.\pipe\docker_engine (Windows) ◄─── 실제 도커 데몬이 여기서 실행
```

#### 🎯 사용자 관점에서의 경험

```bash
# WSL2 터미널에서 입력
$ docker ps

# 내부 동작:
1. /var/run/docker.sock 찾음
2. WSL2 내부 Agent가 interceptor 역할
3. Hyper-V 채널 통해 Windows Docker Engine에 요청 전달
4. 결과를 역방향으로 돌려받음
5. WSL2 터미널에 출력

# 사용자는 마치 같은 컴퓨터에서 실행되는 것처럼 느낌 ✨
```

#### ❓ 왜 네트워크(TCP/IP)를 쓰지 않나요?

네트워크를 쓸 수도 있지만(TCP 2375, 2376), Docker Desktop은 **IPC(Inter-Process Communication)**를 선택합니다:

| 방식 | 속도 | 보안 | 설정 |
|------|------|------|------|
| **IPC (Named Pipe + Unix Socket)** | ⚡ 매우 빠름 | 🔒 같은 호스트만 접근 | 자동 |
| TCP (localhost:2375) | 네트워크 오버헤드 | ⚠️ 외부 접근 가능 | 수동 설정 |

**결론:** Docker Desktop은 Windows와 WSL2 사이에 IPC 연결을 자동으로 설정하므로, 사용자가 아무것도 설정할 필요 없이 `docker` 명령어가 그냥 작동합니다! 🎉

---

### H2 Console의 `web-allow-others` 설정이 필요한 이유

#### 🚨 문제 상황

```
H2 Console 접속 시 에러:
"Sorry, remote connections ('webAllowOthers') are disabled on this server."
```

#### 🤔 핵심 원인: 네트워크 연결 방식의 차이

##### 📍 WSL2에서 java -jar 실행할 때 (잘 작동됨)

```
┌─────────────────────────────────────┐
│        Windows 11 / 10              │
│                                     │
│  ┌──────────────┐                  │
│  │   Chrome     │                  │
│  │ localhost:80 │                  │
│  └──────┬───────┘                  │
│         │                          │
│    [방 문만 나눔]  ← Localhost Forwarding
│         │          (마이크로소프트 특수 기능)
│  ┌──────┴─────────────┐           │
│  │  WSL2 (Linux)      │           │
│  │  java -jar app.jar │           │
│  │  H2 (localhost)    │           │
│  │ "같은 집 식구인가?" │           │
│  │ ✅ "네, 문 열어줄게"│           │
│  └────────────────────┘           │
│                                     │
└─────────────────────────────────────┘
```

**왜 잘 작동할까?**
- WSL2는 Windows와 **특수한 관계**입니다
- Microsoft의 Localhost Forwarding 기능이 WSL2의 포트를 Windows의 localhost와 일치시켜줍니다
- H2는 요청이 **같은 컴퓨터 안(Loopback)**에서 온 것처럼 인식합니다
- 보안 검사: ✅ 통과

##### 📍 Docker 컨테이너에서 실행할 때 (에러 발생)

```
┌──────────────────────────────────────────┐
│         Windows 11 / 10                  │
│                                          │
│  ┌──────────────┐                       │
│  │   Chrome     │                       │
│  │ localhost:80 │                       │
│  └──────┬───────┘                       │
│         │                               │
│    [가상 네트워크 스위치를 타고 들어옴]  │
│    (포트 포워딩: -p 8080:8080)          │
│         │                               │
│  ┌──────────────────────────────┐      │
│  │  Docker Container (옆집)    │      │
│  │                              │      │
│  │  독립된 네트워크:            │      │
│  │  - eth0 가상 카드             │      │
│  │  - 고유 IP: 172.17.0.x      │      │
│  │  - localhost = 127.0.0.1     │      │
│  │    (컨테이너 내부만)         │      │
│  │                              │      │
│  │  H2: "172.17.0.1에서        │      │
│  │       요청이 왔네?"           │      │
│  │  ❌ "이건 Remote Connection!" │      │
│  │                              │      │
│  └──────────────────────────────┘      │
│                                          │
└──────────────────────────────────────────┘
```

**왜 에러가 날까?**

1. **Docker의 격리(Isolation) 특성**
   - 컨테이너는 완전히 격리된 가상 환경입니다
   - 자신만의 네트워크 인터페이스(eth0)와 고유 IP를 가집니다
   - localhost(127.0.0.1)는 **컨테이너 내부만을** 의미합니다

2. **포트 포워딩의 본질**
   ```
   $ docker run -p 8080:8080 ...
         ↑
         이 순간, Windows의 요청이 "가상 네트워크 스위치"를 거쳐 컨테이너로 들어갑니다
   ```

3. **H2의 요청 검증 프로세스**
   ```
   요청 도착: Windows Chrome → http://localhost:8080/h2-console
   
   [포트 포워딩 통과]
   
   Docker 컨테이너의 Spring Boot가 요청을 받음
   
   H2: "이 요청의 출처가 누지?"
   → 요청 IP 확인: 127.0.0.1? ❌ 아니다!
   → 실제 출처: 172.17.0.1 (Docker 게이트웨이)
   
   H2의 판정: "어? 내 localhost(127.0.0.1)가 아니라
              다른 IP(172.17.0.1)에서 온 외부 요청이네?"
   
   보안 검사: ❌ REJECT
   에러 메시지: "Remote connection denied!"
   ```


#### 🏘️ 쉽게 비유하면

| 상황 | WSL2 (java -jar) | Docker 컨테이너 |
|------|------------------|-----------------|
| 위치 | 같은 집의 다른 방 | 옆집 (완전히 격리됨) |
| 네트워크 | 같은 WiFi | 독립된 가상 네트워크 |
| 방문자 ID | 집 식구 (127.0.0.1) | 외부인 (172.17.x.x) |
| H2의 판정 | ✅ "내 사람이네" | ❌ "모르는 사람이 초인종을 눌렀네?" |

#### ✅ 해결방법: `web-allow-others: true`

```yaml
spring:
  h2:
    console:
      enabled: true
      path: /h2-console
      settings:
        web-allow-others: true  # ← Docker에서 필수!
```

**이 설정의 의미:**
```
web-allow-others: true

= H2에게 이렇게 말하는 것:

"H2야, 너 지금 Docker라는 '옆집'에 살고 있어.
 그래서 내가 Windows에서 접속하면 너한테 외부인처럼 보일 거야.
 (IP 주소가 172.17.0.x처럼 보일 거야)
 
 그래도 나는 신뢰할 수 있는 사람이니까,
 IP 주소를 따지지 말고 그냥 문 열어줄래?"
```

#### 📊 동작 흐름: Before & After

**🔴 BEFORE (web-allow-others: false 또는 미설정)**

```
┌─────────────────────────────────────┐
│  Windows Chrome                     │
│  GET /h2-console                    │
└────────────┬────────────────────────┘
             │
        [포트 포워딩]
        -p 8080:8080
             │
┌────────────▼────────────────────────┐
│  Docker Container                   │
│  Spring Boot (8080)                 │
│                                     │
│  요청 도착: /h2-console             │
│  출처: 172.17.0.1 (Docker Gateway)  │
│                                     │
│  H2 보안 검증:                      │
│  "이 요청이 remote인가?"            │
│  ├─ 127.0.0.1? ❌ 아니다!          │
│  ├─ localhost? ❌ 아니다!            │
│  └─ 판정: REMOTE CONNECTION ❌     │
│                                     │
│  결과: ❌ "Sorry, remote           │
│        connections are disabled"    │
│        (페이지 접속 차단!)          │
│                                     │
│  사용자 화면: 403 Forbidden         │
└─────────────────────────────────────┘
```

**🟢 AFTER (web-allow-others: true)**

```
┌─────────────────────────────────────┐
│  Windows Chrome                     │
│  GET /h2-console                    │
└────────────┬────────────────────────┘
             │
        [포트 포워딩]
        -p 8080:8080
             │
┌────────────▼────────────────────────┐
│  Docker Container                   │
│  Spring Boot (8080)                 │
│                                     │
│  요청 도착: /h2-console             │
│  출처: 172.17.0.1 (Docker Gateway)  │
│                                     │
│  H2 보안 검증:                      │
│  "이 요청이 remote인가?"            │
│  ├─ 127.0.0.1? ❌ 아니다!          │
│  ├─ 하지만 web-allow-others: ✅   │
│  └─ 판정: ALLOW (IP 무시)          │
│                                     │
│  결과: ✅ H2 Console 페이지 로드!  │
│     http://localhost:8080/h2-console│
│     ┌──────────────────────────────┐│
│     │  H2 Console UI 표시          ││
│     │  - JDBC URL                  ││
│     │  - 쿼리 입력창                ││
│     │  - 테이블 목록                ││
│     └──────────────────────────────┘│
│                                     │
│  그리고 쿼리 실행도 성공!           │
│  SELECT * FROM users;              │
│  ┌──────────────────────────────┐  │
│  │ 1, user1, password1, ...     │  │
│  │ 2, user2, password2, ...     │  │
│  │ ...                          │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

#### 🔒 보안 고려사항

| 환경 | web-allow-others | 이유 | 위험도 |
|------|------------------|------|--------|
| **로컬 개발 (Docker)** | `true` | 자신의 컴퓨터이므로 안전 | 🟢 안전 |
| **개발팀 네트워크** | `true` | 내부 네트워크만 접근 가능 | 🟡 방화벽 필수 |
| **프로덕션** | `false` 권장 | H2 외부 접근 차단 | 🔴 위험 |
| **프로덕션 (권장)** | RDS/PostgreSQL 등 | 외부 DB 사용 | 🟢 안전 |

**결론:**
- ✅ Docker로 **로컬 개발**할 때: `web-allow-others: true` 사용
- ❌ **프로덕션 배포**할 때: H2 제거, RDS/MySQL 같은 외부 DB로 전환


---

## 📚 API 문서

### Swagger UI
```
http://localhost:8080/swagger-ui.html
```

**주요 API 그룹:**
- **User Controller**: 사용자 CRUD
- **Stock Controller**: 주식 CRUD
- **Transaction Controller**: 거래 실행 및 조회
- **Portfolio Controller**: 포트폴리오 조회
- **Stock Analysis Controller**: 분석 및 통계

### Actuator 엔드포인트
```
http://localhost:8080/actuator/
```

- `/health`: 애플리케이션 상태
- `/metrics`: 성능 지표
- `/info`: 애플리케이션 정보

---

## 🔍 실행 흐름

### Docker 실행 흐름

```
1. docker build -t stock-trading-app:v1 .
   └─ Dockerfile 읽음
      ├─ Stage 1: gradle:8.5-jdk21에서 소스 컴파일
      │   ├─ gradlew, build.gradle 복사
      │   ├─ gradle dependencies 실행 (캐시)
      │   ├─ src/ 복사
      │   └─ gradle bootJar 실행 → JAR 생성
      └─ Stage 2: eclipse-temurin:21-jre에서 런타임
          ├─ Stage 1의 JAR 파일만 복사
          ├─ 포트 8080 노출
          └─ java -jar app.jar 실행

2. docker run -d -p 8080:8080 --name stock-service stock-trading-app:v1
   └─ 이미지로부터 컨테이너 생성 및 실행
      ├─ 8080 포트 매핑 (호스트:컨테이너)
      ├─ 백그라운드 실행
      └─ Spring Boot 애플리케이션 시작

3. Application 시작 순서
   ├─ Spring Boot ApplicationContext 초기화
   ├─ DataSource 설정 (H2 in-memory DB)
   ├─ JPA 엔티티 테이블 생성 (create-drop)
   ├─ data.sql 실행 (초기 데이터 로드)
   ├─ AOP Aspect 등록 (@ExecutionTimeAspect)
   ├─ Spring Data JPA repositories 스캔
   ├─ Actuator 엔드포인트 등록
   └─ Swagger/OpenAPI 생성 → 준비 완료!

4. http://localhost:8080/swagger-ui.html 접속
   └─ API 테스트 시작!
```

---

## 📊 성능 모니터링

### AOP 기반 자동 로깅

모든 Controller 메서드는 자동으로 실행 시간이 로깅됩니다:

```log
2026-01-28T16:25:15.123+09:00 INFO [API REQUEST] com.skala.stock.controller.UserController.getAllUsers() | Params: [] - 시작
2026-01-28T16:25:15.234+09:00 INFO [API RESPONSE] com.skala.stock.controller.UserController.getAllUsers() - 완료 (소요 시간: 111 ms)
```

### Actuator Metrics 확인

```bash
# 모든 메트릭 조회
curl http://localhost:8080/actuator/metrics

# 특정 메트릭 상세 조회
curl http://localhost:8080/actuator/metrics/jvm.memory.used
```

---