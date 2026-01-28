package com.skala.stock.repository;

import com.skala.stock.entity.Portfolio;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface PortfolioRepository extends JpaRepository<Portfolio, Long> {
    List<Portfolio> findByUserId(Long userId);
    Optional<Portfolio> findByUserIdAndStockId(Long userId, Long stockId);
    boolean existsByUserIdAndStockId(Long userId, Long stockId);

    // 포트폴리오 평가 손익 조회
    @Query("SELECT p FROM Portfolio p " +
           "JOIN FETCH p.stock s " +
           "JOIN FETCH p.user u " +
           "WHERE p.user.id = :userId")
    List<Portfolio> findPortfolioWithStockByUserId(@Param("userId") Long userId);

    // 총 투자금액 계산
    @Query("SELECT COALESCE(SUM(p.quantity * p.averagePrice), 0) " +
           "FROM Portfolio p WHERE p.user.id = :userId")
    Long calculateTotalInvestment(@Param("userId") Long userId);

    // 현재 평가액 계산
    @Query("SELECT COALESCE(SUM(p.quantity * p.stock.currentPrice), 0) " +
           "FROM Portfolio p WHERE p.user.id = :userId")
    Long calculateCurrentValue(@Param("userId") Long userId);
}
