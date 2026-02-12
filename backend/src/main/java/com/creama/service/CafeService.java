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

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class CafeService {

    private final CafeRepository cafeRepository;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public List<CafeDTO> getAllCafes() {
        return cafeRepository.findAllWithSensoryData().stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    private CafeDTO convertToDTO(Cafe cafe) {
        return CafeDTO.builder()
                .id(cafe.getId())
                .name(cafe.getName())
                .address(cafe.getAddress())
                .latitude(cafe.getLatitude())
                .longitude(cafe.getLongitude())
                .mainImageUrl(cafe.getMainImageUrl())
                .sensoryData(cafe.getSensoryDataList().stream()
                        .map(sd -> {
                            List<String> keywords = null;
                            try {
                                if (sd.getKeywords() != null) {
                                    keywords = objectMapper.readValue(sd.getKeywords(),
                                            new TypeReference<List<String>>() {
                                            });
                                }
                            } catch (Exception e) {
                                // Handle JSON parsing error
                            }

                            return SensoryDataDTO.builder()
                                    .id(sd.getId())
                                    .acidity(sd.getAcidity())
                                    .body(sd.getBody())
                                    .sweetness(sd.getSweetness())
                                    .bitterness(sd.getBitterness())
                                    .aroma(sd.getAroma())
                                    .noiseLevel(sd.getNoiseLevel())
                                    .lighting(sd.getLighting())
                                    .comfort(sd.getComfort())
                                    .keywords(keywords)
                                    .build();
                        })
                        .collect(Collectors.toList()))
                .build();
    }
}
