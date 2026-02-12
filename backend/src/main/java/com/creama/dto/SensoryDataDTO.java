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

    // Tags
    private List<String> keywords;
}
