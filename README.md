# cvs_2: 편의점 데이터베이스 설계

## 개요
이 프로젝트는 편의점 운영을 위한 데이터베이스 설계
주요 테이블은 상품, 공급업체, 재고관리, 직원, 고객, 주문으로 구성

## 테이블 설명

### 1. Product (상품)
- 상품 정보를 저장하는 테이블
- 공급업체와 연관됨

**컬럼:**
- `product_id` (PK) - 상품 ID
- `name` - 상품명
- `category` - 상품 카테고리
- `price` - 상품 가격
- `supplier_id` (FK) - 공급업체 ID
- `created_at` - 등록 날짜

### 2. Supplier (공급업체)
- 상품을 공급하는 업체 정보를 저장

**컬럼:**
- `supplier_id` (PK) - 공급업체 ID
- `name` - 공급업체명
- `contact_name` - 담당자명
- `phone` - 연락처
- `address` - 주소

### 3. Inventory (재고관리)
- 상품별 재고를 관리하는 테이블

**컬럼:**
- `inventory_id` (PK) - 재고 ID
- `product_id` (FK) - 상품 ID
- `quantity` - 재고 수량
- `last_updated` - 마지막 업데이트 날짜

### 4. Employee (직원)
- 직원 정보를 저장하는 테이블

**컬럼:**
- `employee_id` (PK) - 직원 ID
- `name` - 직원명
- `position` - 직급
- `phone` - 연락처
- `hire_date` - 입사일

### 5. Customer (고객)
- 고객 정보를 저장하는 테이블

**컬럼:**
- `customer_id` (PK) - 고객 ID
- `name` - 고객명
- `phone` - 연락처
- `email` - 이메일
- `registered_at` - 가입 날짜

### 6. Order (주문)
- 고객이 주문한 내역을 저장

**컬럼:**
- `order_id` (PK) - 주문 ID
- `customer_id` (FK) - 고객 ID
- `employee_id` (FK) - 담당 직원 ID
- `order_date` - 주문 날짜
- `total_amount` - 총 결제 금액

-------------------------------------------------------------
#### SQL 코드
```sql
-- 상품 테이블
CREATE TABLE Product (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    supplier_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
);

-- 공급업체 테이블
CREATE TABLE Supplier (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255),
    phone VARCHAR(20),
    address TEXT
);

-- 재고관리 테이블
CREATE TABLE Inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

-- 직원 테이블
CREATE TABLE Employee (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    position VARCHAR(100),
    phone VARCHAR(20),
    hire_date DATE
);

-- 고객 테이블
CREATE TABLE Customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 주문 테이블
CREATE TABLE `Order` (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    employee_id INT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- 샘플 데이터 삽입
INSERT INTO Supplier (name, contact_name, phone, address) VALUES
('ABC 식품', '김철수', '010-1234-5678', '서울시 강남구'),
('XYZ 유통', '이영희', '010-5678-1234', '부산시 해운대구');

INSERT INTO Product (name, category, price, supplier_id) VALUES
('콜라', '음료', 1500, 1),
('사이다', '음료', 1400, 1),
('컵라면', '식품', 1200, 2);

INSERT INTO Inventory (product_id, quantity) VALUES
(1, 50),
(2, 30),
(3, 100);

INSERT INTO Employee (name, position, phone, hire_date) VALUES
('박지훈', '매니저', '010-9876-5432', '2023-01-15'),
('정수빈', '캐셔', '010-6543-2109', '2023-05-20');

INSERT INTO Customer (name, phone, email) VALUES
('김민지', '010-1111-2222', 'minji@example.com'),
('박현우', '010-3333-4444', 'hyunwoo@example.com');

INSERT INTO `Order` (customer_id, employee_id, total_amount) VALUES
(1, 1, 2900),
(2, 2, 1400);
```

