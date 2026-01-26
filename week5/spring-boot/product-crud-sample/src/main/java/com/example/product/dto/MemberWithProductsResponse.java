package com.example.product.dto;
import lombok.Builder;
import lombok.Data;
import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
public class MemberWithProductsResponse {
    private Long id;
    private String email;
    private String name;
    private String phone;
    private String address;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private List<PurchasedProductDTO> purchasedProducts;

    @Data
    @Builder
    public static class PurchasedProductDTO {
        private Long productId;
        private String productName;
        private Integer quantity;
        private String description;
        private LocalDateTime purchasedAt;
    }
}
