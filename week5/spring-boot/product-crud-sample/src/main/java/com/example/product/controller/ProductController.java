package com.example.product.controller;
import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import com.example.product.dto.ProductRequest;
import com.example.product.dto.ProductResponse;
import com.example.product.service.ProductService;

import io.swagger.v3.oas.annotations.Parameter;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
@Validated
public class ProductController {
 private final ProductService service;

 @GetMapping
 public List<ProductResponse> all() { return service.getProducts(); }

 @GetMapping("/{id}")
 public ProductResponse one(@PathVariable(name = "id")
                            @Parameter(description = "상품 ID", example = "1")
                            @Min(value = 1, message = "ID는 1 이상이어야 합니다") Long id) {
   return service.getProduct(id);
 }

 @PostMapping
 @ResponseStatus(HttpStatus.CREATED)
 public ProductResponse create(@RequestBody @Valid ProductRequest r) {
   return service.createProduct(r);
 }

 @PutMapping("/{id}")
 public ProductResponse update(@PathVariable(name = "id")
                               @Parameter(description = "상품 ID", example = "1")
                               @Min(value = 1, message = "ID는 1 이상이어야 합니다") Long id,
                               @RequestBody @Valid ProductRequest r) {
   return service.updateProduct(id, r);
 }

 @DeleteMapping("/{id}")
 @ResponseStatus(HttpStatus.NO_CONTENT)
 public void delete(@PathVariable(name = "id")
                    @Parameter(description = "상품 ID", example = "1")
                    @Min(value = 1, message = "ID는 1 이상이어야 합니다") Long id) {
   service.deleteProduct(id);
 }
}