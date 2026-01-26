-- 상품 데이터 삽입
INSERT INTO products(name,description,price,stock)
VALUES('노트북','게이밍 노트북',1500000,10);
INSERT INTO products(name,description,price,stock)
VALUES('마우스','무선 마우스',25000,100);
INSERT INTO products(name,description,price,stock)
VALUES('키보드','기계식 키보드',120000,50);

-- 회원 데이터 삽입 (단순 텍스트 비밀번호)
INSERT INTO members(email,name,phone,address,password)
VALUES('john@example.com','김철수','010-1234-5678','서울시 강남구','pass123');
INSERT INTO members(email,name,phone,address,password)
VALUES('park@example.com','박영희','010-2345-6789','서울시 서초구','pass123');
INSERT INTO members(email,name,phone,address,password)
VALUES('lee@example.com','이순신','010-3456-7890','부산시 해운대구','pass123');

-- 구매 기록 삽입
INSERT INTO purchases(member_id,product_id,quantity,total_price)
VALUES(1, 1, 1, 1500000);
INSERT INTO purchases(member_id,product_id,quantity,total_price)
VALUES(1, 2, 2, 50000);
INSERT INTO purchases(member_id,product_id,quantity,total_price)
VALUES(2, 3, 1, 120000);
INSERT INTO purchases(member_id,product_id,quantity,total_price)
VALUES(3, 1, 1, 1500000);

