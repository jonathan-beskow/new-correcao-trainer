package com.example.demo.service.saveService;

import com.example.demo.model.CasoCorrigido;
import com.example.demo.repository.CasoCorrigidoRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

@Service
public class InserirCasoCorrigidoService {

    private static final Logger logger = LoggerFactory.getLogger(InserirCasoCorrigidoService.class);
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private final String URL_PYTHON = "http://localhost:8000";

    @Autowired
    private CasoCorrigidoRepository casoCorrigidoRepository;

    public ResponseEntity<Map<String, String>> inserir(CasoCorrigido caso) {
        Map<String, String> resposta = new HashMap<>();

        if (caso.getTipo() == null || caso.getTipo().trim().isEmpty()) {
            resposta.put("mensagem", "O campo 'tipo' é obrigatório.");
            return ResponseEntity.badRequest().body(resposta);
        }

        String tipoNormalizado = Character.toUpperCase(caso.getTipo().charAt(0)) + caso.getTipo().substring(1).toLowerCase();
        caso.setTipo(tipoNormalizado);

        boolean sucesso = inserirCasoCorrigido(caso);

        if (sucesso) {
            logger.info("Novo caso corrigido cadastrado com sucesso:\n{}", caso.getCodigoCorrigido());
            resposta.put("mensagem", "Caso inserido com sucesso.");
            return ResponseEntity.ok(resposta);
        } else {
            logger.error("Erro ao tentar cadastrar o caso.");
            resposta.put("mensagem", "Erro ao inserir caso.");
            return ResponseEntity.status(500).body(resposta);
        }
    }

    // 🛠️ Adiciona esse método privado ausente
    private boolean inserirCasoCorrigido(CasoCorrigido caso) {
        try {
            Map<String, String> json = new HashMap<>();
            json.put("codigoOriginal", caso.getCodigoOriginal());
            json.put("codigoCorrigido", caso.getCodigoCorrigido());
            json.put("tipo", caso.getTipo());

            String requestBody = objectMapper.writeValueAsString(json);
            logger.info("Enviando novo caso para Python: {}", requestBody);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(URL_PYTHON + "/adicionar"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(requestBody, StandardCharsets.UTF_8))
                    .build();

            HttpResponse<String> response = HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
            logger.info("Resposta do Python ao adicionar caso: {}", response.body());

            casoCorrigidoRepository.save(caso);
            return true;

        } catch (Exception e) {
            logger.error("Erro ao inserir caso corrigido", e);
            return false;
        }
    }
}
