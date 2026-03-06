# ── 빌드 스테이지 ──
FROM eclipse-temurin:17-jdk-alpine AS builder
WORKDIR /app

# Gradle 설치
RUN apk add --no-cache wget unzip && \
    wget -q https://services.gradle.org/distributions/gradle-8.5-bin.zip -O /tmp/gradle.zip && \
    unzip -q /tmp/gradle.zip -d /opt && \
    rm /tmp/gradle.zip && \
    ln -s /opt/gradle-8.5/bin/gradle /usr/local/bin/gradle

# 의존성 캐시 활용을 위해 빌드 설정 파일 먼저 복사
COPY settings.gradle build.gradle ./
RUN gradle dependencies --no-daemon 2>/dev/null || true

# 소스코드 복사 후 빌드 (테스트 스킵)
COPY src ./src
RUN gradle bootJar --no-daemon -x test

# ── 실행 스테이지 ──
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

COPY --from=builder /app/build/libs/*.jar app.jar

EXPOSE 8081

ENTRYPOINT ["java", "-jar", "app.jar"]
