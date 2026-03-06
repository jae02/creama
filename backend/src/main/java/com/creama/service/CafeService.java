package com.creama.service;

import com.creama.dto.CafeDTO;
import com.creama.dto.SensoryDataDTO;
import com.creama.entity.Cafe;
import com.creama.repository.CafeRepository;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class CafeService {

    private final CafeRepository cafeRepository;
    private final ObjectMapper objectMapper = new ObjectMapper();

    // 제외 키워드: 키즈카페, PC카페, 코인노래방, 독서실, 스터디카페 등
    private static final List<String> EXCLUDED_KEYWORDS = List.of(
            "키즈카페", "키즈 카페", "kids cafe", "kids 카페",
            "pc카페", "pc방", "인터넷카페", "인터넷 카페",
            "코인노래", "노래방", "노래연습",
            "독서실", "스터디카페", "스터디 카페",
            "찜질방", "방탈출", "보드게임");

    private boolean isExcludedCafe(Cafe cafe) {
        String name = cafe.getName() == null ? "" : cafe.getName().toLowerCase();
        return EXCLUDED_KEYWORDS.stream().anyMatch(name::contains);
    }

    public List<CafeDTO> getAllCafes() {
        return cafeRepository.findAllWithSensoryData().stream()
                .filter(cafe -> !isExcludedCafe(cafe))
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    public CafeDTO getCafeById(Long id) {
        Cafe cafe = cafeRepository.findByIdWithSensoryData(id)
                .orElseThrow(() -> new RuntimeException("카페를 찾을 수 없습니다. id: " + id));
        return convertToDTO(cafe);
    }

    /**
     * 키워드 검색: 이름, 주소, keywords, vibeKeywords, recommendedFor에서 검색
     */
    public List<CafeDTO> searchCafes(String query) {
        if (query == null || query.trim().isEmpty()) {
            return getAllCafes();
        }
        return cafeRepository.searchByKeyword("%" + query.trim() + "%").stream()
                .filter(cafe -> !isExcludedCafe(cafe))
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    /**
     * 위치 기반 추천: 주어진 좌표에서 가까운 카페를 거리순으로 반환
     */
    public List<CafeDTO> getNearbyCafes(Double lat, Double lng, int limit) {
        List<Cafe> allCafes = cafeRepository.findAllWithSensoryData();
        return allCafes.stream()
                .filter(cafe -> !isExcludedCafe(cafe))
                .map(cafe -> {
                    CafeDTO dto = convertToDTO(cafe);
                    dto.setDistance(calculateDistance(lat, lng, cafe.getLatitude(), cafe.getLongitude()));
                    return dto;
                })
                .sorted(Comparator.comparingDouble(CafeDTO::getDistance))
                .limit(limit)
                .collect(Collectors.toList());
    }

    /**
     * Haversine 공식으로 두 좌표 간 거리(km) 계산
     */
    private double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
        final double R = 6371; // 지구 반지름 (km)
        double dLat = Math.toRadians(lat2 - lat1);
        double dLon = Math.toRadians(lon2 - lon1);
        double a = Math.sin(dLat / 2) * Math.sin(dLat / 2)
                + Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2))
                        * Math.sin(dLon / 2) * Math.sin(dLon / 2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return Math.round((R * c) * 100.0) / 100.0; // 소수점 2자리
    }

    private List<String> parseJsonArray(String json) {
        if (json == null || json.isEmpty()) {
            return Collections.emptyList();
        }
        // 1) JSON 배열 형식 시도 ["a","b","c"]
        try {
            if (json.trim().startsWith("[")) {
                return objectMapper.readValue(json, new TypeReference<List<String>>() {
                });
            }
        } catch (Exception ignored) {
        }
        // 2) 콤마 구분 문자열로 fallback (import_analyzed.py가 "a,b,c" 형식으로 저장)
        return java.util.Arrays.stream(json.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .collect(Collectors.toList());
    }

    /**
     * 기본값(리뷰 없을 때 채워진 값)이면 빈 리스트 반환.
     * defaultValues: 소문자 정규화된 기본값 문자열 목록
     */
    private List<String> filterDefault(String raw, String... defaultValues) {
        if (raw == null || raw.isBlank())
            return Collections.emptyList();
        String normalized = raw.trim().toLowerCase();
        for (String d : defaultValues) {
            if (normalized.equals(d))
                return Collections.emptyList();
        }
        return parseJsonArray(raw);
    }

    private CafeDTO convertToDTO(Cafe cafe) {
        var sensoryDTOs = cafe.getSensoryDataList().stream()
                .map(sd -> SensoryDataDTO.builder()
                        .id(sd.getId())
                        .acidity(sd.getAcidity())
                        .body(sd.getBody())
                        .sweetness(sd.getSweetness())
                        .bitterness(sd.getBitterness())
                        .aroma(sd.getAroma())
                        .noiseLevel(sd.getNoiseLevel())
                        .lighting(sd.getLighting())
                        .comfort(sd.getComfort())
                        .musicGenre(sd.getMusicGenre())
                        .crowdedness(sd.getCrowdedness())
                        .hasConcent(sd.getHasConcent())
                        .hasWifi(sd.getHasWifi())
                        .hasParking(sd.getHasParking())
                        .seatTypes(filterDefault(sd.getSeatTypes(), "table", "테이블"))
                        .vibeKeywords(filterDefault(sd.getVibeKeywords(), "modern,simple", "모던,심플",
                                "modern, simple", "모던, 심플"))
                        .recommendedFor(filterDefault(sd.getRecommendedFor(), "cafe tour", "카페투어", "카페 투어"))
                        .keywords(filterDefault(sd.getKeywords(), "coffee,cafe", "커피,카페", "coffee, cafe",
                                "커피, 카페"))
                        .build())
                .collect(Collectors.toList());

        return CafeDTO.builder()
                .id(cafe.getId())
                .name(cafe.getName())
                .address(cafe.getAddress())
                .latitude(cafe.getLatitude())
                .longitude(cafe.getLongitude())
                .mainImageUrl(cafe.getMainImageUrl())
                .phone(cafe.getPhone())
                .operatingHours(cafe.getOperatingHours())
                .imageUrls(parseJsonArray(cafe.getImageUrls()))
                .sensoryData(sensoryDTOs)
                .creamaScore(calculateCreamaScore(cafe))
                .build();
    }

    /**
     * 크리마 점수 계산 (10점 만점)
     * 맛(30%) + 분위기(35%) + 편의시설(20%) + 콘텐츠 풍부도(15%)
     * 기본값만 있는 카페는 0.0 반환
     */
    private Double calculateCreamaScore(Cafe cafe) {
        if (cafe.getSensoryDataList().isEmpty())
            return 0.0;
        var sd = cafe.getSensoryDataList().get(0);

        // 기본값 체크: vibeKeywords가 기본값이면 0점
        String vk = sd.getVibeKeywords();
        if (vk == null || vk.isBlank())
            return 0.0;
        String vkLower = vk.trim().toLowerCase();
        if (vkLower.equals("modern,simple") || vkLower.equals("디자인,심플")
                || vkLower.equals("modern, simple") || vkLower.equals("디자인, 심플")
                || vkLower.equals("모던,심플") || vkLower.equals("모던, 심플")
                || vkLower.equals("normal") || vkLower.equals("cozy")
                || vkLower.equals("general") || vkLower.equals("cafe"))
            return 0.0;

        // 1. 맛 점수 (0~10): 5항목 평균 × 2
        double taste = ((sd.getAcidity() + sd.getBody() + sd.getSweetness()
                + sd.getBitterness() + sd.getAroma()) / 5.0) * 2.0;

        // 2. 분위기 점수 (0~10): comfort 기반
        double vibe = Math.min(10.0, (sd.getComfort() != null ? sd.getComfort() : 50) / 10.0);

        // 3. 편의시설 점수 (0~10)
        double facility = 0;
        if (Boolean.TRUE.equals(sd.getHasWifi()))
            facility += 2.5;
        if (Boolean.TRUE.equals(sd.getHasConcent()))
            facility += 2.5;
        if (Boolean.TRUE.equals(sd.getHasParking()))
            facility += 1.5;
        // 음악
        String music = sd.getMusicGenre();
        if (music != null && !music.isBlank() && !music.equalsIgnoreCase("none")
                && !music.equals("없음"))
            facility += 1.5;
        // 좌석 다양성
        List<String> seats = parseJsonArray(sd.getSeatTypes());
        facility += Math.min(2.0, seats.size() * 0.7);

        // 4. 콘텐츠 풍부도 (0~10): 태그 수
        List<String> vibes = parseJsonArray(vk);
        List<String> recs = parseJsonArray(sd.getRecommendedFor());
        double richness = Math.min(10.0, (vibes.size() + recs.size()) * 1.2);

        // 가중 평균
        double score = taste * 0.30 + vibe * 0.35 + facility * 0.20 + richness * 0.15;
        return Math.round(score * 10.0) / 10.0;
    }
}
