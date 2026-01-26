package com.example.product.mapper;
import com.example.product.domain.Purchase;
import com.example.product.dto.PurchaseResponse;
import org.apache.ibatis.annotations.Mapper;
import java.util.*;

@Mapper
public interface PurchaseMapper {
    List<PurchaseResponse> findAll();
    Optional<PurchaseResponse> findById(Long id);
    void insert(Purchase p);
    List<PurchaseResponse> findByMemberId(Long memberId);
    List<PurchaseResponse> findByProductId(Long productId);
}
