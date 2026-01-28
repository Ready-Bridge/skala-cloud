package com.skala.stock.service;

import com.skala.stock.dto.*;
import com.skala.stock.entity.Portfolio;
import com.skala.stock.entity.Transaction;
import com.skala.stock.entity.User;
import com.skala.stock.repository.PortfolioRepository;
import com.skala.stock.repository.TransactionRepository;
import com.skala.stock.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class StockAnalysisService {

    private final PortfolioRepository portfolioRepository;
    private final TransactionRepository transactionRepository;
    private final UserRepository userRepository;

    // 1. 포트폴리오 평가 손익 조회
    public List<PortfolioProfitLossDto> getPortfolioProfitLoss(Long userId) {
        List<Portfolio> portfolios = portfolioRepository.findPortfolioWithStockByUserId(userId);
        
        return portfolios.stream().map(p -> {
            Long totalInvestment = p.getQuantity() * p.getAveragePrice();
            Long currentValue = p.getQuantity() * p.getStock().getCurrentPrice();
            Long profitLoss = currentValue - totalInvestment;
            Double profitLossRate = totalInvestment > 0 ? 
                    (profitLoss.doubleValue() / totalInvestment.doubleValue() * 100) : 0.0;

            return PortfolioProfitLossDto.builder()
                    .portfolioId(p.getId())
                    .stockCode(p.getStock().getCode())
                    .stockName(p.getStock().getName())
                    .quantity(p.getQuantity())
                    .averagePrice(p.getAveragePrice())
                    .currentPrice(p.getStock().getCurrentPrice())
                    .totalInvestment(totalInvestment)
                    .currentValue(currentValue)
                    .profitLoss(profitLoss)
                    .profitLossRate(profitLossRate)
                    .build();
        }).collect(Collectors.toList());
    }

    // 2. 거래 내역 상세 조회
    public List<TransactionDto> getDetailedTransactions(Long userId) {
        List<Transaction> transactions = transactionRepository.findDetailedTransactionsByUserId(userId);
        
        return transactions.stream().map(t -> TransactionDto.builder()
                .id(t.getId())
                .userId(t.getUser().getId())
                .username(t.getUser().getUsername())
                .stockId(t.getStock().getId())
                .stockCode(t.getStock().getCode())
                .stockName(t.getStock().getName())
                .type(t.getType())
                .quantity(t.getQuantity())
                .price(t.getPrice())
                .totalAmount(t.getTotalAmount())
                .transactionDate(t.getTransactionDate())
                .createdAt(t.getCreatedAt())
                .build()
        ).collect(Collectors.toList());
    }

    // 3. 특정 주식 포트폴리오 조회 (Portfolio 기반)
    public PortfolioDto getStockPortfolio(Long userId, Long stockId) {
        Portfolio portfolio = portfolioRepository.findByUserIdAndStockId(userId, stockId)
                .orElseThrow(() -> new RuntimeException("포트폴리오를 찾을 수 없습니다. userId: " + userId + ", stockId: " + stockId));
        
        Long currentPrice = portfolio.getStock().getCurrentPrice();
        Long totalValue = portfolio.getQuantity() * currentPrice;
        Long profitLoss = totalValue - (portfolio.getQuantity() * portfolio.getAveragePrice());

        return PortfolioDto.builder()
                .id(portfolio.getId())
                .userId(portfolio.getUser().getId())
                .username(portfolio.getUser().getUsername())
                .stockId(portfolio.getStock().getId())
                .stockCode(portfolio.getStock().getCode())
                .stockName(portfolio.getStock().getName())
                .quantity(portfolio.getQuantity())
                .averagePrice(portfolio.getAveragePrice())
                .currentPrice(currentPrice)
                .totalValue(totalValue)
                .profitLoss(profitLoss)
                .build();
    }

    // 4. 총 자산 조회
    public TotalAssetDto getTotalAsset(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("사용자를 찾을 수 없습니다: " + userId));

        Long cashBalance = user.getBalance();
        Long totalInvestment = portfolioRepository.calculateTotalInvestment(userId);
        Long totalStockValue = portfolioRepository.calculateCurrentValue(userId);
        Long totalAsset = cashBalance + totalStockValue;
        Long totalProfitLoss = totalStockValue - totalInvestment;
        Double totalProfitLossRate = totalInvestment > 0 ? 
                (totalProfitLoss.doubleValue() / totalInvestment.doubleValue() * 100) : 0.0;

        return TotalAssetDto.builder()
                .userId(user.getId())
                .username(user.getUsername())
                .cashBalance(cashBalance)
                .totalStockValue(totalStockValue)
                .totalAsset(totalAsset)
                .totalInvestment(totalInvestment)
                .totalProfitLoss(totalProfitLoss)
                .totalProfitLossRate(totalProfitLossRate)
                .build();
    }

    // 5. 총 수익률 조회
    public Double getTotalReturnRate(Long userId) {
        Long totalInvestment = portfolioRepository.calculateTotalInvestment(userId);
        Long currentValue = portfolioRepository.calculateCurrentValue(userId);
        
        if (totalInvestment == 0) {
            return 0.0;
        }
        
        Long profitLoss = currentValue - totalInvestment;
        return (profitLoss.doubleValue() / totalInvestment.doubleValue() * 100);
    }

    // 6. 거래 통계 조회
    public TradeStatisticsDto getTradeStatistics(Long userId) {
        Long totalTradeCount = transactionRepository.countByUserId(userId);
        Long buyCount = transactionRepository.countBuyByUserId(userId);
        Long sellCount = transactionRepository.countSellByUserId(userId);
        Long totalBuyAmount = transactionRepository.sumBuyAmountByUserId(userId);
        Long totalSellAmount = transactionRepository.sumSellAmountByUserId(userId);
        Long totalBuyQuantity = transactionRepository.sumBuyQuantityByUserId(userId);
        Long totalSellQuantity = transactionRepository.sumSellQuantityByUserId(userId);

        return TradeStatisticsDto.builder()
                .userId(userId)
                .totalTradeCount(totalTradeCount)
                .buyCount(buyCount)
                .sellCount(sellCount)
                .totalBuyAmount(totalBuyAmount)
                .totalSellAmount(totalSellAmount)
                .totalBuyQuantity(totalBuyQuantity)
                .totalSellQuantity(totalSellQuantity)
                .build();
    }

    // 7. 일별 거래 내역 조회
    public List<DailyTransactionDto> getDailyTransactions(Long userId, LocalDate startDate, LocalDate endDate) {
        LocalDateTime startDateTime = startDate.atStartOfDay();
        LocalDateTime endDateTime = endDate.atTime(23, 59, 59);
        
        List<Object[]> results = transactionRepository.findDailyTransactions(userId, startDateTime, endDateTime);
        
        return results.stream().map(row -> DailyTransactionDto.builder()
                .tradeDate((LocalDate) row[0])
                .tradeCount((Long) row[1])
                .totalAmount((Long) row[2])
                .buyCount((Long) row[3])
                .sellCount((Long) row[4])
                .buyAmount((Long) row[5])
                .sellAmount((Long) row[6])
                .build()
        ).collect(Collectors.toList());
    }
}
