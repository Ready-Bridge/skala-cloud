package com.example.product.dto;
import lombok.Data;
import jakarta.validation.constraints.*;

@Data
public class PurchaseRequest {
    @NotNull(message="회원 ID는 필수입니다")
    @Min(value=1, message="회원 ID는 1 이상")
    private Long memberId;

    @NotNull(message="상품 ID는 필수입니다")
    @Min(value=1, message="상품 ID는 1 이상")
    private Long productId;

    @NotNull(message="수량은 필수입니다")
    @Min(value=1, message="수량은 1 이상")
    private Integer quantity;
}
