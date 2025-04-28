package com.example.demo.service;

import com.example.demo.dto.BlocoSimilarDTO;
import com.example.demo.dto.CodigoCorrigidoComSimilaridadeDTO;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class SimilaridadeService {

    private static final Logger logger = LoggerFactory.getLogger(SimilaridadeService.class);
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final String URL_PYTHON = "http://localhost:8000/similaridade/buscar_similar";

    private BlocoSimilarDTO blocoMaisSimilar; // ← adiciona campo de instância para reutilizar

    public List<CodigoCorrigidoComSimilaridadeDTO> buscarSimilaresTopK(String codigoNovo, String tipo, int k) {
        List<CodigoCorrigidoComSimilaridadeDTO> similares = new ArrayList<>();
        this.blocoMaisSimilar = null; // resetar

        try {
            logger.info("🔧 Iniciando montagem do JSON da requisição...");

            Map<String, Object> payload = new HashMap<>();
            payload.put("codigo", codigoNovo);
            payload.put("tipo", tipo);
            payload.put("k", k);

            logger.debug("📦 Payload enviado para o Python: {}", payload);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(payload, headers);
            RestTemplate restTemplate = new RestTemplate(new HttpComponentsClientHttpRequestFactory());
            ResponseEntity<String> response = restTemplate.postForEntity(URL_PYTHON, requestEntity, String.class);

            logger.info("✅ Status da resposta: {}", response.getStatusCodeValue());
            logger.debug("📩 Conteúdo da resposta:\n{}", response.getBody());

            JsonNode root = objectMapper.readTree(response.getBody());

            // ➕ Bloco mais similar
            JsonNode blocoNode = root.get("blocoMaisSimilar");
            if (blocoNode != null && !blocoNode.isNull()) {
                blocoMaisSimilar = new BlocoSimilarDTO();
                blocoMaisSimilar.setBlocoOriginal(blocoNode.get("blocoOriginal").asText());
                blocoMaisSimilar.setBlocoCorrigido(blocoNode.get("blocoCorrigido").asText());
                blocoMaisSimilar.setNomeMetodo(blocoNode.get("nomeMetodo").asText());
                blocoMaisSimilar.setSimilaridade(blocoNode.get("similaridade").asDouble());
                blocoMaisSimilar.setOrigemId(blocoNode.get("origemId").asText());

                logger.info("🧩 Bloco mais similar encontrado com similaridade {}.", blocoMaisSimilar.getSimilaridade());
            } else {
                logger.warn("⚠️ Nenhum bloco mais similar retornado.");
            }

            // ➕ Casos similares
            JsonNode array = root.get("similares");
            if (array != null && array.isArray()) {
                logger.info("🔎 Total de casos similares retornados: {}", array.size());

                for (JsonNode item : array) {
                    String original = item.get("codigoOriginal").asText();
                    String corrigido = item.get("codigoCorrigido").asText();
                    double similaridade = item.get("similaridade").asDouble();
                    String origemId = item.has("origemId") ? item.get("origemId").asText() : null;

                    logger.debug("📌 Similar encontrado - Similaridade: {}", similaridade);

                    CodigoCorrigidoComSimilaridadeDTO dto = new CodigoCorrigidoComSimilaridadeDTO(original, corrigido, similaridade);
                    dto.setOrigemId(origemId);
                    similares.add(dto);
                }
            } else {
                logger.warn("⚠️ Campo 'similares' não encontrado ou não é um array.");
            }

        } catch (Exception e) {
            logger.error("💥 Erro ao buscar similares", e);
        }

        logger.info("📤 Total de similares processados e retornados: {}", similares.size());
        return similares;
    }


    public BlocoSimilarDTO getBlocoMaisSimilar() {
        return blocoMaisSimilar;
    }

}
