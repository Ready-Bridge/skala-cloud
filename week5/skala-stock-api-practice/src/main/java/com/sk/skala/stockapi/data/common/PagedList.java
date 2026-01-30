package com.sk.skala.stockapi.data.common;

import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class PagedList {
	private long total;
	private long count;
	private long offset;
	private Object list;
}
