package com.example.product.service;
import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import com.example.product.domain.Member;
import com.example.product.dto.MemberRequest;
import com.example.product.dto.MemberResponse;
import com.example.product.dto.MemberWithProductsResponse;
import com.example.product.mapper.MemberMapper;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
@Transactional(readOnly=true)
public class MemberService {
    private final MemberMapper mapper;

    public List<MemberResponse> getMembers() {
        return mapper.findAll().stream().map(this::toRes).toList();
    }

    public MemberResponse getMember(Long id) {
        Member m = mapper.findById(id).orElseThrow();
        return toRes(m);
    }

    @Transactional
    public MemberResponse createMember(MemberRequest r) {
        Member m = new Member();
        m.setEmail(r.getEmail());
        m.setName(r.getName());
        m.setPassword(r.getPassword());
        m.setPhone(r.getPhone());
        m.setAddress(r.getAddress());
        mapper.insert(m);
        return getMember(m.getId());
    }

    @Transactional
    public MemberResponse updateMember(Long id, MemberRequest r) {
        Member m = mapper.findById(id).orElseThrow();
        m.setEmail(r.getEmail());
        m.setName(r.getName());
        m.setPassword(r.getPassword());
        m.setPhone(r.getPhone());
        m.setAddress(r.getAddress());
        mapper.update(m);
        return getMember(id);
    }

    @Transactional
    public void deleteMember(Long id) {
        mapper.deleteById(id);
    }

    public MemberWithProductsResponse getMemberWithPurchases(Long memberId) {
        return mapper.findMemberWithProducts(memberId);
    }

    public MemberResponse login(String email, String password) {
        Member member = mapper.findByEmail(email)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "이메일 또는 비밀번호가 올바르지 않습니다"));
        if (!member.getPassword().equals(password)) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "이메일 또는 비밀번호가 올바르지 않습니다");
        }
        return toRes(member);
    }

    private MemberResponse toRes(Member m) {
        return MemberResponse.builder()
                .id(m.getId())
                .email(m.getEmail())
                .name(m.getName())
                .phone(m.getPhone())
                .address(m.getAddress())
                .createdAt(m.getCreatedAt())
                .updatedAt(m.getUpdatedAt())
                .build();
    }
}
