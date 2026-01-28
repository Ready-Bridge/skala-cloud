package com.skala.stock.dto;

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
public class PortfolioProfitLossDto {
    private Long portfolioId;
    private String stockCode;
    private String stockName;
    private Long quantity;
    private Long averagePrice;
    private Long currentPrice;
    private Long totalInvestment;    // 총 투자금액
    private Long currentValue;       // 현재 평가액
    private Long profitLoss;         // 손익
    private Double profitLossRate;   // 손익률 (%)
}
