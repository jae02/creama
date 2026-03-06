package com.creama.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ReviewDTO {
    private Long id;
    private Long cafeId;
    private String nickname;
    private String content;
    private String imageUrl;
    private String createdAt;
}
