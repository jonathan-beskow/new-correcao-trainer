package com.example.demo.controller;

import com.example.demo.dto.TipoContagemDTO;
import org.bson.Document;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.aggregation.Aggregation;
import org.springframework.data.mongodb.core.aggregation.AggregationOperation;
import org.springframework.data.mongodb.core.aggregation.AggregationResults;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@RestController
public class RelatorioController {

    private static final Logger log = LoggerFactory.getLogger(RelatorioController.class);

    @Autowired
    private MongoTemplate mongoTemplate;

    @GetMapping("/estatisticas/tipos")
    public List<TipoContagemDTO> contarTiposDeVulnerabilidade() {
        log.info("⏳ Iniciando agregação para contar tipos de vulnerabilidades...");

        List<AggregationOperation> operations = new ArrayList<>();

        // 🔍 Match inicial para garantir que o campo 'tipo' está preenchido
        log.info("🔍 Adicionando etapa $match (filtrando 'tipo' nulo ou vazio)");
        operations.add(context -> new Document("$match",
                new Document("tipo", new Document("$nin", Arrays.asList(null, "")))
        ));

        // 🔧 Normaliza o campo com trim + lowercase
        log.info("📦 Adicionando etapa $addFields (normalização de 'tipo')");
        operations.add(context -> new Document("$addFields",
                new Document("tipoNormalizado", new Document("$toLower",
                        new Document("$trim", new Document("input", "$tipo"))
                ))
        ));

        // 📊 Agrupamento por tipoNormalizado
        log.info("📊 Adicionando etapa $group");
        operations.add(context -> new Document("$group",
                new Document("_id", "$tipoNormalizado")
                        .append("total", new Document("$sum", 1))
        ));

        // ↕️ Ordenação decrescente por total
        log.info("↕️ Adicionando etapa $sort");
        operations.add(context -> new Document("$sort",
                new Document("total", -1)
        ));

        // 🔧 Construção da agregação
        Aggregation agg = Aggregation.newAggregation(operations);

        // 🧪 Log do pipeline gerado (útil para debugging)
        operations.forEach(op -> log.debug("🔎 Etapa do pipeline: {}", op.toDocument(null).toJson()));

        // 🚀 Execução
        log.info("🚀 Executando agregação no MongoDB...");
        AggregationResults<Document> results = mongoTemplate.aggregate(agg, "casosCorrigidos", Document.class);

        List<Document> rawResults = results.getMappedResults();
        log.info("📋 Total de documentos retornados: {}", rawResults.size());
        rawResults.forEach(doc -> log.info("📄 Documento: {}", doc.toJson()));

        log.info("✅ Agregação finalizada com sucesso.");

        return rawResults.stream()
                .map(doc -> new TipoContagemDTO(
                        doc.getString("_id"),
                        ((Number) doc.get("total")).longValue()
                ))
                .collect(Collectors.toList());
    }

}
