package com.skala.stock.repository;

import com.skala.stock.entity.Transaction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface TransactionRepository extends JpaRepository<Transaction, Long> {
    List<Transaction> findByUserIdOrderByTransactionDateDesc(Long userId);
    List<Transaction> findByUserIdAndStockIdOrderByTransactionDateDesc(Long userId, Long stockId);

    // 거래 내역 상세 조회
    @Query("SELECT t FROM Transaction t " +
           "JOIN FETCH t.user u " +
           "JOIN FETCH t.stock s " +
           "WHERE t.user.id = :userId " +
           "ORDER BY t.transactionDate DESC")
    List<Transaction> findDetailedTransactionsByUserId(@Param("userId") Long userId);

    // 특정 주식 거래 내역 조회
    @Query("SELECT t FROM Transaction t " +
           "JOIN FETCH t.user u " +
           "JOIN FETCH t.stock s " +
           "WHERE t.user.id = :userId AND t.stock.id = :stockId " +
           "ORDER BY t.transactionDate DESC")
    List<Transaction> findTransactionsByUserAndStock(@Param("userId") Long userId, 
                                                      @Param("stockId") Long stockId);

    // 거래 통계 - 총 거래 횟수
    @Query("SELECT COUNT(t) FROM Transaction t WHERE t.user.id = :userId")
    Long countByUserId(@Param("userId") Long userId);

    // 거래 통계 - 매수 횟수
    @Query("SELECT COUNT(t) FROM Transaction t " +
           "WHERE t.user.id = :userId AND t.type = 'BUY'")
    Long countBuyByUserId(@Param("userId") Long userId);

    // 거래 통계 - 매도 횟수
    @Query("SELECT COUNT(t) FROM Transaction t " +
           "WHERE t.user.id = :userId AND t.type = 'SELL'")
    Long countSellByUserId(@Param("userId") Long userId);

    // 거래 통계 - 총 매수 금액
    @Query("SELECT COALESCE(SUM(t.totalAmount), 0) FROM Transaction t " +
           "WHERE t.user.id = :userId AND t.type = 'BUY'")
    Long sumBuyAmountByUserId(@Param("userId") Long userId);

    // 거래 통계 - 총 매도 금액
    @Query("SELECT COALESCE(SUM(t.totalAmount), 0) FROM Transaction t " +
           "WHERE t.user.id = :userId AND t.type = 'SELL'")
    Long sumSellAmountByUserId(@Param("userId") Long userId);

    // 거래 통계 - 총 매수 수량
    @Query("SELECT COALESCE(SUM(t.quantity), 0) FROM Transaction t " +
           "WHERE t.user.id = :userId AND t.type = 'BUY'")
    Long sumBuyQuantityByUserId(@Param("userId") Long userId);

    // 거래 통계 - 총 매도 수량
    @Query("SELECT COALESCE(SUM(t.quantity), 0) FROM Transaction t " +
           "WHERE t.user.id = :userId AND t.type = 'SELL'")
    Long sumSellQuantityByUserId(@Param("userId") Long userId);

    // 일별 거래 내역 조회 (GROUP BY 사용)
    @Query("SELECT CAST(t.transactionDate AS LocalDate) as tradeDate, " +
           "COUNT(t) as tradeCount, " +
           "SUM(t.totalAmount) as totalAmount, " +
           "SUM(CASE WHEN t.type = 'BUY' THEN 1 ELSE 0 END) as buyCount, " +
           "SUM(CASE WHEN t.type = 'SELL' THEN 1 ELSE 0 END) as sellCount, " +
           "SUM(CASE WHEN t.type = 'BUY' THEN t.totalAmount ELSE 0 END) as buyAmount, " +
           "SUM(CASE WHEN t.type = 'SELL' THEN t.totalAmount ELSE 0 END) as sellAmount " +
           "FROM Transaction t " +
           "WHERE t.user.id = :userId " +
           "AND t.transactionDate BETWEEN :startDate AND :endDate " +
           "GROUP BY CAST(t.transactionDate AS LocalDate) " +
           "ORDER BY CAST(t.transactionDate AS LocalDate) DESC")
    List<Object[]> findDailyTransactions(@Param("userId") Long userId,
                                          @Param("startDate") LocalDateTime startDate,
                                          @Param("endDate") LocalDateTime endDate);
}
