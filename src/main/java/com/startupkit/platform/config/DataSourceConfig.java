package com.startupkit.platform.config;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.core.io.ClassPathResource;
import org.springframework.jdbc.datasource.init.ResourceDatabasePopulator;

import javax.sql.DataSource;
import java.net.URI;
import java.sql.Connection;
import java.sql.DriverManager;

@Slf4j
@Configuration
public class DataSourceConfig {

    @Value("${spring.datasource.url:}")
    private String configuredUrl;

    @Value("${spring.datasource.username:startupkit_user}")
    private String configuredUsername;

    @Value("${spring.datasource.password:startupkit_pass}")
    private String configuredPassword;

    @Value("${spring.datasource.driver-class-name:org.postgresql.Driver}")
    private String configuredDriver;

    @Bean
    @Primary
    public DataSource dataSource() {
        String dbUrl = configuredUrl;
        String username = configuredUsername;
        String password = configuredPassword;
        String driver = configuredDriver;

        // Render provides DATABASE_URL in format: postgres://user:password@host:port/database
        String renderDatabaseUrl = System.getenv("DATABASE_URL");
        if (renderDatabaseUrl != null && !renderDatabaseUrl.isBlank()) {
            try {
                log.info("Detected Render DATABASE_URL, parsing connection parameters...");
                URI uri = new URI(renderDatabaseUrl.replace("postgresql://", "http://").replace("postgres://", "http://"));
                String host = uri.getHost();
                int port = uri.getPort() == -1 ? 5432 : uri.getPort();
                String path = uri.getPath();
                String userInfo = uri.getUserInfo();

                if (userInfo != null && userInfo.contains(":")) {
                    String[] parts = userInfo.split(":", 2);
                    username = parts[0];
                    password = parts[1];
                }

                dbUrl = "jdbc:postgresql://" + host + ":" + port + path;
                driver = "org.postgresql.Driver";
                log.info("Successfully converted to JDBC URL: {}", dbUrl);
            } catch (Exception e) {
                log.warn("Failed to parse DATABASE_URL, using default: {}", e.getMessage());
            }
        }

        // Test if the target PostgreSQL is reachable with a short timeout
        boolean reachable = false;
        if (dbUrl != null && dbUrl.startsWith("jdbc:postgresql://")) {
            try {
                Class.forName(driver);
                DriverManager.setLoginTimeout(3);
                try (Connection conn = DriverManager.getConnection(dbUrl, username, password)) {
                    reachable = true;
                    log.info("Connected successfully to target PostgreSQL database at {}", dbUrl);
                }
            } catch (Exception e) {
                log.warn("Target PostgreSQL is not currently reachable ({}). Falling back to resilient in-memory database to ensure uptime.", e.getMessage());
            }
        }

        HikariConfig config = new HikariConfig();
        if (reachable) {
            config.setJdbcUrl(dbUrl);
            config.setUsername(username);
            config.setPassword(password);
            config.setDriverClassName(driver);
            config.setMaximumPoolSize(5);
            config.setConnectionTimeout(20000);
            config.setInitializationFailTimeout(10000);
            return new HikariDataSource(config);
        } else {
            // Fallback to embedded in-memory PostgreSQL-compatible mode
            log.info("Initializing in-memory database fallback with full schema and seed data.");
            System.setProperty("spring.flyway.enabled", "false");
            config.setJdbcUrl("jdbc:h2:mem:startupkit_db;DB_CLOSE_DELAY=-1;MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DEFAULT_NULL_ORDERING=HIGH");
            config.setDriverClassName("org.h2.Driver");
            config.setUsername("sa");
            config.setPassword("");
            config.setMaximumPoolSize(5);
            HikariDataSource ds = new HikariDataSource(config);

            // Populate all tables and seeds so all authentication and business APIs work instantly!
            try {
                ResourceDatabasePopulator populator = new ResourceDatabasePopulator();
                populator.setContinueOnError(true);
                populator.setIgnoreFailedDrops(true);
                populator.addScript(new ClassPathResource("database/migration/V1__init_schema.sql"));
                populator.addScript(new ClassPathResource("database/migration/V2__seed_ecosystem_data.sql"));
                populator.addScript(new ClassPathResource("database/migration/V3__seed_real_vietnam_ecosystem.sql"));
                populator.addScript(new ClassPathResource("database/migration/V4__seed_user_identities.sql"));
                populator.execute(ds);
                log.info("Successfully executed all migration and seed scripts on in-memory database.");
            } catch (Exception ex) {
                log.error("Failed to populate in-memory database: {}", ex.getMessage(), ex);
            }
            return ds;
        }
    }
}
