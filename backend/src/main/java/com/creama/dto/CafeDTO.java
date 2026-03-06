package com.creama.dto;

import lombok.*;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CafeDTO {
    private Long id;
    private String name;
    private String address;
    private Double latitude;
    private Double longitude;
    private String mainImageUrl;
    private String phone;
    private String operatingHours;
    private List<String> imageUrls;
    private List<SensoryDataDTO> sensoryData;

    // 위치 기반 추천 시 거리 표시용
    private Double distance;

    // 크리마 점수 (0.0 ~ 10.0, null이면 미표시)
    private Double creamaScore;
}
