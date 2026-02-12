# Creama - Cafe Taste & Vibe Discovery Service

A polyglot monorepo project for discovering cafes based on sensory data (taste profiles) and vibe metrics (atmosphere).

## 📁 Project Structure

```
creama/
├── docker-compose.yml          # MariaDB container
├── frontend/                   # Vue 3 + Vite
│   ├── src/
│   │   ├── components/
│   │   │   └── RadarChart.vue
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── backend/                    # Spring Boot
│   ├── src/main/java/com/creama/
│   │   ├── entity/
│   │   │   ├── Cafe.java
│   │   │   └── SensoryData.java
│   │   ├── repository/
│   │   ├── service/
│   │   └── controller/
│   ├── src/main/resources/
│   │   └── application.yml
│   ├── build.gradle
│   └── settings.gradle
└── data/                       # Python Data Processor
    ├── requirements.txt
    ├── models.py
    └── seed_data.py
```

## 🚀 Quick Start

### 1. Start Database
```bash
docker-compose up -d
```

### 2. Seed Data (Python)
```bash
cd data
pip install -r requirements.txt
python seed_data.py
```

### 3. Run Backend (Spring Boot)
```bash
cd backend
./gradlew bootRun
```

### 4. Run Frontend (Vue)
```bash
cd frontend
npm install
npm run dev
```

## 🎯 Core Features

### Taste Metrics (0.0 - 5.0)
- **Acidity** (산미)
- **Body** (바디감)
- **Sweetness** (단맛)
- **Bitterness** (쓴맛)
- **Aroma** (향)

### Vibe Metrics (0 - 100)
- **Noise Level** (0: Library → 100: Market)
- **Lighting** (0: Dark/Mood → 100: Bright/Work)
- **Comfort** (0: Hard Chair → 100: Sofa)

## 🔧 Tech Stack

- **Frontend:** Vue 3, TypeScript, TailwindCSS, vue-chartjs
- **Backend:** Java 17, Spring Boot 3.2+, Gradle
- **Data:** Python 3.10+, SQLAlchemy, PyMySQL
- **Database:** MariaDB (Docker)
