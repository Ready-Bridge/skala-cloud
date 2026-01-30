# 3가지 도전과제 가이드

## 목차
1. [입력값 검증(@Valid)과 GlobalExceptionHandler를 이용한 요청 파라미터 예외 처리](#1-입력값-검증valid과-globalexceptionhandler를-이용한-요청-파라미터-예외-처리)
2. [H2 DB 데이터를 로컬 파일로 저장해서 유지하기](#2-h2-db-데이터를-로컬-파일로-저장해서-유지하기)
3. [OAS 기반으로 REST API 문서 자동화 구성하기](#3-oas-기반으로-rest-api-문서-자동화-구성하기)

---

## 1. 입력값 검증(@Valid)과 GlobalExceptionHandler를 이용한 요청 파라미터 예외 처리

### 1.1 개념 설명

REST API에서 클라이언트가 보낸 데이터가 올바른지 검증하는 것은 보안과 안정성의 핵심입니다.

**3가지 검증 전략**:

```
1. Controller 검증 (❌ 권장 안 함)
   └─ 검증 로직이 Controller에 섞여 코드가 지저분함

2. Service 검증 (△ 부분적 가능)
   └─ Service까지 도달했으므로 불필요한 계층 통과 (성능 문제)

3. DTO 검증 (✓ 권장)
   └─ Request 바운더리에서 조기 실패 (fail fast)
   └─ 검증 규칙과 비즈니스 로직 분리
   └─ 재사용 가능 (웹 요청, 메시지큐, etc)
```

### 1.2 구현 방식

#### Step 1: Request DTO에 검증 애노테이션 추가

**StockCreateRequest.java**:
```java
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

public record StockCreateRequest(
    // @NotBlank: null, 빈 문자열, 공백만 있는 문자열 모두 거부
    @NotBlank(message = "주식명은 필수입니다")
    String stockName,
    
    // @NotNull: null만 거부, 0은 허용
    @NotNull(message = "주식 가격은 필수입니다")
    // @Positive: 0 초과만 허용 (0은 불가)
    @Positive(message = "주식 가격은 0보다 커야 합니다")
    Double stockPrice
) {
}
```

**PlayerCreateRequest.java**:
```java
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record PlayerCreateRequest(
    @NotBlank(message = "플레이어 ID는 필수입니다")
    // @Size: 문자열 길이 범위 검증
    @Size(min = 3, max = 20, message = "플레이어 ID는 3자 이상 20자 이하여야 합니다")
    String playerId,
    
    @NotBlank(message = "비밀번호는 필수입니다")
    @Size(min = 4, max = 20, message = "비밀번호는 4자 이상 20자 이하여야 합니다")
    String playerPassword
) {
}
```

**PlayerUpdateRequest.java**:
```java
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;

public record PlayerUpdateRequest(
    String playerId,
    
    @NotNull(message = "플레이어 금액은 필수입니다")
    // @PositiveOrZero: 0 이상만 허용 (음수 불가)
    @PositiveOrZero(message = "플레이어 금액은 0 이상이어야 합니다")
    Double playerMoney
) {
}
```

**자주 사용하는 검증 애노테이션 목록**:

| 애노테이션 | 검증 조건 | 사용 예시 |
|-----------|---------|---------|
| `@NotNull` | null이 아님 | Double, Integer, Object |
| `@NotBlank` | null, 빈 문자열, 공백 제외 | String (필수 입력) |
| `@NotEmpty` | null, 빈 컬렉션 제외 | List, Set, Map |
| `@Size` | 문자열 길이 또는 컬렉션 크기 | username @Size(min=3, max=20) |
| `@Positive` | 0 초과 | price @Positive |
| `@PositiveOrZero` | 0 이상 | stock quantity @PositiveOrZero |
| `@Negative` | 0 미만 | discount @Negative |
| `@Email` | 이메일 형식 | email @Email |
| `@Min / @Max` | 숫자 범위 | age @Min(18) @Max(120) |
| `@Pattern` | 정규표현식 | phone @Pattern(regexp="^[0-9]{10,11}$") |

#### Step 2: Controller에서 @Valid 적용

**StockController.java**:
```java
import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/stocks")
public class StockController {
    
    @PostMapping
    @Operation(summary = "주식 등록")
    public Response<Stock> createStock(
        // @Valid: DTO의 검증 애노테이션을 Spring이 처리하도록 지시
        @Valid @RequestBody StockCreateRequest request
    ) {
        return stockService.createStock(request);
    }
    
    @PutMapping
    @Operation(summary = "주식 정보 수정")
    public Response<Stock> updateStock(
        @Valid @RequestBody StockUpdateRequest request
    ) {
        return stockService.updateStock(request);
    }
}
```

**PlayerController.java**:
```java
@PostMapping
@Operation(summary = "플레이어 등록")
public Response<Player> createPlayer(
    @Valid @RequestBody PlayerCreateRequest request
) {
    return playerService.createPlayer(request);
}

@PostMapping("/login")
@Operation(summary = "플레이어 로그인")
public Response<PlayerLoginDto> loginPlayer(
    @Valid @RequestBody PlayerSession playerSession
) {
    return playerService.loginPlayer(playerSession);
}

@PostMapping("/buy")
@Operation(summary = "주식 매수")
public Response<Void> buyPlayerStock(
    @Valid @RequestBody StockOrder order
) {
    return playerService.buyPlayerStock(order);
}

@PostMapping("/sell")
@Operation(summary = "주식 매도")
public Response<Void> sellPlayerStock(
    @Valid @RequestBody StockOrder order
) {
    return playerService.sellPlayerStock(order);
}
```

#### Step 3: GlobalExceptionHandler에서 검증 실패 처리

**GlobalExceptionHandler.java**:
```java
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;
import lombok.extern.slf4j.Slf4j;

@ControllerAdvice
@Slf4j
public class GlobalExceptionHandler {
    
    /**
     * @Valid 검증 실패 시 자동으로 MethodArgumentNotValidException 발생
     * 이 메서드에서 해당 예외를 처리
     */
    @ExceptionHandler(value = MethodArgumentNotValidException.class)
    public @ResponseBody Response<?> takeMethodArgumentNotValidException(
        MethodArgumentNotValidException e
    ) {
        // 모든 검증 오류를 하나의 메시지로 합침
        String errorMessage = e.getBindingResult()
            .getFieldErrors()
            .stream()
            // 각 필드의 오류를 "필드명: 메시지" 형식으로 변환
            .map(error -> error.getField() + ": " + error.getDefaultMessage())
            // 여러 오류는 쉼표로 연결
            .reduce((m1, m2) -> m1 + ", " + m2)
            // 오류가 없으면 기본 메시지
            .orElse("검증 실패");
        
        log.warn("GlobalExceptionHandler.MethodArgumentNotValidException: {}", errorMessage);
        return Response.error(Error.PARAMETER_MISSED.getCode(), errorMessage);
    }
    
    // ... 기타 예외 처리
}
```

### 1.3 동작 흐름도

```
클라이언트 요청
    ↓
{"stockName": "", "stockPrice": -100}  ← 잘못된 데이터
    ↓
StockController.createStock() 호출
    ↓
@Valid 검증 시작
    ├─ stockName 검증: @NotBlank 실패 (빈 문자열)
    └─ stockPrice 검증: @Positive 실패 (-100은 음수)
    ↓
MethodArgumentNotValidException 발생 (자동)
    ↓
GlobalExceptionHandler.takeMethodArgumentNotValidException() 처리
    ↓
{
    "result": "error",
    "code": "PARAMETER_MISSED",
    "message": "stockName: 주식명은 필수입니다, stockPrice: 주식 가격은 0보다 커야 합니다"
} ← JSON 응답
```

### 1.4 테스트 방법

**잘못된 요청 테스트**:

```bash
# ❌ 검증 실패 예시
curl -X POST http://localhost:8080/api/stocks \
  -H "Content-Type: application/json" \
  -d '{
    "stockName": "",
    "stockPrice": -100
  }'

# 응답:
{
    "result": "error",
    "code": "PARAMETER_MISSED",
    "message": "stockName: 주식명은 필수입니다, stockPrice: 주식 가격은 0보다 커야 합니다"
}
```

```bash
# ✓ 올바른 요청
curl -X POST http://localhost:8080/api/stocks \
  -H "Content-Type: application/json" \
  -d '{
    "stockName": "Apple",
    "stockPrice": 150.5
  }'

# 응답:
{
    "result": "success",
    "code": "OK",
    "body": {
        "id": 1,
        "stockName": "Apple",
        "stockPrice": 150.5
    }
}
```

### 1.5 핵심 이점

1. **조기 실패 (Fail Fast)**
   - 잘못된 데이터가 Service/Repository에 도달하기 전에 걸러짐
   - 불필요한 DB 접근 방지

2. **코드 간결성**
   - 검증 로직이 DTO에 선언적으로 표현됨
   - Controller/Service가 비즈니스 로직에만 집중

3. **재사용성**
   - 같은 DTO를 여러 엔드포인트에서 사용 가능
   - 메시지큐, gRPC 등 다른 입력 소스에도 적용 가능

4. **명확한 API 계약**
   - DTO 만 보면 어떤 필드가 필수인지 알 수 있음
   - 클라이언트 개발자에게 명확한 요구사항 전달

---

## 2. H2 DB 데이터를 로컬 파일로 저장해서 유지하기

### 2.1 개념 설명

**H2 데이터베이스의 두 가지 모드**:

```
┌─────────────────────────────────────────────────────────────────┐
│                     H2 데이터베이스                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ❌ 메모리 모드 (In-Memory)                                      │
│  └─ URL: jdbc:h2:mem:skala-stock                               │
│  └─ 특징:                                                       │
│     - 데이터가 RAM에만 저장됨                                   │
│     - 애플리케이션 종료 시 모든 데이터 소실                     │
│     - 개발/테스트용으로 사용                                    │
│     - 매우 빠름 (디스크 I/O 없음)                              │
│                                                                 │
│  ✓ 파일 모드 (File-based)                                       │
│  └─ URL: jdbc:h2:./data/skala-stock                            │
│  └─ 특징:                                                       │
│     - 데이터가 디스크에 저장됨                                  │
│     - 애플리케이션 재시작 후에도 데이터 유지                    │
│     - 로컬 개발 및 테스트에 적합                                │
│     - 메모리 모드보다 느림                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 구현 방식

#### Step 1: application.yml 수정

**이전 (메모리 모드)**:
```yaml
spring:
  datasource:
    url: jdbc:h2:mem:skala-stock  # ❌ 메모리에만 저장
    driver-class-name: org.h2.Driver
    username: sa
    password:
```

**이후 (파일 모드)**:
```yaml
spring:
  datasource:
    url: jdbc:h2:./data/skala-stock  # ✓ ./data 디렉토리에 파일로 저장
    driver-class-name: org.h2.Driver
    username: sa
    password:
  h2:
    console:
      enabled: true
      path: /h2-console
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    open-in-view: false
```

**URL 형식 설명**:

```
jdbc:h2:./data/skala-stock
    │  │ │                 │
    │  │ │                 └─ 파일명 (skala-stock.mv.db, skala-stock.trace.db 생성)
    │  │ └─ 상대 경로 (프로젝트 루트 기준)
    │  └─ H2 드라이버 지정
    └─ JDBC URL 스키마

실제 생성 파일:
- skala-stock.mv.db: 데이터 파일 (메인)
- skala-stock.trace.db: 추적 로그 파일
```

**절대 경로 사용 예시** (권장하지 않음):
```yaml
# Linux/Mac
url: jdbc:h2:/tmp/h2-db/skala-stock

# Windows
url: jdbc:h2:C:/data/h2/skala-stock
```

#### Step 2: 데이터 디렉토리 생성

```bash
# 프로젝트 루트에서 data 디렉토리 생성
mkdir -p ./data

# 생성 확인
ls -la | grep data
# drwxr-xr-x  data/
```

#### Step 3: .gitignore 수정

데이터베이스 파일이 Git에 커밋되지 않도록 설정:

**.gitignore**:
```
# H2 Database - 개발 환경의 로컬 데이터는 커밋 대상 제외
data/
*.mv.db
*.trace.db
```

**왜 제외하는가?**

```
❌ data/을 커밋하면:
   - 리포지토리 크기 증가
   - 팀원의 로컬 데이터와 충돌
   - 프로덕션 데이터와 혼동 가능

✓ .gitignore에 추가하면:
   - 각자 로컬 개발 환경에서만 데이터 유지
   - 팀원 간 협업 간편
   - 프로덕션 데이터는 별도 관리
```

### 2.3 파일 구조

```
skala-stock-api-practice/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/sk/skala/...
│   │   └── resources/
│   │       └── application.yml  ← jdbc:h2:./data/skala-stock
│   └── test/
├── data/                         ← 새로 생성된 디렉토리
│   ├── skala-stock.mv.db        ← 데이터 파일 (자동 생성)
│   └── skala-stock.trace.db     ← 추적 로그 (자동 생성)
├── build.gradle
├── .gitignore                    ← data/ 추가됨
└── README.md
```

### 2.4 동작 원리

```
1. 애플리케이션 시작
   └─ application.yml 읽음
   └─ jdbc:h2:./data/skala-stock URL 파싱
   
2. H2 드라이버 초기화
   └─ ./data 디렉토리 확인
   └─ skala-stock.mv.db 파일 확인
   
3. 첫 시작 (파일 없을 때)
   └─ 새 DB 파일 생성
   └─ 스키마 초기화 (ddl-auto: update)
   
4. 데이터 저장
   └─ INSERT/UPDATE 쿼리 실행
   └─ 결과가 skala-stock.mv.db에 기록됨
   └─ 동시에 메모리 캐시에도 저장됨
   
5. 애플리케이션 종료
   └─ DB 연결 종료
   └─ 메모리 캐시 소실
   └─ 파일은 디스크에 유지됨
   
6. 애플리케이션 재시작
   └─ skala-stock.mv.db 파일 존재 확인
   └─ 이전 데이터 로드
   └─ 데이터 복구 완료 ✓
```

### 2.5 성능 최적화

#### H2 파일 모드 옵션

```yaml
spring:
  datasource:
    url: jdbc:h2:./data/skala-stock;MODE=MySQL;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE
    # ↑ 옵션 설명:
    # MODE=MySQL: MySQL 호환 모드 (기존 MySQL 코드 호환)
    # DB_CLOSE_DELAY=-1: 마지막 연결 종료 후에도 DB 유지 (기본값)
    # DB_CLOSE_ON_EXIT=FALSE: JVM 종료 시에도 DB 파일 유지
```

#### 권장 옵션

```yaml
spring:
  datasource:
    url: jdbc:h2:./data/skala-stock;AUTO_SERVER=TRUE;MULTI_THREADED=1
    # AUTO_SERVER=TRUE: 동시 접근 지원
    # MULTI_THREADED=1: 멀티스레드 환경 최적화
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: false  # 프로덕션에서는 false로 설정
    open-in-view: false
```

### 2.6 데이터 확인 방법

#### 방법 1: H2 Console (웹 UI)

```bash
# 애플리케이션 시작 후 브라우저에서 접속
http://localhost:8080/h2-console

# 로그인 정보
- JDBC URL: jdbc:h2:./data/skala-stock
- User Name: sa
- Password: (빈칸)

# SQL 쿼리 실행 가능
SELECT * FROM stock;
SELECT * FROM player;
```

#### 방법 2: 파일 시스템 확인

```bash
# 디렉토리 내용 확인
ls -lah data/

# 출력 예시:
# -rw-r--r--  user  group  512 Jan 30 10:45 skala-stock.mv.db
# -rw-r--r--  user  group  256 Jan 30 10:45 skala-stock.trace.db

# 파일 크기 추적 (데이터 저장 확인)
du -sh data/skala-stock.mv.db
# 첫 실행: 512K
# 데이터 추가 후: 1M, 2M 등으로 증가
```

#### 방법 3: 로그 확인

```bash
# 애플리케이션 시작 시 H2 초기화 로그
# 콘솔에서 다음 메시지 확인:
# H2 console available at '/h2-console'
# Database url: 'jdbc:h2:./data/skala-stock'
```

### 2.7 주의사항

**⚠️ 파일 삭제 시**:

```bash
# data 디렉토리 삭제 시 모든 데이터 손실
rm -rf data/

# 애플리케이션 재시작 시 새 DB 생성됨
# (이전 데이터 복구 불가)
```

**⚠️ 동시 접근**:

```yaml
# 여러 애플리케이션 인스턴스가 동시에 같은 DB 파일 접근 불가
# (락 파일 에러 발생 가능)

# 해결: AUTO_SERVER=TRUE 옵션 사용
url: jdbc:h2:./data/skala-stock;AUTO_SERVER=TRUE
```

---

## 3. OAS 기반으로 REST API 문서 자동화 구성하기

### 3.1 개념 설명

**OAS (OpenAPI Specification)란?**

```
OpenAPI = REST API를 표준화된 형식으로 문서화하는 규약

┌──────────────────────────────────────────────────────────┐
│                 OpenAPI 스펙                             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ✓ 장점:                                                │
│  - 코드와 문서를 분리하지 않음                          │
│  - API가 변경되면 자동 업데이트                         │
│  - 여러 클라이언트 라이브러리 자동 생성 가능           │
│  - Swagger UI로 API 테스트 가능                        │
│  - 팀 간 커뮤니케이션 효율화                           │
│                                                          │
│  구성 요소:                                             │
│  ├─ 정보 (API 이름, 버전, 설명)                        │
│  ├─ 서버 (호스트 정보)                                │
│  ├─ 경로 (엔드포인트 정의)                             │
│  │   ├─ 메서드 (GET, POST, PUT, DELETE)              │
│  │   ├─ 파라미터 (query, path, body)                  │
│  │   ├─ 요청 바디 스키마                               │
│  │   ├─ 응답 (200, 400, 500 등)                       │
│  │   └─ 응답 스키마                                    │
│  ├─ 컴포넌트 (재사용 가능한 스키마)                   │
│  └─ 보안 (인증 방식)                                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 3.2 구현 방식

#### Step 1: 의존성 확인 (이미 추가됨)

**build.gradle**:
```gradle
dependencies {
    implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:2.1.0'
    // ↑ 이것이 Swagger UI와 OpenAPI 스펙을 제공
}
```

**springdoc-openapi의 두 가지 핵심 부분**:
```
springdoc-openapi-starter-webmvc-ui
├─ 1. OpenAPI 스펙 자동 생성
│  ├─ Spring 애노테이션 분석
│  ├─ @RequestMapping, @GetMapping, @PostMapping 등 파싱
│  └─ OpenAPI JSON/YAML 생성
│
└─ 2. Swagger UI 제공
   ├─ 웹 기반 API 문서 뷰어
   ├─ 브라우저에서 API 테스트 가능
   └─ 완전한 사용자 인터페이스
```

#### Step 2: application.yml 설정

**application.yml**:
```yaml
springdoc:
  swagger-ui:
    path: /api/swagger-ui  # Swagger UI 접속 경로
  api-docs:
    path: /api/oas-docs    # OpenAPI JSON/YAML 문서 경로
```

#### Step 3: Controller에 OpenAPI 애노테이션 추가

**StockController.java**:
```java
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;

@RestController
@RequestMapping("/api/stocks")
@Tag(name = "Stock API", description = "주식 정보 관리 API")
public class StockController {
    
    @GetMapping("/list")
    @Operation(summary = "전체 주식 목록 조회", description = "페이징을 적용하여 주식 목록을 조회합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "조회 성공",
            content = @Content(schema = @Schema(implementation = Response.class))),
        @ApiResponse(responseCode = "400", description = "잘못된 요청"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<PagedList> getAllStocks(
        @Parameter(description = "페이지 오프셋 (기본값: 0)", example = "0")
        @RequestParam(defaultValue = "0") Integer offset,
        @Parameter(description = "페이지당 항목 수 (기본값: 10)", example = "10")
        @RequestParam(defaultValue = "10") Integer count) {
        return stockService.getAllStocks(offset, count);
    }
    
    @PostMapping
    @Operation(summary = "주식 등록", description = "새로운 주식 정보를 등록합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "등록 성공"),
        @ApiResponse(responseCode = "400", description = "필수 파라미터 누락 또는 중복"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<Stock> createStock(
        @io.swagger.v3.oas.annotations.parameters.RequestBody(
            description = "등록할 주식 정보",
            content = @Content(schema = @Schema(implementation = StockCreateRequest.class))
        )
        @Valid @RequestBody StockCreateRequest request) {
        return stockService.createStock(request);
    }
}
```

**PlayerController.java**:
```java
@RestController
@RequestMapping("/api/players")
@Tag(name = "Player API", description = "플레이어 정보 및 주식 거래 API")
public class PlayerController {
    
    @PostMapping
    @Operation(summary = "플레이어 등록", description = "새로운 플레이어를 등록합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "등록 성공"),
        @ApiResponse(responseCode = "400", description = "필수 파라미터 누락 또는 중복"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<Player> createPlayer(
        @io.swagger.v3.oas.annotations.parameters.RequestBody(
            description = "등록할 플레이어 정보",
            content = @Content(schema = @Schema(implementation = PlayerCreateRequest.class))
        )
        @Valid @RequestBody PlayerCreateRequest request) {
        return playerService.createPlayer(request);
    }
    
    @PostMapping("/login")
    @Operation(summary = "플레이어 로그인", description = "플레이어가 로그인합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "로그인 성공"),
        @ApiResponse(responseCode = "400", description = "인증 실패")
    })
    public Response<PlayerLoginDto> loginPlayer(
        @io.swagger.v3.oas.annotations.parameters.RequestBody(
            description = "플레이어 로그인 정보",
            content = @Content(schema = @Schema(implementation = PlayerSession.class))
        )
        @Valid @RequestBody PlayerSession playerSession) {
        return playerService.loginPlayer(playerSession);
    }
}
```

### 3.3 OpenAPI 애노테이션 상세 설명

#### @Tag
```java
@Tag(name = "Stock API", description = "주식 정보 관리 API")
public class StockController { }

// 용도:
// - 관련 엔드포인트들을 그룹화
// - Swagger UI에서 탭으로 표시됨
```

#### @Operation
```java
@Operation(
    summary = "주식 등록",  // 요약 (Swagger UI의 제목)
    description = "새로운 주식 정보를 등록합니다"  // 상세 설명
)
public Response<Stock> createStock(...) { }

// 용도: 엔드포인트의 목적을 명확히 설명
```

#### @Parameter
```java
@Parameter(
    description = "페이지 오프셋 (기본값: 0)",
    example = "0"  // Swagger UI에서 예제로 표시
)
@RequestParam(defaultValue = "0") Integer offset

// 용도:
// - 쿼리/경로 파라미터 설명
// - 예제 값 제공
// - 필수 여부 표시
```

#### @ApiResponse / @ApiResponses
```java
@ApiResponses(value = {
    @ApiResponse(
        responseCode = "200",
        description = "조회 성공",
        content = @Content(schema = @Schema(implementation = Response.class))
    ),
    @ApiResponse(responseCode = "400", description = "잘못된 요청"),
    @ApiResponse(responseCode = "500", description = "서버 오류")
})
public Response<Stock> getStock(...) { }

// 용도:
// - 가능한 HTTP 상태 코드 표시
// - 각 상태의 응답 형식 정의
// - 에러 메시지 설명
```

#### @Schema
```java
@Schema(
    implementation = StockCreateRequest.class,
    description = "등록할 주식 정보"
)
@RequestBody StockCreateRequest request

// 용도:
// - Request/Response 바디의 구조 표현
// - DTO 클래스 참조하여 자동으로 필드 정보 추출
```

### 3.4 Swagger UI 접속 및 사용

#### URL

```
http://localhost:8080/api/swagger-ui/index.html
```

#### Swagger UI 화면 구성

```
┌─────────────────────────────────────────────────────────────┐
│ Swagger UI                                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 1. 좌측 네비게이션                                          │
│    ├─ Stock API ▼                                          │
│    │  ├─ GET   /api/stocks/list                           │
│    │  ├─ GET   /api/stocks/{id}                           │
│    │  ├─ POST  /api/stocks                                │
│    │  ├─ PUT   /api/stocks                                │
│    │  └─ DELETE /api/stocks                               │
│    └─ Player API ▼                                         │
│       ├─ GET   /api/players/list                          │
│       ├─ POST  /api/players                               │
│       ├─ POST  /api/players/login                         │
│       └─ POST  /api/players/buy                           │
│                                                             │
│ 2. 우측 상세 정보                                           │
│    ├─ 요청 방식 (GET, POST 등)                            │
│    ├─ 엔드포인트 경로                                      │
│    ├─ 설명                                                 │
│    ├─ 파라미터 (query, body)                              │
│    ├─ 요청 예시                                            │
│    ├─ 응답 예시                                            │
│    └─ "Try it out" 버튼 (API 테스트)                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 실제 사용 방법

**1. 엔드포인트 클릭**:
```
POST /api/stocks 클릭
└─ 엔드포인트 상세 정보 펼쳐짐
```

**2. 요청 바디 확인**:
```json
{
  "stockName": "string (필수)",
  "stockPrice": "number (필수, 0보다 커야함)"
}
```

**3. "Try it out" 버튼 클릭**:
```
└─ 요청 바디 입력 필드 활성화
```

**4. 데이터 입력**:
```json
{
  "stockName": "Apple",
  "stockPrice": 150.5
}
```

**5. "Execute" 버튼 클릭**:
```
└─ API 호출
└─ 응답 결과 표시
```

### 3.5 OpenAPI 스펙 (JSON/YAML) 확인

#### OpenAPI JSON 다운로드

```
http://localhost:8080/api/oas-docs

# 또는 YAML 형식
http://localhost:8080/api/oas-docs.yaml
```

#### OpenAPI 스펙 구조

```yaml
openapi: 3.0.0
info:
  title: SKALA-STOCK-API
  version: 0.0.1-SNAPSHOT
servers:
  - url: http://localhost:8080
paths:
  /api/stocks:
    post:
      tags:
        - Stock API
      summary: 주식 등록
      description: 새로운 주식 정보를 등록합니다
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/StockCreateRequest'
      responses:
        '200':
          description: 등록 성공
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Response'
        '400':
          description: 필수 파라미터 누락
components:
  schemas:
    StockCreateRequest:
      type: object
      required:
        - stockName
        - stockPrice
      properties:
        stockName:
          type: string
          description: 주식명은 필수입니다
        stockPrice:
          type: number
          format: double
          description: 주식 가격은 0보다 커야 합니다
```

### 3.6 CLI에서 API 테스트 (cURL)

**Swagger UI 없이 cURL로도 테스트 가능**:

```bash
# 주식 목록 조회
curl -X GET "http://localhost:8080/api/stocks/list?offset=0&count=10" \
  -H "Content-Type: application/json"

# 주식 등록
curl -X POST "http://localhost:8080/api/stocks" \
  -H "Content-Type: application/json" \
  -d '{
    "stockName": "Apple",
    "stockPrice": 150.5
  }'

# 플레이어 등록
curl -X POST "http://localhost:8080/api/players" \
  -H "Content-Type: application/json" \
  -d '{
    "playerId": "user123",
    "playerPassword": "pass1234"
  }'

# 플레이어 로그인
curl -X POST "http://localhost:8080/api/players/login" \
  -H "Content-Type: application/json" \
  -d '{
    "playerId": "user123",
    "playerPassword": "pass1234"
  }'

# 주식 매수
curl -X POST "http://localhost:8080/api/players/buy" \
  -H "Content-Type: application/json" \
  -d '{
    "stockId": 1,
    "quantity": 10
  }'
```

### 3.7 주요 이점

```
1. 자동 동기화
   ├─ API 코드 변경 → 문서 자동 업데이트
   ├─ 수동 업데이트 불필요
   └─ 문서 버전 관리 간편

2. 개발자 경험 향상
   ├─ Swagger UI에서 직접 API 테스트 가능
   ├─ 명확한 요청/응답 형식 제시
   └─ 오류 메시지 상세 설명

3. 팀 협업 효율화
   ├─ 백엔드 개발자: API 스펙 정의
   ├─ 프론트엔드 개발자: Swagger UI 기반 개발
   ├─ 동시 작업 가능
   └─ 소통 오류 감소

4. 생산성 향상
   ├─ 클라이언트 라이브러리 자동 생성 가능
   ├─ 외부 시스템과의 통합 용이
   └─ 타사 개발자들도 쉽게 API 이용

5. 테스트 자동화
   ├─ OpenAPI 스펙 기반으로 테스트 작성 가능
   ├─ 명확한 계약(Contract) 정의
   └─ API 변경 시 테스트 자동 검증
```

### 3.8 Advanced: 요청/응답 예시 직접 정의

```java
@Operation(summary = "주식 등록", description = "새로운 주식을 등록합니다")
@ApiResponses(value = {
    @ApiResponse(
        responseCode = "200",
        description = "등록 성공",
        content = @Content(
            mediaType = "application/json",
            schema = @Schema(implementation = Response.class),
            examples = {
                @ExampleObject(
                    name = "Success Example",
                    value = """
                    {
                        "result": "success",
                        "code": "OK",
                        "body": {
                            "id": 1,
                            "stockName": "Apple",
                            "stockPrice": 150.5
                        }
                    }
                    """
                )
            }
        )
    )
})
@PostMapping
public Response<Stock> createStock(@Valid @RequestBody StockCreateRequest request) {
    return stockService.createStock(request);
}
```

### 3.9 Swagger UI 커스터마이징 (선택)

```yaml
springdoc:
  swagger-ui:
    path: /api/swagger-ui
    title: "SKALA 주식 거래 API"
    url: "/api/oas-docs"
    operationsSorter: method  # 정렬 방식 (method, alpha 등)
    tagsSorter: alpha  # 태그 정렬
    tryItOutEnabled: true  # "Try it out" 활성화
  api-docs:
    path: /api/oas-docs
  api-docs.servers:
    - url: http://localhost:8080
      description: Local development
    - url: https://api.example.com
      description: Production
```

---

## 종합 정리

### 3가지 도전과제의 연관성

```
1. @Valid 검증
   └─ Request 바운더리에서 데이터 검증
   └─ GlobalExceptionHandler로 통일된 에러 응답

2. H2 파일 저장
   └─ 로컬 개발 환경에서 데이터 유지
   └─ 검증된 데이터가 안전하게 저장됨

3. OpenAPI 문서화
   └─ 검증 규칙이 문서에 명시됨
   └─ 클라이언트는 올바른 포맷으로 요청
   └─ 저장된 데이터의 구조가 명확함

    ┌──────────────────────────┐
    │   클라이언트 요청 (JSON)   │
    └──────────────────────────┘
              ↓
    ┌──────────────────────────┐
    │  1️⃣ @Valid 검증        │
    │  (요청 파라미터 검증)     │
    └──────────────────────────┘
              ↓ (통과)
    ┌──────────────────────────┐
    │  2️⃣ 비즈니스 로직        │
    │  (Service에서 처리)      │
    └──────────────────────────┘
              ↓
    ┌──────────────────────────┐
    │  3️⃣ H2 저장            │
    │  (디스크 파일 저장)      │
    └──────────────────────────┘
              ↓
    ┌──────────────────────────┐
    │  응답 (JSON)             │
    │  (4. OpenAPI 문서 기반)   │
    └──────────────────────────┘
```

### 각 도전과제를 수행할 때의 체크리스트

**✓ @Valid 검증**:
- [ ] Request DTO에 검증 애노테이션 추가 (@NotBlank, @NotNull 등)
- [ ] Controller 메서드에 @Valid 추가
- [ ] GlobalExceptionHandler에 MethodArgumentNotValidException 핸들러 추가
- [ ] API 테스트: 잘못된 데이터로 요청 → 에러 응답 확인

**✓ H2 파일 저장**:
- [ ] application.yml의 datasource URL 변경 (jdbc:h2:mem → jdbc:h2:./data)
- [ ] data/ 디렉토리 생성
- [ ] .gitignore에 data/ 추가
- [ ] 애플리케이션 재시작 → 데이터 유지 확인

**✓ OpenAPI 문서화**:
- [ ] build.gradle에 springdoc-openapi 의존성 확인
- [ ] application.yml에 springdoc 설정 추가
- [ ] Controller에 @Tag, @Operation, @ApiResponse 애노테이션 추가
- [ ] http://localhost:8080/api/swagger-ui/index.html 접속 → 문서 확인

---

## 참고 자료

- [Spring Boot Validation 공식 문서](https://docs.spring.io/spring-framework/docs/current/reference/html/core.html#validation)
- [H2 Database 공식 사이트](http://www.h2database.com/)
- [OpenAPI 3.0 명세](https://spec.openapis.org/oas/v3.0.0)
- [Springdoc OpenAPI 문서](https://springdoc.org/)
- [Jakarta Bean Validation 표준](https://beanvalidation.org/)
