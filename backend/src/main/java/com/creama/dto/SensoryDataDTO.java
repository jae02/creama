package com.creama.dto;

import lombok.*;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SensoryDataDTO {
    private Long id;

    // Taste Metrics
    private Double acidity;
    private Double body;
    private Double sweetness;
    private Double bitterness;
    private Double aroma;

    // Vibe Metrics
    private Integer noiseLevel;
    private Integer lighting;
    private Integer comfort;

    // 신규 Vibe 필드
    private String musicGenre;
    private Integer crowdedness;
    private Boolean hasConcent;
    private Boolean hasWifi;
    private Boolean hasParking;
    private List<String> seatTypes;
    private List<String> vibeKeywords;
    private List<String> recommendedFor;

    // Tags
    private List<String> keywords;
}
