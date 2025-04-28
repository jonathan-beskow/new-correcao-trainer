package com.example.demo.service;

import com.example.demo.dto.BlocoSimilarDTO;
import com.example.demo.util.PromptUtils;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class CodeCorrectionService {

    private static final Logger logger = LoggerFactory.getLogger(CodeCorrectionService.class);

    @Value("${codet5.api.url:http://localhost:8000/codet5/codet5_sugerir}")
    private String sugestaoCodet5Url;

    @Value("${openai.api.key}")
    private String openaiApiKey;

    @Value("${openai.model:gpt-4-turbo}")
    private String openaiModel;

    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();

    public String sugerirCorrecaoViaPython(
            String tipo,
            String exemplo,
            String correcao,
            String alvo,
            String origemId,
            BlocoSimilarDTO bloco // Novo argumento
    ) {
        try {
            Map<String, Object> payload = new HashMap<>();
            payload.put("tipo", tipo);
            payload.put("exemplo", exemplo);
            payload.put("correcao", correcao);
            payload.put("alvo", alvo);
            if (origemId != null) {
                payload.put("origemId", origemId);
            }
            if (bloco != null) {
                payload.put("blocoOriginal", bloco.getBlocoOriginal());
                payload.put("blocoCorrigido", bloco.getBlocoCorrigido());
            }

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(payload, headers);

            ResponseEntity<String> response = restTemplate.exchange(
                    sugestaoCodet5Url,
                    HttpMethod.POST,
                    requestEntity,
                    String.class
            );

            if (response.getStatusCode() == HttpStatus.OK) {
                JsonNode json = new ObjectMapper().readTree(response.getBody());
                return json.get("sugestao").asText();
            } else {
                logger.error("Erro na resposta da API Python: status {}", response.getStatusCode());
                return "Erro: resposta inesperada da API de sugestão";
            }

        } catch (Exception e) {
            logger.error("Erro ao sugerir correção via Python: {}", e.getMessage(), e);
            return "Erro: falha ao comunicar com microserviço de sugestão";
        }
    }

//    public String gerarCorrecaoViaChatGPT(String tipo, String codigoOriginal, String codigoCorrigido, String codigoAlvo) {
//        logger.info("🤖 Iniciando fallback com ChatGPT...");
//
//        String prompt;
//        if (codigoCorrigido == null || codigoCorrigido.isBlank()) {
//            prompt = PromptUtils.generatePromptWithOutBase(tipo, codigoAlvo);
//        } else {
//            prompt = PromptUtils.generatePrompt(tipo, codigoCorrigido, codigoAlvo);
//        }
//
//        try {
//            JsonNode messagesNode = objectMapper.createArrayNode()
//                    .add(objectMapper.createObjectNode()
//                            .put("role", "system")
//                            .put("content", "Você é um especialista em correção de código seguro."))
//                    .add(objectMapper.createObjectNode()
//                            .put("role", "user")
//                            .put("content", prompt));
//
//            JsonNode payloadNode = objectMapper.createObjectNode()
//                    .put("model", openaiModel)
//                    .set("messages", messagesNode);
//
//            String payload = objectMapper.writeValueAsString(payloadNode);
//
//            HttpHeaders headers = new HttpHeaders();
//            headers.set("Authorization", "Bearer " + openaiApiKey);
//            headers.setContentType(MediaType.APPLICATION_JSON);
//            HttpEntity<String> entity = new HttpEntity<>(payload, headers);
//
//            String apiUrl = "https://api.openai.com/v1/chat/completions";
//
//            ResponseEntity<String> response = restTemplate.exchange(apiUrl, HttpMethod.POST, entity, String.class);
//            String responseBody = response.getBody();
//
//            logger.info("🧠 Resposta bruta do ChatGPT: {}", tratarResponseGPT(responseBody));
//
//            JsonNode json = objectMapper.readTree(responseBody);
//            String conteudo = json.path("choices").get(0).path("message").path("content").asText().trim();
//
//            if (conteudo.isBlank()) {
//                return "Erro: resposta vazia do modelo ChatGPT.";
//            }
//
//            String somenteCodigo = extrairCodigosMarkdown(conteudo);
//            return somenteCodigo.isEmpty() ? conteudo : somenteCodigo;
//
//        } catch (Exception e) {
//            logger.error("💥 Erro no fallback com ChatGPT: {}", e.getMessage(), e);
//            return "Erro ao usar ChatGPT.";
//        }
//    }

    public String gerarCorrecaoViaChatGPT(String tipo, String codigoOriginal, String codigoCorrigido, String codigoAlvo) {
        logger.info("🤖 Iniciando fallback com ChatGPT...");

        String prompt;
        if (codigoCorrigido == null || codigoCorrigido.isBlank()) {
            prompt = PromptUtils.generatePromptWithOutBase(tipo, codigoAlvo);
        } else {
            prompt = PromptUtils.generatePrompt(tipo, codigoCorrigido, codigoAlvo);
        }

        try {
            JsonNode messagesNode = objectMapper.createArrayNode()
                    .add(objectMapper.createObjectNode()
                            .put("role", "system")
                            .put("content", "Você é um especialista em correção de código seguro."))
                    .add(objectMapper.createObjectNode()
                            .put("role", "user")
                            .put("content", prompt));

            JsonNode payloadNode = objectMapper.createObjectNode()
                    .put("model", openaiModel)
                    .set("messages", messagesNode);

            String payload = objectMapper.writeValueAsString(payloadNode);

            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", "Bearer " + openaiApiKey);
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<String> entity = new HttpEntity<>(payload, headers);

            String apiUrl = "https://api.openai.com/v1/chat/completions";

            ResponseEntity<String> response = restTemplate.exchange(apiUrl, HttpMethod.POST, entity, String.class);
            String responseBody = response.getBody();

            logger.info("🧠 Resposta bruta do ChatGPT: {}", tratarResponseGPT(responseBody));

            JsonNode json = objectMapper.readTree(responseBody);
            String conteudo = json.path("choices").get(0).path("message").path("content").asText().trim();

            if (conteudo.isBlank()) {
                logger.error("❌ Conteúdo vazio vindo do ChatGPT.");
                return "Erro: resposta vazia do modelo ChatGPT.";
            }

            String somenteCodigo = extrairCodigosMarkdown(conteudo);

            if (somenteCodigo == null || somenteCodigo.isBlank()) {
                logger.warn("⚠️ Nenhum código detectado no markdown. Usando conteúdo bruto...");
                return conteudo;
            }

            return somenteCodigo;

        } catch (Exception e) {
            logger.error("💥 Erro no fallback com ChatGPT: {}", e.getMessage(), e);
            return "Erro ao usar ChatGPT.";
        }
    }


    public String sugerirComFallback(
            String tipo,
            String exemplo,
            String correcao,
            String alvo,
            String origemId,
            BlocoSimilarDTO bloco
    ) {
        String resposta = sugerirCorrecaoViaPython(tipo, exemplo, correcao, alvo, origemId, bloco);

        // Respostas muito curtas são provavelmente inválidas
        boolean deveUsarFallback = resposta == null || resposta.isBlank() || resposta.trim().length() < 5 || resposta.toLowerCase().contains("erro");

        if (deveUsarFallback) {
            logger.warn("⚠️ Sugestão do CodeT5 inválida. Ativando fallback com GPT...");

            resposta = gerarCorrecaoViaChatGPT(tipo, exemplo, correcao, alvo);

            if (resposta == null || resposta.isBlank()) {
                logger.error("❌ GPT também não retornou uma resposta válida.");
                return "Erro: nenhuma sugestão de correção foi gerada.";
            }

            logger.info("✅ Sugestão gerada com sucesso via GPT.");
        } else {
            logger.info("✅ Sugestão válida recebida do modelo CodeT5.");
        }

        return resposta;
    }

    private String tratarResponseGPT(String responseBody) {
        try {
            JsonNode rootNode = objectMapper.readTree(responseBody);

            String content = rootNode.path("choices").get(0).path("message").path("content").asText();
            int promptTokens = rootNode.path("usage").path("prompt_tokens").asInt();
            int completionTokens = rootNode.path("usage").path("completion_tokens").asInt();
            int totalTokens = rootNode.path("usage").path("total_tokens").asInt();

            return String.format(
                    "\n✅ Conteúdo sugerido:\n%s\n\n🔢 Tokens usados - Prompt: %d | Completion: %d | Total: %d",
                    content, promptTokens, completionTokens, totalTokens
            );
        } catch (Exception e) {
            logger.error("💥 Erro ao tratar a resposta do ChatGPT: {}", e.getMessage(), e);
            return "Erro: resposta inválida recebida do ChatGPT.";
        }
    }



    public static String extrairCodigosMarkdown(String texto) {
        StringBuilder codigos = new StringBuilder();
        Pattern pattern = Pattern.compile("(?s)```(?:\\w+)?\\s*(.*?)```");
        Matcher matcher = pattern.matcher(texto);

        while (matcher.find()) {
            codigos.append(matcher.group(1).trim()).append("\n\n");
        }

        return codigos.toString().trim();
    }
}
