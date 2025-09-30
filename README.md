# StylerStack Backend API
# StylerStack Backend API

A **Node.js + FastAPI hybrid backend** powering the StylerStack mobile app with payments, caching, rate limiting, and an admin dashboard.  
This backend manages everything from **secure API access via Firebase Auth + JWTs** to **inventory control, order processing, image management (Cloudinary), and real-time payment verification** via Mpesa Daraja API + Firebase Cloud Messaging (FCM).


---
## 🚀 Features
- **Authentication & Security**
  - **Firebase Authentication** – Handles user login & role-based access (admin/user)
  - **JWT middleware** – Verifies Firebase ID tokens and issues JWTs for backend API access
  - Rate limiting on sensitive endpoints (e.g., payments)
- **Payments**
  - Mpesa Daraja API integration (STK Push & callbacks)
  - Webhook support for payment confirmation
  - Real-time status pushed to frontend via FCM
- **Caching & Performance**
  - **Redis** for caching frequently accessed data (e.g., products, carts)
  - Redis-backed session & token management
- **Media Management**
  - **Cloudinary** integration for product images
  - Upload, store, and optimize images in the cloud
- **Admin Dashboard**
  - Built with Node.js + Tailwind CSS
  - Manage inventory (add, update, delete products)
  - Upload product images directly to Cloudinary
  - View analytics (sales, user activity, order history)
- **E-commerce Features**
  - Product browsing with image support
  - Category-based filtering
  - Cart & Favorites management
  - Address management
  - Orders (create, update, track)


---

## 🛠️ Tech Stack
- **FastAPI (Python)** – Core API services (products, categories, payments, orders)
- **Node.js + Tailwind** – Admin dashboard (inventory + analytics)
- **Firebase Auth** – User authentication & role-based access
- **JWT Middleware** – Secure backend endpoints
- **PostgreSQL** – Primary relational database
- **SQLAlchemy + Alembic** – ORM & database migrations
- **Redis** – Caching layer & rate limiting
- **Docker / Docker Compose** – Containerized development & deployment
- **Firebase Admin SDK** – Verify Firebase tokens & send FCM notifications
- **Mpesa Daraja API** – Payment gateway integration
- **Cloudinary** – Image storage & CDN delivery

---

## 🔐 Authentication Flow

User Request (POST /products)  
       ↓  
   🔐 Auth Middleware (`verify_firebase_token`)  
       ↓  
📨 Router (/products)  
       ↓  
📦 Schema (ProductCreate)  
       ↓  
🧠 Service or CRUD Function  
       ↓  
🗄️ SQLAlchemy Model (DB Write)  
       ↓  
📤 Response Schema (Product)  
       ↓  
Client Response

---
## 🔑 Environment Variables

The backend requires a `.env` file. An example is provided in `.env.example`.

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fashiondb
DATABASE_URL=postgresql://postgres:postgres@fashion-db:5432/fashiondb

# JWT Auth
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Mpesa Daraja API
MPESA_CONSUMER_KEY=your_mpesa_consumer_key
MPESA_CONSUMER_SECRET=your_mpesa_consumer_secret
MPESA_SHORTCODE=your_mpesa_shortcode
MPESA_PASSKEY=your_mpesa_passkey
MPESA_CALLBACK_URL=https://your-ngrok-url/payment/mpesa/callback

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Rate Limiting
RATE_LIMIT=20/minute

# Cloudinary
CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>
```
📂 API Structure
app.include_router(product_routes.router)
app.include_router(category_routes.router)
app.include_router(cart_routes.router)
app.include_router(favorite_routes.router)
app.include_router(address_router.router)
app.include_router(payments_routes.router)
app.include_router(user_router.router)
app.include_router(admin_routes.router)
app.include_router(order_router.router)

📂 Endpoints (Sample)
🔐 Auth
POST /auth/register – Register new user
POST /auth/login – Login (returns JWT)
🛒 E-commerce
GET /products – List products
GET /categories – Browse categories
POST /cart – Add item to cart
GET /favorites – Get user favorites
POST /address – Save shipping address
💳 Payments
POST /payments/initiate – Initiate Mpesa STK Push
POST /payments/webhook – Receive payment callback
GET /payments/status/{id} – Query payment status (with Redis cache)
📦 Orders
POST /orders – Place order
GET /orders – View order history
🛠️ Admin
GET /admin/products – View & manage inventory
GET /admin/analytics – View sales & user analytics


🏗️ Setup Instructions

# clone repo
git clone https://github.com/MboyaDan/StylersStack_back_end
cd stylerstack-backend

# create environment file
cp .env.example .env

# run docker
docker-compose up --build
## 🔗 Related Repositories

🔗 Related Repositories
- [Frontend (Flutter App)](https://github.com/MboyaDan/StylersStack_front_end)
## 📸 Screenshots (Admin Dashboard)

### Dashboard
![Dashboard Screenshot](https://github.com/MboyaDan/StylersStack_back_end/blob/main/docs/admin_dashbord.png)

### Orders
![Orders Screen](https://github.com/MboyaDan/StylersStack_back_end/blob/main/docs/order_screen.png)

### Add New Product
![Add Product Screen](https://github.com/MboyaDan/StylersStack_back_end/blob/main/docs/add_new_product_screen.png)

### Payments
![Payment Screen](https://github.com/MboyaDan/StylersStack_back_end/blob/main/docs/payment_screen.png)

### Products
![Product Screen](https://github.com/MboyaDan/StylersStack_back_end/blob/main/docs/product_screen.png)


