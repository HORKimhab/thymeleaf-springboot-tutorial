# Blog Web Application Tutorial

## 1. Goal

In this tutorial, you will build a blog web application with:

- Spring Boot using MVC architecture
- Thymeleaf for server-side rendering
- Bootstrap 5 for responsive UI
- Spring Security for authentication and authorization
- MySQL for persistent storage

By the end, the application will support:

- User registration
- Login and logout
- BCrypt password encryption
- Email verification with secure tokens
- Role-based authorization with ADMIN, USER, and EDITOR
- Public blog listing and detail pages
- Post creation, editing, and deletion for ADMIN and EDITOR
- Search, filtering, and pagination
- Validation for forms, email, and password strength

## 2. Final Architecture

Use a clean 3-layer architecture:

```text
Controller Layer
    receives HTTP requests, validates web input, returns views

Service Layer
    contains business rules, security workflow, email verification, post logic

Repository Layer
    communicates with MySQL using Spring Data JPA
```

The request flow looks like this:

```text
Browser -> Controller -> Service -> Repository -> MySQL
Browser <- Thymeleaf View <- Controller
```

## 3. Project Structure

Create a package structure like this:

```text
src/main/java/com/example/blog
├── config
│   ├── MailConfig.java
│   └── SecurityConfig.java
├── controller
│   ├── AdminController.java
│   ├── AuthController.java
│   ├── HomeController.java
│   └── PostController.java
├── dto
│   ├── LoginRequest.java
│   ├── PostForm.java
│   └── RegisterRequest.java
├── entity
│   ├── Post.java
│   ├── Role.java
│   ├── User.java
│   └── VerificationToken.java
├── repository
│   ├── PostRepository.java
│   ├── UserRepository.java
│   └── VerificationTokenRepository.java
├── security
│   ├── CustomUserDetails.java
│   └── CustomUserDetailsService.java
├── service
│   ├── AuthService.java
│   ├── EmailService.java
│   ├── PostService.java
│   └── UserService.java
├── validation
│   ├── AllowedEmailDomain.java
│   ├── AllowedEmailDomainValidator.java
│   ├── PasswordStrength.java
│   └── PasswordStrengthValidator.java
└── BlogApplication.java

src/main/resources
├── templates
│   ├── admin
│   │   └── dashboard.html
│   ├── auth
│   │   ├── login.html
│   │   ├── register.html
│   │   └── verify-result.html
│   ├── fragments
│   │   └── navbar.html
│   ├── posts
│   │   ├── detail.html
│   │   ├── form.html
│   │   └── list.html
│   └── index.html
├── static
│   └── css
│       └── app.css
└── application.properties
```

## 4. Create the Project

Start with these dependencies in `pom.xml`:

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-thymeleaf</artifactId>
    </dependency>

    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>

    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>

    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>

    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-mail</artifactId>
    </dependency>

    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
        <scope>runtime</scope>
    </dependency>

    <dependency>
        <groupId>org.thymeleaf.extras</groupId>
        <artifactId>thymeleaf-extras-springsecurity6</artifactId>
    </dependency>

    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>

    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

Explanation:

- `web` handles controllers and MVC
- `thymeleaf` renders HTML on the server
- `security` gives login and authorization features
- `data-jpa` maps Java entities to MySQL tables
- `validation` enables bean validation annotations
- `mail` sends verification emails

## 5. Configure MySQL and Mail

Add the following to `application.properties`:

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/blog_app?createDatabaseIfNotExist=true&useSSL=false&serverTimezone=UTC
spring.datasource.username=root
spring.datasource.password=your_password

spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true

spring.thymeleaf.cache=false

spring.mail.host=smtp.gmail.com
spring.mail.port=587
spring.mail.username=your_email@gmail.com
spring.mail.password=your_app_password
spring.mail.properties.mail.smtp.auth=true
spring.mail.properties.mail.smtp.starttls.enable=true

app.base-url=http://localhost:8080
app.allowed-email-domains=gmail.com,yahoo.com,outlook.com,hotmail.com
```

Explanation:

- MySQL stores users, posts, and verification tokens
- `ddl-auto=update` is convenient while learning
- SMTP configuration sends verification emails
- `app.base-url` is used to build verification links
- `app.allowed-email-domains` limits accepted email providers

## 6. Create the Main Domain Model

### 6.1 Role Enum

```java
package com.example.blog.entity;

public enum Role {
    ADMIN,
    USER,
    EDITOR
}
```

### 6.2 User Entity

```java
package com.example.blog.entity;

import jakarta.persistence.CollectionTable;
import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.Table;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 120)
    private String fullName;

    @Column(nullable = false, unique = true, length = 160)
    private String email;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false)
    private boolean enabled = false;

    @Column(nullable = false)
    private boolean accountNonLocked = true;

    @Column(nullable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(name = "user_roles", joinColumns = @JoinColumn(name = "user_id"))
    @Enumerated(EnumType.STRING)
    @Column(name = "role")
    private Set<Role> roles = new HashSet<>();

    public Long getId() { return id; }
    public String getFullName() { return fullName; }
    public void setFullName(String fullName) { this.fullName = fullName; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }
    public boolean isAccountNonLocked() { return accountNonLocked; }
    public void setAccountNonLocked(boolean accountNonLocked) { this.accountNonLocked = accountNonLocked; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public Set<Role> getRoles() { return roles; }
    public void setRoles(Set<Role> roles) { this.roles = roles; }
}
```

Explanation:

- `enabled=false` means the user cannot log in until email verification succeeds
- Roles are stored in a separate table using `@ElementCollection`

### 6.3 VerificationToken Entity

```java
package com.example.blog.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import java.time.LocalDateTime;

@Entity
@Table(name = "verification_tokens")
public class VerificationToken {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String token;

    private LocalDateTime expiresAt;

    private boolean used = false;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    public Long getId() { return id; }
    public String getToken() { return token; }
    public void setToken(String token) { this.token = token; }
    public LocalDateTime getExpiresAt() { return expiresAt; }
    public void setExpiresAt(LocalDateTime expiresAt) { this.expiresAt = expiresAt; }
    public boolean isUsed() { return used; }
    public void setUsed(boolean used) { this.used = used; }
    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }
}
```

### 6.4 Post Entity

```java
package com.example.blog.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import java.time.LocalDateTime;

@Entity
@Table(name = "posts")
public class Post {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 180)
    private String title;

    @Column(nullable = false, unique = true, length = 200)
    private String slug;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String summary;

    @Column(nullable = false, columnDefinition = "LONGTEXT")
    private String content;

    @Column(nullable = false, length = 100)
    private String category;

    @Column(nullable = false)
    private boolean published = true;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private User author;

    @PrePersist
    public void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    public void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getSlug() { return slug; }
    public void setSlug(String slug) { this.slug = slug; }
    public String getSummary() { return summary; }
    public void setSummary(String summary) { this.summary = summary; }
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    public boolean isPublished() { return published; }
    public void setPublished(boolean published) { this.published = published; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public User getAuthor() { return author; }
    public void setAuthor(User author) { this.author = author; }
}
```

## 7. Create Repositories

Repositories keep database access inside the repository layer.

### 7.1 UserRepository

```java
package com.example.blog.repository;

import com.example.blog.entity.User;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
    boolean existsByEmail(String email);
}
```

### 7.2 VerificationTokenRepository

```java
package com.example.blog.repository;

import com.example.blog.entity.VerificationToken;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface VerificationTokenRepository extends JpaRepository<VerificationToken, Long> {
    Optional<VerificationToken> findByToken(String token);
}
```

### 7.3 PostRepository

```java
package com.example.blog.repository;

import com.example.blog.entity.Post;
import java.util.Optional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

public interface PostRepository extends JpaRepository<Post, Long> {

    Optional<Post> findBySlugAndPublishedTrue(String slug);

    @Query("""
        select p from Post p
        where p.published = true
          and (:keyword is null or lower(p.title) like lower(concat('%', :keyword, '%'))
               or lower(p.summary) like lower(concat('%', :keyword, '%')))
          and (:category is null or p.category = :category)
        order by p.createdAt desc
    """)
    Page<Post> searchPublished(String keyword, String category, Pageable pageable);
}
```

Explanation:

- `Page<Post>` supports pagination
- The custom query supports search and category filtering in one method

## 8. Create DTOs for Forms

DTOs are safer than binding web forms directly to entities.

### 8.1 RegisterRequest

```java
package com.example.blog.dto;

import com.example.blog.validation.AllowedEmailDomain;
import com.example.blog.validation.PasswordStrength;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class RegisterRequest {

    @NotBlank(message = "Full name is required")
    @Size(min = 3, max = 120)
    private String fullName;

    @NotBlank(message = "Email is required")
    @Email(message = "Email format is invalid")
    @AllowedEmailDomain
    private String email;

    @NotBlank(message = "Password is required")
    @PasswordStrength
    private String password;

    @NotBlank(message = "Please confirm your password")
    private String confirmPassword;

    public String getFullName() { return fullName; }
    public void setFullName(String fullName) { this.fullName = fullName; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
    public String getConfirmPassword() { return confirmPassword; }
    public void setConfirmPassword(String confirmPassword) { this.confirmPassword = confirmPassword; }
}
```

### 8.2 LoginRequest

```java
package com.example.blog.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

public class LoginRequest {

    @NotBlank
    @Email
    private String email;

    @NotBlank
    private String password;

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
}
```

### 8.3 PostForm

```java
package com.example.blog.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class PostForm {

    @NotBlank(message = "Title is required")
    @Size(max = 180)
    private String title;

    @NotBlank(message = "Summary is required")
    @Size(max = 1000)
    private String summary;

    @NotBlank(message = "Content is required")
    private String content;

    @NotBlank(message = "Category is required")
    private String category;

    private boolean published = true;

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getSummary() { return summary; }
    public void setSummary(String summary) { this.summary = summary; }
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    public boolean isPublished() { return published; }
    public void setPublished(boolean published) { this.published = published; }
}
```

Important note:

- Add a custom validator to ensure `password` and `confirmPassword` match

## 9. Create Custom Validators

### 9.1 Allowed Email Domain Annotation

```java
package com.example.blog.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target({ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = AllowedEmailDomainValidator.class)
public @interface AllowedEmailDomain {
    String message() default "Email domain is not allowed";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

### 9.2 Allowed Email Domain Validator

```java
package com.example.blog.validation;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import java.util.Arrays;
import java.util.Set;
import java.util.stream.Collectors;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class AllowedEmailDomainValidator implements ConstraintValidator<AllowedEmailDomain, String> {

    @Value("${app.allowed-email-domains}")
    private String configuredDomains;

    @Override
    public boolean isValid(String email, ConstraintValidatorContext context) {
        if (email == null || email.isBlank() || !email.contains("@")) {
            return false;
        }

        String domain = email.substring(email.indexOf('@') + 1).toLowerCase();
        Set<String> allowedDomains = Arrays.stream(configuredDomains.split(","))
                .map(String::trim)
                .map(String::toLowerCase)
                .collect(Collectors.toSet());

        return allowedDomains.contains(domain);
    }
}
```

### 9.3 Password Strength Annotation

```java
package com.example.blog.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target({ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = PasswordStrengthValidator.class)
public @interface PasswordStrength {
    String message() default "Password must be at least 8 characters and include upper, lower, digit, and special character";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

### 9.4 Password Strength Validator

```java
package com.example.blog.validation;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import java.util.regex.Pattern;

public class PasswordStrengthValidator implements ConstraintValidator<PasswordStrength, String> {

    private static final Pattern PATTERN = Pattern.compile(
            "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[!@#$%^&*()_+\\-={}\\[\\]:;\"'<>,.?/]).{8,}$"
    );

    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        return value != null && PATTERN.matcher(value).matches();
    }
}
```

## 10. Configure Spring Security

### 10.1 CustomUserDetails

```java
package com.example.blog.security;

import com.example.blog.entity.Role;
import com.example.blog.entity.User;
import java.util.Collection;
import java.util.stream.Collectors;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

public class CustomUserDetails implements UserDetails {

    private final User user;

    public CustomUserDetails(User user) {
        this.user = user;
    }

    public Long getId() {
        return user.getId();
    }

    public String getFullName() {
        return user.getFullName();
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return user.getRoles()
                .stream()
                .map(Role::name)
                .map(role -> new SimpleGrantedAuthority("ROLE_" + role))
                .collect(Collectors.toSet());
    }

    @Override
    public String getPassword() {
        return user.getPassword();
    }

    @Override
    public String getUsername() {
        return user.getEmail();
    }

    @Override
    public boolean isEnabled() {
        return user.isEnabled();
    }

    @Override
    public boolean isAccountNonLocked() {
        return user.isAccountNonLocked();
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }
}
```

### 10.2 CustomUserDetailsService

```java
package com.example.blog.security;

import com.example.blog.entity.User;
import com.example.blog.repository.UserRepository;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

@Service
public class CustomUserDetailsService implements UserDetailsService {

    private final UserRepository userRepository;

    public CustomUserDetailsService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("User not found"));

        return new CustomUserDetails(user);
    }
}
```

### 10.3 SecurityConfig

```java
package com.example.blog.config;

import com.example.blog.security.CustomUserDetailsService;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public DaoAuthenticationProvider authenticationProvider(
            CustomUserDetailsService userDetailsService,
            PasswordEncoder passwordEncoder) {
        DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
        provider.setUserDetailsService(userDetailsService);
        provider.setPasswordEncoder(passwordEncoder);
        return provider;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/", "/register", "/login", "/verify", "/posts", "/posts/*", "/css/**", "/js/**", "/images/**").permitAll()
                .requestMatchers("/admin/**").hasRole("ADMIN")
                .requestMatchers("/editor/**", "/posts/new", "/posts/*/edit", "/posts/*/delete").hasAnyRole("ADMIN", "EDITOR")
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/login")
                .defaultSuccessUrl("/", true)
                .failureUrl("/login?error")
                .permitAll()
            )
            .logout(logout -> logout
                .logoutSuccessUrl("/login?logout")
                .permitAll()
            )
            .rememberMe(Customizer.withDefaults());

        return http.build();
    }
}
```

Explanation:

- Public pages are visible to everyone
- `ADMIN` can manage users and posts
- `EDITOR` can create and edit posts
- `USER` can log in and read protected pages but cannot access admin or editor routes

## 11. Build the Service Layer

The service layer contains the real business logic.

### 11.1 EmailService

```java
package com.example.blog.service;

import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

@Service
public class EmailService {

    private final JavaMailSender mailSender;

    public EmailService(JavaMailSender mailSender) {
        this.mailSender = mailSender;
    }

    public void sendVerificationEmail(String to, String verifyUrl) {
        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(to);
        message.setSubject("Verify your blog account");
        message.setText("Welcome to the blog app.\n\nPlease verify your account by clicking this link:\n" + verifyUrl);
        mailSender.send(message);
    }
}
```

### 11.2 UserService

```java
package com.example.blog.service;

import com.example.blog.entity.Role;
import com.example.blog.entity.User;
import com.example.blog.repository.UserRepository;
import java.util.Set;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public UserService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Transactional
    public User registerUser(String fullName, String email, String rawPassword) {
        if (userRepository.existsByEmail(email)) {
            throw new IllegalArgumentException("Email is already registered");
        }

        User user = new User();
        user.setFullName(fullName);
        user.setEmail(email.toLowerCase());
        user.setPassword(passwordEncoder.encode(rawPassword));
        user.setEnabled(false);
        user.setRoles(Set.of(Role.USER));

        return userRepository.save(user);
    }

    @Transactional
    public void enableUser(User user) {
        user.setEnabled(true);
        userRepository.save(user);
    }

    public User getRequiredByEmail(String email) {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("User not found"));
    }
}
```

### 11.3 AuthService

```java
package com.example.blog.service;

import com.example.blog.dto.RegisterRequest;
import com.example.blog.entity.User;
import com.example.blog.entity.VerificationToken;
import com.example.blog.repository.VerificationTokenRepository;
import java.time.LocalDateTime;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {

    private final UserService userService;
    private final VerificationTokenRepository verificationTokenRepository;
    private final EmailService emailService;

    @Value("${app.base-url}")
    private String baseUrl;

    public AuthService(
            UserService userService,
            VerificationTokenRepository verificationTokenRepository,
            EmailService emailService) {
        this.userService = userService;
        this.verificationTokenRepository = verificationTokenRepository;
        this.emailService = emailService;
    }

    @Transactional
    public void register(RegisterRequest request) {
        if (!request.getPassword().equals(request.getConfirmPassword())) {
            throw new IllegalArgumentException("Passwords do not match");
        }

        User user = userService.registerUser(
                request.getFullName(),
                request.getEmail(),
                request.getPassword()
        );

        VerificationToken token = new VerificationToken();
        token.setToken(UUID.randomUUID().toString());
        token.setUser(user);
        token.setExpiresAt(LocalDateTime.now().plusHours(24));
        verificationTokenRepository.save(token);

        String verifyUrl = baseUrl + "/verify?token=" + token.getToken();
        emailService.sendVerificationEmail(user.getEmail(), verifyUrl);
    }

    @Transactional
    public boolean verifyEmail(String tokenValue) {
        VerificationToken token = verificationTokenRepository.findByToken(tokenValue)
                .orElseThrow(() -> new IllegalArgumentException("Invalid token"));

        if (token.isUsed() || token.getExpiresAt().isBefore(LocalDateTime.now())) {
            return false;
        }

        userService.enableUser(token.getUser());
        token.setUsed(true);
        verificationTokenRepository.save(token);
        return true;
    }
}
```

### 11.4 PostService

```java
package com.example.blog.service;

import com.example.blog.dto.PostForm;
import com.example.blog.entity.Post;
import com.example.blog.entity.User;
import com.example.blog.repository.PostRepository;
import java.util.Locale;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class PostService {

    private final PostRepository postRepository;

    public PostService(PostRepository postRepository) {
        this.postRepository = postRepository;
    }

    public Page<Post> getPublishedPosts(String keyword, String category, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        String cleanKeyword = keyword == null || keyword.isBlank() ? null : keyword.trim();
        String cleanCategory = category == null || category.isBlank() ? null : category.trim();
        return postRepository.searchPublished(cleanKeyword, cleanCategory, pageable);
    }

    public Post getPublishedBySlug(String slug) {
        return postRepository.findBySlugAndPublishedTrue(slug)
                .orElseThrow(() -> new IllegalArgumentException("Post not found"));
    }

    @Transactional
    public Post createPost(PostForm form, User author) {
        Post post = new Post();
        post.setTitle(form.getTitle());
        post.setSlug(toSlug(form.getTitle()));
        post.setSummary(form.getSummary());
        post.setContent(form.getContent());
        post.setCategory(form.getCategory());
        post.setPublished(form.isPublished());
        post.setAuthor(author);
        return postRepository.save(post);
    }

    @Transactional
    public Post updatePost(Post post, PostForm form) {
        post.setTitle(form.getTitle());
        post.setSlug(toSlug(form.getTitle()));
        post.setSummary(form.getSummary());
        post.setContent(form.getContent());
        post.setCategory(form.getCategory());
        post.setPublished(form.isPublished());
        return postRepository.save(post);
    }

    @Transactional
    public void deletePost(Post post) {
        postRepository.delete(post);
    }

    private String toSlug(String input) {
        return input.toLowerCase(Locale.ENGLISH)
                .replaceAll("[^a-z0-9]+", "-")
                .replaceAll("(^-|-$)", "");
    }
}
```

Production note:

- Add a unique-slug strategy in real projects to avoid collisions when two posts use the same title

## 12. Build the Controller Layer

### 12.1 HomeController

```java
package com.example.blog.controller;

import com.example.blog.service.PostService;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import com.example.blog.entity.Post;

@Controller
public class HomeController {

    private final PostService postService;

    public HomeController(PostService postService) {
        this.postService = postService;
    }

    @GetMapping("/")
    public String home(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String category,
            Model model) {

        Page<Post> posts = postService.getPublishedPosts(keyword, category, page, 6);
        model.addAttribute("posts", posts);
        model.addAttribute("keyword", keyword);
        model.addAttribute("category", category);
        return "index";
    }
}
```

### 12.2 AuthController

```java
package com.example.blog.controller;

import com.example.blog.dto.RegisterRequest;
import com.example.blog.service.AuthService;
import jakarta.validation.Valid;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @GetMapping("/register")
    public String showRegisterForm(Model model) {
        model.addAttribute("registerRequest", new RegisterRequest());
        return "auth/register";
    }

    @PostMapping("/register")
    public String register(
            @Valid RegisterRequest registerRequest,
            BindingResult bindingResult,
            Model model) {

        if (bindingResult.hasErrors()) {
            return "auth/register";
        }

        try {
            authService.register(registerRequest);
            model.addAttribute("message", "Registration successful. Please check your email to verify your account.");
            return "auth/verify-result";
        } catch (IllegalArgumentException ex) {
            model.addAttribute("error", ex.getMessage());
            return "auth/register";
        }
    }

    @GetMapping("/login")
    public String login() {
        return "auth/login";
    }

    @GetMapping("/verify")
    public String verify(@RequestParam String token, Model model) {
        boolean success = authService.verifyEmail(token);
        model.addAttribute("success", success);
        model.addAttribute("message",
                success ? "Email verified. You can now log in."
                        : "Verification link is invalid or expired.");
        return "auth/verify-result";
    }
}
```

### 12.3 PostController

```java
package com.example.blog.controller;

import com.example.blog.dto.PostForm;
import com.example.blog.entity.Post;
import com.example.blog.entity.User;
import com.example.blog.security.CustomUserDetails;
import com.example.blog.service.PostService;
import com.example.blog.service.UserService;
import jakarta.validation.Valid;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.security.core.annotation.AuthenticationPrincipal;

@Controller
@RequestMapping("/posts")
public class PostController {

    private final PostService postService;
    private final UserService userService;

    public PostController(PostService postService, UserService userService) {
        this.postService = postService;
        this.userService = userService;
    }

    @GetMapping("/{slug}")
    public String detail(@PathVariable String slug, Model model) {
        model.addAttribute("post", postService.getPublishedBySlug(slug));
        return "posts/detail";
    }

    @PreAuthorize("hasAnyRole('ADMIN','EDITOR')")
    @GetMapping("/new")
    public String createForm(Model model) {
        model.addAttribute("postForm", new PostForm());
        return "posts/form";
    }

    @PreAuthorize("hasAnyRole('ADMIN','EDITOR')")
    @PostMapping
    public String create(
            @Valid @ModelAttribute("postForm") PostForm postForm,
            BindingResult bindingResult,
            @AuthenticationPrincipal CustomUserDetails currentUser) {

        if (bindingResult.hasErrors()) {
            return "posts/form";
        }

        User author = userService.getRequiredByEmail(currentUser.getUsername());
        Post post = postService.createPost(postForm, author);
        return "redirect:/posts/" + post.getSlug();
    }

    @PreAuthorize("hasAnyRole('ADMIN','EDITOR')")
    @GetMapping("/{slug}/edit")
    public String editForm(@PathVariable String slug, Model model) {
        Post post = postService.getPublishedBySlug(slug);
        PostForm form = new PostForm();
        form.setTitle(post.getTitle());
        form.setSummary(post.getSummary());
        form.setContent(post.getContent());
        form.setCategory(post.getCategory());
        form.setPublished(post.isPublished());
        model.addAttribute("post", post);
        model.addAttribute("postForm", form);
        return "posts/form";
    }

    @PreAuthorize("hasAnyRole('ADMIN','EDITOR')")
    @PostMapping("/{slug}/edit")
    public String update(
            @PathVariable String slug,
            @Valid @ModelAttribute("postForm") PostForm postForm,
            BindingResult bindingResult,
            Model model) {

        Post post = postService.getPublishedBySlug(slug);

        if (bindingResult.hasErrors()) {
            model.addAttribute("post", post);
            return "posts/form";
        }

        Post updated = postService.updatePost(post, postForm);
        return "redirect:/posts/" + updated.getSlug();
    }

    @PreAuthorize("hasAnyRole('ADMIN','EDITOR')")
    @PostMapping("/{slug}/delete")
    public String delete(@PathVariable String slug) {
        Post post = postService.getPublishedBySlug(slug);
        postService.deletePost(post);
        return "redirect:/";
    }
}
```

Explanation:

- This version uses `UserService` to load the current user from the database
- Edit and delete endpoints are protected with role checks
- Use `POST` for delete actions to keep the flow CSRF-protected

### 12.4 AdminController

```java
package com.example.blog.controller;

import com.example.blog.repository.PostRepository;
import com.example.blog.repository.UserRepository;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
@PreAuthorize("hasRole('ADMIN')")
public class AdminController {

    private final UserRepository userRepository;
    private final PostRepository postRepository;

    public AdminController(UserRepository userRepository, PostRepository postRepository) {
        this.userRepository = userRepository;
        this.postRepository = postRepository;
    }

    @GetMapping("/admin/dashboard")
    public String dashboard(Model model) {
        model.addAttribute("userCount", userRepository.count());
        model.addAttribute("postCount", postRepository.count());
        model.addAttribute("users", userRepository.findAll());
        model.addAttribute("posts", postRepository.findAll());
        return "admin/dashboard";
    }
}
```

## 13. Build the Thymeleaf Views

Use Bootstrap 5 from CDN or local static files.

### 13.1 Shared Navbar Fragment

`templates/fragments/navbar.html`

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org"
      xmlns:sec="http://www.thymeleaf.org/extras/spring-security">
<body>
<nav th:fragment="navbar" class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
        <a class="navbar-brand" th:href="@{/}">Blog App</a>

        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNav">
            <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="mainNav">
            <ul class="navbar-nav me-auto">
                <li class="nav-item">
                    <a class="nav-link" th:href="@{/}">Home</a>
                </li>

                <li class="nav-item" sec:authorize="hasAnyRole('ADMIN','EDITOR')">
                    <a class="nav-link" th:href="@{/posts/new}">Write Post</a>
                </li>

                <li class="nav-item" sec:authorize="hasRole('ADMIN')">
                    <a class="nav-link" th:href="@{/admin/dashboard}">Admin</a>
                </li>
            </ul>

            <ul class="navbar-nav">
                <li class="nav-item" sec:authorize="isAnonymous()">
                    <a class="nav-link" th:href="@{/login}">Login</a>
                </li>
                <li class="nav-item" sec:authorize="isAnonymous()">
                    <a class="nav-link" th:href="@{/register}">Register</a>
                </li>
                <li class="nav-item" sec:authorize="isAuthenticated()">
                    <form th:action="@{/logout}" method="post">
                        <button class="btn btn-outline-light btn-sm mt-1" type="submit">Logout</button>
                    </form>
                </li>
            </ul>
        </div>
    </div>
</nav>
</body>
</html>
```

Explanation:

- `sec:authorize` shows menu items only for the right users
- Anonymous users see login and register links
- Admins see the dashboard link

### 13.2 Home Page with Search and Pagination

`templates/index.html`

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Blog App</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div th:replace="~{fragments/navbar :: navbar}"></div>

<main class="container py-4">
    <div class="row mb-4">
        <div class="col-lg-8">
            <h1 class="fw-bold">Latest Posts</h1>
            <p class="text-muted">Read recent articles from our community.</p>
        </div>
    </div>

    <form class="row g-3 mb-4" method="get" th:action="@{/}">
        <div class="col-md-6">
            <input class="form-control" type="text" name="keyword" th:value="${keyword}" placeholder="Search posts">
        </div>
        <div class="col-md-4">
            <select class="form-select" name="category">
                <option value="">All categories</option>
                <option value="Java">Java</option>
                <option value="Spring Boot">Spring Boot</option>
                <option value="Security">Security</option>
            </select>
        </div>
        <div class="col-md-2">
            <button class="btn btn-primary w-100">Filter</button>
        </div>
    </form>

    <div class="row g-4">
        <div class="col-md-6 col-lg-4" th:each="post : ${posts.content}">
            <div class="card h-100 shadow-sm">
                <div class="card-body">
                    <span class="badge bg-secondary mb-2" th:text="${post.category}"></span>
                    <h5 class="card-title" th:text="${post.title}"></h5>
                    <p class="card-text text-muted" th:text="${post.summary}"></p>
                    <a class="btn btn-outline-primary btn-sm" th:href="@{'/posts/' + ${post.slug}}">Read More</a>
                </div>
            </div>
        </div>
    </div>

    <nav class="mt-4" th:if="${posts.totalPages > 1}">
        <ul class="pagination">
            <li class="page-item" th:classappend="${posts.first} ? 'disabled'">
                <a class="page-link" th:href="@{/(page=${posts.number - 1}, keyword=${keyword}, category=${category})}">Previous</a>
            </li>
            <li class="page-item" th:each="i : ${#numbers.sequence(0, posts.totalPages - 1)}"
                th:classappend="${i == posts.number} ? 'active'">
                <a class="page-link" th:text="${i + 1}"
                   th:href="@{/(page=${i}, keyword=${keyword}, category=${category})}"></a>
            </li>
            <li class="page-item" th:classappend="${posts.last} ? 'disabled'">
                <a class="page-link" th:href="@{/(page=${posts.number + 1}, keyword=${keyword}, category=${category})}">Next</a>
            </li>
        </ul>
    </nav>
</main>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### 13.3 Registration Form

`templates/auth/register.html`

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Register</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div th:replace="~{fragments/navbar :: navbar}"></div>

<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
            <div class="card shadow-sm">
                <div class="card-body p-4">
                    <h2 class="mb-4">Create Account</h2>

                    <div class="alert alert-danger" th:if="${error}" th:text="${error}"></div>

                    <form th:action="@{/register}" th:object="${registerRequest}" method="post">
                        <div class="mb-3">
                            <label class="form-label">Full Name</label>
                            <input class="form-control" th:field="*{fullName}">
                            <div class="text-danger small" th:errors="*{fullName}"></div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input class="form-control" th:field="*{email}">
                            <div class="text-danger small" th:errors="*{email}"></div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Password</label>
                            <input type="password" class="form-control" th:field="*{password}">
                            <div class="text-danger small" th:errors="*{password}"></div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Confirm Password</label>
                            <input type="password" class="form-control" th:field="*{confirmPassword}">
                            <div class="text-danger small" th:errors="*{confirmPassword}"></div>
                        </div>

                        <button class="btn btn-primary w-100" type="submit">Register</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
</body>
</html>
```

### 13.4 Login Page

`templates/auth/login.html`

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div th:replace="~{fragments/navbar :: navbar}"></div>

<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
            <div class="card shadow-sm">
                <div class="card-body p-4">
                    <h2 class="mb-4">Login</h2>

                    <div class="alert alert-danger" th:if="${param.error}">Invalid email or password.</div>
                    <div class="alert alert-success" th:if="${param.logout}">You have been logged out.</div>

                    <form th:action="@{/login}" method="post">
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input class="form-control" name="username" type="email" required>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Password</label>
                            <input class="form-control" name="password" type="password" required>
                        </div>

                        <button class="btn btn-dark w-100" type="submit">Login</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
</body>
</html>
```

### 13.5 Post Form

`templates/posts/form.html`

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Post Form</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div th:replace="~{fragments/navbar :: navbar}"></div>

<main class="container py-5">
    <div class="row justify-content-center">
        <div class="col-lg-9">
            <div class="card shadow-sm">
                <div class="card-body p-4">
                    <h2 class="mb-4">Create or Edit Post</h2>
                    <form th:action="@{/posts}" th:object="${postForm}" method="post">
                        <div class="mb-3">
                            <label class="form-label">Title</label>
                            <input class="form-control" th:field="*{title}">
                            <div class="text-danger small" th:errors="*{title}"></div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Category</label>
                            <input class="form-control" th:field="*{category}">
                            <div class="text-danger small" th:errors="*{category}"></div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Summary</label>
                            <textarea class="form-control" rows="3" th:field="*{summary}"></textarea>
                            <div class="text-danger small" th:errors="*{summary}"></div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Content</label>
                            <textarea class="form-control" rows="10" th:field="*{content}"></textarea>
                            <div class="text-danger small" th:errors="*{content}"></div>
                        </div>

                        <div class="form-check mb-3">
                            <input class="form-check-input" type="checkbox" th:field="*{published}">
                            <label class="form-check-label">Published</label>
                        </div>

                        <button class="btn btn-primary" type="submit">Save Post</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</main>
</body>
</html>
```

### 13.6 Admin Dashboard

`templates/admin/dashboard.html`

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Admin Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div th:replace="~{fragments/navbar :: navbar}"></div>

<main class="container py-4">
    <h1 class="mb-4">Admin Dashboard</h1>

    <div class="row g-4 mb-4">
        <div class="col-md-6">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h5>Total Users</h5>
                    <p class="display-6" th:text="${userCount}"></p>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h5>Total Posts</h5>
                    <p class="display-6" th:text="${postCount}"></p>
                </div>
            </div>
        </div>
    </div>

    <div class="card shadow-sm">
        <div class="card-body">
            <h4 class="mb-3">Users</h4>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Enabled</th>
                        <th>Roles</th>
                    </tr>
                </thead>
                <tbody>
                    <tr th:each="user : ${users}">
                        <td th:text="${user.fullName}"></td>
                        <td th:text="${user.email}"></td>
                        <td th:text="${user.enabled}"></td>
                        <td th:text="${user.roles}"></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <div class="card shadow-sm mt-4">
        <div class="card-body">
            <h4 class="mb-3">Posts</h4>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Category</th>
                        <th>Published</th>
                    </tr>
                </thead>
                <tbody>
                    <tr th:each="post : ${posts}">
                        <td th:text="${post.title}"></td>
                        <td th:text="${post.category}"></td>
                        <td th:text="${post.published}"></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</main>
</body>
</html>
```

## 14. Add Bootstrap Styling

Create `static/css/app.css`:

```css
body {
    background-color: #f8f9fa;
}

.card {
    border: 0;
    border-radius: 1rem;
}

.navbar-brand {
    font-weight: 700;
    letter-spacing: 0.03em;
}

.post-content {
    line-height: 1.8;
}
```

Explanation:

- Bootstrap gives the layout system, form styles, cards, navbar, and utilities
- Your custom CSS should be small and focused

## 15. How Email Verification Works

Use this sequence:

```text
1. User submits registration form
2. Validation checks name, email, password, and allowed domain
3. Service creates user with enabled=false
4. Password is stored with BCrypt
5. Verification token is generated and stored
6. Email is sent with /verify?token=...
7. User clicks email link
8. Token is validated
9. User is enabled
10. Login becomes possible
```

Important rules:

- Expire tokens after 24 hours
- Reject reused tokens
- Keep `enabled=false` until verification is complete

## 16. How Role-Based Authorization Works

Recommended access matrix:

```text
PUBLIC
- view home page
- view blog posts
- register
- login
- verify email

USER
- same public pages
- authenticated features if you add profile or comments later

EDITOR
- create posts
- update posts
- delete posts if business rules allow

ADMIN
- manage users
- manage posts
- access dashboard
```

Security tips:

- Use both URL rules and method-level rules
- Never trust hidden buttons in HTML as security
- Enforce authorization in the backend

## 17. Add Post Search, Filter, and Pagination

This was already introduced in `PostRepository` and `HomeController`.

The main idea is:

```java
Page<Post> posts = postService.getPublishedPosts(keyword, category, page, 6);
```

Benefits:

- Search keeps the homepage useful when many posts exist
- Pagination avoids loading every row at once
- Filtering by category improves content discovery

## 18. Validation Checklist

Apply validation in these places:

- `@NotBlank` for required text fields
- `@Email` for email format
- `@AllowedEmailDomain` for accepted providers
- `@PasswordStrength` for strong passwords
- controller methods with `@Valid`
- `BindingResult` to show field errors in Thymeleaf

Also validate in the service layer:

- unique email
- matching passwords
- token expiry
- duplicate slugs if needed

## 19. Production Hardening

For a real deployment, improve these areas:

- Replace `ddl-auto=update` with database migrations such as Flyway
- Use HTML email templates instead of plain text
- Add resend verification email
- Add forgot password and reset password flow
- Add CSRF-safe forms for delete actions
- Use audit fields for createdBy and updatedBy
- Add integration tests for auth and role checks
- Store secrets in environment variables
- Add rate limiting for login and registration endpoints

## 20. Testing Strategy

Recommended tests:

```text
Unit tests
- password validator
- email domain validator
- slug generation

Repository tests
- search query
- find by email
- find by token

MVC tests
- register page loads
- invalid form shows errors
- unverified user cannot log in
- admin pages reject non-admin users

Integration tests
- registration creates disabled user
- verify endpoint enables user
- editor can create post
- public can search published posts
```

## 21. Step-by-Step Build Order

Follow this order when implementing the project:

1. Create Spring Boot project with required dependencies
2. Configure MySQL and mail in `application.properties`
3. Create entities and repositories
4. Create DTOs and validators
5. Configure Spring Security and password encoder
6. Implement user registration with BCrypt
7. Implement verification token generation and email sending
8. Block login until email verification completes
9. Build public post listing and detail pages
10. Build post management for ADMIN and EDITOR
11. Add admin dashboard
12. Add search, filtering, and pagination
13. Improve UI with Bootstrap 5
14. Add testing and production hardening

## 22. Common Beginner Mistakes

Avoid these issues:

- Binding forms directly to entities without DTOs
- Forgetting `@Valid` and `BindingResult`
- Saving raw passwords instead of BCrypt hashes
- Allowing login before verification
- Relying only on menu visibility for authorization
- Forgetting to permit static resources in Spring Security
- Using nullable columns for required business fields

## 23. Final Summary

You now have a blueprint for a production-ready blog application with:

- MVC design
- Thymeleaf templates
- Bootstrap 5 UI
- Spring Security
- BCrypt passwords
- Email verification
- Role-based authorization
- MySQL persistence
- Search, filter, pagination
- Clean 3-layer architecture

The most important design decision is keeping responsibilities separated:

- controllers handle web requests
- services handle business logic
- repositories handle persistence

This separation keeps the application easier to test, maintain, and extend.
