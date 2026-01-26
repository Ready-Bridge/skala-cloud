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

import com.example.product.dto.MemberLoginRequest;
import com.example.product.dto.MemberRequest;
import com.example.product.dto.MemberResponse;
import com.example.product.dto.MemberWithProductsResponse;
import com.example.product.service.MemberService;

import io.swagger.v3.oas.annotations.Parameter;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/members")
@RequiredArgsConstructor
@Validated
public class MemberController {
    private final MemberService service;

    @GetMapping
    public List<MemberResponse> all() {
        return service.getMembers();
    }

    @GetMapping("/{id}")
    public MemberResponse one(@PathVariable(name = "id")
                              @Parameter(description = "회원 ID", example = "1")
                              @Min(value = 1, message = "ID는 1 이상이어야 합니다") Long id) {
        return service.getMember(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public MemberResponse create(@RequestBody @Valid MemberRequest r) {
        return service.createMember(r);
    }

    @PutMapping("/{id}")
    public MemberResponse update(@PathVariable(name = "id")
                                 @Parameter(description = "회원 ID", example = "1")
                                 @Min(value = 1, message = "ID는 1 이상이어야 합니다") Long id,
                                 @RequestBody @Valid MemberRequest r) {
        return service.updateMember(id, r);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable(name = "id")
                       @Parameter(description = "회원 ID", example = "1")
                       @Min(value = 1, message = "ID는 1 이상이어야 합니다") Long id) {
        service.deleteMember(id);
    }

    @GetMapping("/{id}/purchases")
    public MemberWithProductsResponse getMemberWithPurchases(@PathVariable(name = "id")
                                                             @Parameter(description = "회원 ID", example = "1")
                                                             @Min(value = 1, message = "ID는 1 이상이어야 합니다") Long id) {
        return service.getMemberWithPurchases(id);
    }

    @PostMapping("/login")
    public MemberResponse login(@RequestBody @Valid MemberLoginRequest request) {
        return service.login(request.email(), request.password());
    }
}
