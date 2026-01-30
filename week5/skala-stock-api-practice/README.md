# Skala Stock API - 학습 노트

## 프로젝트 개요

### 기본 정보
- **프로젝트명**: Skala Stock API (주식 거래 시뮬레이션 REST API)
- **Spring Boot 버전**: 3.1.4
- **Java 버전**: 21
- **빌드 도구**: Gradle
- **데이터베이스**: H2 In-Memory Database (jdbc:h2:mem:skala-stock)

### 핵심 기능
- 주식 정보 관리 (CRUD)
- 플레이어 관리 및 인증 (Session 기반)
- 주식 매매 (buy/sell)
- 페이징을 통한 목록 조회
- JWT 기반 세션 관리

### 프로젝트 구조
```
src/main/java/com/sk/skala/stockapi/
├── controller/           # REST API 엔드포인트
│   ├── StockController
│   └── PlayerController
├── service/              # 비즈니스 로직 (@Transactional 적용)
│   ├── StockService
│   ├── PlayerService
│   └── SessionHandler
├── repository/           # 데이터 접근 계층 (JpaRepository)
│   ├── StockRepository
│   ├── PlayerRepository
│   └── PlayerStockRepository
├── data/                 # 엔티티 및 DTO
│   ├── table/           # JPA Entity
│   │   ├── Stock
│   │   ├── Player
│   │   └── PlayerStock
│   ├── dto/
│   │   ├── request/     # API 요청 DTO
│   │   │   ├── StockCreateRequest
│   │   │   ├── StockUpdateRequest
│   │   │   ├── StockDeleteRequest
│   │   │   ├── PlayerCreateRequest
│   │   │   ├── PlayerUpdateRequest
│   │   │   ├── PlayerDeleteRequest
│   │   │   ├── PlayerSession
│   │   │   └── StockOrder
│   │   └── response/    # API 응답 DTO
│   │       ├── PlayerLoginDto
│   │       ├── PlayerStockDto
│   │       └── PlayerStockListDto
│   └── common/          # 공통 클래스
│       ├── Response<T>  # 제네릭 응답 래퍼
│       ├── PagedList    # 페이징 응답
│       └── ApiLog       # 요청/응답 로그
├── exception/           # 커스텀 Exception
│   ├── ParameterException
│   └── ResponseException
├── aop/                 # 횡단 관심사 (AOP)
│   ├── LoggingAspect
│   └── SkipLogging
├── config/              # 설정 및 상수
│   ├── Error           # 에러 코드 정의
│   ├── Constant        # 상수 정의
│   ├── DataInitializer # 초기 데이터 로드
│   ├── ApplicationProperties # 애플리케이션 설정
│   └── WebConfig       # 웹 설정
├── tools/              # 유틸리티 클래스
│   ├── PaginationTool  # 페이징 처리
│   ├── JsonTool        # JSON 변환
│   ├── StringTool      # 문자열 처리
│   ├── JwtTool         # JWT 생성/검증
│   └── HostInfo        # 호스트 정보
├── GlobalExceptionHandler    # 전역 예외 처리
└── SkalaStockApiApplication  # 애플리케이션 진입점
```

---

## Exception 단 학습 내용

### 1. serialVersionUID의 역할과 필요성

#### 용도
```java
public class ParameterException extends RuntimeException {
    private static final long serialVersionUID = -1485573803677705666L;
    // ...
}
```

- **serialVersionUID**: JVM이 직렬화된 객체를 역직렬화할 때 클래스 버전을 검증하는 번호
- JVM은 내부적으로 클래스 구조(필드, 메서드 시그니처 등)를 기반으로 자동 생성 가능

#### 왜 필요한가?

**과거 (Java 초기 ~ 2000년대)**
- 네트워크를 통해 객체 그대로 직렬화해서 보냄 (Java Serialization)
- 서버 A에서 Person 클래스 v1, 서버 B에서 Person 클래스 v2로 필드가 다르면 역직렬화 실패
- serialVersionUID로 클래스 호환성 관리

**현재 (REST API 시대)**
- JSON(Jackson), Protocol Buffers 등 포맷 사용 → Java native 직렬화 거의 안 씀
- **그런데 여전히 필요한 경우들**:
  - JVM 종료 대비해 객체 상태를 파일에 저장했다가 재기동 시 복원
  - HTTP 세션 객체를 인-메모리 저장소(Redis)에 저장/복원
  - Tomcat Cluster 환경에서 세션 객체를 서버 간 복제할 때
  - Spring Session에서 session attribute 객체 직렬화 필요

이 프로젝트에서는 HTTP 세션 관리 때문에 `PlayerSession` 객체를 직렬화할 수 있도록 설계.

---

### 2. RuntimeException 상속과 getMessage() vs getCode()

```java
public class ParameterException extends RuntimeException {
    private final int code;

    public ParameterException(String... parameters) {
        super(Error.PARAMETER_MISSED.getMessage() + ": " + StringTool.join(parameters));
        this.code = Error.PARAMETER_MISSED.getCode();
    }

    public int getCode() {
        return this.code;
    }
}
```

#### 상속 구조
```
Exception (Checked Exception)
    ↓
RuntimeException (Unchecked Exception - 선택적 처리)
    ↓
ParameterException / ResponseException
```

#### getMessage() vs getCode() 설계 원리

| 메서드 | 출처 | 역할 |
|--------|------|------|
| `getMessage()` | RuntimeException (부모) | 사용자에게 보여줄 메시지 |
| `getCode()` | ResponseException (커스텀) | API 응답 코드 (200, 400, 500 등과 별도) |

부모 클래스의 `getMessage()`는 이미 잘 구현되어 있으므로 `super(message)` 호출로 재사용:
- 스택 트레이스 캡처
- 메시지 저장
- toString() 등에 활용

**왜 RuntimeException을 상속받는가?**

Checked Exception (Exception)을 상속받으면:
```java
// throws 선언 필수 - 코드가 지저분해짐
public Response<Stock> createStock(StockCreateRequest request) throws ParameterException {
    // ...
}
```

Unchecked Exception (RuntimeException)을 상속받으면:
```java
// throws 선언 불필요 - 간결함
// @ExceptionHandler나 @ControllerAdvice로 처리 가능
public Response<Stock> createStock(StockCreateRequest request) {
    // ...
}
```

REST API 환경에서는 모든 예외를 `@ControllerAdvice`에서 처리하므로 Unchecked Exception 사용이 적절.

---

### 3. GlobalExceptionHandler의 동작 원리

#### 예외 흐름도
```
1. Controller 메서드 실행 중 예외 발생
   ↓
2. Spring이 예외 캐치
   ↓
3. @ControllerAdvice가 적용된 GlobalExceptionHandler 검색
   ↓
4. @ExceptionHandler 메서드 매칭
   ↓
5. 해당 메서드 실행 (예: takeParameterException)
   ↓
6. Response 객체 생성
   ↓
7. @ResponseBody로 JSON 변환 후 응답
```

#### 예제
```java
@ControllerAdvice  // 모든 @RestController의 예외 처리
@Slf4j            // Lombok이 log 필드 자동 생성
public class GlobalExceptionHandler {

    @ExceptionHandler(value = ParameterException.class)
    public @ResponseBody Response<?> takeParameterException(ParameterException e) {
        return Response.error(e.getCode(), e.getMessage());
    }
}

// 어디서든 throws하면 자동 처리
public Response<Stock> createStock(StockCreateRequest request) {
    if (request.stockName() == null) {
        throw new ParameterException("stockName");  // 예외 발생
        // → GlobalExceptionHandler.takeParameterException() 호출
        // → Response.error() 반환
    }
}
```

#### Slf4j (@Slf4j) 사용 이유

**@Slf4j 없이 로그를 찍으면**
```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(Exception.class)
    public Response<?> handleException(Exception e) {
        System.out.println(e.getMessage());  // ❌ 문제
        // 1. 프로덕션 환경에서 출력 레벨 제어 불가 (DEBUG, INFO, ERROR 구분 불가)
        // 2. 성능: stdout 버퍼링으로 오버헤드
        // 3. 파일 기록 불가
        // 4. 타임스탐프, 스택 트레이스 자동 추가 불가
        return Response.error(500, e.getMessage());
    }
}
```

**@Slf4j 사용하면**
```java
@ControllerAdvice
@Slf4j  // Lombok이 private static final Logger log = LoggerFactory.getLogger(...) 생성
public class GlobalExceptionHandler {
    
    @ExceptionHandler(Exception.class)
    public Response<?> handleException(Exception e) {
        log.error("GlobalExceptionHandler.Exception: {}", e.getMessage());
        // ✓ 1. application.yml에서 로그 레벨 제어 가능
        // ✓ 2. DEBUG, INFO, WARN, ERROR 구분
        // ✓ 3. 파일/콘솔 출력 설정 가능
        // ✓ 4. 성능 최적화 (lazy evaluation)
        return Response.error(500, e.getMessage());
    }
}
```

application.yml 설정 예시:
```yaml
logging:
  level:
    com.sk.skala.stockapi: DEBUG    # 우리 패키지는 DEBUG 레벨
    org.springframework: INFO         # Spring 프레임워크는 INFO 레벨
  file:
    name: logs/application.log        # 파일 저장
```

---

## JPA Entity 단 학습 내용

### 1. Entity에서 @Data 지양해야 하는 이유

#### @Data의 문제점

```java
@Entity
@Data  // ❌ 지양
public class Player {
    @Id
    private String playerId;
    private Double playerMoney;
}
```

**문제 1: 양방향 참조 (Infinite Loop)**
```java
@Entity
@Data
public class PlayerStock {
    @ManyToOne
    private Player player;
    
    // @Data는 자동으로 toString() 생성
    // toString() → player.toString() → playerStocks.toString() → 무한 루프!
}

// 결과: StackOverflowError
```

**문제 2: 불필요한 Setter 생성**
```java
@Entity
@Data
public class Player {
    @Id
    private String playerId;  // PK는 setter로 변경되면 안 됨!
}

// setter가 있으면 누구나 playerId를 변경 가능
player.setPlayerId("hacker");  // 심각한 보안/데이터 무결성 문제
```

**문제 3: 비즈니스 로직이 드러나지 않음**
```java
// @Data로 setter 남용
player.setPlayerMoney(5000);  // 돈을 설정한다? 어디서 왔는가?

// 비즈니스 메서드로 의도 명확
player.addMoney(5000);  // 상점에서 산 아이템 가격
player.subtractMoney(1000);  // 주식 매수
```

#### 올바른 패턴

```java
@Entity
@Getter  // 조회만 가능
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Player {
    @Id
    private String playerId;
    private String playerPassword;
    private Double playerMoney;

    // 객체 생성
    public Player(String playerId, Double playerMoney) {
        this.playerId = playerId;
        this.playerMoney = playerMoney;
    }

    // 비즈니스 메서드 - 의도가 명확함
    public void updateMoney(Double newAmount) {
        if (newAmount == null || newAmount < 0) {
            throw new ResponseException(Error.INVALID_PARAMETER, "금액은 0 이상");
        }
        this.playerMoney = newAmount;
    }

    public void addMoney(Double amount) {
        if (amount == null || amount <= 0) {
            throw new ResponseException(Error.INVALID_PARAMETER, "증가 금액은 0보다 커야");
        }
        this.playerMoney += amount;
    }
}
```

---

### 2. NoArgsConstructor(access = AccessLevel.PROTECTED) 사용 이유

#### JPA의 Entity 생성 메커니즘

```java
// JPA는 다음과 같이 엔티티를 생성함 (리플렉션)
Class<?> clazz = Class.forName("com.sk.skala.stockapi.data.table.Player");
Constructor<?> constructor = clazz.getDeclaredConstructor();  // 매개변수 없는 생성자
Object instance = constructor.newInstance();  // 객체 생성
```

JPA가 요구하는 조건: **매개변수 없는 생성자 필요**

#### 왜 public이 아닌 protected인가?

```java
// public NoArgsConstructor
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PUBLIC)  // ❌
public class Player {
    @Id
    private String playerId;
    private Double playerMoney;
}

// 누구나 접근 가능 → 데이터 무결성 깨짐
Player player = new Player();  // 아무 데이터 없이 생성
System.out.println(player.getPlayerId());  // null (위험!)
```

**JPA 내부 동작 (Proxy 생성)**

JPA는 lazy loading을 위해 Entity의 Proxy 클래스를 바이트코드 조작으로 생성:
```java
// JPA가 생성하는 프록시
public class Player$Proxy extends Player {
    public Player$Proxy() {
        super();  // 부모 생성자 호출 필수
    }
}

// protected면 상속 클래스에서 접근 가능
// private면 상속 클래스에서 접근 불가 (컴파일 오류)
```

#### 올바른 패턴

```java
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)  // ✓ JPA 전용
public class Player {
    @Id
    private String playerId;
    private Double playerMoney;

    // 비즈니스 로직용 생성자 (public)
    public Player(String playerId, Double playerMoney) {
        this.playerId = playerId;
        this.playerMoney = playerMoney;
    }
}

// JPA는 protected 생성자 사용
// 개발자는 public 생성자 사용
Player player = new Player("user123", 10000.0);
```

---

### 3. Setter 대신 의미 있는 비즈니스 메서드를 사용하는 이유

#### 패턴 비교

```java
// ❌ Setter 패턴 - 의도 모호
Player player = playerRepository.findById("user1").get();
player.setPlayerMoney(15000);  // 왜 변경?
playerRepository.save(player);
```

**문제**: 누가 읽어도 돈을 왜 변경하는지 알 수 없음. 급여인가? 보너스인가? 손실인가?

```java
// ✓ 비즈니스 메서드 패턴 - 의도 명확
Player player = playerRepository.findById("user1").get();
player.addMoney(5000);        // 돈 증가 (언제 사용: 상점 구매 환급)
player.subtractMoney(2000);   // 돈 감소 (언제 사용: 주식 매수)
player.updateMoney(15000);    // 돈 업데이트 (언제 사용: 관리자 설정)
playerRepository.save(player);
```

#### 추가 이점

**1. 유효성 검증 통합**
```java
// ❌ Setter만으로는 검증 불가
player.setPlayerMoney(-1000);  // 음수는 이상하지만... 아무도 못 막음!

// ✓ 비즈니스 메서드에 검증
public void subtractMoney(Double amount) {
    if (amount == null || amount <= 0) {
        throw new ResponseException(Error.INVALID_PARAMETER, "감소 금액은 0보다 커야");
    }
    if (this.playerMoney < amount) {
        throw new ResponseException(Error.INSUFFICIENT_FUNDS, "잔액 부족");
    }
    this.playerMoney -= amount;
}
```

**2. 도메인 모델의 자율성**
```java
// ❌ Service에서 모든 로직
public Response<Void> sellPlayerStock(...) {
    PlayerStock ps = playerStockRepository.findById(id).get();
    ps.setQuantity(ps.getQuantity() - quantity);  // Service에서 직접 조작
    Player player = ps.getPlayer();
    player.setPlayerMoney(player.getPlayerMoney() + totalPrice);  // Service에서 직접 조작
    // ...
}

// ✓ Entity가 스스로 처리
public Response<Void> sellPlayerStock(...) {
    PlayerStock ps = playerStockRepository.findById(id).get();
    ps.subtractQuantity(quantity);  // 도메인 로직
    Player player = ps.getPlayer();
    player.addMoney(totalPrice);     // 도메인 로직
    // Service는 오케스트레이션만
}
```

---

### 4. @ManyToOne vs @OneToMany

#### 연관관계 기본 개념

```
Player (1) ←→ (N) PlayerStock

한 명의 플레이어가 여러 주식을 보유
```

| 관계 | 다 쪽 (N) | 한 쪽 (1) |
|------|---------|---------|
| 주요 외래키 | PlayerStock (player_id) | Player |
| DB 테이블 | playerstock | player |
| Java 표현 | PlayerStock → Player | Player → List\<PlayerStock\> |

#### @ManyToOne (권장)

```java
@Entity
public class PlayerStock {
    @Id
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)  // ✓ 한 개 객체 참조
    @JoinColumn(name = "player_id")
    private Player player;  // 항상 하나의 Player
    
    private Integer quantity;
}

// 사용
PlayerStock ps = playerStockRepository.findById(1).get();
Player owner = ps.getPlayer();  // 즉시 접근, 추가 쿼리 불필요 (관계 설정된 쪽)
```

**장점**:
1. DB 설계와 일치 (외래키는 다 쪽에만)
2. 추가 업데이트 쿼리 없음
3. 지연 로딩 효율적

#### @OneToMany (특수한 경우에만)

```java
@Entity
public class Player {
    @Id
    private String playerId;
    
    @OneToMany(mappedBy = "player", fetch = FetchType.LAZY)  // ❌ 피함
    private List<PlayerStock> stocks = new ArrayList<>();  // 여러 개 객체 참조
}

// 사용
Player player = playerRepository.findById("user1").get();
List<PlayerStock> stocks = player.getStocks();  // 추가 쿼리 발생
```

**문제점**:
```java
// @OneToMany 사용 시 불필요한 UPDATE 발생
Player player = playerRepository.findById("user1").get();

// 1. stocks List에서 item 제거
player.getStocks().remove(0);  // N쪽 엔티티 제거

// JPA 동작 (문제!)
// 1) UPDATE playerstock SET player_id = NULL WHERE id = ?  (불필요!)
// 2) DELETE playerstock WHERE id = ?

// @ManyToOne 사용 시
PlayerStock ps = playerStockRepository.findById(1).get();
playerStockRepository.delete(ps);  // 한 번의 DELETE만 발생 ✓
```

#### 언제 @OneToMany를 사용하는가?

```java
// 예외: N쪽 엔티티 접근이 불필요한 경우
@Entity
public class Order {
    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL)
    private List<OrderItem> items;  // Order가 items를 완전히 소유
}

// OrderItem은 독립적으로 조회하지 않음
// Order를 조회할 때만 items를 가져옴
```

---

### 5. @ManyToOne(fetch = FetchType.LAZY) - 지연 로딩

#### 개념

```java
@Entity
public class PlayerStock {
    @ManyToOne(fetch = FetchType.LAZY)  // 즉시 로드 안 함
    @JoinColumn(name = "player_id")
    private Player player;  // Proxy 객체 (실제 데이터 미로드)
}
```

#### 동작 원리

```java
// 1. PlayerStock 로드 (player_id만 로드)
PlayerStock ps = playerStockRepository.findById(1).get();
// SQL: SELECT * FROM playerstock WHERE id = 1
// player: Proxy 객체 (실제 데이터 없음)

// 2. player 필드 접근 (이 때 쿼리 발생)
System.out.println(ps.getPlayer().getPlayerId());
// SQL: SELECT * FROM player WHERE id = ?
// 이제 실제 Player 데이터 로드됨

// 3. 같은 session에서 다시 접근 (쿼리 없음)
System.out.println(ps.getPlayer().getPlayerMoney());
// SQL: 발생 안 함 (캐시에서 가져옴)
```

#### 왜 지연 로딩을 사용하는가?

**시나리오 1: 불필요한 조인 회피**

```java
// ❌ EAGER (즉시 로딩)
@ManyToOne(fetch = FetchType.EAGER)
private Player player;

// 목록 조회 (1000개)
List<PlayerStock> stocks = playerStockRepository.findAll();
// SQL: SELECT ps.*, p.* FROM playerstock ps
//      LEFT JOIN player p ON ps.player_id = p.id
// 문제: 1000개 PlayerStock과 Player를 모두 로드 (필요 없을 수도)

// ✓ LAZY (지연 로딩)
@ManyToOne(fetch = FetchType.LAZY)
private Player player;

// 목록 조회
List<PlayerStock> stocks = playerStockRepository.findAll();
// SQL: SELECT * FROM playerstock LIMIT 10
// Player는 로드하지 않음

// Player가 필요한 항목만 접근할 때 로드
for (PlayerStock ps : stocks) {
    if (ps.getQuantity() > 100) {
        Player owner = ps.getPlayer();  // 여기서만 쿼리
    }
}
```

**시나리오 2: N+1 문제**

```java
// EAGER 사용 시
List<PlayerStock> stocks = playerStockRepository.findAll();
// SQL: SELECT ps.*, p.* FROM playerstock ps
//      LEFT JOIN player p ON ps.player_id = p.id
// 1개 쿼리로 끝남

// LAZY 사용 시 (부주의)
List<PlayerStock> stocks = playerStockRepository.findAll();
// SQL: SELECT * FROM playerstock  (1개)

for (PlayerStock ps : stocks) {
    Player player = ps.getPlayer();  // 1000개 항목 × 1쿼리 = 1000개 쿼리!
    // SQL: SELECT * FROM player WHERE id = ?  (1000번)
}
// 총 1001개 쿼리 (1 + N) → N+1 문제!
```

**해결: 필요한 데이터만 fetch join**

```java
@Query("SELECT ps FROM PlayerStock ps JOIN FETCH ps.player")
List<PlayerStock> findAllWithPlayer();

// SQL: SELECT ps.*, p.* FROM playerstock ps
//      INNER JOIN player p ON ps.player_id = p.id
// 장점: 1개 쿼리로 모두 로드
```

#### 트레이드오프

| EAGER | LAZY |
|-------|------|
| 즉시 로드 | 필요할 때만 로드 |
| 조인 쿼리 (무겁다) | 추가 쿼리 가능 |
| N+1 회피 | N+1 위험 |
| 메모리 사용 많음 | 메모리 효율적 |

#### 이 프로젝트의 선택

```java
// PlayerStock에서 Player 참조
@ManyToOne(fetch = FetchType.LAZY)
@JoinColumn(name = "player_id")
private Player player;

// 이유:
// 1. PlayerStock 조회 시 Player를 항상 필요한 게 아님
// 2. 조회 시에만 fetch join으로 명시적 로드
// 3. 목록 조회는 PlayerStock 정보만 필요
```

---

## DTO 단 학습 내용

### 1. Entity를 API 응답으로 직접 쓰면 안 되는 이유

#### 문제점 1: 보안 정보 노출

```java
// ❌ Entity를 직접 응답
@GetMapping("/{playerId}")
public Response<Player> getPlayer(@PathVariable String playerId) {
    Player player = playerRepository.findById(playerId).get();
    return Response.success(player);
}

// API 응답
{
    "playerId": "user123",
    "playerPassword": "hashed_password_1234",  // ❌ 노출!
    "playerMoney": 10000
}

// ✓ DTO로 응답
@GetMapping("/{playerId}")
public Response<PlayerLoginDto> getPlayer(@PathVariable String playerId) {
    Player player = playerRepository.findById(playerId).get();
    return Response.success(PlayerLoginDto.from(player.getPlayerId(), player.getPlayerMoney()));
}

// API 응답
{
    "playerId": "user123",
    "playerMoney": 10000
}
```

#### 문제점 2: Lazy 로딩 프록시 직렬화 오류

```java
@Entity
public class PlayerStock {
    @ManyToOne(fetch = FetchType.LAZY)
    private Player player;  // Proxy 객체
    
    private Integer quantity;
}

// ❌ Entity 직접 응답
@GetMapping("/{id}")
public Response<PlayerStock> getPlayerStock(@PathVariable Long id) {
    PlayerStock ps = playerStockRepository.findById(id).get();
    return Response.success(ps);  // player는 Proxy
}

// Jackson 직렬화
// 1. PlayerStock 필드 순회
// 2. player 필드 접근 (Proxy 객체)
// 3. Proxy는 Jackson이 처리 불가능 → LazyInitializationException!
// "could not initialize proxy - no Session"

// 왜? Jackson이 player.getClass()를 호출하면 Proxy의 타입이 나오는데,
//    이는 HibernateProxy이므로 JSON 변환 불가
```

**상세 흐름**:
```java
// @Transactional 내에서는 정상 (Session 유지)
@Transactional
public PlayerStock getAndSerialize() {
    PlayerStock ps = playerStockRepository.findById(1).get();
    return ps;  // 트랜잭션 내에서 반환
}

// 하지만 Controller 응답 시점에는 @Transactional 종료됨
@GetMapping("/{id}")
public Response<PlayerStock> get(@PathVariable Long id) {
    PlayerStock ps = playerStockRepository.findById(id).get();
    return Response.success(ps);
    // 이 시점에 Jackson이 ps를 직렬화하려 하면
    // player proxy를 건드려서 오류 발생
}
```

**DTO로 해결**:
```java
public record PlayerStockDto(
    Long stockId,
    String stockName,
    Double stockPrice,
    Integer quantity
) {}

// Service에서 명시적 변환
@Transactional(readOnly = true)
public Response<PlayerStockDto> getPlayerStock(Long id) {
    PlayerStock ps = playerStockRepository.findById(id).get();
    
    // 트랜잭션 내에서 필요한 데이터만 로드
    PlayerStockDto dto = new PlayerStockDto(
        ps.getStock().getId(),    // 이 순간 Stock proxy 로드됨
        ps.getStock().getStockName(),
        ps.getStock().getStockPrice(),
        ps.getQuantity()
    );
    
    return Response.success(dto);  // DTO는 순수 데이터 (Proxy 없음)
}
```

#### 문제점 3: 추가 필드 노출 위험

```java
// Entity에 audit 필드 추가
@Entity
public class Stock {
    @Id
    private Long id;
    
    private String stockName;
    private Double stockPrice;
    
    @CreationTimestamp
    private LocalDateTime createdAt;  // 내부용 (API에서 노출 X)
    
    @UpdateTimestamp
    private LocalDateTime updatedAt;  // 내부용
    
    private String adminNotes;  // 기밀 정보
}

// ❌ Entity 직접 응답 → 모든 필드 노출
@GetMapping("/{id}")
public Response<Stock> getStock(@PathVariable Long id) {
    Stock stock = stockRepository.findById(id).get();
    return Response.success(stock);  // 모든 필드가 JSON에 포함됨!
}

// ✓ DTO로 제어
public record StockResponse(
    Long id,
    String stockName,
    Double stockPrice
) {}

@GetMapping("/{id}")
public Response<StockResponse> getStock(@PathVariable Long id) {
    Stock stock = stockRepository.findById(id).get();
    return Response.success(
        new StockResponse(stock.getId(), stock.getStockName(), stock.getStockPrice())
    );  // 필요한 필드만 포함
}
```

---

### 2. DTO를 Record (Java 17+)로 선언해야 하는 이유

#### Record 개념

Java 17+에서 도입된 **데이터 전달 전용 불변 클래스**:

```java
// ❌ 전통적인 DTO (보일러플레이트 코드)
public class StockCreateRequest {
    private String stockName;
    private Double stockPrice;
    
    public StockCreateRequest(String stockName, Double stockPrice) {
        this.stockName = stockName;
        this.stockPrice = stockPrice;
    }
    
    public String getStockName() {
        return stockName;
    }
    
    public Double getStockPrice() {
        return stockPrice;
    }
    
    @Override
    public equals(Object o) { /* ... */ }
    
    @Override
    public hashCode() { /* ... */ }
    
    @Override
    public toString() { /* ... */ }
}

// ✓ Record로 선언 (간결함)
public record StockCreateRequest(
    String stockName,
    Double stockPrice
) {}

// 자동으로 제공:
// - 불변 필드 (final)
// - Constructor
// - Getter (getStockName 아닌 stockName())
// - equals()
// - hashCode()
// - toString()
```

#### Record의 장점

**1. 코드 간결함**
```java
// 줄 수 비교
// POJO: 50줄
// @Data + Lombok: 10줄
// Record: 2줄
```

**2. 불변성 보장**
```java
public record StockCreateRequest(String stockName, Double stockPrice) {}

StockCreateRequest req = new StockCreateRequest("Apple", 150.0);
// req.stockName = "Microsoft";  // ❌ 컴파일 오류 (setter 없음)

// setter가 없으므로 스레드 안전
```

**3. API 계약 명확**
```java
// Record = 이 객체는 데이터 전달만 목적
// 메서드 없음 = 비즈니스 로직 없음

public record PlayerCreateRequest(String playerId, String playerPassword) {}

// vs

public class PlayerCreateRequest {
    // getter/setter로 도배
    // 누군가 이 클래스에 메서드를 추가해도 됨?
    // 혼란 발생
}
```

#### Record vs @Data 비교

| 측면 | Record | @Data |
|------|--------|-------|
| 불변성 | 강제 | 선택적 |
| Setter | 없음 | 자동 생성 |
| 목적 | 데이터 전달만 | 다목적 |
| 상속 | 불가 (Object만) | 가능 |
| IDE 지원 | 완벽 | 완벽 |

#### 이 프로젝트의 패턴

```java
// Request DTO는 Record (불변 데이터)
public record StockCreateRequest(
    String stockName,
    Double stockPrice
) {}

// Response DTO도 Record (읽기 전용 응답)
public record PlayerLoginDto(
    String playerId,
    Double playerMoney
) {
    public static PlayerLoginDto from(String playerId, Double playerMoney) {
        return new PlayerLoginDto(playerId, playerMoney);
    }
}

// 하지만 Spring Form Binding이 필요한 경우는 @Getter/@Setter
// (record는 setter가 없으므로 POST 바디 바인딩 때 문제 가능)
@Getter
@Setter
public class StockOrder {  // 요청 본문 바인딩용
    private Long stockId;
    private Integer quantity;
}
```

---

### 3. Request DTO와 Response DTO를 분리해야 하는 이유

#### 예시

```java
// ❌ 하나의 DTO로 요청/응답 모두 처리
public record PlayerDto(
    String playerId,
    String playerPassword,  // 요청 시 필수, 응답 시 노출 X
    Double playerMoney,     // 요청 시 선택, 응답 시 필수
    LocalDateTime createdAt // 요청 시 불가, 응답 시만
) {}

@PostMapping
public Response<PlayerDto> createPlayer(@RequestBody PlayerDto request) {
    // request.createdAt은 null (요청에서 보낼 수 없음)
    // 응답의 playerPassword는 노출 위험
}

@GetMapping("/{id}")
public Response<PlayerDto> getPlayer(@PathVariable String id) {
    // 응답에 playerPassword가 포함됨 (보안 문제)
}
```

**문제점**:
1. **필드 의미 모호** - 어떤 필드는 요청/응답에 사용되나?
2. **보안 위험** - 응답에 민감한 필드 포함 가능
3. **버전 관리 어려움** - 요청 형식이 바뀌면 응답도 바뀜
4. **검증 로직 혼재** - Request 검증과 Response 포맷이 뒤섞임

#### ✓ 올바른 패턴

```java
// Request DTO (POST 요청)
public record PlayerCreateRequest(
    String playerId,
    String playerPassword
) {}

// Response DTO (API 응답)
public record PlayerLoginDto(
    String playerId,
    Double playerMoney
) {}

// 각각의 역할 명확
@PostMapping
public Response<Player> createPlayer(@RequestBody PlayerCreateRequest request) {
    // request에는 playerId, playerPassword만
    // 응답은 Player 엔티티 (실제로는 PlayerLoginDto가 낫지만)
}

@GetMapping("/{id}")
public Response<PlayerLoginDto> getPlayer(@PathVariable String id) {
    Player player = playerRepository.findById(id).get();
    // PlayerLoginDto로 변환 (playerPassword 노출 X)
    return Response.success(
        PlayerLoginDto.from(player.getPlayerId(), player.getPlayerMoney())
    );
}
```

#### 추가 이점

**1. API 버전 관리**
```java
// v1 응답
public record PlayerDtoV1(String playerId, Double playerMoney) {}

// v2 응답 (필드 추가)
public record PlayerDtoV2(
    String playerId,
    Double playerMoney,
    Integer totalTransactions,  // 신규
    LocalDateTime lastLogin      // 신규
) {}

// 기존 클라이언트는 v1 사용, 새 클라이언트는 v2 사용
@GetMapping("/v1/{id}")
public Response<PlayerDtoV1> getPlayerV1(...) { }

@GetMapping("/v2/{id}")
public Response<PlayerDtoV2> getPlayerV2(...) { }
```

**2. Update 시 응답 제어**
```java
// Request: 수정할 필드만
public record PlayerUpdateRequest(Double playerMoney) {}

// Response: 수정 후 전체 정보
public record PlayerResponse(
    String playerId,
    Double playerMoney,
    Integer level,
    LocalDateTime updatedAt
) {}

@PutMapping("/{id}")
public Response<PlayerResponse> updatePlayer(
    @PathVariable String id,
    @RequestBody PlayerUpdateRequest request
) {
    // 업데이트 로직
    // Response는 최신 상태 반영
}
```

---

### 4. Validation을 DTO 단에서 해야 하는 이유

#### Controller에서 검증하면 안 되는 이유

```java
// ❌ Controller에서 검증
@PostMapping
public Response<Stock> createStock(@RequestBody StockCreateRequest request) {
    // 검증 로직이 Controller에 섞여있음
    if (request.stockName() == null || request.stockName().trim().isEmpty()) {
        return Response.error(400, "stockName is required");
    }
    if (request.stockPrice() == null || request.stockPrice() <= 0) {
        return Response.error(400, "stockPrice must be positive");
    }
    
    Stock stock = new Stock(request.stockName(), request.stockPrice());
    return Response.success(stockRepository.save(stock));
}

// 문제점:
// 1. 검증 로직 반복 (모든 엔드포인트에서)
// 2. Controller가 비대해짐
// 3. 다른 계층에서 같은 DTO를 받으면 검증 안 함
// 4. 테스트하기 어려움
```

#### Service에서 검증하면 안 되는 이유

```java
// ❌ Service에서 검증
@Service
public class StockService {
    public Response<Stock> createStock(StockCreateRequest request) {
        if (request.stockName() == null) {
            throw new ParameterException("stockName");
        }
        // ... 비즈니스 로직
    }
}

// 문제점:
// 1. API 바운더리에서 검증 실패 (불필요한 계층 통과)
// 2. REST의 원칙: 빨리 실패 (fail fast)
// 3. 성능: 불필요한 DB 조회 가능
```

#### ✓ DTO 단에서 검증 (Spring Validation)

```java
// 현재 프로젝트 패턴
public record StockCreateRequest(
    String stockName,
    Double stockPrice
) {}

// Service에서 검증
@Service
@Transactional
public class StockService {
    private void validateStockRequest(StockCreateRequest request) {
        if (request == null || request.stockName() == null || 
            request.stockName().trim().isEmpty()) {
            throw new ParameterException("stockName");
        }
        if (request.stockPrice() == null || request.stockPrice() <= 0) {
            throw new ParameterException("stockPrice");
        }
    }
    
    public Response<Stock> createStock(StockCreateRequest request) {
        validateStockRequest(request);  // DTO 검증
        Stock stock = new Stock(request.stockName(), request.stockPrice());
        return Response.success(stockRepository.save(stock));
    }
}

// 또는 @Valid + Spring Validation (더 선호)
public record StockCreateRequest(
    @NotBlank(message = "stockName is required")
    String stockName,
    
    @NotNull(message = "stockPrice is required")
    @Positive(message = "stockPrice must be positive")
    Double stockPrice
) {}

@PostMapping
public Response<Stock> createStock(
    @Valid @RequestBody StockCreateRequest request
) {
    // 자동 검증 + MethodArgumentNotValidException → GlobalExceptionHandler 처리
}
```

#### 검증 계층의 이점

**1. 중앙화된 검증**
```java
// 어디서나 같은 검증
StockCreateRequest req = new StockCreateRequest("Apple", 150.0);

// Web Controller
@PostMapping
public Response createStock(@Valid StockCreateRequest req) { }

// Message Queue Consumer
public void processStockEvent(StockCreateRequest req) {
    // 같은 검증 적용됨
}
```

**2. 재사용성**
```java
// 여러 엔드포인트에서 재사용
@PostMapping("/batch")
public Response createMultipleStocks(
    @Valid List<StockCreateRequest> requests  // 리스트 검증도 자동
) { }

@PostMapping("/async")
public Response createStockAsync(@Valid StockCreateRequest request) { }
```

**3. 명확한 API 계약**
```java
// DTO 클래스만 봐도 어떤 필드가 필수인지 알 수 있음
public record PlayerCreateRequest(
    @NotBlank(message = "playerId required")
    String playerId,
    
    @Size(min = 4, message = "password must be 4+ chars")
    String playerPassword
) {}

// API 문서 자동 생성 가능 (Springdoc OpenAPI)
```

---

### 5. Response DTO는 @Valid가 불필요한 이유

```java
// ❌ Response에 @Valid (불필요)
@PostMapping
public Response<PlayerLoginDto> loginPlayer(@Valid @RequestBody PlayerSession session) {
    Player player = playerRepository.findById(session.getPlayerId()).get();
    
    // 응답 DTO (우리가 생성하는 데이터)
    PlayerLoginDto response = PlayerLoginDto.from(
        player.getPlayerId(),
        player.getPlayerMoney()
    );
    
    return Response.success(response);
    // response의 내용이 잘못되었을 수 있나? 아니다. 우리가 만들었으니 이미 올바름!
}
```

#### 이유

| Request DTO | Response DTO |
|-------------|--------------|
| **클라이언트**가 보냄 | **서버**가 생성 |
| 검증 필요 (신뢰할 수 없음) | 검증 불필요 (우리가 통제) |
| 공격 벡터 가능 | 안전함 |
| @Valid 적용 | @Valid 불필요 |

```java
// Request: 신뢰할 수 없음
public record StockCreateRequest(
    @NotBlank
    String stockName,
    
    @NotNull
    @Positive
    Double stockPrice
) {}

// 누가 보냄?
// - 클라이언트 (신뢰할 수 없음)
// - API 스펙을 따르지 않을 수 있음
// - 악의적 입력 가능


// Response: 신뢰할 수 있음
public record StockResponse(
    Long id,
    String stockName,
    Double stockPrice
) {}

// 누가 생성?
// - 서버 (우리 코드)
// - 반드시 올바른 데이터만 포함
// - 검증할 필요 없음
```

#### 예외: Response 내부 객체

```java
// 만약 Response 안에 리스트가 있다면?
public record PlayerStockListDto(
    String playerId,
    Double playerMoney,
    List<PlayerStockDto> stocks  // 복잡한 구조
) {}

// @Valid는 여전히 불필요 (우리가 만든 데이터)
// 하지만 테스트에서 검증은 필요
@Test
public void testPlayerStockListDto() {
    var dto = new PlayerStockListDto(
        "user1",
        10000.0,
        List.of(new PlayerStockDto(...))
    );
    
    // 데이터 무결성 확인
    assertNotNull(dto.playerId());
    assertNotEmpty(dto.stocks());
}
```

---

## Repository 단 학습 내용

### 1. JpaRepository의 쿼리 메서드 작동 원리

#### 메서드명 기반 쿼리 생성

```java
public interface StockRepository extends JpaRepository<Stock, Long> {
    // 메서드명만으로 쿼리 자동 생성
    Optional<Stock> findByStockName(String stockName);
}

// Spring이 런타임에 이를 해석해서 생성:
// SELECT * FROM stock WHERE stock_name = ?
```

**작동 원리**:
1. JpaRepository 상속
2. Spring이 메서드 분석 (Reflection)
3. 메서드명 파싱: find(조회) + By(조건) + StockName(필드)
4. JPQL 생성 및 컴파일
5. 메서드 호출 시 실행

#### JpaRepository의 기본 메서드

```java
public interface JpaRepository<T, ID> extends PagingAndSortingRepository<T, ID> {
    // CRUD 메서드 (직접 추가 안 해도 사용 가능)
    List<T> findAll();                      // 모든 엔티티 조회
    T save(T entity);                       // 저장/업데이트
    Optional<T> findById(ID id);            // ID로 조회
    void delete(T entity);                  // 삭제
    long count();                           // 개수
    boolean existsById(ID id);              // 존재 여부
}

// 이미 구현되어있어서 Repository에서 정의할 필요 없음
public interface StockRepository extends JpaRepository<Stock, Long> {
    // findAll() 등은 JpaRepository에서 상속받아서 바로 사용 가능
}

// 사용
List<Stock> stocks = stockRepository.findAll();
```

#### 직접 추가해야 하는 경우

```java
public interface StockRepository extends JpaRepository<Stock, Long> {
    // 특정 필드로 조회 (메서드명으로 쿼리 생성)
    Optional<Stock> findByStockName(String stockName);
    
    // 복잡한 조건 (JPQL 필요)
    @Query("SELECT s FROM Stock s WHERE s.stockPrice > :minPrice ORDER BY s.stockPrice DESC")
    List<Stock> findExpensiveStocks(@Param("minPrice") Double minPrice);
    
    // 네이티브 SQL
    @Query(value = "SELECT * FROM stock WHERE stock_name LIKE %:name%", nativeQuery = true)
    List<Stock> searchByName(@Param("name") String name);
}

// 사용
Optional<Stock> apple = stockRepository.findByStockName("Apple");
List<Stock> expensive = stockRepository.findExpensiveStocks(100.0);
```

#### 이 프로젝트의 Repository

```java
// PlayerStockRepository
public interface PlayerStockRepository extends JpaRepository<PlayerStock, Long> {
    // 메서드명 기반: 플레이어의 모든 주식 조회
    List<PlayerStock> findByPlayer_PlayerId(String playerId);
    
    // 메서드명 기반: 특정 플레이어의 특정 주식 조회
    Optional<PlayerStock> findByPlayerAndStock(Player player, Stock stock);
}

// findAll() 등은 JpaRepository에서 상속받아 바로 사용
List<PlayerStock> allStocks = playerStockRepository.findAll();
```

---

### 2. Repository 반환값에서 Optional을 사용해야 하는 이유

#### 문제점: null 참조

```java
// ❌ Optional 미사용
public interface StockRepository extends JpaRepository<Stock, Long> {
    Stock findByStockName(String name);  // 없으면 null 반환
}

// 사용
Stock stock = stockRepository.findByStockName("NonExistent");
System.out.println(stock.getStockPrice());  // NullPointerException!

// 누군가는 findByStockName() 결과가 null일 수 있다는 걸 알아야 함
// 하지만 코드만 봐서는 알기 어려움
```

#### ✓ Optional 사용

```java
public interface StockRepository extends JpaRepository<Stock, Long> {
    Optional<Stock> findByStockName(String name);  // 결과가 없을 수 있음을 명시
}

// 사용
Optional<Stock> stock = stockRepository.findByStockName("NonExistent");
if (stock.isPresent()) {
    System.out.println(stock.get().getStockPrice());
} else {
    System.out.println("Stock not found");
}

// 더 나은 방법
stock.ifPresent(s -> System.out.println(s.getStockPrice()));
```

#### Optional의 API

```java
Optional<Stock> stock = stockRepository.findByStockName("Apple");

// 1. isPresent() - 존재 확인
if (stock.isPresent()) { }

// 2. get() - 값 추출 (없으면 NoSuchElementException)
Stock s = stock.get();

// 3. orElse() - 기본값
Stock s = stock.orElse(null);
Stock s = stock.orElse(new Stock("Unknown", 0.0));

// 4. orElseThrow() - 예외 발생 (이 프로젝트의 패턴)
Stock s = stock.orElseThrow(
    () -> new ResponseException(Error.DATA_NOT_FOUND, "Stock not found")
);

// 5. ifPresentOrElse() - 있을 때/없을 때
stock.ifPresentOrElse(
    s -> System.out.println(s.getStockName()),
    () -> System.out.println("Not found")
);

// 6. map() - 변환
Optional<String> name = stock.map(Stock::getStockName);

// 7. filter() - 조건 필터
Optional<Stock> expensiveStock = stock
    .filter(s -> s.getStockPrice() > 100);
```

#### 이 프로젝트의 패턴

```java
@Transactional
public Response<Stock> getStockById(Long id) {
    Stock stock = stockRepository.findById(id)
        .orElseThrow(() -> new ResponseException(
            Error.DATA_NOT_FOUND, 
            "Stock not found"
        ));
    return Response.success(stock);
}
```

**왜 orElseThrow()를 사용하는가?**
1. **지연 평가**: Optional이 비어있을 때만 람다 실행 (예외 객체 생성 비용 절감)
2. **명확한 의도**: 데이터가 없으면 무조건 예외 발생
3. **조기 반환**: 예외 처리는 GlobalExceptionHandler에서

---

### 3. PlayerStockRepository.findByPlayer_PlayerId() - 속성 경로 순회

#### 메서드 해석

```java
List<PlayerStock> findByPlayer_PlayerId(String playerId);
```

**파싱**:
1. `find` → 조회 메서드
2. `By` → 조건 시작
3. `Player` → PlayerStock의 **필드명** (실제 쿼리 생성에 영향 없음)
4. `_` → 구분자 (필드 경로 표시)
5. `PlayerId` → Player 엔티티의 **필드명** (실제 조건)

**생성되는 SQL**:
```sql
SELECT ps.* FROM playerstock ps
JOIN player p ON ps.player_id = p.id
WHERE p.player_id = ?
```

#### 다양한 표현

```java
public interface PlayerStockRepository extends JpaRepository<PlayerStock, Long> {
    // 모두 동일한 쿼리 생성
    List<PlayerStock> findByPlayer_PlayerId(String playerId);
    List<PlayerStock> findByPlayerPlayerId(String playerId);      // _ 없어도 됨
    List<PlayerStock> findStocksByPlayer_PlayerId(String playerId); // 가운데 Subject
    List<PlayerStock> findAllByPlayer_PlayerId(String playerId);     // find + All
}

// 모두 같은 SQL 생성
// SELECT * FROM playerstock WHERE player_id = ?
```

#### 복잡한 경로 순회

```java
@Entity
public class PlayerStock {
    @ManyToOne
    private Player player;
    
    @ManyToOne
    private Stock stock;
}

// 깊이 있는 경로도 가능
public interface PlayerStockRepository extends JpaRepository<PlayerStock, Long> {
    // Player의 playerId로 조회
    List<PlayerStock> findByPlayer_PlayerId(String playerId);
    
    // Stock의 stockName으로 조회
    List<PlayerStock> findByStock_StockName(String stockName);
    
    // Player의 playerId와 Stock의 stockName으로 조회
    Optional<PlayerStock> findByPlayer_PlayerIdAndStock_StockName(
        String playerId, 
        String stockName
    );
}
```

---

### 4. JPA 쿼리 메서드 작명 가이드

#### 기본 구조

```
[ 조회동작 ]  [ Subject ]  By  [ Predicate ]

find         (선택사항)     By   (필수)
get
read
query
search
```

#### Subject (find와 By 사이) - 가독성용

```java
// 모두 같은 쿼리 생성 (WHERE player_id = ?)
List<PlayerStock> findByPlayer_PlayerId(String playerId);
List<PlayerStock> findStocksByPlayer_PlayerId(String playerId);
List<PlayerStock> findAllStocksByPlayer_PlayerId(String playerId);
List<PlayerStock> findPlayerStocksByPlayer_PlayerId(String playerId);

// 개발자 가독성만 다름 (Subject는 쿼리에 영향 없음)
// 권장: 비즈니스 의미에 맞게 선택
```

#### Predicate (By 이후) - 실제 쿼리 조건

```java
// 기본 비교
Optional<Stock> findById(Long id);                           // WHERE id = ?
Optional<Stock> findByStockName(String name);                // WHERE stock_name = ?

// 비교 연산자
List<Stock> findByStockPriceGreaterThan(Double price);       // WHERE stock_price > ?
List<Stock> findByStockPriceLessThan(Double price);          // WHERE stock_price < ?
List<Stock> findByStockPriceGreaterThanEqual(Double price);  // WHERE stock_price >= ?
List<Stock> findByStockPriceBetween(Double min, Double max); // WHERE stock_price BETWEEN ? AND ?

// 문자열 패턴
List<Stock> findByStockNameContaining(String name);          // WHERE stock_name LIKE %name%
List<Stock> findByStockNameStartingWith(String prefix);      // WHERE stock_name LIKE prefix%
List<Stock> findByStockNameEndingWith(String suffix);        // WHERE stock_name LIKE %suffix

// 다중 조건
List<PlayerStock> findByPlayer_PlayerIdAndStock_Id(
    String playerId, 
    Long stockId
);                                                            // WHERE player_id = ? AND stock_id = ?

List<Stock> findByStockNameOrStockPrice(String name, Double price);  // WHERE stock_name = ? OR stock_price = ?

// Null 체크
List<Stock> findByAdminNotesIsNull();                        // WHERE admin_notes IS NULL
List<Stock> findByAdminNotesIsNotNull();                     // WHERE admin_notes IS NOT NULL

// 정렬
List<Stock> findByStockPriceGreaterThan(Double price, Sort sort);  // with sorting

// 페이징
Page<Stock> findByStockPriceGreaterThan(Double price, Pageable page);  // with pagination

// Distinct
List<Player> findDistinctByPlayerMoney(Double money);        // SELECT DISTINCT
```

#### 가독성 비교

```java
// ❌ 다른 의도인데 혼동 가능
List<PlayerStock> findByPlayer_PlayerId(String playerId);
List<PlayerStock> findByPlayerPlayerId(String playerId);
// 첫 번째가 명확함

// ❌ 너무 길면 복잡
List<PlayerStock> findStocksByPlayer_PlayerIdAndStock_StockNameOrQuantityGreaterThan(
    String playerId, 
    String stockName, 
    Integer quantity
);

// ✓ 복잡하면 @Query 사용
@Query("SELECT ps FROM PlayerStock ps " +
       "WHERE ps.player.playerId = :playerId " +
       "AND (ps.stock.stockName = :stockName OR ps.quantity > :quantity)")
List<PlayerStock> findPlayerStocksWithFilter(
    @Param("playerId") String playerId,
    @Param("stockName") String stockName,
    @Param("quantity") Integer quantity
);
```

---

## Service 단 관련 학습 내용

### 1. Pagination의 필요성과 구현

#### 페이징이 필요한 이유

```java
// ❌ 페이징 없이 모든 데이터 조회
@GetMapping("/stocks")
public Response<List<Stock>> getAllStocks() {
    List<Stock> stocks = stockRepository.findAll();  // 100만 개?
    return Response.success(stocks);
}

// 문제점:
// 1. 메모리 오버플로우 (100만 개 객체 로드)
// 2. 네트워크 대역폭 낭비 (100MB 이상 응답)
// 3. 응답 지연 (사용자 기다림)
// 4. DB 부하 증가
```

**예**: 유튜브, 네이버, 인스타그램 모두 페이징 사용
- 유튜브: "동영상 150만 개 다 보낼까?" X → "처음 20개만" O
- 인스타그램: 무한 스크롤도 실제로는 청크 단위 페이징

#### 페이징 구현 요소

**요청 정보 (Pageable)**:
```java
@GetMapping("/stocks")
public Response<PagedList> getAllStocks(
    @RequestParam(defaultValue = "0") Integer offset,
    @RequestParam(defaultValue = "10") Integer count
) {
    // offset: 첫 항목의 위치 (0부터 시작)
    // count: 한 번에 몇 개를 가져올 것인가
    // 예: offset=0, count=10 → 첫 번째 페이지 (항목 1-10)
    // 예: offset=10, count=10 → 두 번째 페이지 (항목 11-20)
}
```

**결과 (Page + PagedList)**:
```java
// JPA의 Page (내부용)
Page<Stock> page = stockRepository.findAll(
    PageRequest.of(0, 10)  // 0번째 페이지, 페이지당 10개
);
// - getTotalElements() : 총 항목 수 (DB COUNT 쿼리)
// - getContent() : 현재 페이지의 데이터
// - getNumber() : 현재 페이지 번호
// - getTotalPages() : 총 페이지 수

// API 응답 (PagedList DTO)
public class PagedList {
    long total;              // 총 항목 수
    int count;              // 현재 페이지의 항목 수
    int offset;             // 요청한 offset
    List<?> list;           // 실제 데이터
}
```

#### 이 프로젝트의 페이징 구현

```java
// StockService
@Transactional(readOnly = true)
public Response<PagedList> getAllStocks(Integer offset, Integer count) {
    // 1. Pageable 생성
    Pageable pageable = PageRequest.of(offset / count, count);
    
    // 2. 페이징 조회
    Page<Stock> page = stockRepository.findAll(pageable);
    
    // 3. PagedList DTO로 변환
    PagedList pagedList = PaginationTool.toPagedList(page, offset);
    
    return Response.success(pagedList);
}

// 클라이언트 요청 예시
GET /api/stocks/list?offset=0&count=10  → 첫 페이지
GET /api/stocks/list?offset=10&count=10 → 두 번째 페이지
GET /api/stocks/list?offset=20&count=10 → 세 번째 페이지
```

#### Page를 쓰면 안 되는 경우: 무한 스크롤

```java
// ❌ Page 기반 무한 스크롤 (비효율)
// 매 요청마다 COUNT 쿼리 실행
SELECT COUNT(*) FROM stock;  // 시간 낭비 (읽기만 필요)

// ✓ Cursor 기반 무한 스크롤 (효율)
// 마지막 항목의 ID로 다음 항목 조회
SELECT * FROM stock WHERE id > ? LIMIT 11
// 단순 비교 쿼리만 발생

public interface StockRepository extends JpaRepository<Stock, Long> {
    // id보다 큰 항목들 조회 (cursor-based)
    List<Stock> findByIdGreaterThanOrderByIdAsc(Long id, Pageable pageable);
}

// 사용
List<Stock> items = stockRepository.findByIdGreaterThanOrderByIdAsc(
    lastId,  // 마지막 항목의 ID
    PageRequest.of(0, 11)  // 11개 조회 (10개 + 1개 더 있는지 확인)
);

// 응답
{
    "items": [...10개...],
    "hasMore": items.size() == 11,  // 다음 페이지가 있는가?
    "nextCursor": items.get(9).getId()  // 다음 요청의 cursor
}
```

---

### 2. Optional과 orElseThrow의 람다 함수 사용

#### orElseThrow 문법

```java
// Optional이 비어있으면 예외 발생
Optional<Stock> stock = stockRepository.findById(id);

// 1. 예외 객체를 직접 전달 (❌ 문제)
stock.orElseThrow(new ResponseException(Error.DATA_NOT_FOUND, "Not found"));
// 문제: stock이 있어도 예외 객체가 생성됨 (메모리/성능 낭비)

// 2. 람다 함수로 전달 (✓ 올바름)
stock.orElseThrow(
    () -> new ResponseException(Error.DATA_NOT_FOUND, "Not found")
);
// 이점: Optional이 비어있을 때만 람다 실행 (예외 객체 생성)
```

#### 왜 람다를 사용하는가? (지연 평가)

**Exception 생성 비용**:
```java
new ResponseException(Error.DATA_NOT_FOUND, "Not found");
// 1. Stack trace 캡처 (느림)
//    - 현재 실행 스택 모두 기록
//    - 파일명, 라인 번호, 메서드명 등 포함
// 2. 메시지 생성
// 3. 객체 할당

// 결론: 예외 생성은 비용이 많이 들어감
```

**비교**:
```java
// ❌ 비효율 (100명 중 99명이 stock을 찾음)
for (int i = 1; i <= 100; i++) {
    Optional<Stock> stock = stockRepository.findById((long)i);
    Stock s = stock.orElseThrow(
        new ResponseException(Error.DATA_NOT_FOUND, "")  // 100번 생성!
    );
}
// 100개 예외 객체 생성되지만 대부분 버려짐

// ✓ 효율 (필요할 때만 생성)
for (int i = 1; i <= 100; i++) {
    Optional<Stock> stock = stockRepository.findById((long)i);
    Stock s = stock.orElseThrow(
        () -> new ResponseException(Error.DATA_NOT_FOUND, "")
    );
    // Optional이 비었을 때만 예외 생성
}
// 1개 예외 객체만 생성됨 (101번째 조회 시)
```

#### 이 프로젝트의 패턴

```java
@Transactional(readOnly = true)
public Response<Stock> getStockById(Long id) {
    Stock stock = stockRepository.findById(id)
        .orElseThrow(
            () -> new ResponseException(
                Error.DATA_NOT_FOUND, 
                "Stock with id " + id + " not found"
            )
        );
    return Response.success(stock);
}

// Optional이 비어있으면:
// 1. 람다 함수 실행 (이 시점에만)
// 2. ResponseException 객체 생성
// 3. 예외 발생
// 4. GlobalExceptionHandler에서 처리 → JSON 응답
```

---

### 3. @Id @GeneratedValue와 Request DTO

#### 문제 상황

```java
@Entity
public class Stock {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)  // DB가 자동 생성
    private Long id;
    
    private String stockName;
    private Double stockPrice;
}

// ❌ Request DTO에 id 포함
public record StockCreateRequest(
    Long id,              // 문제!
    String stockName,
    Double stockPrice
) {}

@PostMapping
public Response<Stock> createStock(@RequestBody StockCreateRequest request) {
    Stock stock = new Stock(
        request.id(),           // 1. 클라이언트가 보낸 id 사용
        request.stockName(),
        request.stockPrice()
    );
    return Response.success(stockRepository.save(stock));
}
```

**발생하는 문제들**:

**1. ID 충돌 위험**
```java
// 클라이언트가 보낸 요청
POST /stocks
{
    "id": 9999,  // ❌ 이미 존재하는 ID?
    "stockName": "Hack",
    "stockPrice": 1.0
}

// 결과: 기존 Stock이 수정될 수도, 오류 발생할 수도
// DB 무결성 문제 발생
```

**2. 보안 문제**
```java
// 클라이언트가 임의로 ID 생성
POST /stocks
{
    "id": 1000000,  // 임의로 큰 ID 설정
    "stockName": "Spam",
    "stockPrice": 0.01
}

// 시스템의 시퀀스(sequence) 값이 꼬일 수 있음
```

**3. ID 생성 전략 무시**
```java
// @GeneratedValue가 선언되었는데, 클라이언트가 id를 줌
// ORM의 자동 ID 생성 로직이 제대로 작동하지 않음
```

#### ✓ 올바른 패턴: Request DTO에서 id 제거

```java
// Request DTO (id 필드 없음)
public record StockCreateRequest(
    String stockName,
    Double stockPrice
) {}

@PostMapping
public Response<Stock> createStock(@RequestBody StockCreateRequest request) {
    Stock stock = new Stock(request.stockName(), request.stockPrice());
    // id는 DB가 자동 생성 (@GeneratedValue)
    
    Stock saved = stockRepository.save(stock);
    return Response.success(saved);
}

// 클라이언트 요청
POST /stocks
{
    "stockName": "Apple",
    "stockPrice": 150.0
}

// 응답
{
    "id": 1,  // ← DB가 자동 생성
    "stockName": "Apple",
    "stockPrice": 150.0
}
```

#### 예외: ID를 클라이언트가 제공하는 경우

```java
@Entity
public class Player {
    @Id  // @GeneratedValue 없음 (사용자가 ID를 정함)
    private String playerId;  // "user123" 같은 문자열
}

// 이 경우는 Request DTO에 playerId 포함 가능
public record PlayerCreateRequest(
    String playerId,      // ✓ 클라이언트가 제공해야 함
    String playerPassword
) {}

@PostMapping
public Response<Player> createPlayer(@RequestBody PlayerCreateRequest request) {
    Player player = new Player(request.playerId(), request.playerPassword());
    return Response.success(playerRepository.save(player));
}
```

---

### 4. @Transactional(readOnly=true) 기본 설정

#### 기본 패턴

```java
@Service
@Transactional(readOnly = true)  // 모든 메서드: 읽기 전용
public class StockService {
    
    @Transactional(readOnly = true)  // 명시적 (선택)
    public Response<PagedList> getAllStocks(int offset, int count) {
        // 읽기 전용
    }
    
    @Transactional  // readOnly 해제 (기본: false)
    public Response<Stock> createStock(StockCreateRequest request) {
        // 쓰기 가능
    }
    
    @Transactional
    public Response<Stock> updateStock(Long id, StockUpdateRequest request) {
        // 쓰기 가능
    }
    
    @Transactional
    public Response<Void> deleteStock(Long id) {
        // 쓰기 가능
    }
}
```

#### readOnly=true의 효과

**1. 성능 최적화**
```java
@Transactional(readOnly = true)
public Response<Stock> getStockById(Long id) {
    Stock stock = stockRepository.findById(id).get();
    return Response.success(stock);
}

// Spring이 최적화하는 것:
// 1. 트랜잭션 시작해서 커밋할 때 Flush하지 않음 (쓰기 없으니)
// 2. Dirty Checking 비활성화 (변경 감지할 필요 없음)
// 3. 1차 캐시 활용 최적화
// 4. DB 레플리카에 요청 라우팅 가능 (읽기 전용)
```

**2. 의도 명확화**
```java
// 코드 읽는 사람이 이해하기 쉬움
@Transactional(readOnly = true)  // "이 메서드는 조회만 함"
public List<Stock> getAllStocks() { }

@Transactional
public Stock createStock(StockCreateRequest req) { }  // "이 메서드는 쓰기함"
```

**3. 실수 방지**
```java
@Transactional(readOnly = true)
public Response<Stock> getStockById(Long id) {
    Stock stock = stockRepository.findById(id).get();
    stock.updateStockPrice(100.0);  // ❌ readOnly=true이므로 실패
    // org.springframework.dao.InvalidDataAccessApiUsageException
    return Response.success(stock);
}

// 개발자의 실수를 런타임에 감지
```

#### 이 프로젝트의 적용

```java
@Service
@Transactional(readOnly = true)  // ← 클래스 레벨 적용
public class StockService {
    
    public Response<PagedList> getAllStocks(Integer offset, Integer count) {
        // readOnly=true 상속
    }
    
    public Response<Stock> getStockById(Long id) {
        // readOnly=true 상속
    }
    
    @Transactional  // ← 메서드 레벨 오버라이드
    public Response<Stock> createStock(StockCreateRequest request) {
        // readOnly=false로 설정됨
    }
    
    @Transactional
    public Response<Stock> updateStock(Long id, StockUpdateRequest request) {
        Stock stock = stockRepository.findById(id)
            .orElseThrow(() -> new ResponseException(...));
        stock.updateStockName(request.stockName());
        stock.updateStockPrice(request.stockPrice());
        stockRepository.save(stock);
        return Response.success(stock);
    }
    
    @Transactional
    public Response<Void> deleteStock(Long id) {
        Stock stock = stockRepository.findById(id)
            .orElseThrow(() -> new ResponseException(...));
        stockRepository.delete(stock);
        return Response.success();
    }
}

@Service
@Transactional(readOnly = true)
public class PlayerService {
    // ... 동일한 패턴
}
```

---

### 5. SessionHandler와 Servlet 추상화

#### 계층 구조

```
HttpServletRequest (Servlet API - 낮은 수준)
        ↑
RequestContextHolder (Spring 유틸)
        ↑
ServletRequestAttributes (Spring 추상화)
        ↑
RequestAttributes (Spring 최상위 추상화)
```

#### Servlet 레벨 (낮은 수준)

```java
// Servlet API (Java 표준)
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.Cookie;

public void handleRequest(HttpServletRequest request) {
    // Servlet에서만 사용 가능
    Cookie[] cookies = request.getCookies();
    String headerValue = request.getHeader("Authorization");
}

// 문제:
// 1. ServletRequest 의존성 (테스트 어려움)
// 2. 웹 프레임워크에 강하게 결합
// 3. Reactive 환경에서 사용 불가 (Servlet은 동기식)
```

#### Spring 추상화 레벨 (높은 수준)

```java
// Spring이 제공하는 추상화 계층
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;
import org.springframework.web.context.request.RequestAttributes;

@Component
public class SessionHandler {
    
    public PlayerSession getPlayerSession() {
        // 1. RequestContextHolder - 현재 Thread의 Request 접근
        ServletRequestAttributes attributes = 
            (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        
        // 2. ServletRequestAttributes - ServletRequest 래핑
        HttpServletRequest request = attributes.getRequest();
        
        // 3. 쿠키 추출
        Cookie[] cookies = request.getCookies();
        
        // 실제 구현...
    }
}
```

**Spring 추상화의 이점**:
```java
// 같은 코드가 다양한 환경에서 작동
@Component
public class SessionHandler {
    public PlayerSession getPlayerSession() {
        RequestAttributes attributes = RequestContextHolder.getRequestAttributes();
        // Servlet 환경: ServletRequestAttributes 반환
        // Reactive 환경: ReactiveRequestAttributes 반환 (미래)
    }
}

// 테스트도 쉬워짐
@ExtendWith(SpringExtension.class)
class SessionHandlerTest {
    @Test
    void testGetPlayerSession() {
        // Mock RequestContextHolder 설정
        RequestContextHolder.setRequestAttributes(mockAttributes);
        
        // 테스트 실행
        handler.getPlayerSession();
    }
}
```

#### 이 프로젝트의 SessionHandler

```java
@Component
public class SessionHandler {
    
    public PlayerSession getPlayerSession() {
        ServletRequestAttributes attributes = 
            (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        HttpServletRequest request = attributes.getRequest();
        
        Cookie[] cookies = request.getCookies();
        if (cookies != null) {
            for (Cookie cookie : cookies) {
                if (Constant.JWT_ACCESS_COOKIE.equals(cookie.getName())) {
                    String token = cookie.getValue();
                    String payload = JwtTool.getValidPayload(token);
                    return JsonTool.toObject(payload, PlayerSession.class);
                }
            }
        }
        throw new ResponseException(Error.NOT_AUTHENTICATED, "No session");
    }
    
    public void storeAccessToken(String playerId, String token) {
        ServletRequestAttributes attributes = 
            (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        HttpServletResponse response = attributes.getResponse();
        
        Cookie cookie = new Cookie(Constant.JWT_ACCESS_COOKIE, token);
        cookie.setPath("/");
        cookie.setHttpOnly(true);
        cookie.setSecure(true);  // HTTPS only
        response.addCookie(cookie);
    }
}

// 동작 흐름:
// 1. Controller에서 메서드 호출
// 2. RequestContextHolder가 현재 HTTP Request 조회
// 3. 쿠키에서 JWT 토큰 추출
// 4. JWT 검증 및 payload 추출
// 5. 플레이어 정보 반환
```

---

## Controller 단 관련 학습 내용

### 1. REST API에서 CRUD 응답 설계

#### Create (POST) - 어떤 데이터를 반환할 것인가?

**옵션 1: 생성된 엔티티 전체 반환**

```java
@PostMapping
public Response<Player> createPlayer(@RequestBody PlayerCreateRequest request) {
    Player player = new Player(request.playerId(), 10000.0);
    Player saved = playerRepository.save(player);
    return Response.success(saved);
}

// 응답
{
    "result": "success",
    "body": {
        "playerId": "user123",
        "playerMoney": 10000.0
    }
}

// 장점: 클라이언트가 즉시 생성된 데이터 사용 가능
// 단점: 네트워크 대역폭 사용
```

**옵션 2: ID만 반환**

```java
@PostMapping
public Response<String> createPlayer(@RequestBody PlayerCreateRequest request) {
    Player player = new Player(request.playerId(), 10000.0);
    playerRepository.save(player);
    return Response.success(request.playerId());
}

// 응답
{
    "result": "success",
    "body": "user123"
}

// 장점: 최소한의 데이터 전송
// 단점: 클라이언트가 다시 조회 필요 (추가 요청)
```

**옵션 3: 생성 상태만 반환**

```java
@PostMapping
public Response<Void> createPlayer(@RequestBody PlayerCreateRequest request) {
    playerRepository.save(new Player(request.playerId(), 10000.0));
    return Response.success();
}

// 응답
{
    "result": "success",
    "body": null
}

// 장점: 최소 오버헤드
// 단점: 클라이언트는 아무 정보도 얻지 못함
```

#### 실무 사례별 권장 사항

**REST API 기본 원칙: HATEOAS**
```
- Create: 201 Created + Location 헤더 + 생성 객체 or ID
- Read: 200 OK + 전체 데이터
- Update: 200 OK + 수정된 객체 or 204 No Content
- Delete: 204 No Content or 200 OK + 삭제 확인
```

**이 프로젝트의 패턴 (옵션 1)**

```java
// Create - 생성된 엔티티 전체 반환 (권장)
@PostMapping
@Transactional
public Response<Player> createPlayer(@RequestBody PlayerCreateRequest request) {
    Player player = new Player(request.playerId(), INITIAL_PLAYER_MONEY);
    Player saved = playerRepository.save(player);
    return Response.success(saved);
}

// Read - 엔티티 또는 DTO
@GetMapping("/{playerId}")
@Transactional(readOnly = true)
public Response<PlayerStockListDto> getPlayerById(@PathVariable String playerId) {
    // ...복잡한 정보 조합 → DTO 사용
    return Response.success(playerStockListDto);
}

// Update - 수정된 엔티티 반환
@PutMapping("/{playerId}")
@Transactional
public Response<Player> updatePlayer(
    @PathVariable String playerId,
    @RequestBody PlayerUpdateRequest request
) {
    Player player = playerRepository.findById(playerId)
        .orElseThrow(() -> new ResponseException(...));
    player.updateMoney(request.playerMoney());
    Player updated = playerRepository.save(player);
    return Response.success(updated);
}

// Delete - 빈 응답
@DeleteMapping("/{playerId}")
@Transactional
public Response<Void> deletePlayer(
    @PathVariable String playerId,
    @RequestBody PlayerDeleteRequest request
) {
    Player player = playerRepository.findById(playerId)
        .orElseThrow(() -> new ResponseException(...));
    playerRepository.delete(player);
    return Response.success();
}
```

#### 언제 어떤 응답을 선택할 것인가?

| 시나리오 | 응답 | 이유 |
|---------|------|------|
| 쇼핑몰 상품 생성 | 상품 전체 | 관리자가 즉시 검증 가능 |
| SNS 게시물 생성 | 게시물 전체 | 클라이언트가 UI 업데이트용 |
| 대용량 파일 업로드 | ID만 | 네트워크 최적화 |
| 배치 작업 | 빈 응답 | 비동기 처리, 결과는 나중에 |
| 은행 송금 | 거래 ID | 추적용, 최소 정보 |

---

## 리팩토링 중 적용한 핵심 패턴들

### 1. Validation 메서드 추출 (DRY 원칙)

**Before**:
```java
@Transactional
public Response<Stock> createStock(StockCreateRequest request) {
    if (request == null || request.stockName() == null || request.stockName().trim().isEmpty()) {
        throw new ParameterException("stockName");
    }
    if (request.stockPrice() == null || request.stockPrice() <= 0) {
        throw new ParameterException("stockPrice");
    }
    // 실제 로직...
}

@Transactional
public Response<Stock> updateStock(Long id, StockUpdateRequest request) {
    if (request == null || request.stockName() == null || request.stockName().trim().isEmpty()) {
        throw new ParameterException("stockName");  // 중복!
    }
    if (request.stockPrice() == null || request.stockPrice() <= 0) {
        throw new ParameterException("stockPrice");  // 중복!
    }
    // 실제 로직...
}
```

**After** (추출):
```java
private void validateStockRequest(StockCreateRequest request) {
    if (request == null || request.stockName() == null || request.stockName().trim().isEmpty()) {
        throw new ParameterException("stockName");
    }
    if (request.stockPrice() == null || request.stockPrice() <= 0) {
        throw new ParameterException("stockPrice");
    }
}

@Transactional
public Response<Stock> createStock(StockCreateRequest request) {
    validateStockRequest(request);
    // 실제 로직...
}

@Transactional
public Response<Stock> updateStock(Long id, StockUpdateRequest request) {
    validateStockRequest(request);
    // 실제 로직...
}
```

### 2. 상수 추출 (Magic Number 제거)

**Before**:
```java
public Player createPlayer(PlayerCreateRequest request) {
    Player player = new Player(request.playerId(), 10000.0);  // Magic number
    return playerRepository.save(player);
}
```

**After**:
```java
private static final Double INITIAL_PLAYER_MONEY = 10000.0;

public Player createPlayer(PlayerCreateRequest request) {
    Player player = new Player(request.playerId(), INITIAL_PLAYER_MONEY);
    return playerRepository.save(player);
}
```

### 3. Entity 변경 - Setter 제거, 비즈니스 메서드 추가

**Before**:
```java
// Service에서 직접 setter 호출
player.setPlayerMoney(newAmount);

@Entity
@Getter
@Setter
public class Player {
    private Double playerMoney;
}
```

**After**:
```java
// Service에서 의미 있는 메서드 호출
player.updateMoney(newAmount);

@Entity
@Getter
public class Player {
    private Double playerMoney;
    
    public void updateMoney(Double newAmount) {
        if (newAmount == null || newAmount < 0) {
            throw new ResponseException(Error.INVALID_PARAMETER, "금액은 0 이상");
        }
        this.playerMoney = newAmount;
    }
}
```

### 4. Entity 직접 노출 제거 (DTO 사용)

**Before**:
```java
@PostMapping("/login")
public Response<Player> loginPlayer(@RequestBody PlayerSession session) {
    Player player = playerRepository.findById(session.getPlayerId()).get();
    return Response.success(player);  // ❌ 비밀번호 노출 위험
}
```

**After**:
```java
@PostMapping("/login")
public Response<PlayerLoginDto> loginPlayer(@RequestBody PlayerSession session) {
    Player player = playerRepository.findById(session.getPlayerId()).get();
    return Response.success(
        PlayerLoginDto.from(player.getPlayerId(), player.getPlayerMoney())
    );  // ✓ 안전한 DTO
}
```

### 5. JPA Dirty Checking 활용 (불필요한 save() 제거)

**Before**:
```java
@Transactional
public void buyPlayerStock(String playerId, Long stockId, Integer quantity) {
    Player player = playerRepository.findById(playerId).get();
    PlayerStock ps = playerStockRepository.findByPlayerAndStock(player, stock).get();
    
    ps.addQuantity(quantity);
    playerStockRepository.save(ps);  // ❌ 불필요 (dirty checking으로 충분)
    
    player.subtractMoney(totalPrice);
    playerRepository.save(player);  // ❌ 불필요
}
```

**After**:
```java
@Transactional
public void buyPlayerStock(String playerId, Long stockId, Integer quantity) {
    Player player = playerRepository.findById(playerId).get();
    PlayerStock ps = playerStockRepository.findByPlayerAndStock(player, stock).get();
    
    ps.addQuantity(quantity);
    // save() 호출 안 함 → JPA가 dirty checking으로 자동 감지
    
    player.subtractMoney(totalPrice);
    // save() 호출 안 함 → JPA가 자동 처리
}
// 트랜잭션 종료 시점에 한 번의 UPDATE만 발생
```

---

## 결론

이 프로젝트는 Spring Boot와 JPA를 활용한 **실무 수준의 REST API** 개발을 보여줍니다.

### 핵심 원칙들
1. **보안**: Entity 직접 노출 X, DTO 사용
2. **성능**: Lazy Loading, Pagination, Dirty Checking 활용
3. **유지보수성**: DRY (검증/상수 추출), 명확한 메서드명
4. **안정성**: @Transactional 제대로 사용, Optional 활용, 전역 예외 처리
5. **확장성**: Repository 메서드명 기반 쿼리, 계층 분리

### 실무 체크리스트
- [x] Exception 처리 (GlobalExceptionHandler, serialVersionUID)
- [x] Entity 설계 (NoArgsConstructor, 비즈니스 메서드, 관계 설정)
- [x] DTO 전략 (Request/Response 분리, Record 사용)
- [x] Repository 패턴 (메서드명 기반, Optional)
- [x] Service 트랜잭션 (readOnly=true 기본, CUD는 명시적)
- [x] Controller 설계 (RESTful, 적절한 응답 포맷)

이러한 패턴들을 이해하고 실제 프로젝트에 적용하면 안정적이고 유지보수하기 쉬운 코드를 작성할 수 있습니다.
