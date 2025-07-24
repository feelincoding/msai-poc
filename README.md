# msai-poc

## How to execute the project
``` bash
# VM and Local
cd pro-gen
uv sync
source .venv/bin/activate
# 필요한 key 값 .env 파일에 입력
streamlit run app.py
```

## 구성도
![구성도](./img/스크린샷%202025-07-24%20오전%209.28.27.png)

## 프로젝트 시나리오
```
1. 사용자에게 프로젝트 생성에 필요한 정보를 입력받는다.
2. 입력받은 정보를 바탕으로 ktds 개발규칙(RAG 사용)에 맞는 프로젝트 개요를 생성한다.
3. 생성된 프로젝트 개요와 langchain을 이용한 prompt engineering을 바탕으로 프로젝트를 생성한다.
4. 사용자는 생성된 프로젝트를 다운받아. 프로젝트를 진행한다.
```
## 기대효과
```
1. 사내 아키텍처, 개발 규칙, 개발 방법론, 연동 포인트 등 KTDS의 개발 규칙을 바탕으로 프로젝트를 생성할 수 있다.
2. 통일된 개발 규칙을 바탕으로 프로젝트를 생성함으로써, 개발자들이 프로젝트를 이해하고 유지보수하는데 용이하다.
```
## 시나이로에 따른 화면 구성
1. 프로젝트 정보 입력 화면
![프로젝트 정보 입력 화면](./img/스크린샷%202025-07-24%2001.png)
![프로젝트 정보 입력 화면](./img/스크린샷%202025-07-24%2002.png)
2. 정보 입력에 따른 프로젝트 개요 생성 화면
![프로젝트 개요 생성 화면](./img/스크린샷%202025-07-24%2003.png)
![프로젝트 개요 생성 화면](./img/스크린샷%202025-07-24%2004.png)
![프로젝트 개요 생성 화면](./img/스크린샷%202025-07-24%2005.png)
![프로젝트 개요 생성 화면](./img/스크린샷%202025-07-24%2006.png)
![프로젝트 개요 생성 화면](./img/스크린샷%202025-07-24%2007.png)

### entity example
Entity Name,Description,Primary Key,Foreign Keys (Relationships),Key Fields (for quick understanding)
Users,쇼핑몰의 고객 또는 관리자 정보,id,,email, username, password_hash
Products,판매되는 상품의 정보,id,category_id (Categories),name, price, stock_quantity
Categories,상품을 분류하는 카테고리 정보,id,parent_id (Categories - Self-referencing),name
Orders,고객의 주문 정보,id,user_id (Users),order_date, total_amount, status
Order_Items,각 주문에 포함된 개별 상품의 상세 정보,id,order_id (Orders),product_id (Products),quantity, price_at_order
