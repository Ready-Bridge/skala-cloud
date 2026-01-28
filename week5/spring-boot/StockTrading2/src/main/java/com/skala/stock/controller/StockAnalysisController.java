package com.skala.stock.controller;

import com.skala.stock.dto.*;
import com.skala.stock.service.StockAnalysisService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/analysis")
@RequiredArgsConstructor
@Tag(name = "주식 분석", description = "주식 거래 분석 및 통계 API")
public class StockAnalysisController {

    private final StockAnalysisService stockAnalysisService;

    @GetMapping("/portfolio/profit-loss/{userId}")
    @Operation(summary = "포트폴리오 평가 손익 조회", description = "사용자의 포트폴리오별 평가 손익을 조회합니다")
    public ResponseEntity<List<PortfolioProfitLossDto>> getPortfolioProfitLoss(@PathVariable Long userId) {
        List<PortfolioProfitLossDto> result = stockAnalysisService.getPortfolioProfitLoss(userId);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/transactions/detailed/{userId}")
    @Operation(summary = "거래 내역 상세 조회", description = "사용자의 상세 거래 내역을 조회합니다")
    public ResponseEntity<List<TransactionDto>> getDetailedTransactions(@PathVariable Long userId) {
        List<TransactionDto> transactions = stockAnalysisService.getDetailedTransactions(userId);
        return ResponseEntity.ok(transactions);
    }

    @GetMapping("/portfolio/{userId}/stock/{stockId}")
    @Operation(summary = "특정 주식 포트폴리오 조회", description = "사용자의 특정 주식 포트폴리오 정보를 조회합니다")
    public ResponseEntity<PortfolioDto> getStockPortfolio(
            @PathVariable Long userId, 
            @PathVariable Long stockId) {
        PortfolioDto portfolio = stockAnalysisService.getStockPortfolio(userId, stockId);
        return ResponseEntity.ok(portfolio);
    }

    @GetMapping("/asset/total/{userId}")
    @Operation(summary = "총 자산 조회", description = "사용자의 총 자산(현금 + 주식)을 조회합니다")
    public ResponseEntity<TotalAssetDto> getTotalAsset(@PathVariable Long userId) {
        TotalAssetDto asset = stockAnalysisService.getTotalAsset(userId);
        return ResponseEntity.ok(asset);
    }

    @GetMapping("/return-rate/{userId}")
    @Operation(summary = "총 수익률 조회", description = "사용자의 총 수익률을 조회합니다")
    public ResponseEntity<Double> getTotalReturnRate(@PathVariable Long userId) {
        Double returnRate = stockAnalysisService.getTotalReturnRate(userId);
        return ResponseEntity.ok(returnRate);
    }

    @GetMapping("/statistics/{userId}")
    @Operation(summary = "거래 통계 조회", description = "사용자의 거래 통계를 조회합니다 (매수/매도 횟수, 금액 등)")
    public ResponseEntity<TradeStatisticsDto> getTradeStatistics(@PathVariable Long userId) {
        TradeStatisticsDto statistics = stockAnalysisService.getTradeStatistics(userId);
        return ResponseEntity.ok(statistics);
    }

    @GetMapping("/daily-transactions/{userId}")
    @Operation(summary = "일별 거래 내역 조회", description = "사용자의 일별 거래 내역을 조회합니다")
    public ResponseEntity<List<DailyTransactionDto>> getDailyTransactions(
            @PathVariable Long userId,
            @Parameter(description = "조회 시작일 (YYYY-MM-DD)", example = "2024-01-01", required = true)
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @Parameter(description = "조회 종료일 (YYYY-MM-DD)", example = "2024-12-31", required = true)
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        List<DailyTransactionDto> dailyTransactions = stockAnalysisService.getDailyTransactions(userId, startDate, endDate);
        return ResponseEntity.ok(dailyTransactions);
    }
}
