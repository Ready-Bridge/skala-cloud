package com.example.product.dto;
import lombok.Data;
import jakarta.validation.constraints.*;

@Data
public class MemberRequest {
    @Email(message="올바른 이메일 형식을 입력하세요")
    @NotBlank(message="이메일은 필수입니다")
    private String email;

    @NotBlank(message="이름은 필수입니다")
    private String name;

    @NotBlank(message="비밀번호는 필수입니다")
    @Size(min=4, max=50, message="비밀번호는 4~50자")
    private String password;

    private String phone;
    private String address;
}