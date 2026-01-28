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
public class TotalAssetDto {
    private Long userId;
    private String username;
    private Long cashBalance;           // 현금 잔액
    private Long totalStockValue;       // 주식 평가액
    private Long totalAsset;            // 총 자산
    private Long totalInvestment;       // 총 투자금액
    private Long totalProfitLoss;       // 총 손익
    private Double totalProfitLossRate; // 총 수익률 (%)
}
