package com.example.product.mapper;
import java.util.List;
import java.util.Optional;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import com.example.product.domain.Member;
import com.example.product.dto.MemberWithProductsResponse;

@Mapper
public interface MemberMapper {
    List<Member> findAll();
    Optional<Member> findById(@Param("id") Long id);
    Optional<Member> findByEmail(@Param("email") String email);
    void insert(Member m);
    void update(Member m);
    void deleteById(@Param("id") Long id);
    
    // 회원이 구매한 상품 조회 (조인)
    MemberWithProductsResponse findMemberWithProducts(@Param("memberId") Long memberId);
}
