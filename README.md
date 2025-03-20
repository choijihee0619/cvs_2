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
-- 데이터베이스 생성 및 사용
CREATE DATABASE convenient_store;
USE convenient_store;

-- 공급업체 테이블
CREATE TABLE supplier (
    supplier_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    contact VARCHAR(50) NULL,
    address VARCHAR(100) NULL,
    PRIMARY KEY (supplier_id)
);

-- 매장 테이블
CREATE TABLE store (
    store_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    location VARCHAR(100) NOT NULL,
    manager_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (store_id)
);

-- 직원 테이블
CREATE TABLE employee (
    employee_id INT NOT NULL AUTO_INCREMENT,
    store_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    role ENUM('Manager', 'Cashier', 'Stocker') NOT NULL,
    hire_date DATE NOT NULL,
    phone VARCHAR(15) NULL,
    PRIMARY KEY (employee_id),
    FOREIGN KEY (store_id) REFERENCES store(store_id) ON DELETE CASCADE
);

-- 매장의 관리자 관계 설정 (관리자가 사라지면 NULL)
ALTER TABLE store 
ADD CONSTRAINT FK_STORE_MANAGER 
FOREIGN KEY (manager_id) REFERENCES employee(employee_id) ON DELETE SET NULL;

-- **📌 상품 테이블 (Product) 추가**
CREATE TABLE product (
    product_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    supplier_id INT NOT NULL,
    PRIMARY KEY (product_id),
    FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id) ON DELETE CASCADE
);

-- 주문 테이블 (매장이 공급업체에 주문하는 내역)
CREATE TABLE order_table (
    order_id INT NOT NULL AUTO_INCREMENT,
    store_id INT NOT NULL,
    supplier_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pending', 'Shipped', 'Delivered') DEFAULT 'Pending',
    PRIMARY KEY (order_id),
    FOREIGN KEY (store_id) REFERENCES store(store_id) ON DELETE CASCADE,
    FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id) ON DELETE CASCADE
);

-- 주문 상세 테이블 (각 주문 내 제품 목록)
CREATE TABLE order_details (
    order_detail_id INT NOT NULL AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (order_detail_id),
    FOREIGN KEY (order_id) REFERENCES order_table(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE
);

-- 재고 테이블 (매장의 재고 관리)
CREATE TABLE stock (
    stock_id INT NOT NULL AUTO_INCREMENT,
    store_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity >= 0),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (stock_id),
    FOREIGN KEY (store_id) REFERENCES store(store_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE
);

-- 거래(판매) 테이블
CREATE TABLE transaction (
    transaction_id INT NOT NULL AUTO_INCREMENT,
    store_id INT NOT NULL,
    employee_id INT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    payment_method ENUM('Cash', 'Card', 'Mobile Payment') NOT NULL,
    PRIMARY KEY (transaction_id),
    FOREIGN KEY (store_id) REFERENCES store(store_id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id) ON DELETE SET NULL
);

-- 거래 상세 테이블 (각 거래에서 판매된 제품 목록)
CREATE TABLE transaction_details (
    transaction_detail_id INT NOT NULL AUTO_INCREMENT,
    transaction_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    subtotal DECIMAL(10,2) NOT NULL CHECK (subtotal >= 0),
    PRIMARY KEY (transaction_detail_id),
    FOREIGN KEY (transaction_id) REFERENCES transaction(transaction_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE
);

```

