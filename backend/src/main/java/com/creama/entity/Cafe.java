package com.creama.entity;

import jakarta.persistence.*;
import lombok.*;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "cafes")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Cafe {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String name;

    @Column(length = 500)
    private String address;

    private Double latitude;

    private Double longitude;

    @Column(name = "main_image_url", length = 1000)
    private String mainImageUrl;

    // 신규 필드
    @Column(length = 20)
    private String phone;

    @Column(name = "operating_hours", length = 200)
    private String operatingHours;

    @Column(name = "image_urls", columnDefinition = "TEXT")
    private String imageUrls; // JSON 배열: ["url1","url2","url3"]

    @OneToMany(mappedBy = "cafe", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @Builder.Default
    private List<SensoryData> sensoryDataList = new ArrayList<>();

    // Helper method to add sensory data
    public void addSensoryData(SensoryData sensoryData) {
        sensoryDataList.add(sensoryData);
        sensoryData.setCafe(this);
    }
}
