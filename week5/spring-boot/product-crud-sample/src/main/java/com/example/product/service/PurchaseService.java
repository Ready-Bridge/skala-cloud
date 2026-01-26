package com.example.product.service;
import java.math.BigDecimal;
import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.example.product.domain.Product;
import com.example.product.domain.Purchase;
import com.example.product.dto.PurchaseRequest;
import com.example.product.dto.PurchaseResponse;
import com.example.product.mapper.ProductMapper;
import com.example.product.mapper.PurchaseMapper;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
@Transactional(readOnly=true)
public class PurchaseService {
    private final PurchaseMapper purchaseMapper;
    private final ProductMapper productMapper;

    public List<PurchaseResponse> getPurchases() {
        return purchaseMapper.findAll();
    }

    public PurchaseResponse getPurchase(Long id) {
        return purchaseMapper.findById(id).orElseThrow();
    }

    @Transactional
    public PurchaseResponse createPurchase(PurchaseRequest r) {
        // 상품 조회 및 재고 확인
        Product product = productMapper.findById(r.getProductId()).orElseThrow();
        if (product.getStock() < r.getQuantity()) {
            throw new IllegalArgumentException("재고가 부족합니다");
        }

        // 구매 기록 생성
        Purchase p = new Purchase();
        p.setMemberId(r.getMemberId());
        p.setProductId(r.getProductId());
        p.setQuantity(r.getQuantity());
        p.setTotalPrice(product.getPrice().multiply(BigDecimal.valueOf(r.getQuantity())));
        purchaseMapper.insert(p);

        // 상품 재고 감소
        product.setStock(product.getStock() - r.getQuantity());
        productMapper.update(product);

        return purchaseMapper.findById(p.getId()).orElseThrow();
    }

    public List<PurchaseResponse> getPurchasesByMember(Long memberId) {
        return purchaseMapper.findByMemberId(memberId);
    }

    public List<PurchaseResponse> getPurchasesByProduct(Long productId) {
        return purchaseMapper.findByProductId(productId);
    }
}
