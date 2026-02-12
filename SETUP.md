# Creama Setup & Execution Guide

This guide will help you set up and run the Creama polyglot monorepo project.

## 📋 Prerequisites

- **Docker Desktop** (for MariaDB)
- **Java 17+** (for Spring Boot)
- **Python 3.10+** (for data seeding)
- **Node.js 18+** (for Vue frontend)
- **Gradle** (or use the wrapper `./gradlew`)

---

## 🚀 Quick Start (Step-by-Step)

### **Step 1: Start the Database**

```bash
# From the root directory (creama/)
docker-compose up -d
```

This will:
- Download and start a MariaDB container
- Create the `creama_db` database
- Expose it on `localhost:3306`

Verify it's running:
```bash
docker ps
```

---

### **Step 2: Seed the Database (Python)**

```bash
# Navigate to the data directory
cd data

# Install Python dependencies
pip install -r requirements.txt

# Run the seed script
python seed_data.py
```

Expected output:
```
🌱 Starting seed process...
✅ Successfully seeded 3 cafes with distinct profiles!
🎉 Seed complete!
```

This creates **3 cafes**:
1. **Creama Signature** - High acidity, specialty, bright workspace
2. **Velvet Lounge** - Dark chocolate, cozy date spot, low lighting
3. **Focus Study** - Balanced taste, quiet workspace

---

### **Step 3: Run the Backend (Spring Boot)**

```bash
# Navigate to the backend directory
cd ../backend

# Run using Gradle (Windows)
.\gradlew.bat bootRun

# Or on Mac/Linux
./gradlew bootRun
```

The server will start on **http://localhost:8080**

Verify the API:
```bash
# Test endpoint
curl http://localhost:8080/api/cafes
```

Or visit in browser: http://localhost:8080/api/cafes

---

### **Step 4: Run the Frontend (Vue)**

Open a **new terminal** (keep backend running):

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The Vue app will start on **http://localhost:5173**

---

## 🎯 Expected Result

Open your browser to **http://localhost:5173**

You should see:
- ☕️ **Creama** header
- **3 cafe cards** in a grid layout
- Each card shows:
  - Cafe image
  - **Radar chart** with 5 taste metrics (acidity, body, sweetness, bitterness, aroma)
  - **Vibe bars** showing noise, lighting, comfort levels (0-100)
  - **Keyword tags** (e.g., "Specialty", "Date Spot", "Study")

---

## 📦 Project Structure

```
creama/
├── docker-compose.yml          # MariaDB container
├── backend/                    # Spring Boot (Java 17)
│   ├── src/main/java/com/creama/
│   │   ├── entity/            # Cafe, SensoryData
│   │   ├── repository/        # CafeRepository
│   │   ├── service/           # CafeService
│   │   ├── controller/        # CafeController (API)
│   │   └── dto/               # Data Transfer Objects
│   └── build.gradle
├── data/                       # Python Data Processor
│   ├── models.py              # SQLAlchemy models
│   ├── seed_data.py           # Seed script
│   └── requirements.txt
└── frontend/                   # Vue 3 + TypeScript
    ├── src/
    │   ├── components/
    │   │   └── RadarChart.vue # Taste radar chart
    │   ├── App.vue            # Main app
    │   └── main.ts
    └── package.json
```

---

## 🔧 Troubleshooting

### Database Connection Issues

If backend can't connect to MariaDB:

1. Check Docker is running:
   ```bash
   docker ps
   ```

2. Check MariaDB logs:
   ```bash
   docker logs creama_mariadb
   ```

3. Verify connection settings in `backend/src/main/resources/application.yml`:
   ```yaml
   url: jdbc:mariadb://localhost:3306/creama_db
   username: root
   password: root
   ```

### Port Conflicts

- **3306** (MariaDB): Change in `docker-compose.yml` and `application.yml`
- **8080** (Spring Boot): Change in `application.yml` (`server.port`)
- **5173** (Vite): Change in `frontend/vite.config.ts`

### Seed Script Fails

If `seed_data.py` fails:

1. Ensure MariaDB is running
2. Test connection:
   ```bash
   # Install mysql client
   pip install pymysql
   
   # Test connection in Python
   python -c "import pymysql; pymysql.connect(host='localhost', user='root', password='root', database='creama_db')"
   ```

---

## 🎨 Key Features Implemented

### Backend (Spring Boot)
- ✅ JPA entities with proper relationships
- ✅ REST API endpoint: `GET /api/cafes`
- ✅ DTO pattern for clean data transfer
- ✅ CORS enabled for local development

### Data Processor (Python)
- ✅ SQLAlchemy models matching Java entities
- ✅ 3 distinct cafe profiles for testing
- ✅ JSON keywords storage

### Frontend (Vue 3)
- ✅ **Radar Chart** using vue-chartjs (taste profile)
- ✅ **Vibe Metrics** with progress bars
- ✅ TailwindCSS styling with gradient backgrounds
- ✅ Responsive grid layout
- ✅ Loading and error states

---

## 🔄 Development Workflow

1. **Make backend changes** → Spring Boot auto-reloads
2. **Make frontend changes** → Vite hot-reloads
3. **Add more cafes** → Run `python seed_data.py` again (clears old data)

---

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cafes` | Get all cafes with sensory data |

Response format:
```json
[
  {
    "id": 1,
    "name": "Creama Signature Roastery",
    "address": "Seoul, Gangnam-gu...",
    "latitude": 37.5276,
    "longitude": 127.0382,
    "mainImageUrl": "https://...",
    "sensoryData": [
      {
        "id": 1,
        "acidity": 4.5,
        "body": 3.0,
        "sweetness": 3.5,
        "bitterness": 2.0,
        "aroma": 4.8,
        "noiseLevel": 40,
        "lighting": 85,
        "comfort": 60,
        "keywords": ["Specialty", "Single Origin", "Bright", "Fruity", "Roastery"]
      }
    ]
  }
]
```

---

## 🎯 Next Steps

To extend this project:

1. **Add more endpoints** (POST, PUT, DELETE cafes)
2. **Implement filtering** (by taste profile, vibe metrics)
3. **Add user ratings** (new table + relationship)
4. **Geocoding** (search by location)
5. **Authentication** (Spring Security + JWT)
6. **Deploy** (Docker compose for all services)

---

## 📚 Technology References

- [Spring Boot Docs](https://spring.io/projects/spring-boot)
- [Vue 3 Docs](https://vuejs.org/)
- [vue-chartjs](https://vue-chartjs.org/)
- [SQLAlchemy Docs](https://www.sqlalchemy.org/)
- [TailwindCSS](https://tailwindcss.com/)
