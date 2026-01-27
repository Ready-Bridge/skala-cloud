package com.skala.stock.dto;

import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PortfolioDto {

    private Long id;
    
    @NotNull(message = "사용자 ID는 필수입니다")
    private Long userId;
    
    private String username;
    
    @NotNull(message = "주식 ID는 필수입니다")
    private Long stockId;
    
    private String stockCode;
    private String stockName;
    
    @NotNull(message = "수량은 필수입니다")
    private Long quantity;
    
    @NotNull(message = "평균 매입가는 필수입니다")
    private Long averagePrice;
    
    private Long currentPrice;
    private Long totalValue; // 현재 평가 금액
    private Long profitLoss; // 평가 손익
}
