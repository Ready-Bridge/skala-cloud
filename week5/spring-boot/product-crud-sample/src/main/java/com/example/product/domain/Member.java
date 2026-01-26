package com.example.product.domain;
import lombok.Data;
import java.time.LocalDateTime;

@Data
public class Member {
    private Long id;
    private String email;
    private String name;
    private String phone;
    private String address;
    private String password;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
