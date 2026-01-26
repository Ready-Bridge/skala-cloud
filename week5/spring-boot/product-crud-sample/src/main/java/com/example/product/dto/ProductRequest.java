package com.example.product.dto;
import lombok.Data;
import java.math.BigDecimal;
import jakarta.validation.constraints.*;
@Data
public class ProductRequest{
 @NotBlank(message="상품명은 필수입니다")
 private String name;
 private String description;
 @NotNull(message="가격은 필수입니다")
 @DecimalMin(value="0.0", inclusive=false, message="가격은 0보다 커야 합니다")
 private BigDecimal price;
 @NotNull(message="재고는 필수입니다")
 @Min(value=0, message="재고는 0 이상이어야 합니다")
 private Integer stock;
}