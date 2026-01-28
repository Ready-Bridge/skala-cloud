package com.skala.stock.service;

import com.skala.stock.dto.TradeRequestDto;
import com.skala.stock.dto.TransactionDto;
import com.skala.stock.entity.Portfolio;
import com.skala.stock.entity.Stock;
import com.skala.stock.entity.Transaction;
import com.skala.stock.entity.User;
import com.skala.stock.repository.PortfolioRepository;
import com.skala.stock.repository.StockRepository;
import com.skala.stock.repository.TransactionRepository;
import com.skala.stock.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class TransactionService {

    private final TransactionRepository transactionRepository;
    private final UserRepository userRepository;
    private final StockRepository stockRepository;
    private final PortfolioRepository portfolioRepository;

    public List<TransactionDto> getUserTransactions(Long userId) {
        List<Transaction> transactions = transactionRepository.findByUserIdOrderByTransactionDateDesc(userId);
        return transactions.stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    public List<TransactionDto> getUserStockTransactions(Long userId, Long stockId) {
        List<Transaction> transactions = transactionRepository.findByUserIdAndStockIdOrderByTransactionDateDesc(userId, stockId);
        return transactions.stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    public TransactionDto getTransactionById(Long id) {
        Transaction transaction = transactionRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("거래 내역을 찾을 수 없습니다: " + id));
        return convertToDto(transaction);
    }

    @Transactional
    public TransactionDto executeTrade(TradeRequestDto request) {
        // 사용자 조회
        User user = userRepository.findById(request.getUserId())
                .orElseThrow(() -> new RuntimeException("사용자를 찾을 수 없습니다: " + request.getUserId()));

        // 주식 조회
        Stock stock = stockRepository.findById(request.getStockId())
                .orElseThrow(() -> new RuntimeException("주식을 찾을 수 없습니다: " + request.getStockId()));

        Long currentPrice = stock.getCurrentPrice();
        Long totalAmount = currentPrice * request.getQuantity();

        if (request.getType() == Transaction.TransactionType.BUY) {
            // 매수: 잔액 확인
            if (user.getBalance() < totalAmount) {
                throw new RuntimeException("잔액이 부족합니다. 필요 금액: " + totalAmount + ", 현재 잔액: " + user.getBalance());
            }
            user.setBalance(user.getBalance() - totalAmount);

            // 포트폴리오 업데이트
            Optional<Portfolio> existingPortfolio = portfolioRepository.findByUserIdAndStockId(user.getId(), stock.getId());
            if (existingPortfolio.isPresent()) {
                Portfolio portfolio = existingPortfolio.get();
                Long totalQuantity = portfolio.getQuantity() + request.getQuantity();
                Long totalValue = (portfolio.getQuantity() * portfolio.getAveragePrice()) + totalAmount;
                portfolio.setAveragePrice(totalValue / totalQuantity);
                portfolio.setQuantity(totalQuantity);
                portfolioRepository.save(portfolio);
            } else {
                Portfolio newPortfolio = Portfolio.builder()
                        .user(user)
                        .stock(stock)
                        .quantity(request.getQuantity())
                        .averagePrice(currentPrice)
                        .build();
                portfolioRepository.save(newPortfolio);
            }
        } else {
            // 매도: 보유 수량 확인
            Portfolio portfolio = portfolioRepository.findByUserIdAndStockId(user.getId(), stock.getId())
                    .orElseThrow(() -> new RuntimeException("보유한 주식이 없습니다"));

            if (portfolio.getQuantity() < request.getQuantity()) {
                throw new RuntimeException("보유 수량이 부족합니다. 보유 수량: " + portfolio.getQuantity() + ", 매도 요청: " + request.getQuantity());
            }

            user.setBalance(user.getBalance() + totalAmount);

            // 포트폴리오 업데이트
            if (portfolio.getQuantity().equals(request.getQuantity())) {
                portfolioRepository.delete(portfolio);
            } else {
                portfolio.setQuantity(portfolio.getQuantity() - request.getQuantity());
                portfolioRepository.save(portfolio);
            }
        }

        userRepository.save(user);

        // 거래 내역 저장
        Transaction transaction = Transaction.builder()
                .user(user)
                .stock(stock)
                .type(request.getType())
                .quantity(request.getQuantity())
                .price(currentPrice)
                .totalAmount(totalAmount)
                .transactionDate(LocalDateTime.now())
                .build();

        Transaction savedTransaction = transactionRepository.save(transaction);
        return convertToDto(savedTransaction);
    }

    private TransactionDto convertToDto(Transaction transaction) {
        return TransactionDto.builder()
                .id(transaction.getId())
                .userId(transaction.getUser().getId())
                .username(transaction.getUser().getUsername())
                .stockId(transaction.getStock().getId())
                .stockCode(transaction.getStock().getCode())
                .stockName(transaction.getStock().getName())
                .type(transaction.getType())
                .quantity(transaction.getQuantity())
                .price(transaction.getPrice())
                .totalAmount(transaction.getTotalAmount())
                .transactionDate(transaction.getTransactionDate())
                .createdAt(transaction.getCreatedAt())
                .build();
    }
}
