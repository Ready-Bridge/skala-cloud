package com.sk.skala.stockapi.tools;

import org.springframework.data.domain.Page;

import com.sk.skala.stockapi.data.common.PagedList;

public final class PaginationTool {
	private PaginationTool() {
	}

	public static <T> PagedList toPagedList(Page<T> page, int pageNumber) {
		return PagedList.builder()
			.total(page.getTotalElements())
			.count(page.getContent().size())
			.offset(pageNumber)
			.list(page.getContent())
			.build();
	}
}
