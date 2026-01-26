package com.example.product.controller;
import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import com.example.product.dto.PurchaseRequest;
import com.example.product.dto.PurchaseResponse;
import com.example.product.service.PurchaseService;

import io.swagger.v3.oas.annotations.Parameter;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/purchases")
@RequiredArgsConstructor
@Validated
public class PurchaseController {
    private final PurchaseService service;

    @GetMapping
    public List<PurchaseResponse> all() {
        return service.getPurchases();
    }

    @GetMapping("/{id}")
    public PurchaseResponse one(@PathVariable(name = "id")
                                @Parameter(description = "구매 ID", example = "1")
                                @Min(value = 1, message = "ID는 1 이상이어야 합니다") Long id) {
        return service.getPurchase(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public PurchaseResponse create(@RequestBody @Valid PurchaseRequest r) {
        return service.createPurchase(r);
    }

    @GetMapping("/member/{memberId}")
    public List<PurchaseResponse> getPurchasesByMember(@PathVariable(name = "memberId")
                                                       @Parameter(description = "회원 ID", example = "1")
                                                       @Min(value = 1, message = "ID는 1 이상이어야 합니다") Long memberId) {
        return service.getPurchasesByMember(memberId);
    }

    @GetMapping("/product/{productId}")
    public List<PurchaseResponse> getPurchasesByProduct(@PathVariable(name = "productId")
                                                        @Parameter(description = "상품 ID", example = "1")
                                                        @Min(value = 1, message = "ID는 1 이상이어야 합니다") Long productId) {
        return service.getPurchasesByProduct(productId);
    }
}
