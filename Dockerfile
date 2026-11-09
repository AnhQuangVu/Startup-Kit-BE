# Stage 1: Build Spring Boot 4 JAR with Maven + Java 21
FROM maven:3.9.9-eclipse-temurin-21 AS builder

WORKDIR /app

ENV MAVEN_OPTS="-Xmx384m -XX:+TieredCompilation -XX:TieredStopAtLevel=1"

COPY pom.xml ./
COPY src ./src

RUN mvn clean package -DskipTests -B

# Stage 2: Production Java 21 JRE Runtime
FROM eclipse-temurin:21-jre-jammy

WORKDIR /app

ENV JAVA_TOOL_OPTIONS="-XX:+UseContainerSupport -Xmx384m -Xms128m -XX:+ExitOnOutOfMemoryError"

COPY --from=builder /app/target/platform-0.0.1-SNAPSHOT.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
